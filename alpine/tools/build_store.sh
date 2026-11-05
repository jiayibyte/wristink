#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
sdk_path="$(tr -d '\r\n' < "$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg")"
version="${1:-1.0.0}"
mkdir -p dist
python_bin="${ALPINE_PYTHON:-python3}"
"$python_bin" tools/settings.py
"$python_bin" tools/generate.py
"$sdk_path/bin/monkeyc" -f monkey.jungle -e -o "dist/Alpine-${version}.iq" -y "$HOME/.Garmin/keys/developer_key.der" -r -O 2z --disable-api-has-check-removal -w --no-gen-styles > "dist/store-build-${version}.log" 2>&1
"$JAVA_HOME/bin/javac" -cp "$sdk_path/bin/monkeybrains.jar" -d dist tools/VerifyIq.java
"$JAVA_HOME/bin/java" -cp "dist:$sdk_path/bin/monkeybrains.jar" VerifyIq "dist/Alpine-${version}.iq" "$HOME/.Garmin/keys/developer_key.der"
shasum -a 256 "dist/Alpine-${version}.iq" > "dist/Alpine-${version}.sha256"
