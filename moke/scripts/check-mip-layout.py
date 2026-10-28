"""Validate generated native asset bounds and screen transforms for every MIP target."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET,math
from PIL import Image
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'config/mip-devices.json').read_text());seen=set();count=0
for row in rows:
 g=row['geometry'];s=g['scale'];w,h=g['width'],g['height'];assert g['x']>=0 and g['y']>=0
 # Canonical region corners fit the physical display bounds. Round model profiles
 # deliberately reserve an inset; Instinct's dedicated circle has a separate scale.
 assert g['x']+176*s<=w+1 and g['y']+176*s<=h+1,row['id']
 cx=g['circle_x']+144*g['circle_scale'];cy=g['circle_y']+31*g['circle_scale'];radius=31*g['circle_scale']
 assert cx-radius>=-1 and cy-radius>=-1 and cx+radius<=w+1 and cy+radius<=h+1,row['id']
 if g['shape']=='round':assert math.hypot(cx-w/2,cy-h/2)+radius<=min(w,h)/2+1,row['id']
 if not row['on_watch_settings']:assert not (R/'generated/assets'/row['asset_key']/'resources/config').exists()
 key=row['asset_key']
 if key in seen:continue
 seen.add(key);folder=R/'generated/assets'/key/'resources'
 for f in (folder/'fonts').glob('*.fnt'):
  text=f.read_text();page=re.search(r'page id=0 file="([^"]+)"',text)
  if not page:continue
  with Image.open(f.parent/page[1]) as im:
   for line in text.splitlines():
    if not line.startswith('char id='):continue
    d={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
    assert 0<=d['x']<im.width and 0<=d['y']<im.height,(key,f.name,d)
    assert d['x']+d['width']<=im.width and d['y']+d['height']<=im.height,(key,f.name,d)
    count+=1
 for item in ET.parse(folder/'drawables/drawables.xml').getroot():assert (folder/'drawables'/item.get('filename')).exists()
result=dict(status='passed',devices=len(rows),asset_profiles=len(seen),glyph_bounds=count,scope='Native assets and transform geometry; representative simulator results are recorded separately.')
(R/'bin/mip-layout-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
