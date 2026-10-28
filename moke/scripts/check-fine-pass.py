"""Verify visual refinements without changing bold time, layout or behavior."""
from pathlib import Path
import hashlib,json,importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];BEFORE=ROOT/'releases/instinct3-before-fine-pass-2026-10-27'
for n,h in json.loads((BEFORE/'functional-sha256.json').read_text()).items():
    assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
for path in (ROOT/'resources/fonts').glob('*.fnt'):
    assert path.read_bytes()==(BEFORE/'resources/fonts'/path.name).read_bytes(),path.name
for path in (ROOT/'resources/fonts').glob('time*.png'):
    assert path.read_bytes()==(BEFORE/'resources/fonts'/path.name).read_bytes(),path.name
sp=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def tile(f,c):
    e=f.chars[ord(c)];return f.atlas.crop((e['x'],e['y'],e['x']+e['width'],e['y']+e['height']))
def topology(im):
    pts={(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))};unseen=set(pts);parts=0
    spurs=sum(sum((x+dx,y+dy) in pts for dx in [-1,0,1] for dy in [-1,0,1] if dx or dy)<=1 for x,y in pts)
    while unseen:
        stack=[unseen.pop()];parts+=1
        while stack:
            x,y=stack.pop()
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    p=x+dx,y+dy
                    if p in unseen:unseen.remove(p);stack.append(p)
    return len(pts),spurs,parts
new=m.Font('garmin-icons',ROOT/'resources/native');old=m.Font('garmin-icons',BEFORE/'resources/native')
for c in new.chars:
    a,b=topology(tile(old,chr(c))),topology(tile(new,chr(c)))
    assert b[0]<=a[0] and b[1]<=a[1] and b[2]==a[2],(chr(c),a,b)
for path in (ROOT/'resources/native').glob('white-heart-*.fnt'):
    assert path.read_bytes()==(BEFORE/'resources/native'/path.name).read_bytes(),path.name
new=m.Font('white-heart-f0-s26',ROOT/'resources/native');old=m.Font('white-heart-f0-s26',BEFORE/'resources/native')
before_ink=sum(bool(v) for c in '96' for v in tile(old,c).getdata());after_ink=sum(bool(v) for c in '96' for v in tile(new,c).getdata())
assert after_ink<before_ink
for c in '0123456789-':assert tile(new,c).getbbox() is not None
r=dict(status='passed',bold_main_time_exactly_preserved=True,all_font_metrics_preserved=True,
       all_functional_code_settings_and_layout_preserved=True,large_arrow_preserved=True,
       white_heart_ink_before=before_ink,white_heart_ink_after=after_ink,
       standard_icons_no_extra_spurs_or_lost_components=True,
       scope='Native one-bit resources; no grayscale or physical-display claim')
(ROOT/'bin/fine-pass-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
