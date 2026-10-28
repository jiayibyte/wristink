"""Keep the refinement visual: layouts, data and numeral metrics stay fixed."""
from pathlib import Path
import hashlib,json,re,runpy,importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'releases/instinct3-before-three-details-2026-10-27'
for name,h in json.loads((BEFORE/'functional-sha256.json').read_text()).items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name

spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
count=0
for path in (ROOT/'resources/fonts').glob('*.fnt'):
    previous=BEFORE/'resources/fonts'/path.name
    assert path.read_bytes()==previous.read_bytes(),path.name
    a=m.Font(path.stem,ROOT/'resources/fonts');b=m.Font(path.stem,BEFORE/'resources/fonts')
    for code,e in a.chars.items():
        box=(e['x'],e['y'],e['x']+e['width'],e['y']+e['height'])
        if code<0x4e00 and chr(code) not in '/:':
            assert a.atlas.crop(box).tobytes()==b.atlas.crop(box).tobytes(),(path.name,chr(code))
        count+=1

def glyph(font,char):
    e=font.chars[ord(char)];return font.atlas.crop((e['x'],e['y'],e['x']+e['width'],e['y']+e['height']))
font=m.Font('dataf0s14',ROOT/'resources/fonts')
digit=glyph(font,'2').getbbox();unit=glyph(font,'天').getbbox();slash=glyph(font,'/').getbbox()
assert unit[3]-unit[1]<=digit[3]-digit[1]+1
assert slash[3]-slash[1]<=digit[3]-digit[1]

weather=runpy.run_path(str(ROOT/'scripts/make-weather-icons.py'))['glyph']
old_weather=runpy.run_path(str(BEFORE/'scripts/make-weather-icons.py'))['glyph']
images=[weather(i) for i in range(11)]
assert len({im.tobytes() for im in images})==11
assert images[0].tobytes()==old_weather(0).convert('L').tobytes()
for im in images:assert im.size==(15,15) and set(im.getdata())<={0,255}

upper=m.Font('upper-details',ROOT/'resources/native');old=m.Font('upper-details',BEFORE/'resources/native')
for char in 'Ql':assert glyph(upper,char).tobytes()==glyph(old,char).tobytes()
levels=[glyph(upper,str(i)) for i in range(9)]
assert all(im.size==(14,12) for im in levels)
assert len({im.tobytes() for im in levels})==9
areas=[sum(bool(v) for v in im.getdata()) for im in levels]
assert all(a<b for a,b in zip(areas,areas[1:]))
for name in ['upper-moon.png','upper-moon.fnt','garmin-icons.png','garmin-icons.fnt']:
    assert (ROOT/'resources/native'/name).read_bytes()==(BEFORE/'resources/native'/name).read_bytes(),name

result=dict(status='passed',unchanged_glyph_metrics=count,unchanged_numeric_shapes=True,
            chinese_unit_height=unit[3]-unit[1],numeric_cap_height=digit[3]-digit[1],
            weather_states=11,battery_states=9,original_layout_and_settings=True,
            heart_curve_and_five_second_reading_unchanged=True,
            scope='Native monochrome resources; no grayscale smoothing or real-watch claim')
(ROOT/'bin/three-details-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
