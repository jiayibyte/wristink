"""Check bilingual release resources without changing the approved layout or defaults."""
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
prior=json.loads((R/'releases/instinct3-before-fine-pass-2026-10-27/config/settings-catalog.json').read_text())
assert [(r['key'],r['type'],r['default'],r['min'],r['max']) for r in schema['settings']]==[(r['key'],r['type'],r['default'],r['min'],r['max']) for r in prior['settings']]
assert (R/'source/FaceLayout.mc').read_bytes()==(R/'releases/instinct3-before-fine-pass-2026-10-27/source/FaceLayout.mc').read_bytes()
checks=0
for path in (R/'resources-eng/fonts').glob('dataf*.fnt'):
    def glyphs(p):return {int(m['id']):m for line in p.read_text().splitlines() if line.startswith('char id=') for m in [dict((k,int(v)) for k,v in re.findall(r'(\w+)=(-?\d+)',line))]}
    enchars=glyphs(path);cnpath=R/'resources/fonts'/path.name;cnchars=glyphs(cnpath)
    assert set(map(ord,'SunMonTueWedThuFriSatAMPd'))<=enchars.keys()
    old=Image.open(cnpath.with_suffix('.png')).getchannel('A');new=Image.open(path.with_suffix('.png')).getchannel('A')
    for ident,char in cnchars.items():
        assert enchars[ident]==char
        box=(char['x'],char['y'],char['x']+char['width'],char['y']+char['height'])
        assert ImageChops.difference(old.crop(box),new.crop(box)).getbbox() is None
    for text in ['10/19 Mon','10/19 Wed','Mon 10/19','2026/10/19','AM','PM','28d']:
        assert all(ord(c) in enchars for c in text)
    checks+=1
# Main time pixels remain the approved bold 1.0.9/1.0.10 glyphs.
for path in (R/'resources/fonts').glob('time*.png'):
    prior=R/'releases/instinct3-before-fine-pass-2026-10-27/resources/fonts'/path.name
    assert prior.read_bytes()==path.read_bytes(),path
result=dict(status='passed',settings=94,groups=13,languages=['zhs','eng'],english_data_fonts=checks,unchanged_chinese_glyphs=True,unchanged_bold_time=True,scope='Generated bilingual resources and font geometry; device runtime checked separately.')
(R/'bin/english-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
