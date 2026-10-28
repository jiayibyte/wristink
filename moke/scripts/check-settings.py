#!/usr/bin/env python3
"""Check the native menus, phone metadata and defaults against one catalog."""
import json
import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--builds',nargs='+',default=['InstinctFace','InstinctFace-demo'])
args=parser.parse_args()
catalog = json.loads((ROOT / 'config/settings-catalog.json').read_text())
rows = catalog['settings']
assert json.loads((ROOT/'resources/config/groups.json').read_text()) == [g[1] for g in catalog['groups']]
keys = [r['key'] for r in rows]
assert len(set(keys)) == len(keys)
phone_xml = {e.get('propertyKey').split('.')[-1]: e for e in ET.parse(ROOT / 'resources/settings/settings.xml').getroot()}
properties = {e.get('id'): e for e in ET.parse(ROOT / 'resources/settings/properties.xml').getroot()}
assert set(keys) == set(phone_xml) == set(properties)
for name in args.builds:
    compiled = json.loads((ROOT / f'bin/{name}-settings.json').read_text())
    phone = {r['key']: r for r in compiled['settings']}
    assert set(phone) == set(keys)
    translations = compiled['languages']['valyrian']
    for row in rows:
        key = row['key']
        setting = phone[key]
        assert setting['defaultValue'] == row['default'], key
        assert translations[setting['configTitle']] == catalog['groups'][row['group']][1] + ' · ' + row['label'], key
        if row['type'] == 0:
            assert 0 <= row['default'] < len(row['options']), key
            opts = setting['configOptions']
            assert [o['value'] for o in opts] == list(range(len(row['options']))), key
            assert [translations[o['display']] for o in opts] == row['options'], key
        elif row['type'] == 2:
            assert setting['configMin'] == row['min'] and setting['configMax'] == row['max'], key
    for g in range(len(catalog['groups'])):
        packed = json.loads((ROOT / f'resources/config/group-{g}.json').read_text())
        original = [r for r in rows if r['group'] == g]
        assert len(packed) == len(original)
        paged=[]
        for page in range((len(packed)+5)//6):
            chunk=json.loads((ROOT / f'resources/config/group-{g}-page-{page}.json').read_text())
            assert 0 < len(chunk) <= 6
            paged.extend(chunk)
        assert paged == packed
        for native, row in zip(packed, original):
            assert native[:4] == [row['key'], row['label'], row['type'], row['default']]
            options = json.loads((ROOT / f'resources/config/options-{native[4]}.json').read_text())
            assert options == row['options']
            if len(options) > 12:
                packed = json.loads((ROOT / f'resources/config/labels-{native[4]}.json').read_text())
                width = max(map(len, options))
                assert packed == ''.join(label.ljust(width) for label in options)

defaults = {r['key']: r['default'] for r in rows}
assert defaults['timeFormat'] == 0
assert defaults['heartRefresh'] == 0
assert defaults['powerProfile'] == 0 and defaults['secondsMode'] == 0
assert defaults['topCardImage'] == 1 and defaults['bottomCardImage'] == 2
for key in ['topCardImage', 'bottomCardImage']:
    assert len(next(r for r in rows if r['key'] == key)['options']) == 21
artwork = json.loads((ROOT / 'config/card-artwork.json').read_text())
assert [r['id'] for r in artwork] == list(range(1, 21))
from PIL import Image
for theme in ['dark', 'light']:
    path=ROOT / f"resources/drawables/card-art-atlas-{theme}.png"
    with Image.open(path) as im:
        assert im.size == (504, 13) and len(im.getcolors()) == 2
        for row in artwork[2:]:
            tile=im.crop(((row['id']-3)*28,0,(row['id']-2)*28,13))
            assert len(tile.getcolors()) == 2
assert defaults['ringSource'] == 0 and defaults['cellsSource'] == 0
assert defaults['circle'] == 6 and defaults['circleBackground'] == 1
assert len(catalog['metrics']) == 29 and catalog['metrics'][0] == '隐藏'
for font in ET.parse(ROOT / 'resources/fonts/fonts.xml').getroot():
    path = ROOT / 'resources/fonts' / font.get('filename')
    content = path.read_text()
    glyphs = set(map(int, re.findall(r'char id=(\d+)', content)))
    expected = '0123456789'
    if font.get('id') == 'Chart' or font.get('id').startswith(('Data', 'Circle', 'LiveHeart')):
        expected += '-'
    if font.get('id').startswith('Data'):
        expected += '天月日一二三四五六上下午/:.%°kmhPaCFft'
    assert all(ord(c) in glyphs for c in expected), path
    for atlas in re.findall(r'page id=\d+ file="([^"]+)"', content):
        assert (path.parent / atlas).is_file()

result = {
    'status': 'passed', 'settings': len(rows), 'groups': len(catalog['groups']),
    'metric_choices_excluding_hidden': len(catalog['metrics']) - 1,
    'checks': ['unique keys', 'phone XML and properties parity', 'both compiled phone settings',
               'native packed menus and options parity', '24-hour default',
               'default plain white heart window without progress rings', 'font glyphs and atlases'],
    'scope': 'Schema and generated resource validation; phone connection is not exercised.'
}
(ROOT / 'bin/settings-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(f"Passed settings validation: {len(rows)} settings, {len(catalog['groups'])} groups.")
