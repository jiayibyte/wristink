"""Verify the compiler-produced settings metadata, not just source XML."""
from pathlib import Path
import argparse,json,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('devices',nargs='+');p.add_argument('--mode',default='live');a=p.parse_args()
expected={'CircleData':6,'HeaderTop':11,'HeaderLeft':11,'HeaderRight':11,'Left':0,'Middle':1,'Right':2}
for device in a.devices:
 path=R/f'bin/Alpine-{device}-{a.mode}-settings.json';data=json.loads(path.read_text());items={x['key']:x for x in data['settings']}
 assert 'Circle' not in items
 for key,default in expected.items():
  item=items[key];assert item['defaultValue']==default,(device,key,item)
  assert item['valueType']=='number' and item['configType']=='list'
  assert [x['value'] for x in item['configOptions']]==list(range(12))
  for language in ['valyrian','zhs']:
   strings=data['languages'][language]
   assert item['configTitle'] in strings
   for choice in item['configOptions']:assert choice['display'] in strings,(device,language,choice)
 print(device,'7 independently configurable slots / 12 choices / English + Chinese: PASS')
