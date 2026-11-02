#!/usr/bin/env python3
"""Read-only Connect IQ regional API baseline report; Python standard library."""
import argparse
import json
import re
from pathlib import Path


def api_version(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", value):
        raise ValueError(f"invalid connectIQVersion: {value!r}")
    parts = tuple(int(v) for v in value.split('.'))
    return parts + (0,) * (3 - len(parts))


def summarize(data):
    parts = data.get('partNumbers')
    if not isinstance(parts, list) or not parts:
        raise ValueError('partNumbers must contain at least one hardware variant')
    versions = []
    variants = []
    for part in parts:
        if not isinstance(part, dict):
            raise ValueError('each hardware variant must be an object')
        version = api_version(part.get('connectIQVersion'))
        versions.append(version)
        variants.append({
            'partNumber': part.get('number'),
            'api': '.'.join(map(str, version)),
            'minimumFirmware': part.get('firmwareVersion'),
        })
    limits = [a.get('memoryLimit') for a in data.get('appTypes', [])
              if isinstance(a, dict) and a.get('type') == 'watchFace']
    return {
        'device': data.get('deviceId'),
        'minimumApi': '.'.join(map(str, min(versions))),
        'mixedApi': len(set(versions)) > 1,
        'watchFaceMemoryBytes': limits[0] if limits else None,
        'variants': variants,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('compiler_json', nargs='+', type=Path)
    args = parser.parse_args()
    reports = []
    for path in args.compiler_json:
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                raise ValueError('compiler.json must be an object')
            reports.append(summarize(data))
        except (OSError, ValueError) as error:
            parser.error(f'{path}: {error}')
    print(json.dumps(reports, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
