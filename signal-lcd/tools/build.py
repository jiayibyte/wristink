"""Generate native resources, compile one or more targets, or export a signed IQ."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw

from settings import FIELDS, generate as settings_resources
from themes import THEME_NAMES, display_palettes, rgb
from typefaces import aod_font, clock_fonts, data_fonts, data_heights, window_fonts, window_heights, write_atlas

ROOT = Path(__file__).resolve().parents[1]
CIQ = Path(os.environ.get("CIQ_HOME", Path.home() / "Library/Application Support/Garmin/ConnectIQ"))
KEY = Path(os.environ.get("CIQ_KEY", Path.home() / ".Garmin/keys/developer_key.der"))
APP_ID = "ba601b9abc3a44c89a481f1da0234faa"
VERSION = "1.0.1"
NS = "http://www.garmin.com/xml/connectiq"
ET.register_namespace("iq", NS)
LIMIT = 100_000


def profile(id):
    pack = CIQ/"Devices"/id
    c = json.loads((pack/"compiler.json").read_text())
    s = json.loads((pack/"simulator.json").read_text())
    # SDK resolution and compiler device family normally agree. The family
    # records the drawable framebuffer when the bezel extends the skin rect.
    w,h = map(int,c["deviceFamily"].split("-")[-1].split("x"))
    size = min(w,h)
    mono = c["bitsPerPixel"] == 1
    amoled = c["displayType"] == "amoled"
    sub = None if amoled else s.get("subscreen")
    cx = cy = 0
    r = -1
    if sub:
        bounds = sub["location"]
        lcd = s["display"]["location"]
        cx = bounds["x"] - lcd["x"] + bounds["width"]//2 - max(0,lcd["width"]-w)
        cy = bounds["y"] - lcd["y"] + bounds["height"]//2
        r = min(bounds["width"],bounds["height"])//2 - (2 if mono else round(size*.015))
    # Preserve the reference drawing coordinates on regular screens. Reserve
    # the upper physical aperture on window models and rebuild fonts natively.
    lcd_size = round(size*.88) if sub else size
    lcd_y = (h-size)//2
    if sub:
        top = round(size*.437)
        lcd_y += top-round(lcd_size*.203)
    return {
        "lcd_size": lcd_size, "lcd_x": (w-lcd_size)//2, "lcd_y": lcd_y,
        "id": id, "name": c["displayName"], "width": w, "height": h, "size": size,
        "shape": s["display"]["shape"], "cx": cx, "cy": cy, "r": r,
        "window_default": (1 if id.startswith("instinct") else 2) if sub else 0,
        "mono": mono, "amoled": amoled, "aa": amoled and c.get("antiAliasedFontSupport") is not False,
        "palettes": display_palettes(c,mono,amoled),
        "launcher": c["launcherIcon"], "parts": len(c["partNumbers"]),
        "ram": next(a["memoryLimit"] for a in c["appTypes"] if a["type"]=="watchFace"),
    }


def mc(value):
    if isinstance(value,bool):
        return "true" if value else "false"
    if isinstance(value,list):
        return "["+",".join(map(mc,value))+"]"
    return str(value)


def make_profile(dest, d, demo):
    s = d["size"]
    lcd_size = d["lcd_size"]
    profile_vars = {
        "SIZE": s, "X": (d["width"]-s)//2, "Y": (d["height"]-s)//2,
        "LCD_SIZE": lcd_size, "LCD_X": d["lcd_x"], "LCD_Y": d["lcd_y"],
        "CX": d["cx"], "CY": d["cy"], "XR": d["r"], "WINDOW_DEFAULT": d["window_default"],
        "MONO": d["mono"], "AMOLED": d["amoled"],
        "THEME_MAX": len(THEME_NAMES)-1, "COLORS": d["palettes"],
        "TIME_GAP": max(2,round(lcd_size*.012)), "AOD_H": round(s*.089),
        "AOD_GAP": max(3,round(s*.061)//6),
        "DEMO": demo is not None, "EXTREME": bool(demo and demo["extreme"]),
        "HOUR": demo["hour"] if demo else 10, "MINUTE": demo["minute"] if demo else 8,
        "AOD_PREVIEW": bool(demo and demo["aod"] is not None), "AOD_PHASE": (demo["aod"] or 0) if demo else 0,
    }
    heights = data_heights(lcd_size)
    window = window_heights(d["r"])
    heights.update({"WINDOW_VALUE":window["WindowValue"],"WINDOW_SYMBOL":window["WindowSymbol"]})
    for name,height in heights.items():
        profile_vars[name.upper()+"_H"] = height
        profile_vars[name.upper()+"_GAP"] = max(1,round(height*.105))
    data = "module Profile {\n"
    data += "".join(f"    const {key} = {mc(value)};\n" for key,value in profile_vars.items())
    stamp = int(datetime(2030,6,30,12,tzinfo=timezone.utc).timestamp())
    data += f"    var DEMO_DATE = new Toybox.Time.Moment({stamp});\n"
    value_id = "WindowValue" if d["r"] >= 0 else "Value"
    symbol_id = "WindowSymbol" if d["r"] >= 0 else "Symbol"
    data += f"    function windowValueId() {{ return Rez.Fonts.{value_id}; }}\n"
    data += f"    function windowSymbolId() {{ return Rez.Fonts.{symbol_id}; }}\n}}\n"
    (dest/"Profile.mc").write_text(data)


@lru_cache(maxsize=64)
def glyphs(size, aa, lcd_size=None):
    lcd_size = lcd_size if lcd_size is not None else size
    return {**clock_fonts(lcd_size, aa), **data_fonts(lcd_size, aa), "AlwaysOn": aod_font(size)}


def make_resources(dest, d, demo):
    dest.mkdir(parents=True,exist_ok=True)
    settings_resources(dest, demo["settings"] if demo else {}, "Signal LCD Preview" if demo else "Signal LCD", d["window_default"], d["mono"])
    fonts = ET.Element("fonts")
    families = glyphs(d["size"], d["aa"], d["lcd_size"]).copy()
    if d["r"] >= 0:
        families.update(window_fonts(d["r"]))
    for name,family in families.items():
        write_atlas(dest/name,family)
        attrs = {"id": name, "filename": f"{name}.fnt"}
        if d["aa"] and name in ("Segment","Contour","Matrix","Date","Seconds"):
            attrs["antialias"] = "true"
        ET.SubElement(fonts,"font",attrs)
    ET.ElementTree(fonts).write(dest/"fonts.xml")
    drawables = ET.Element("drawables")
    ET.SubElement(drawables,"bitmap",id="LauncherIcon",filename="launcher.png")
    ET.ElementTree(drawables).write(dest/"drawables.xml")
    icon = Image.new("RGB",(30,30),0x160e08)
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle((1,5,28,24),radius=4,outline="#67DFCE",width=2)
    draw.line([(4,15),(9,15),(12,10),(16,20),(19,15),(25,15)],fill="#FFB677",width=2)
    launcher = d["launcher"]
    icon.resize((launcher["width"],launcher["height"]),Image.Resampling.NEAREST).save(dest/"launcher.png")


def manifest(path, ids, demo):
    elem = ET.Element(f"{{{NS}}}manifest",version="3")
    app = ET.SubElement(elem,f"{{{NS}}}application",type="watchface",name="@Strings.AppName",
                        entry="SignalApp",launcherIcon="@Drawables.LauncherIcon",minApiLevel="3.2.0",
                        id=demo["id"] if demo else APP_ID,version=VERSION)
    products = ET.SubElement(app,f"{{{NS}}}products")
    for id in ids:
        ET.SubElement(products,f"{{{NS}}}product",id=id)
    ET.SubElement(app,f"{{{NS}}}permissions")
    languages = ET.SubElement(app,f"{{{NS}}}languages")
    ET.SubElement(languages,f"{{{NS}}}language").text = "eng"
    ET.SubElement(app,f"{{{NS}}}barrels")
    ET.indent(elem)
    ET.ElementTree(elem).write(path,encoding="utf-8",xml_declaration=True)


def jungle(dest, devices, demo):
    dest.mkdir(parents=True,exist_ok=True)
    manifest(dest/"manifest.xml",[d["id"] for d in devices],demo)
    content = ["project.manifest = manifest.xml", f"base.sourcePath = {ROOT/'source'}"]
    for d in devices:
        target = dest/d["id"]
        make_resources(target/"resources",d,demo)
        make_profile(target,d,demo)
        content.extend([f"{d['id']}.sourcePath = $(base.sourcePath);{d['id']}/Profile.mc",
                        f"{d['id']}.resourcePath = {d['id']}/resources"])
    path = dest/"monkey.jungle"
    path.write_text("\n".join(content)+"\n")
    return path


def compiler(config, artifact, device):
    if os.environ.get("CIQ_SDK"):
        sdk = Path(os.environ["CIQ_SDK"])
    else:
        sdk = Path((CIQ/"current-sdk.cfg").read_text().strip())
    env = os.environ.copy()
    java_home = Path(env.get("JAVA_HOME", "/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"))
    if java_home.is_dir():
        env["PATH"] = str(java_home/"bin") + os.pathsep + env["PATH"]
    args = [str(sdk/"bin/monkeyc"), "-f", str(config), "-o", str(artifact),
            "-y", str(KEY), "-r", "-O", "3z", "-l", "1", "-w", "--no-gen-styles",
            "--disable-api-has-check-removal"]
    args += ["-d",device] if device else ["-e"]
    log = artifact.with_suffix(".log")
    with log.open("w") as stream:
        result = subprocess.run(args,cwd=config.parent,env=env,stdout=stream,stderr=subprocess.STDOUT)
    if result.returncode or not artifact.is_file():
        print(log.read_text()[-9000:],flush=True)
        return None
    size = artifact.stat().st_size
    if device and size > LIMIT:
        print(f"{device}: {size} bytes exceeds the {LIMIT} byte limit",flush=True)
        return None
    return {"bytes": size, "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("devices",nargs="*")
    ap.add_argument("--jobs",type=int,default=3)
    ap.add_argument("--out",type=Path,default=ROOT/"bin")
    ap.add_argument("--export",action="store_true")
    ap.add_argument("--demo",metavar="NAME")
    ap.add_argument("--hour",type=int,choices=range(24),default=10)
    ap.add_argument("--minute",type=int,choices=range(60),default=58)
    ap.add_argument("--settings",type=json.loads,default={})
    ap.add_argument("--extreme",action="store_true")
    ap.add_argument("--always-on",type=int,choices=range(4))
    args = ap.parse_args()
    targets = json.loads((ROOT/"devices.json").read_text())
    ids = args.devices or targets
    if len(set(ids)) != len(ids) or not set(ids) <= set(targets):
        ap.error("all target IDs must be unique and present in devices.json")
    if not set(args.settings) <= set(FIELDS):
        ap.error("unknown setting")
    if args.demo and args.export:
        ap.error("the IQ export must use live data")
    if args.jobs < 1:
        ap.error("--jobs must be positive")
    devices = [profile(id) for id in ids]
    dest = args.out.resolve()
    if args.export:
        config = jungle(dest/"export",devices,None)
        artifact = dest/f"Signal-LCD-{VERSION}.iq"
        result = compiler(config,artifact,None)
        if result:
            print(artifact,result,flush=True)
        return int(result is None)

    if args.demo:
        dest /= "demo"
        dest /= args.demo

    def single(d):
        id = d["id"]
        demo = None
        if args.demo:
            demo = dict(hour=args.hour, minute=args.minute, extreme=args.extreme,
                        aod=args.always_on,settings={"TimeFormat":2,**args.settings})
            demo["id"] = uuid.uuid5(uuid.UUID(APP_ID),json.dumps([id,args.demo,demo],sort_keys=True)).hex
        config = jungle(dest/id,[d],demo)
        artifact = config.parent/("SignalDemo.prg" if demo else "SignalLCD.prg")
        result = compiler(config,artifact,id)
        print(id, result["bytes"] if result else "FAIL", flush=True)
        return {**d,"artifact":str(artifact),"build":result}

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        rows = list(pool.map(single,devices))
    (dest/"device-matrix.json").write_text(json.dumps(rows,indent=2)+"\n")
    return int(any(d["build"] is None for d in rows))


if __name__ == "__main__":
    raise SystemExit(main())
