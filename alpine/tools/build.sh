#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="${JAVA_HOME:-/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home}"
export PATH="$JAVA_HOME/bin:$PATH"
sdk_path="$(tr -d '\r\n' < "$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg")"
"${ALPINE_PYTHON:-python3}" tools/settings.py
"${ALPINE_PYTHON:-python3}" tools/generate.py
mkdir -p bin dist
mode="${1:-live}"
jungle=monkey.jungle
[[ "$mode" == live ]] || jungle="$mode.jungle"
shift $(( $# > 0 ? 1 : 0 ))
devices=("$@")
(( ${#devices} )) || devices=(instinct3solar45mm instinct2 instinct2s instinct2x fenix7 epix2)
flags=(-r -O 0)
[[ "$mode" != tests ]] || flags=(-t)
for device in $devices; do
  [[ "$mode" == live ]] || jungle="$mode-$device.jungle"
  "$sdk_path/bin/monkeyc" -f "$jungle" -d "$device" -o "bin/Alpine-$device-$mode.prg" -y "$HOME/.Garmin/keys/developer_key.der" $flags -w > "bin/$device-$mode-build.log" 2>&1 || { cat "bin/$device-$mode-build.log"; exit 1; }
  echo "$device $mode: built"
done
