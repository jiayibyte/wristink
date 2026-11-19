"""Extract the named Tide Grid station subset from PANGAEA TICON-3."""
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import hashlib
import json
import math

from uptide import tidal

ROOT = Path(__file__).resolve().parents[1]
TERMS = ("M2", "S2", "N2", "K2", "K1", "O1", "P1", "Q1", "J1", "L2", "2N2",
         "M4", "MS4", "MN4", "M6", "SA", "SSA")
# These are the published gauge coordinates, in decimal degrees. The catalogue
# order is part of the app settings contract. Add new locations at the end.
PORTS = [
    ("DALIAN", "CHINA", 38.925, 121.658), ("RIZHAO", "CHINA", 35.383, 119.550),
    ("LIANYUNGANG", "CHINA", 34.750, 119.417), ("KANMEN", "CHINA", 28.088, 121.282),
    ("XIAMEN", "CHINA", 24.450, 118.067), ("SHANWEI", "CHINA", 22.750, 115.350),
    ("ZHAPO", "CHINA", 21.583, 111.833), ("HAIKOU", "CHINA", 20.017, 110.283),
    ("BEIHAI", "CHINA", 21.483, 109.083), ("BASUO", "CHINA", 19.100, 108.617),
    ("KEELUNG", "TAIWAN", 25.155, 121.752), ("KAOHSIUNG", "TAIWAN", 22.615, 120.288),
    ("TOKYO", "JAPAN", 35.637, 139.754), ("YOKOHAMA", "JAPAN", 35.454, 139.644),
    ("OSAKA", "JAPAN", 34.658, 135.433), ("SINGAPORE", "SINGAPORE", 1.262, 103.853),
    ("SYDNEY", "AUSTRALIA", -33.855, 151.226), ("BRISBANE", "AUSTRALIA", -27.367, 153.167),
    ("AUCKLAND", "NEW ZEALAND", -36.850, 174.767), ("WELLINGTON", "NEW ZEALAND", -41.283, 174.783),
    ("VANCOUVER", "CANADA", 49.290, 236.890), ("HALIFAX", "CANADA", 44.667, 296.417),
    ("SAN FRANCISCO", "USA", 37.806, 237.534), ("SAN DIEGO", "USA", 32.713, 242.827),
    ("NEW YORK", "USA", 40.701, 285.986), ("HONOLULU", "USA", 21.307, 202.133),
    ("PORTSMOUTH", "UK", 50.800, 358.890), ("BREST", "FRANCE", 48.383, 355.505),
    ("CASCAIS", "PORTUGAL", 38.692, 350.583), ("CAPE TOWN", "SOUTH AFRICA", -33.900, 18.433),
]
# NOAA positions used by earlier installations that can be matched directly.
LEGACY = {"SAN FRANCISCO": "9414290", "SAN DIEGO": "9410170", "NEW YORK": "8518750",
          "HONOLULU": "1612340"}


def extract(path):
    groups = {}
    keep = {(lat, lon) for _, _, lat, lon in PORTS}
    for row in path.read_text().splitlines():
        fields = row.split("\t")
        if len(fields) != 14:
            continue
        lat, lon, name, amp, phase, _, _, missing, size, _, start, end, source, kind = fields
        coords = float(lat), float(lon)
        if coords in keep and kind == "Coastal":
            group = (coords, start, end, source, int(size), float(missing))
            groups.setdefault(group, {})[name] = float(amp), float(phase)
    stations = []
    for title, region, lat, lon in PORTS:
        candidates = [g for g, values in groups.items() if g[0] == (lat, lon) and all(c in values for c in TERMS)]
        assert candidates, title
        group = max(candidates, key=lambda g:g[4]*(1-g[5]/100))
        result = []
        for term in TERMS:
            amplitude, phase = groups[group][term]
            result += [round(amplitude*10), round(phase*100)%36000]
        stations.append({
            "name": title, "region": region, "lat": lat, "lon": (lon+180)%360-180,
            "amplitudeTenthCM_phaseHundredthDeg": result,
            "record": {"start": group[1], "end": group[2], "source": group[3]},
            **({"legacyNoaa": LEGACY[title]} if title in LEGACY else {}),
        })
    reference = datetime(2026, 1, 1)
    day_after = reference + timedelta(days=1)
    engine = []
    for name in TERMS:
        phase = float(tidal.tidal_arguments((name,), reference)[0])
        tomorrow = float(tidal.tidal_arguments((name,), day_after)[0])
        engine.append({
            "term": name, "phase": round(phase % (2*math.pi), 9),
            "driftPerDay": round(tomorrow-phase, 10),
            "advance1800": float(tidal.omega[name])*1800,
            "f0": tidal.nodal_correction_f0.get(name,1), "f1": tidal.nodal_correction_f1.get(name,0),
            "u1": tidal.nodal_correction_u1.get(name,0),
        })
    nodal = tidal.astronomical_argument(reference)[4]
    next_nodal = tidal.astronomical_argument(day_after)[4]
    output = {"citation": "Hart-Davis, Dettmering & Seitz (2022), TICON-3, PANGAEA.951610",
              "source": "https://doi.org/10.1594/PANGAEA.951610", "license": "CC BY 4.0",
              "sourceSha256": hashlib.sha256(path.read_bytes()).hexdigest(), "stations": stations,
              "epochUnixDay": (reference - datetime(1970,1,1)).days,
              "lunarNode": [math.radians(nodal) % (2*math.pi), math.radians(next_nodal - nodal)],
              "constituents": engine}
    return output


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("source",type=Path)
    args=cli.parse_args()
    data=extract(args.source)
    (ROOT/"assets/tide-ports.json").write_text(json.dumps(data,indent=2)+"\n")
    print(len(data["stations"]),"coastal gauges", len(data["constituents"]), "harmonic constituents each")
