#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
"${ALPINE_PYTHON:-python3}" tools/settings.py
"${ALPINE_PYTHON:-python3}" tools/generate.py
mkdir -p bin dist
mode="${1:-live}"
jungle=monkey.jungle
[[ "$mode" == live ]] || jungle="$mode.jungle"
shift $(( $# > 0 ? 1 : 0 ))
devices=("$@")
(( ${#devices} )) || devices=(instinct3solar45mm instinct2 instinct2s instinct2x fenix7 epix2)
for device in $devices; do
  optimization=0
  [[ "$device" != instinct2 && "$device" != instinct2s && "$device" != instinct2x ]] || optimization=2z
  flags=(-r -O "$optimization")
  if [[ "$mode" == tests ]]; then
    flags=(-t)
    [[ "$optimization" != 2z ]] || flags+=(-O 2z)
  fi
  [[ "$optimization" != 2z ]] || flags+=(--disable-api-has-check-removal)
  [[ "$mode" == live ]] || jungle="$mode-$device.jungle"
  "$sdk_path/bin/monkeyc" -f "$jungle" -d "$device" -o "bin/Alpine-$device-$mode.prg" -y "$HOME/.Garmin/keys/developer_key.der" $flags -w --no-gen-styles > "bin/$device-$mode-build.log" 2>&1 || { cat "bin/$device-$mode-build.log"; exit 1; }
  echo "$device $mode: built"
done
