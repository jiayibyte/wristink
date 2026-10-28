#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
sdk_path="$(tr -d '\r\n' < "$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg")"
mkdir -p bin dist
python_bin="${RETRO_PYTHON:-python3}"
"$python_bin" tools/device_profiles.py
"$python_bin" - <<'PY'
from pathlib import Path
s=Path('manifest.xml').read_text().replace('d2fd1f269ea4491f9bf5c77046e0e301','d2fd1f269ea4491f9bf5c77046e0e302')
Path('preview/manifest.xml').write_text(s)
Path('tests/manifest.xml').write_text(Path('manifest.xml').read_text().replace('d2fd1f269ea4491f9bf5c77046e0e301','d2fd1f269ea4491f9bf5c77046e0e303'))
PY
"$sdk_path/bin/monkeyc" -f monkey.jungle -d instinct3solar45mm -o bin/RetroWorld-Instinct3.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
"$sdk_path/bin/monkeyc" -f preview.jungle -d instinct3solar45mm -o bin/RetroWorld-demo.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
"$sdk_path/bin/monkeyc" -f monkey.jungle -e -o dist/RetroWorld-2.0.0.iq -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
cp bin/RetroWorld-Instinct3.prg dist/RetroWorld-Instinct3.prg
shasum -a 256 dist/RetroWorld-Instinct3.prg dist/RetroWorld-2.0.0.iq > dist/SHA256SUMS
