#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
version="${1:-1.2.0}"
mkdir -p dist
python_bin="${ALPINE_PYTHON:-python3}"
"$python_bin" tools/settings.py
"$python_bin" tools/generate.py
"$sdk_path/bin/monkeyc" -f monkey.jungle -e -o "dist/Alpine-${version}.iq" -y "$HOME/.Garmin/keys/developer_key.der" -r -O 2z --disable-api-has-check-removal -w --no-gen-styles > "dist/store-build-${version}.log" 2>&1
"$python_bin" tools/check_size.py "dist/Alpine-${version}.iq" > "dist/size-audit-${version}.json"
"$JAVA_HOME/bin/javac" -cp "$sdk_path/bin/monkeybrains.jar" -d dist tools/VerifyIq.java
openssl pkey -inform DER -in "$HOME/.Garmin/keys/developer_key.der" -pubout -outform DER -out dist/developer-public.der
"$JAVA_HOME/bin/java" -cp "dist:$sdk_path/bin/monkeybrains.jar" VerifyIq "dist/Alpine-${version}.iq" dist/developer-public.der
shasum -a 256 "dist/Alpine-${version}.iq" > "dist/Alpine-${version}.sha256"

# Preserve SDK output; the store transport copy retains identical signed files.
"$python_bin" tools/recompress_iq.py "dist/Alpine-${version}.iq" "dist/Alpine-${version}-compact.iq"
"$JAVA_HOME/bin/java" -cp "dist:$sdk_path/bin/monkeybrains.jar" VerifyIq "dist/Alpine-${version}-compact.iq" dist/developer-public.der
