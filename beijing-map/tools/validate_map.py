#!/usr/bin/env python3
import json,math,re,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
stats=json.loads((ROOT/'data/map-stats.json').read_text());data=json.loads((ROOT/'data/packed-preview.json').read_text())
places=re.findall(r'\["([^\"]+)",([0-9.]+),([0-9.]+)\]',(ROOT/'source/BeijingMapApp.mc').read_text())
coverage={}
for name,lon,lat in places:
 x=(float(lon)-115)*111320*math.cos(math.radians(40));y=(float(lat)-39)*111320
 key=f'{math.floor(x/stats["tile_meters"])},{math.floor(y/stats["tile_meters"])}'
 coverage[name]={'tile':key,'present':key in data}
assert len(coverage)==16 and all(v['present'] for v in coverage.values())
records=points=0
for chunks in data.values():
 for chunk in chunks:
  i=0
  while i<len(chunk):
   kind=ord(chunk[i])-33;n=(ord(chunk[i+1])-33)*64+ord(chunk[i+2])-33;i+=3
   assert kind in range(4) and n>=2 and i+4*n<=len(chunk)
   for j in range(n*2):
    v=(ord(chunk[i+2*j])-33)*64+ord(chunk[i+2*j+1])-33;assert 0<=v<=stats['tile_meters']//stats.get('coordinate_unit_meters',2)
   i+=4*n;records+=1;points+=n
  assert i==len(chunk)
resources=E.parse(ROOT/'resources/map/maps.xml').getroot();max_payload=max(len(json.loads(x.text)) for x in resources)
assert max_payload<=7008
result={'districts':coverage,'packed_records':records,'coordinate_pairs':points,'resources':len(resources),'largest_payload_bytes':max_payload,'passed':True}
(ROOT/'dist/data-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='districts'}))
