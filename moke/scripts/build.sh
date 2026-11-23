#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
mkdir -p bin
"$sdk_path/bin/monkeyc" -f monkey.jungle -d instinct3solar45mm -o bin/InstinctFace.prg -y "$HOME/.Garmin/keys/developer_key.der" -w "$@"
