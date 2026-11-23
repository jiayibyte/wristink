#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
python3 tools/enable_paging.py
mkdir -p dist
"$sdk_path/bin/monkeyc" -f monkey.jungle -d instinct3solar45mm -o dist/BeijingMap-Instinct3Solar.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -w -O 3z --no-gen-styles --build-stats 0
shasum -a 256 dist/BeijingMap-Instinct3Solar.prg > dist/BeijingMap-Instinct3Solar.sha256
