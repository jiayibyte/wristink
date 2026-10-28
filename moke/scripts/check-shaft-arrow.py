"""Retain the arrow family and original position while enlarging the head."""
from pathlib import Path
import hashlib,json,importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];BEFORE=ROOT/'releases/instinct3-before-large-arrow-head-2026-10-27'
for n,h in json.loads((BEFORE/'unchanged-sha256.json').read_text()).items():
    if n=='resources/native/fonts.xml':continue
    assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
old=(BEFORE/'source/InstinctFaceView.mc').read_text();new=(ROOT/'source/InstinctFaceView.mc').read_text()
added='''        var bearing=PreviewMode.ENABLED ? 90 : _weather.windBearing;
        if(NativeStyle.enabled()){NativeStyle.windArrow(dc,center,cy,bearing,FaceDraw.foreground,FaceDraw.background);dc.setPenWidth(1);return;}
        var a=(bearing-90)*Math.PI/180;'''
assert new.replace(added,'        var bearing=PreviewMode.ENABLED ? 90 : _weather.windBearing;var a=(bearing-90)*Math.PI/180;')==old
sp=importlib.util.spec_from_file_location('w',ROOT/'scripts/render-white-heart.py');w=importlib.util.module_from_spec(sp);sp.loader.exec_module(w)
f=w.three.m.Font('shaft-wind',ROOT/'resources/native');codes='0123456789ABCDEFGHIJKLMNOPQRSTUV'
tiles=[]
for c in codes:
    e=f.chars[ord(c)];im=f.atlas.crop((e['x'],e['y'],e['x']+15,e['y']+15))
    assert set(im.getdata())<={0,255} and im.getbbox() is not None;tiles.append(im)
east=tiles[8]
assert all(east.getpixel((x,y)) for x in range(2,8) for y in [7,8])
assert not any(east.getpixel((x,y)) for x in range(2,6) for y in [3,4,11,12])
previous=w.after.crop((81,7,96,22)).convert('L');a=previous.crop((8,0,15,15)).getbbox();b=east.crop((8,0,15,15)).getbbox()
assert b[3]-b[1]>a[3]-a[1],(a,b)
r=dict(status='passed',shaft_retained=True,head_height_before=a[3]-a[1],head_height_after=b[3]-b[1],
       anchor=[88,14],directions=32,all_other_product_resources_and_settings_unchanged=True,
       white_heart_and_five_second_reading_unchanged=True,scope='Native monochrome asset preview and source invariants')
(ROOT/'bin/shaft-arrow-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
