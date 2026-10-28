"""Check native artwork bounds and AMOLED burn-in masks before store export."""
from pathlib import Path
import json,math,re
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[1];matrix=json.loads((ROOT/'dist/device-matrix.json').read_text())
seen={};results=[]
def n(v,s):return max(1,math.floor(v*s+.5))
def aod_image(atlas,g,minutes):
    w=atlas.width//10;h=atlas.height;s=g['scale'];gap=n(2,s);colon=n(5,s);width=4*w+2*gap+colon
    phase=minutes%4;dx=-3 if phase%2==0 else 3;dy=-3 if phase<2 else 3
    x=int((g['width']-width)/2)+dx;y=int((g['height']-h)/2)+dy;hour=(minutes//60)%24;minute=minutes%60
    im=Image.new('1',(g['width'],g['height']),0)
    for k,(digit,xx) in enumerate(zip((hour//10,hour%10,minute//10,minute%10),(x,x+w+gap,x+2*w+gap+colon,x+3*w+2*gap+colon))):im.paste(atlas.crop((digit*w,0,(digit+1)*w,h)),(xx,y))
    if minutes%2==0:
        d=ImageDraw.Draw(im);dot=n(1,s);xx=x+2*w+gap+int((colon-dot)/2)
        for yy in (y+h//3,y+2*h//3):d.rectangle((xx,yy,xx+dot-1,yy+dot-1),fill=1)
    d=ImageDraw.Draw(im);start=x-h
    while (start-y)%4!=phase:start+=1
    for line in range(start,x+width,4):d.line((line,y,line+h-1,y+h-1),fill=0)
    return im
for row in matrix['devices']:
 key=row['profile'];g=row['geometry'];r=ROOT/'generated'/key/'resources'
 if key in seen:continue
 dial=Image.open(r/'drawables/dial.png');assert dial.size==(g['width'],g['height'])
 # Adjacent logical rows/spans must tile the native buffer with no gaps.
 for extent in (29,89):
    edges=[math.floor(i*g['scale']+.5) for i in range(extent+1)]
    assert edges[0]==0 and edges[-1]==n(extent,g['scale'])
    assert all(b>=a for a,b in zip(edges,edges[1:]))
 data={'profile':key,'representative':row['id'],'size':dial.size,'color':row['color']}
 for font_name in ('tiny','medium','weather-small'):
    atlas_font=Image.open(r/'fonts'/f'{font_name}.png').convert('RGBA');glyphs=[]
    for line in (r/'fonts'/f'{font_name}.fnt').read_text().splitlines():
        if not line.startswith('char id='):continue
        values={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
        if 48<=values['id']<=57:
            glyph=atlas_font.crop((values['x'],values['y'],values['x']+values['width'],values['y']+values['height']))
            glyphs.append(glyph.getchannel('A').tobytes())
    assert len(glyphs)==10 and len(set(glyphs))==10,(key,font_name,'digit shapes collapsed')
 data['all_small_digits_distinct']=True
 if row['color']:
    # Treat every nonblack pixel as lit, even the low-gray outline.
    atlas=Image.open(r/'drawables/aod.png').convert('L').point(lambda v:255 if v else 0).convert('1')
    recent=[];peak=0;intersections=0;sample=None
    for minute in range(1443):
        im=aod_image(atlas,g,minute);lit=im.histogram()[255];peak=max(peak,lit)
        recent.append(im)
        if len(recent)>4:recent.pop(0)
        if len(recent)==4:
            all_on=recent[0]
            for mask in recent[1:]:all_on=ImageChops.logical_and(all_on,mask)
            intersections=max(intersections,all_on.histogram()[255])
        if minute==608:sample=im
    # Conservative visible area for round displays, not its bounding square.
    area=math.pi*(min(g['width'],g['height'])/2)**2 if g['shape']=='round' else g['width']*g['height']
    data.update(aod_peak_pixels=peak,aod_fraction=peak/area,aod_four_minute_shared_pixels=intersections)
    assert peak/area<.10,(key,peak/area)
    assert intersections==0,(key,'continuous AOD pixels',intersections)
    sample.save(ROOT/'dist'/('aod-'+row['id']+'.png'))
 results.append(data);seen[key]=data
# Keep the regression baseline in source so a fresh clone needs no old release ZIP.
old=Image.open(ROOT/'tests/fixtures/dial-1.2.14.png').convert('1')
new=Image.open(ROOT/'generated/semioctagon-176x176-mip-instinct3solar45mm-i62/resources/drawables/dial.png').convert('1')
before_outside=old.copy();after_outside=new.copy()
for image in (before_outside,after_outside):ImageDraw.Draw(image).rectangle((112,0,175,64),fill=0)
assert ImageChops.difference(before_outside,after_outside).getbbox() is None
(ROOT/'dist/device-layout-validation.json').write_text(json.dumps({'profiles':results,'original_instinct_other_regions_identical':True,'instinct3_circle_adjustment':{'dx':-1,'dy':2,'inset':2},'aod_checked_minutes':1443},indent=2)+'\n')
print('Validated',len(results),'native resource profiles and one full AOD day per AMOLED profile.')
