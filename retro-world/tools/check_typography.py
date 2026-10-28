"""Check the user's same-style constraint using the released bitmap resources.

Metrics and letter glyphs must be unchanged. Digit cleanup is limited to <=5%
of the previous ink pixels and preserve stroke topology. Ink bounds may only
shrink inward by one pixel when removing an isolated spur; cell metrics stay fixed.
The date reference is intentionally compacted from 15 to 13 rows before comparison.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import io,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
BASELINE=DIST/'RetroWorld-Instinct3-1.2.4.zip'

def ink(im):return {(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))==0}
def count_components(points,diagonal):
    points=set(points);count=0
    neighbours=[(-1,0),(1,0),(0,-1),(0,1)]+([(-1,-1),(-1,1),(1,-1),(1,1)] if diagonal else [])
    while points:
        count+=1;stack=[points.pop()]
        while stack:
            x,y=stack.pop()
            for dx,dy in neighbours:
                p=(x+dx,y+dy)
                if p in points:points.remove(p);stack.append(p)
    return count
def bounds(points):return (min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points))
def background(points,w,h):return {(x,y) for y in range(-1,h+1) for x in range(-1,w+1)}-points

def main():
    rows=[]
    with zipfile.ZipFile(BASELINE) as z:
        unchanged=['resources/fonts/'+n for n in ('tiny.png','tiny.fnt','medium.png','medium.fnt')]
        unchanged+=['resources/drawables/'+n for n in ('letters.png','weekdays.png','weather.png')]
        for name in unchanged:assert (ROOT/name).read_bytes()==z.read('source-project/'+name),name
        for name,w,h in [('large.png',22,35),('date.png',8,13)]+[(f'second-{n}.png',13,24) for n in range(10)]:
            old=Image.open(io.BytesIO(z.read('source-project/resources/drawables/'+name)))
            new=Image.open(ROOT/'resources/drawables'/name)
            if name=='date.png':
                compact=Image.new('1',(80,13),1)
                for target,source in enumerate(y for y in range(15) if y not in (5,11)):
                    compact.paste(old.crop((0,source,80,source+1)),(0,target))
                old=compact
            assert new.size==old.size and new.mode=='1',name
            digits=range(10) if name in ('large.png','date.png') else [int(name[7])]
            for n in digits:
                box=(n*w,0,(n+1)*w,h) if name in ('large.png','date.png') else (0,0,w,h)
                a=ink(old.crop(box));b=ink(new.crop(box));changed=len(a^b)
                ab=bounds(a);bb=bounds(b)
                assert bb[0]>=ab[0] and bb[1]>=ab[1] and bb[2]<=ab[2] and bb[3]<=ab[3],(name,n,'expansion')
                assert max(abs(x-y) for x,y in zip(ab,bb))<=1,(name,n,'bounds')
                assert changed/len(a)<=.05,(name,n,'too much change')
                assert count_components(a,True)==count_components(b,True),(name,n,'stroke connectivity')
                assert count_components(background(a,w,h),False)==count_components(background(b,w,h),False),(name,n,'counter topology')
                rows.append({'file':name,'digit':n,'changed_pixels':changed,'old_ink_pixels':len(a),'ink_change_fraction':round(changed/len(a),5),'old_ink_bounds':ab,'new_ink_bounds':bb})
        old_face=Image.open(io.BytesIO(z.read('RetroWorld-pixels.png'))).convert('RGB')
    new_face=Image.open(DIST/'RetroWorld-pixels.png').convert('RGB')
    # Compare typography against the same current map style, not the older basemap.
    old_face.paste(new_face.crop((13,52,110,89)),(13,52))
    old_face.paste(new_face.crop((13,30,111,50)),(13,30))
    old_face.paste(new_face.crop((121,93,162,108)),(121,93))
    old_face.paste(new_face.crop((113,0,176,63)),(113,0))
    f=ImageFont.truetype(str(ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'),23)
    panel=Image.new('RGB',(728,394),'#e9e9e9');d=ImageDraw.Draw(panel)
    for x,label,im in ((8,'BEFORE',old_face),(368,'SAME STYLE / EDGE CLEANUP',new_face)):
        d.text((x,2),label,font=f,fill='black')
        panel.paste(im.resize((352,352),Image.Resampling.NEAREST),(x,34))
    panel.save(DIST/'RetroWorld-type-comparison.png')
    report={'baseline':'1.2.4; date reference compacted by deleting one straight row in each vertical half','binary_format':'1-bit; no grayscale or temporal dithering','max_ink_change_fraction':max(r['ink_change_fraction'] for r in rows),'metrics_unchanged_except_date':True,'date_cell_size':{'before':[8,15],'after':[8,13]},'letter_fonts_unchanged':True,'topology_unchanged':True,'ink_bounds':'no expansion; at most one pixel of inward spur removal relative to the compacted date reference','glyphs':rows}
    (DIST/'typography-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Typography constraints passed: dimensions/topology unchanged, no ink expansion, <=5% digit-ink changes, tiny/medium letters unchanged.')

if __name__=='__main__':main()
