# Connect IQ toolchain locations shared by the zsh build scripts.
# Source it after `cd`-ing into a project folder: source ../tools/ciq_env.sh
# Sets JAVA_HOME (when known), ciq_home, ciq_devices and sdk_path, and puts the
# active SDK's bin directory on PATH so plain `monkeyc` works too.
#
# Overrides: CIQ_HOME (SDK Manager data folder), CIQ_SDK (one SDK folder).

# Keep the macOS JDK the project was built with; elsewhere use JAVA_HOME or the
# java already on PATH.
if [[ -d /Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home ]]; then
  export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home
fi
if [[ -n "${JAVA_HOME:-}" ]]; then
  export PATH="$JAVA_HOME/bin:$PATH"
fi
# Java's default heap is a quarter of RAM; Alpine alone needs ~11 GB to compile.
if [[ "${JAVA_TOOL_OPTIONS:-}" != *-Xmx* && "${JAVA_TOOL_OPTIONS:-}" != *MaxRAM* ]]; then
  export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:+$JAVA_TOOL_OPTIONS }-XX:MaxRAMPercentage=70"
fi

if [[ -n "${CIQ_HOME:-}" ]]; then
  ciq_home="$CIQ_HOME"
elif [[ "$OSTYPE" == darwin* ]]; then
  ciq_home="$HOME/Library/Application Support/Garmin/ConnectIQ"
else
  ciq_home="$HOME/.Garmin/ConnectIQ"
fi
ciq_devices="$ciq_home/Devices"

if [[ -n "${CIQ_SDK:-}" ]]; then
  sdk_path="$CIQ_SDK"
elif [[ -s "$ciq_home/current-sdk.cfg" ]]; then
  sdk_path="$(tr -d '\r\n' < "$ciq_home/current-sdk.cfg")"
else
  print -u2 "请先在 Connect IQ SDK Manager 中安装 SDK 并设为当前版本（未找到 $ciq_home/current-sdk.cfg）。"
  exit 1
fi
sdk_path="${sdk_path%/}"
export PATH="$sdk_path/bin:$PATH"
