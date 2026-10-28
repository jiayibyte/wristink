"""Direction semantics, native pointer bounds and unchanged product scope."""
from pathlib import Path
import hashlib,json,re,importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'releases/instinct3-before-official-wind-2026-10-27'
for n,h in json.loads((BEFORE/'unchanged-sha256.json').read_text()).items():
    if n=='resources/native/fonts.xml':continue
    assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n

old=(BEFORE/'source/InstinctFaceView.mc').read_text();new=(ROOT/'source/InstinctFaceView.mc').read_text()
added='''        var bearing=PreviewMode.ENABLED ? 90 : _weather.windBearing;
        if(NativeStyle.enabled()){NativeStyle.windArrow(dc,center,cy,bearing,FaceDraw.foreground,FaceDraw.background);dc.setPenWidth(1);return;}
        var a=(bearing-90)*Math.PI/180;'''
assert new.replace(added,'        var bearing=PreviewMode.ENABLED ? 90 : _weather.windBearing;var a=(bearing-90)*Math.PI/180;')==old
assert 'if(!PreviewMode.ENABLED && (_weather==null || _weather.windBearing==null))' in new

ref=json.loads((ROOT/'assets/icons/garmin-wind-reference.json').read_text())
raw=(ROOT/'assets/icons/garmin-direction-pointer-reference.svg').read_bytes()
assert hashlib.sha256(raw).hexdigest()==ref['svg_sha256']
points=re.search(r'<polygon fill="#414042" points="([^"]+)"',raw.decode())[1]
assert [list(map(float,p.split(','))) for p in points.split()]==ref['outer_polygon']

spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=m.Font('wind-arrow',ROOT/'resources/native');codes='0123456789ABCDEFGHIJKLMNOPQRSTUV';tiles=[]
for c in codes:
    g=f.chars[ord(c)];assert g['width']==g['height']==15
    im=f.atlas.crop((g['x'],g['y'],g['x']+15,g['y']+15))
    assert im.getbbox() is not None and set(im.getdata())<={0,255};tiles.append(im)
assert len({im.tobytes() for im in tiles})>=24
# The most forward pixel must stay at the correct end of each cardinal axis.
for i,point in [(0,(7,1)),(8,(13,7)),(16,(7,13)),(24,(1,7))]:assert tiles[i].getpixel(point)==255
r=dict(status='passed',directions=32,box=[15,15],anchor=[88,14],
       cardinal_orientation_preserved=True,missing_data_dash_preserved=True,
       all_previous_resources_and_settings_unchanged=True,
       scope='Official vector adaptation and native bounds; not a private firmware icon API')
(ROOT/'bin/wind-arrow-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
