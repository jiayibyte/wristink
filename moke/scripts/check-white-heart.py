"""Validate the white heart window, numeric transitions and narrow scope."""
from pathlib import Path
import json,re,hashlib,importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'releases/instinct3-before-white-heart-2026-10-27'
for n,h in json.loads((BEFORE/'unchanged-sha256.json').read_text()).items():
    assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
old=json.loads((BEFORE/'config/settings-catalog.json').read_text());new=json.loads((ROOT/'config/settings-catalog.json').read_text())
allowed={'circleBackground':1,'cellsSource':0,'ringSource':0}
assert old['groups']==new['groups'] and old['metrics']==new['metrics']
for a,b in zip(old['settings'],new['settings']):
    expected=dict(a)
    if a['key'] in allowed:expected['default']=allowed[a['key']]
    assert b==expected,a['key']

def body(source,name):
    start=source.index('{',re.search(r'function '+name+r'\(',source).end());end=start+1;depth=1
    while depth:
        if source[end]=='{':depth+=1
        elif source[end]=='}':depth-=1
        end+=1
    return source[start:end]
before=(BEFORE/'source/FaceDraw.mc').read_text();after=(ROOT/'source/FaceDraw.mc').read_text()
for name in ['circle','time','date','seconds','slot','footerRow','heartPanel','walletCards','moon','moveBar','moveBarAt']:
    assert body(before,name)==body(after,name),name

spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
samples=['0','9','99','100','199','299','300','888','--'];checked=0
for family in range(3):
    for h in [22,26,28]:
        f=m.Font(f'white-heart-f{family}-s{h}',ROOT/'resources/native')
        assert set(f.atlas.getdata())<={0,255}
        for with_icon in [True,False]:
            center=38 if with_icon else 31;top=23 if with_icon else 16;height=29 if with_icon else 30
            for x in [121,167]:
                for y in [top,top+height-1]:assert (x-144)**2+(y-31)**2<=31**2
            for value in samples:
                im=Image.new('L',(200,64));f.draw(im,144,center-h//2,value,255,center=True)
                box=im.getbbox();assert box is not None and 121<=box[0] and box[2]<=168 and top<=box[1] and box[3]<=top+height,(family,h,value,box)
                for y in range(box[1],box[3]):
                    for x in range(box[0],box[2]):
                        if im.getpixel((x,y)):assert (x-144)**2+(y-31)**2<=31**2
                checked+=1
r=dict(status='passed',font_families=3,numeric_sizes=[22,26,28],numeric_clip_cases=checked,
       only_changed_setting_defaults=allowed,main_face_layout_unchanged=True,
       heart_curve_and_five_second_reading_unchanged=True,
       partial_clear_stays_inside_white_disc=True,
       scope='Resources, source invariants and clip geometry; real-watch appearance still needs retest')
(ROOT/'bin/white-heart-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
