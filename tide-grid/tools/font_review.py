"""Audit every generated clock atlas and create all-style comparison images."""
from collections import defaultdict
from pathlib import Path
import argparse
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont

from generate import FONTS, OUT, REPO
sys.path.insert(0, str(REPO / "skills/garmin-watchface-replica/scripts"))
from pixel_review import atlas as audit

SAMPLES = ("0123456789", "10:08", "11:11", "23:59")
FIRST = {"fenix847mm": "fenix8", "instinct3solar45mm": "instinct3"}


def typeface(size):
    for path in ("/System/Library/Fonts/Helvetica.ttc", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def load(path):
    with Image.open(path.with_suffix(".png")) as image:
        coverage = image.getchannel("A") if image.mode == "RGBA" else image.convert("L")
    data = {}
    for line in path.read_text().splitlines():
        if line.startswith("char "):
            item = {key: int(value) for key, value in re.findall(r"(\w+)=(-?\d+)", line)}
            x, y, w, h = (item[k] for k in ("x","y","width","height"))
            data[chr(item["id"])] = coverage.crop((x,y,x+w,y+h)), item["xadvance"]
    return data


def sample(path, text, scale, dark=True):
    data = load(path)
    height = next(iter(data.values()))[0].height
    mask = Image.new("L", (sum(data[c][1] for c in text), height))
    pen = 0
    for c in text:
        glyph, advance = data[c]
        mask.paste(glyph, (pen,0))
        pen += advance
    out = Image.new("RGB", mask.size, "#101f22" if dark else "#ffffff")
    out.paste("#e9f5e9" if dark else "#000000", (0,0,*mask.size), mask)
    return out.resize((out.width * scale, out.height * scale), Image.Resampling.NEAREST)


def sheet(folder, filename, headline, scale, dark):
    margin = 30
    faces = [folder / f"{name}.fnt" for name in FONTS]
    widgets = [[sample(path, phrase, scale, dark) for phrase in SAMPLES] for path in faces]
    font = typeface(23)
    width = max(widgets[0][0].width + margin*2, sum(im.width for im in widgets[0][1:]) + margin*4)
    row_height = widgets[0][0].height * 2 + 88
    title_space = 85
    sheet = Image.new("RGB", (width, title_space + len(faces)*row_height), "#101f22" if dark else "#ffffff")
    canvas = ImageDraw.Draw(sheet)
    ink = "#9acdc1" if dark else "#222222"
    canvas.text((margin,30), headline, font=font, fill=ink)
    for index, (path, row) in enumerate(zip(faces, widgets)):
        y = title_space + index * row_height
        canvas.text((margin,y), path.stem.upper(), font=font, fill=ink)
        sheet.paste(row[0], (margin,y+30))
        x = margin
        for image in row[1:]:
            sheet.paste(image, (x,y+43+row[0].height))
            x += image.width + margin
    sheet.save(filename)


def instrument_sheet(folder, filename, headline, scale, dark):
    font = folder / "Instrument.fnt"
    rows = [
        ("SECONDS", "0123456789  50  59"),
        ("DATA / NUMBERS", "0123456789  -6°C  86%  6.3KM  15:34"),
        ("DATA / LETTERS", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        ("ICONS / READOUTS", "c d e f g h i j k l m n o p"),
        ("ICONS / WEATHER", " ".join(chr(0x100+i) for i in range(13))),
    ]
    samples = [sample(folder / "Seconds.fnt" if name == "SECONDS" else font, text.replace(" ", "") if name == "SECONDS" else text, scale, dark)
               for name, text in rows]
    background = "#101f22" if dark else "#ffffff"
    ink = "#9acdc1" if dark else "#222222"
    label = typeface(19)
    width = max(im.width for im in samples) + 48
    height = 65 + sum(im.height + 54 for im in samples)
    result = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(result)
    draw.text((24, 22), headline, fill=ink, font=label)
    y = 65
    for (name, _), im in zip(rows, samples):
        draw.text((24, y), name, fill=ink, font=label)
        result.paste(im, (24, y+24))
        y += im.height+54
    result.save(filename)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    configs = json.loads((OUT / "device-matrix.json").read_text())
    collected = defaultdict(list)
    for p in configs:
        collected[p["fontResources"]].append(p)
    checked = []
    for key, devices in collected.items():
        folder = OUT / "profiles" / key / "fonts"
        antialias = devices[0]["antialias"]
        for name in (*FONTS, "Seconds"):
            path = folder / f"{name}.fnt"
            record = audit(path, out/"font-metrics"/key/f"{name}.json", "light" if antialias else "dark", not antialias)
            assert not record["errors"], (path, record)
            checked.append({"profile": key, "font": name, "devices": [p["device"] for p in devices], **record})
        font_paths = [p for p in devices if p["device"] in FIRST]
        for p in font_paths:
            name = FIRST[p["device"]]
            kind = "AMOLED coverage" if antialias else "1-bit pixels"
            sheet(folder, out/f"fonts-{name}.png", f"TIDE GRID   /   {p['display']}   /   {kind}",
                  2 if antialias else 4, antialias)
            instrument_sheet(folder, out/f"instrument-{name}.png", f"TIDE GRID   /   {name.upper()} READOUT",
                             2 if antialias else 4, antialias)
    (out/"font-audit.json").write_text(json.dumps(checked,indent=2)+"\n")
    print(f"{len(checked)} time and seconds atlases audited")

if __name__ == "__main__":
    main()
