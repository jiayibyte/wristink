"""Exercise real settings writes, redraws and a second simulator process.

Each invocation uses a new app ID. The two launches share the exact PRG and ID;
the second launch verifies values restored by Garmin's persistent store.
"""
from pathlib import Path
import argparse
import json
import os
import signal
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("device")
parser.add_argument("--timeout", type=int, default=45)
parser.add_argument("--build-only", action="store_true")
args = parser.parse_args()
rows = {row["id"]: row for row in json.loads((ROOT / "config/mip-devices.json").read_text())}
row = rows[args.device]
folder = ROOT / "bin/settings-recovery" / args.device
folder.mkdir(parents=True, exist_ok=True)
ns = "http://www.garmin.com/xml/connectiq"
ET.register_namespace("iq", ns)
tree = ET.parse(ROOT / "manifest.xml")
app = tree.getroot().find("{" + ns + "}application")
app_id = uuid.uuid4().hex
app.set("id", app_id)
app.set("entry", "RecoveryApp")
tree.write(folder / "manifest.xml", encoding="utf-8")
lines = (ROOT / "monkey.jungle").read_text().splitlines()
setting = lambda suffix: next(line.split(" = ")[1] for line in lines if line.startswith(args.device + suffix))
absolute = lambda paths: ";".join(str(ROOT / item) for item in paths.split(";"))
source = absolute(setting(".sourcePath"))
resources = absolute(setting(".resourcePath"))
jungle = "project.manifest = manifest.xml\nbase.sourcePath = .;" + source + "\nbase.resourcePath = " + resources + "\n"
if row["renderer"] == "legacy" and row["on_watch_settings"]:
    jungle += "base.excludeAnnotations = classicPrefs\n"
(folder / "recovery.jungle").write_text(jungle)
base = "LegacyFace" if row["renderer"] == "legacy" else "InstinctFaceView"
views = "LegacyPower.views(_view)" if row["renderer"] == "legacy" else "[_view,new PowerDelegate(_view)]"
phone_probe = "var noMenu=Application.getApp().getSettingsView();if(noMenu!=null || _suspended){fail(\"empty_menu_suspended\");return;}" if not row["on_watch_settings"] else ""
program = '''import Toybox.Application;
import Toybox.System;
import Toybox.WatchUi;
class RecoveryApp extends InstinctFaceApp {
    function initialize(){InstinctFaceApp.initialize();}
    function getInitialView(){_view=new RecoveryView();return VIEWS;}
}
class RecoveryView extends BASE {
    var _recoveryStage=0;var _secondLaunch=false;
    function initialize(){BASE.initialize();_secondLaunch=Application.Storage.getValue("recoveryWritten")==true;}
    function fail(reason){System.println("RECOVERY_FAIL "+reason);System.exit();}
    function valuesMatch(){return !FacePrefs.flag("darkTheme") && FacePrefs.get("timeFormat")==1 && FacePrefs.get("topOne")==2 && FacePrefs.get("sideData")==1 && FacePrefs.get("circle")==1 && !FacePrefs.flag("showWind");}
    function onUpdate(dc){
        BASE.onUpdate(dc);
        if(_recoveryStage==0 && !_secondLaunch){
            PHONE_PROBE
            _recoveryStage=1;
            var app=Application.getApp();
            app.setProperty("darkTheme",false);app.setProperty("timeFormat",1);
            app.setProperty("topOne",2);app.setProperty("sideData",1);
            app.setProperty("circle",1);app.setProperty("showWind",false);
            app.onSettingsChanged();WatchUi.requestUpdate();return;
        }
        if(_recoveryStage<2){
            _recoveryStage=2;
            if(!valuesMatch() || _suspended){fail("values_or_visibility");return;}
            if(!_secondLaunch){
                Application.Storage.setValue("recoveryWritten",true);
                System.println("RECOVERY_PHASE1_OK free="+System.getSystemStats().freeMemory);System.exit();return;
            }
            onHide();onShow();onEnterSleep();onExitSleep();BASE.onUpdate(dc);
            if(!valuesMatch() || _suspended){fail("lifecycle_restore");return;}
            System.println("RECOVERY_PHASE2_OK free="+System.getSystemStats().freeMemory);System.exit();
        }
    }
}
'''.replace("VIEWS", views).replace("BASE", base).replace("PHONE_PROBE", phone_probe)
(folder / "Recovery.mc").write_text(program)
env = dict(os.environ, JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home")
env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]
prg = folder / "recovery.prg"
build = subprocess.run(["monkeyc", "-f", str(folder / "recovery.jungle"), "-d", args.device, "-o", str(prg), "-y", str(Path.home() / ".Garmin/keys/developer_key.der"), "-r", "-O", "3z", "-w"], env=env, capture_output=True, text=True)
(folder / "build.log").write_text(build.stdout + build.stderr)
if build.returncode:
    raise SystemExit(build.stdout + build.stderr)
if args.build_only:
    print(args.device, "RECOVERY_PROBE_COMPILED", flush=True)
    raise SystemExit(0)
results = []
for phase in (1, 2):
    path = folder / ("phase" + str(phase) + ".log")
    marker = "RECOVERY_PHASE" + str(phase) + "_OK"
    with path.open("w") as log:
        proc = subprocess.Popen(["monkeydo", str(prg), args.device], env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            output = path.read_text()
            if marker in output or "RECOVERY_FAIL" in output or "app crash" in output.lower() or proc.poll() is not None:
                break
            time.sleep(.25)
        output = path.read_text()
        passed = marker in output and not any(term in output.lower() for term in ("recovery_fail", "app crash", "error:"))
        if passed:
            try:
                proc.wait(timeout=12)
            except subprocess.TimeoutExpired:
                pass
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGINT)
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
        results.append({"phase": phase, "passed": passed, "log": str(path)})
        print(args.device, phase, "PASS" if passed else output or "NO LAUNCHER OUTPUT", flush=True)
        if not passed:
            break
(folder / "result.json").write_text(json.dumps({"device": args.device, "app_id": app_id, "phases": results, "scope": "SDK simulator; production data; six setting values, redraw and separate-process persistence; not physical-device proof"}, indent=2) + "\n")
raise SystemExit(0 if len(results) == 2 and all(item["passed"] for item in results) else 1)
