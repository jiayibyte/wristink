#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
python_bin="${RETRO_PYTHON:-python3}"
version="${1:-2.2.1}"
mkdir -p bin dist
"$python_bin" tools/device_profiles.py
"$python_bin" tools/check_devices.py
"$sdk_path/bin/monkeyc" -f monkey.jungle -e -o "dist/RetroWorld-${version}.iq" -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
shasum -a 256 "dist/RetroWorld-${version}.iq" > "dist/RetroWorld-${version}.sha256"
