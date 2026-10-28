from pathlib import Path
from PIL import Image
import json,math
ROOT=Path(__file__).resolve().parents[1];PACK=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Devices/instinct3solar45mm'
config=json.loads((PACK/'simulator.json').read_text());skin=Image.open(PACK/'device.png').convert('RGBA');main=config['display']['location'];sub=config['subscreen']['location'];points=[]
for y in range(sub['y']-15,sub['y']+sub['height']+15):
 for x in range(sub['x']-15,sub['x']+sub['width']+15):
  r,g,b,a=skin.getpixel((x,y))
  if r>60 and r>g*1.7 and g>10 and b<g*.6 and a>100:points.append((x,y))
bezel=[(min(x for x,y in points)+max(x for x,y in points))/2,(min(y for x,y in points)+max(y for x,y in points))/2]
matrix=json.loads((ROOT/'dist/device-matrix.json').read_text());row=next(r for r in matrix['devices'] if r['id']=='instinct3solar45mm');g=row['geometry']
center=[main['x']+g['circle_x']+144*g['circle_scale'],main['y']+g['circle_y']+31*g['circle_scale']]
assert center==bezel,(center,bezel)
circle=Image.open(ROOT/'generated'/row['profile']/'resources/drawables/circle.png').convert('1');clipped=0
ox=main['x']+round(g['circle_x']+113*g['circle_scale']);oy=main['y']+round(g['circle_y'])
for y in range(circle.height):
 for x in range(circle.width):
  if circle.getpixel((x,y)) and skin.getpixel((ox+x,oy+y))[3]>=128:clipped+=1
assert clipped==0,clipped
report={'device':'instinct3solar45mm','reference':'Garmin SDK device.png orange bezel and alpha aperture','bezel_center':bezel,'dial_center':center,'previous_center':[245,189],'offset':[-1,2],'white_face_diameter':59,'white_pixels_clipped_by_hardware_mask':clipped,'physical_device_tested':False}
(ROOT/'dist/circle-alignment-2.0.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
