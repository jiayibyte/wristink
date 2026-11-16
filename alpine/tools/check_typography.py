"""Check actual font atlases: coverage, distinct numerals, counters and slot widths."""
from pathlib import Path
from PIL import Image
import re,json
R=Path(__file__).resolve().parents[1]
def holes(im):
    pix=im.point(lambda p:255 if p>=128 else 0);w,h=pix.size;seen=set();count=0
    for y in range(h):
      for x in range(w):
        if pix.getpixel((x,y)) or (x,y) in seen:continue
        stack=[(x,y)];seen.add((x,y));border=False
        while stack:
          xx,yy=stack.pop();border|=xx==0 or yy==0 or xx==w-1 or yy==h-1
          for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
            if 0<=nx<w and 0<=ny<h and (nx,ny) not in seen and not pix.getpixel((nx,ny)):
              seen.add((nx,ny));stack.append((nx,ny))
        if not border:count+=1
    return count
results=[]
for profile in json.loads((R/'generated/profiles.json').read_text()):
 folder=R/'generated'/profile['device']/'resources/fonts'
 for name in ['Time','Circle','Small','Label','Metric','Aod']:
  spec=(folder/f'{name}.fnt').read_text();atlas=Image.open(folder/f'{name}.png').getchannel('A');glyphs={};advance={}
  for line in spec.splitlines():
   if not line.startswith('char id='):continue
   v={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
   assert 0<=v['x'] and v['x']+v['width']<=atlas.width
   assert 0<=v['y'] and v['y']+v['height']<=atlas.height
   glyphs[chr(v['id'])]=atlas.crop((v['x'],v['y'],v['x']+v['width'],v['y']+v['height']));advance[chr(v['id'])]=v['xadvance']
  assert all(glyphs[c].getbbox() for c in '0123456789')
  assert len({glyphs[c].tobytes() for c in '0123456789'})==10
  assert holes(glyphs['0'])==1,(profile['device'],name,'0 counter')
  assert holes(glyphs['8'])==2,(profile['device'],name,'8 counters')
  values=set(atlas.getdata())
  if profile['MONO']:assert values<={0,255}
  if profile['AMOLED']:assert any(0<v<255 for v in values)
  if name=='Metric':
   limit=round((37 if profile['MONO'] else 45)*profile['S'])
   for value in ['8620','1688','-6C','18D','--D']:
    assert sum(advance[c] for c in value)<=limit,(profile['device'],value,limit)
  if name=='Label':assert holes(glyphs['B'])==2,(profile['device'],'B counters')
 results.append({'device':profile['device'],'passed':True,'antialias':profile['AMOLED']})
(R/'dist/typography-audit.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
