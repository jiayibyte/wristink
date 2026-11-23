"""Verify every shipped PRG, its English settings, and all Garmin IQ signatures."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

from generate import APP_ID, CHARTS, FONTS, TIDE_PORTS, MONO_THEMES, NS, OUT, PACKS, REPO, ROOT, SLOTS, THEMES, slot_options
import ciq_env


def inspect(package, report, sdk):
    matrix = json.loads((OUT / "device-matrix.json").read_text())
    expected = {}
    for profile in matrix:
        config = json.loads((PACKS / profile["device"] / "compiler.json").read_text())
        for part in config["partNumbers"]:
            expected[part["number"]] = profile
    locales = json.loads((ROOT / "store/localizations.json").read_text())
    reference = json.loads((REPO / "store-listings/copies.json").read_text())["moke"]
    assert set(locales) == set(reference)
    for item in locales.values():
        assert 1 <= len(item["title"]) <= 50
        assert all(1 <= len(item[key]) <= 4000 for key in ("description", "whatsNew"))
    with TemporaryDirectory(prefix="tide-grid-iq-") as folder:
        root = Path(folder)
        subprocess.run(["7zz", "x", str(package), "-o"+folder, "-y"], check=True, stdout=subprocess.DEVNULL)
        ns = {"iq": NS}
        app = ET.parse(root / "manifest.xml").getroot().find("iq:application", ns)
        assert app.get("id") == APP_ID
        assert {e.text for e in app.findall(".//iq:language", ns)} == {"eng"}
        products = app.findall(".//iq:product", ns)
        assert {p.get("partNumber") for p in products} == set(expected)
        rows = []
        for product in products:
            part = product.get("partNumber")
            profile = expected[part]
            path = root / product.get("filename")
            blob = path.read_bytes()
            assert len(blob) <= 100_000, (part, profile["device"], len(blob))
            assert all(s not in blob for s in (b"30 AUG", b"196CM", b"8:54P"))  # the demo port, CAPE TOWN, is a real catalogue entry
            settings, = path.parent.glob("*settings.json")
            data = json.loads(settings.read_text())
            items = {i["key"]: i for i in data["settings"]}
            assert set(items) == {*SLOTS, "Chart", "ClockFormat", "Theme", "TimeFont", "TidePlace", "WristSeconds"}
            mono = profile["MONO"] or profile["LOW_COLOR"]
            choices = {key: (default, slot_options(key)) for key, default in SLOTS.items()}
            choices.update({
                "Chart": (1, list(range(len(CHARTS)))), "TidePlace": (0, list(range(len(TIDE_PORTS["stations"])+1))), "ClockFormat": (0, [0, 1, 2]),
                "Theme": (MONO_THEMES[0], list(MONO_THEMES)) if mono else (0, list(range(len(THEMES)))),
                "TimeFont": (1, list(range(len(FONTS))))
            })
            for name, (default, options) in choices.items():
                item = items[name]
                assert item["defaultValue"] == default, (part, name, item)
                assert [o["value"] for o in item["configOptions"]] == options, (part, name, item)
            assert data["languages"]["valyrian"]
            rows.append({"partNumber": part, "device": profile["device"], "bytes": len(blob),
                         "sha256": hashlib.sha256(blob).hexdigest(), "sdkApi": product.get("connectIqVersion")})
        java = ciq_env.java()
        subprocess.run([java, "-cp", str(sdk / "bin/monkeybrains.jar"),
                        str(REPO / "alpine/tools/VerifyIq.java"), str(package), str(root / "dev_key.pub")], check=True)
    report.write_text(json.dumps({
        "packageBytes": package.stat().st_size, "packageSha256": hashlib.sha256(package.read_bytes()).hexdigest(),
        "signature": "verified by Garmin IQ verifier", "sdkTargets": len(matrix), "hardwareVariants": len(rows),
        "maxPrgBytes": max(r["bytes"] for r in rows),
        "over50000": [r for r in rows if r["bytes"] > 50_000], "variants": rows,
        "storeLocales": list(locales), "runtimeLanguage": "eng",
    }, ensure_ascii=False, indent=2)+"\n")
    print(f"{len(matrix)} targets, {len(rows)} signed variants; "
          f"largest installed PRG {max(r['bytes'] for r in rows):,} B; archive {package.stat().st_size:,} B")
