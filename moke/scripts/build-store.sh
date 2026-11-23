#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
source ../tools/ciq_env.sh
# Run generation to completion before starting compilers: deleting/rebuilding an
# asset profile concurrently with a compiler invalidates its input snapshot.
version="${1:-1.4.0}"
mkdir -p bin dist
# The committed bitmaps and font atlases are the shipped reference. Different
# FreeType builds rasterise a few small glyphs differently (the 16 px energy
# ring, micro.png), so they are only redrawn on request:
#   MOKE_REGENERATE_ASSETS=1 zsh scripts/<this script>
if [[ "${MOKE_REGENERATE_ASSETS:-0}" == 1 ]]; then
  python3 scripts/make-fonts.py
  python3 scripts/make-weather-icons.py
  python3 scripts/make-garmin-icons.py
  python3 scripts/make-upper-details.py
  python3 scripts/make-white-heart.py
  python3 scripts/make-shaft-arrow.py
  python3 scripts/make-energy-sectors.py
fi
# Also regenerates the English strings and shared Latin glyphs (generate-english.py).
python3 scripts/generate-settings.py
python3 scripts/generate-mip-targets.py
python3 scripts/check-layout.py
python3 scripts/check-mip-layout.py
python3 scripts/check-typography.py
python3 scripts/check-english.py
monkeyc -f monkey.jungle -e -o "dist/Moke-${version}.iq" -y "$HOME/.Garmin/keys/developer_key.der" -r -O 3z -w
shasum -a 256 "dist/Moke-${version}.iq" > "dist/Moke-${version}.sha256"
print "商店安装包：dist/Moke-${version}.iq（正式数据，不含演示数值）"
