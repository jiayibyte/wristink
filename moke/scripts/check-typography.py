"""Check native font compatibility, visible glyphs and reproducible rasterization."""
from pathlib import Path
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image
from font_rasterizer import METRICS, render_font

ROOT = Path(__file__).resolve().parents[1]
active = {Path(e.get('filename')).stem for e in ET.parse(ROOT/'resources/fonts/fonts.xml').getroot()}
count = 0
keys = sorted({r['asset_key'] for r in json.loads((ROOT/'config/mip-devices.json').read_text())})
folders = [ROOT/'resources/fonts'] + [ROOT/'generated/assets'/key/'resources/fonts' for key in keys]
for folder in folders:
    for name in active:
        path = folder/(name+'.fnt')
        if not path.exists():
            continue
        text = path.read_text()
        with Image.open(folder/(name+'.png')) as atlas:
            alpha = atlas.getchannel('A')
            assert set(alpha.getdata()) <= {0, 255}, (folder, name, 'non-binary alpha')
            for line in text.splitlines():
                if not line.startswith('char id='):
                    continue
                e = {k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
                char = chr(e['id'])
                ink = alpha.crop((e['x'],e['y'],e['x']+e['width'],e['y']+e['height'])).getbbox()
                assert char.isspace() or ink is not None, (folder, name, char)
                count += 1
        if folder == ROOT/'resources/fonts':
            old = METRICS[name]['chars']
            actual = [dict((k,int(v)) for k,v in re.findall(r'(\w+)=(-?\d+)',line)) for line in text.splitlines() if line.startswith('char id=')]
            assert actual == [{k:v for k,v in e.items() if k!='ink'} for e in old], name

with tempfile.TemporaryDirectory() as tmp:
    for name, scale in [('timef0s64',1.0), ('dataf0s14',1.122727), ('liveheartf0s22',.838710)]:
        render_font(name,tmp,scale)
        first = (Path(tmp)/(name+'.png')).read_bytes()
        render_font(name,tmp,scale)
        assert (Path(tmp)/(name+'.png')).read_bytes() == first
    # A target font comes from outlines, not a nearest-neighbor base atlas.
    render_font('timef0s64',tmp,1.122727)
    native = Image.open(Path(tmp)/'timef0s64.png').getchannel('A')
    base = Image.open(ROOT/'resources/fonts/timef0s64.png').getchannel('A')
    assert native.tobytes() != base.resize(native.size,Image.Resampling.NEAREST).tobytes()

result = dict(status='passed', active_fonts=len(active), font_folders=len(folders),
              glyph_checks=count, preserves_published_metrics=True, native_outline_rasterization=True,
              scope='Font geometry/resources, not physical-display smoothness or battery life')
(ROOT/'bin/typography-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
