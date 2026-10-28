#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
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
python3 scripts/prepare-instinct3.py
monkeyc -f build/instinct3/live.jungle -d instinct3solar45mm -o bin/Moke-Instinct3.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
monkeyc -f build/instinct3/preview.jungle -d instinct3solar45mm -o bin/Moke-Instinct3-demo.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
monkeyc -f build/instinct3/live.jungle -e -o "dist/Moke-Instinct3-${version}.iq" -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
cp bin/Moke-Instinct3.prg "dist/Moke-Instinct3-${version}.prg"
shasum -a 256 "dist/Moke-Instinct3-${version}.iq" "dist/Moke-Instinct3-${version}.prg" > "dist/Moke-Instinct3-${version}.sha256"
print "本能3 Solar 45/50mm 正式侧载包：bin/Moke-Instinct3.prg（${version}）"
print "商店更新包：dist/Moke-Instinct3-${version}.iq（仅本地，未提交）"
