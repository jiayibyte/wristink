"""Build the phone-only settings regression against a production device profile."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--device", default="instinct2x")
args = parser.parse_args()
row = next(item for item in json.loads((ROOT / "config/mip-devices.json").read_text()) if item["id"] == args.device)
if row["on_watch_settings"]:
    raise SystemExit("This regression targets devices with phone-only settings.")
folder = ROOT / "bin/settings-regression" / args.device
folder.mkdir(parents=True, exist_ok=True)
ns = "http://www.garmin.com/xml/connectiq"
ET.register_namespace("iq", ns)
tree = ET.parse(ROOT / "manifest.xml")
tree.getroot().find("{" + ns + "}application").set("id", uuid.uuid5(uuid.NAMESPACE_DNS, "moke-phone-settings-regression-" + args.device).hex)
tree.write(folder / "manifest.xml", encoding="utf-8")
lines = (ROOT / "monkey.jungle").read_text().splitlines()
setting = lambda suffix: next(line.split(" = ")[1] for line in lines if line.startswith(args.device + suffix))
absolute = lambda value: ";".join(str(ROOT / part) for part in value.split(";"))
(folder / "test.jungle").write_text("project.manifest = manifest.xml\nbase.sourcePath = " + absolute(setting(".sourcePath")) + ";" + str(Path(__file__).resolve().parent) + "\nbase.resourcePath = " + absolute(setting(".resourcePath")) + "\n")
env = dict(os.environ, JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home")
env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]
result = subprocess.run(["monkeyc", "-f", str(folder / "test.jungle"), "-d", args.device, "-o", str(folder / "test.prg"), "-y", str(Path.home() / ".Garmin/keys/developer_key.der"), "-t", "-w"], env=env, capture_output=True, text=True)
(folder / "build.log").write_text(result.stdout + result.stderr)
print(args.device, "COMPILED" if result.returncode == 0 else (result.stdout + result.stderr)[-1800:])
raise SystemExit(result.returncode)
