#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
sdk_config="$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg"
sdk_path="$(tr -d '\r\n' < "$sdk_config")"
python3 tools/enable_paging.py
mkdir -p dist
"$sdk_path/bin/monkeyc" -f monkey.jungle -d instinct3solar45mm -o dist/BeijingMap-Instinct3Solar.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -w -O 3z --no-gen-styles --build-stats 0
shasum -a 256 dist/BeijingMap-Instinct3Solar.prg > dist/BeijingMap-Instinct3Solar.sha256
