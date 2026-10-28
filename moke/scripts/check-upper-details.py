"""Validate native upper details, unchanged layout and retained behavior."""
from pathlib import Path
import hashlib,json,re,importlib.util
from PIL import Image,ImageOps,ImageChops

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'releases/instinct3-before-upper-style-2026-10-27'
frozen=json.loads((BEFORE/'unchanged-scope-sha256.json').read_text())
for name,digest in frozen.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

def function(source,name):
    start=source.index('{',re.search(r'function '+name+r'\(',source).end());depth=1;end=start+1
    while depth:
        if source[end]=='{':depth+=1
        if source[end]=='}':depth-=1
        end+=1
    return source[start:end]
old=(BEFORE/'source/FaceDraw.mc').read_text();new=(ROOT/'source/FaceDraw.mc').read_text()
unchanged=['time','date','seconds','prepareSeconds','slot','footerRow','heartPanel','walletCards','drawCard','prepareLiveHeart','drawLiveHeart','refreshLiveHeart','moveBar']
for name in unchanged:assert function(old,name)==function(new,name),name

spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
moon=m.Font('upper-moon',ROOT/'resources/native')
codes='0123456789ABCDEFGHIJKLMNOPQRSTUV';phases=[]
for c in codes:
    e=moon.chars[ord(c)];im=moon.atlas.crop((e['x'],e['y'],e['x']+15,e['y']+15))
    assert set(im.getdata())<={0,255};assert im.getbbox()==(0,0,15,15)
    phases.append(im)
areas=[sum(1 for v in im.getdata() if v) for im in phases]
assert all(a<=b for a,b in zip(areas[:16],areas[1:17]))
assert all(a>=b for a,b in zip(areas[16:],areas[17:]))
assert ImageOps.mirror(phases[8]).tobytes()==phases[24].tobytes()
assert phases[0].getpixel((7,7))==0 and phases[16].getpixel((7,7))==255
assert phases[8].getpixel((10,7))==255 and phases[8].getpixel((4,7))==0
assert phases[24].getpixel((4,7))==255 and phases[24].getpixel((10,7))==0

details=m.Font('upper-details',ROOT/'resources/native')
for char,w,h in [('Q',9,13),('l',12,12)]:
    e=details.chars[ord(char)];assert e['width']==w and e['height']==h
    im=details.atlas.crop((e['x'],e['y'],e['x']+w,e['y']+h))
    assert im.getbbox() is not None and set(im.getdata())<={0,255}

# The selected texture changes, while the solid-sector choices stay identical.
for pattern in ['energy-v2-*.png','energy-v3-*.png','energy-level-v2-*.png','energy-level-v3-*.png']:
    for path in (ROOT/'resources/drawables').glob(pattern):
        assert Image.open(path).convert('RGBA').tobytes()==Image.open(BEFORE/'resources/drawables'/path.name).convert('RGBA').tobytes(),path.name

result=dict(status='passed',moon_phases=32,original_layout_and_defaults=True,original_fonts=True,
            heart_curve_fix_unchanged=True,five_second_heart_policy_unchanged=True,
            unchanged_render_functions=unchanged,solid_sector_styles_unchanged=True,
            scope='Native assets and source invariants; not real-watch smoothness or battery measurement')
(ROOT/'bin/upper-details-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
