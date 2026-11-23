"""Build and audit signed PRGs, or export the Connect IQ store package."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess

from generate import ROOT, THEMES, generate

WINDOWS = os.name == "nt"
import sys; sys.path.append(str(ROOT.parent / "tools")); import ciq_env
SDK_CONFIG = ciq_env.CIQ_HOME / "current-sdk.cfg"
KEY = Path(os.environ.get("CIQ_KEY", Path.home() / ".Garmin/keys/developer_key.der"))
RECOMMENDED = 50_000
HARD_CAP = 100_000


def build(args):
    if not args.no_generate:
        generate(args.preview, args.fixture, args.theme, args.font, args.test)
    output = ROOT / "bin"
    output.mkdir(exist_ok=True)
    sdk = Path(os.environ["CIQ_SDK"]) if "CIQ_SDK" in os.environ else Path(SDK_CONFIG.read_text().strip())
    env = dict(os.environ)
    env = ciq_env.java_env(env)
    env["JAVA_TOOL_OPTIONS"] = (env.get("JAVA_TOOL_OPTIONS", "") + " -Djava.awt.headless=true").strip()
    command = [str(sdk / "bin" / ("monkeyc.bat" if WINDOWS else "monkeyc")), "-f", "preview.jungle" if args.preview else "monkey.jungle",
               "-y", str(KEY), "-O", "3z", "-w", "--no-gen-styles"]
    if not args.test:
        command += ["-r"]

    def compile_one(flags, package):
        log = output / f"{package.stem}.log"
        package.parent.mkdir(parents=True, exist_ok=True)
        # monkeyc caches compiled resources by position next to the output;
        # a changed font list must not be served from a stale cache.
        for stale in ("gen", "mir", "internal-mir", "external-mir"):
            shutil.rmtree(package.parent / stale, ignore_errors=True)
        with log.open("w") as report:
            result = subprocess.run(command+flags+["-o", str(package)], cwd=ROOT, env=env,
                                    stdout=report, stderr=subprocess.STDOUT)
        if result.returncode:
            print(log.read_text(), flush=True)
            raise RuntimeError(f"Compile failed: {package.name} ({log})")

    if args.preview:
        name = f"tests-{args.preview}" if args.test else f"demo-{args.preview}-{args.fixture}-{args.theme}-{args.font}"
        package = output / f"{name}.prg"
        compile_one(["-d", args.preview] + (["-t"] if args.test else []), package)
        print(f"{package.stat().st_size:>7} B  {package}")
        return
    if args.store:
        if args.device:
            raise SystemExit("--store exports every hardware variant in the manifest.")
        from inspect_store import inspect
        distribution = ROOT / "dist"
        distribution.mkdir(exist_ok=True)
        package = distribution / "TideGrid-1.0.0.iq"
        compile_one(["-e"], package)
        inspect(package, distribution / "store-audit.json", sdk)
        return
    matrix = json.loads((ROOT / "generated/device-matrix.json").read_text())
    by_device = {x["device"]: x for x in matrix}
    devices = args.device or list(by_device)
    if any(device not in by_device for device in devices):
        raise SystemExit("Unknown device. See generated/device-matrix.json.")

    def compile_device(device):
        package = output / "devices" / device / f"TideGrid-{device}.prg"
        compile_one(["-d", device], package)
        size = package.stat().st_size
        if size > HARD_CAP:
            raise RuntimeError(f"{device} exceeds {HARD_CAP} B hard cap: {size} B")
        print(f"{size:>7} B  {device}", flush=True)
        return {**by_device[device], "prgBytes": size, "meets50k": size <= RECOMMENDED,
                "sha256": hashlib.sha256(package.read_bytes()).hexdigest()}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        rows = list(pool.map(compile_device, devices))
    (output / ("sizes.json" if len(rows) == len(matrix) else "sample-sizes.json")).write_text(
        json.dumps(rows, indent=2)+"\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", action="append")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--store", action="store_true")
    parser.add_argument("--no-generate", action="store_true")
    parser.add_argument("--preview")
    parser.add_argument("--test", action="store_true", help="include tests in a preview build")
    parser.add_argument("--fixture", choices=("tide", "steps", "heart", "distance", "calories"), default="tide")
    parser.add_argument("--theme", type=int, choices=range(len(THEMES)), default=0)
    parser.add_argument("--font", type=int, choices=range(3), default=0)
    args = parser.parse_args()
    if args.test and not args.preview:
        parser.error("--test requires --preview DEVICE")
    build(args)
