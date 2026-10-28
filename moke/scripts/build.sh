#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
sdk_config="$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg"
if [[ ! -s "$sdk_config" ]]; then
  print -u2 '请先在 Connect IQ SDK Manager 中安装 SDK 并设为当前版本。'
  exit 1
fi
sdk_path="$(tr -d '\r\n' < "$sdk_config")"
sdk_path="${sdk_path%/}"
mkdir -p bin
"$sdk_path/bin/monkeyc" -f monkey.jungle -d instinct3solar45mm -o bin/InstinctFace.prg -y "$HOME/.Garmin/keys/developer_key.der" -w "$@"
