#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
sdk_path="$(tr -d '\r\n' < "$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg")"
python_bin="${RETRO_PYTHON:-python3}"
mkdir -p bin dist
"$python_bin" tools/device_profiles.py
"$python_bin" tools/check_devices.py
"$sdk_path/bin/monkeyc" -f monkey.jungle -e -o dist/RetroWorld-2.0.0.iq -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
shasum -a 256 dist/RetroWorld-2.0.0.iq > dist/RetroWorld-2.0.0.sha256
