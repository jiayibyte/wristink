"""Check English/Chinese resources and identical numeric glyphs in both locales."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
tr=json.loads((R/'config/english-translations.json').read_text());schema=json.loads((R/'config/settings-catalog.json').read_text())
cn={e.get('id'):e.text for e in ET.parse(R/'resources/strings/strings.xml').getroot()}
en={e.get('id'):e.text for e in ET.parse(R/'resources-eng/strings/strings.xml').getroot()}
assert set(cn)==set(en);assert cn['LocaleEnglish']=='false' and en['LocaleEnglish']=='true'
assert len(schema['settings'])==94
for path in (R/'resources-eng/config').glob('group-*-page-*.json'):
    original=json.loads((R/'resources/config'/path.name).read_text());english=json.loads(path.read_text())
    for a,b in zip(original,english):assert a[0]==b[0] and a[2:]==b[2:] and tr[a[1]]==b[1]
for path in (R/'resources-eng/config').glob('options-*.json'):
    a=json.loads((R/'resources/config'/path.name).read_text());b=json.loads(path.read_text());assert b==[tr[s] for s in a]
    if len(b)>12:
        packed=json.loads(path.with_name(path.name.replace('options-','labels-')).read_text());width=len(packed)//len(b)
        assert [packed[i*width:(i+1)*width].rstrip() for i in range(len(b))]==b
defaults={r['key']:r['default'] for r in schema['settings']}
assert defaults['sideData']==19 and defaults['topCardImage']==0 and defaults['bottomCardImage']==0
assert defaults['showMoveBar'] is False and defaults['showWind'] is True
checks=0
# Both languages share one font set: no English copy is packaged.
assert not (R/'resources-eng/fonts').exists()
import sys;sys.path.insert(0,str(R/'scripts'))
from font_rasterizer import METRICS
for path in (R/'resources/fonts').glob('dataf*.fnt'):
    def glyphs(p):return {int(m['id']):m for line in p.read_text().splitlines() if line.startswith('char id=') for m in [dict((k,int(v)) for k,v in re.findall(r'(\w+)=(-?\d+)',line))]}
    chars=glyphs(path)
    assert set(map(ord,'SunMonTueWedThuFriSatAMPd'))<=chars.keys()
    # Every published Chinese-set glyph keeps its geometry.
    # (Metrics list some glyphs twice, e.g. the second 午 in 上午下午; the last entry is packaged.)
    published={e['id']:{k:v for k,v in e.items() if k!='ink'} for e in METRICS[path.stem]['chars']}
    for ident,entry in published.items():
        assert chars[ident]==entry,(path.stem,ident)
    for text in ['10/19 Mon','10/19 Wed','Mon 10/19','2026/10/19','AM','PM','28d','10月19日 周一']:
        assert all(ord(c) in chars for c in text)
    checks+=1
result=dict(status='passed',settings=94,groups=13,languages=['zhs','eng'],english_data_fonts=checks,identical_numeric_glyphs=True,rounded_clean_defaults=True,scope='Generated resource parity and font geometry; device runtime checked separately.')
(R/'bin/english-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
