#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
version="${1:-1.3.0}"
mkdir -p bin dist
python_bin="${ALPINE_PYTHON:-python3}"
java_bin="${JAVA_HOME:+$JAVA_HOME/bin/}"
key="$HOME/.Garmin/keys/developer_key.der"
flags=(-y "$key" -r -O 2z --disable-api-has-check-removal -w --no-gen-styles)
"$python_bin" tools/settings.py
"$python_bin" tools/generate.py
# Type-check the frozen source once on one profile, then export every variant without
# repeating the inference (-l 0): the PRG bytes are identical (see
# docs/device-expansion-20261116/typecheck-equivalence.json). Repeating it per variant
# takes hours and ~11 GB of heap.
"$sdk_path/bin/monkeyc" -f monkey.jungle -d epix2 -o bin/typecheck-epix2.prg "${flags[@]}" -l 1 > "dist/typecheck-${version}.log" 2>&1
"$sdk_path/bin/monkeyc" -f monkey.jungle -e -o "dist/Alpine-${version}.iq" "${flags[@]}" -l 0 > "dist/store-build-${version}.log" 2>&1
"$python_bin" tools/check_size.py "dist/Alpine-${version}.iq" > "dist/size-audit-${version}.json"
"${java_bin}javac" -cp "$sdk_path/bin/monkeybrains.jar" -d dist tools/VerifyIq.java
openssl pkey -inform DER -in "$key" -pubout -outform DER -out dist/developer-public.der
"${java_bin}java" -cp "dist:$sdk_path/bin/monkeybrains.jar" VerifyIq "dist/Alpine-${version}.iq" dist/developer-public.der
shasum -a 256 "dist/Alpine-${version}.iq" > "dist/Alpine-${version}.sha256"

# Preserve SDK output; the store transport copy retains identical signed files.
rm -f "dist/Alpine-${version}-compact.iq"
"$python_bin" tools/recompress_iq.py "dist/Alpine-${version}.iq" "dist/Alpine-${version}-compact.iq"
"${java_bin}java" -cp "dist:$sdk_path/bin/monkeybrains.jar" VerifyIq "dist/Alpine-${version}-compact.iq" dist/developer-public.der
