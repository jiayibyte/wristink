"""Generate English phone/native settings from the canonical Chinese catalog."""
from pathlib import Path
import json, xml.etree.ElementTree as ET
from english_fonts import generate
R=Path(__file__).resolve().parents[1]
translations=json.loads((R/'config/english-translations.json').read_text())
def tr(text):
    if text in translations:return translations[text]
    if ' · ' in text:return ' · '.join(tr(s) for s in text.split(' · '))
    raise ValueError('Missing English translation: '+text)
out=R/'resources-eng';(out/'strings').mkdir(parents=True,exist_ok=True)
strings=ET.parse(R/'resources/strings/strings.xml')
menu={'MenuOn':'On','MenuOff':'Off','MenuAuto':'Auto / system','MenuNext':'Next page','MenuPrevious':'Previous page','MenuResetGroup':'Reset this section','MenuSelected':'Selected','MenuTitle':'Customize face','MenuResetAll':'Reset all settings'}
for e in strings.getroot():
    key=e.get('id')
    e.text='Moke' if key=='AppName' else ('true' if key=='LocaleEnglish' else (menu[key] if key in menu else tr(e.text)))
strings.write(out/'strings/strings.xml',encoding='utf-8',xml_declaration=True)
folder=out/'config';folder.mkdir(exist_ok=True)
for path in (R/'resources/config').glob('*.json'):
    data=json.loads(path.read_text())
    if not (path.stem.startswith(('labels-','group-','options-')) or path.stem=='groups'):continue
    if path.stem.startswith('labels-'):continue
    if path.stem.startswith('group-'):
        for row in data:row[1]=tr(row[1])
    else:data=[tr(x) for x in data]
    (folder/path.name).write_text(json.dumps(data,ensure_ascii=False))
    if path.stem.startswith('options-') and len(data)>12:
        width=max(map(len,data));(folder/path.name.replace('options-','labels-')).write_text(json.dumps(''.join(s.ljust(width) for s in data)))
(folder/'resources.xml').write_bytes((R/'resources/config/resources.xml').read_bytes())
(out/'strings/font-licenses.xml').write_bytes((R/'resources/strings/font-licenses.xml').read_bytes())
generate(out)
print('Generated English settings and native-size Latin glyphs.')
