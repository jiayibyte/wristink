#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
# Run generation to completion before starting compilers: deleting/rebuilding an
# asset profile concurrently with a compiler invalidates its input snapshot.
version="${1:-1.1.0}"
mkdir -p bin dist
python3 scripts/make-fonts.py
python3 scripts/make-weather-icons.py
python3 scripts/make-garmin-icons.py
python3 scripts/make-upper-details.py
python3 scripts/make-white-heart.py
python3 scripts/make-shaft-arrow.py
python3 scripts/make-energy-sectors.py
python3 scripts/generate-settings.py
python3 scripts/generate-mip-targets.py
python3 scripts/check-layout.py
python3 scripts/check-mip-layout.py
python3 scripts/check-typography.py
python3 scripts/check-english.py
monkeyc -f monkey.jungle -e -o "dist/Moke-${version}.iq" -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
shasum -a 256 "dist/Moke-${version}.iq" > "dist/Moke-${version}.sha256"
print "商店安装包：dist/Moke-${version}.iq（正式数据，不含演示数值）"
