"""Verify the compiler-produced settings metadata, not just source XML."""
from pathlib import Path
import argparse,json,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('devices',nargs='+');p.add_argument('--mode',default='live');a=p.parse_args()
expected={'CircleData':6,'HeaderTop':11,'HeaderLeft':11,'HeaderRight':11,'Left':0,'Middle':1,'Right':2}
for device in a.devices:
 path=R/f'bin/Alpine-{device}-{a.mode}-settings.json';data=json.loads(path.read_text());items={x['key']:x for x in data['settings']}
 assert 'Circle' not in items
 festival=items['Festival']
 assert festival['defaultValue']==0 and festival['valueType']=='number' and festival['configType']=='list'
 assert [x['value'] for x in festival['configOptions']]==list(range(6))
 for language in ['valyrian','zhs']:
  strings=data['languages'][language]
  assert festival['configTitle'] in strings and all(c['display'] in strings for c in festival['configOptions'])
 for key,count in [('TimeFormat',3),('SkyDisplay',2),('Scene',18),('WeatherLink',2),('SkyDecor',4)]:
  item=items[key];assert item['defaultValue']==0 and item['valueType']=='number' and item['configType']=='list'
  assert [c['value'] for c in item['configOptions']]==list(range(count))
  for language in ['valyrian','zhs']:
   strings=data['languages'][language]
   assert item['configTitle'] in strings and all(c['display'] in strings for c in item['configOptions'])
 panel=items['PanelStyle']
 assert panel['defaultValue']==1 and panel['valueType']=='number' and panel['configType']=='list'
 assert [x['value'] for x in panel['configOptions']]==list(range(4))
 for language in ['valyrian','zhs']:
  strings=data['languages'][language]
  assert panel['configTitle'] in strings
  assert all(choice['display'] in strings for choice in panel['configOptions'])
 for key,default in expected.items():
  item=items[key];assert item['defaultValue']==default,(device,key,item)
  assert item['valueType']=='number' and item['configType']=='list'
  assert [x['value'] for x in item['configOptions']]==list(range(12))
  for language in ['valyrian','zhs']:
   strings=data['languages'][language]
   assert item['configTitle'] in strings
   for choice in item['configOptions']:assert choice['display'] in strings,(device,language,choice)
 print(device,'7 slots / 12 metrics / 4 panel styles / automatic + off + 4 holidays / 18 skins / weather link / opt-in birds and airplane / system + 12h + 24h / English + Chinese: PASS')
