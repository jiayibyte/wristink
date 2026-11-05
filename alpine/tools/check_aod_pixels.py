"""Conservative font-mask audit, not a physical battery/burn-in measurement."""
from pathlib import Path
import json,re
from PIL import Image
R=Path(__file__).resolve().parents[1]
folder=R/'generated/epix2/resources/fonts';atlas=Image.open(folder/'Aod.png').getchannel('A')
glyphs={}
for row in (folder/'Aod.fnt').read_text().splitlines():
 if not row.startswith('char id='):continue
 d={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',row)}
 im=atlas.crop((d['x'],d['y'],d['x']+d['width'],d['y']+d['height']))
 glyphs[chr(d['id'])]=(im,d)
results=[]
for fmt in [12,24]:
 max_pixels=0;max_value='';max_width=0
 for minute in range(1440):
  hour=minute//60;shown=hour if fmt==24 else (hour%12 or 12);value=f'{shown:02d}:{minute%60:02d}'
  pixels=sum(sum(v>0 for v in glyphs[c][0].getdata()) for c in value)
  width=sum(glyphs[c][1]['xadvance'] for c in value)
  if pixels>max_pixels:max_pixels=pixels;max_value=value
  max_width=max(max_width,width)
 results.append({'format':fmt,'maximumNonzeroAlphaPixels':max_pixels,'maximumCanvasPercent':round(max_pixels/(416*416)*100,3),'largestInkExample':max_value,'maximumAdvance':max_width})
height=max(v[0].height for v in glyphs.values());rows=[round(v*1.6) for v in [64,105,146,187]]
assert all(abs(a-b)>=height for a,b in zip(rows,rows[1:]+rows[:1]))
assert all(x['maximumCanvasPercent']<3 for x in results)
report={'device':'epix2','kind':'conservative offline bitmap-font mask audit','frames':2880,'fontHeight':height,'minuteRows':rows,'adjacentRowsDoNotOverlap':True,'results':results,'limits':'Not an actual framebuffer capture, device battery measurement or burn-in certification.'}
(R/'dist/evidence/aod-pixel-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
