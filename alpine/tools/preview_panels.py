"""Design contact sheet, NOT simulator evidence. Uses shared geometry and font atlases."""
from pathlib import Path
import math,re
from PIL import Image,ImageDraw,ImageFont
from panels import ROOT,layout


def preview(device,style):
    mono=device!='epix2';scale=1 if mono else 1.6
    w,h=(176,176) if mono else (416,416)
    im=Image.new('RGB',(w,h));d=ImageDraw.Draw(im)
    accent='white' if mono else '#efb85b'
    def p(v):return math.floor(v*scale+.5)
    def line(v):d.line(tuple(p(x) for x in v),fill=accent,width=1)
    fonts={}
    for name in ['Small','Label','Metric']:
        path=ROOT/f'generated/{device}/resources/fonts/{name}.fnt'
        lines=path.read_text().splitlines()
        chars={int(row['id']):{k:int(v) for k,v in row.items()} for s in lines if s.startswith('char ') for row in [dict(re.findall(r'(\w+)=(-?\d+)',s))]}
        fonts[name]=(Image.open(path.with_suffix('.png')).convert('RGBA'),chars)
    def text(x,y,name,value,color='white'):
        atlas,chars=fonts[name];width=sum(chars[ord(c)]['xadvance'] for c in value)
        xx=p(x)-width//2
        for c in value:
            g=chars[ord(c)];glyph=atlas.crop((g['x'],g['y'],g['x']+g['width'],g['y']+g['height']))
            im.paste(Image.new('RGB',glyph.size,color),(xx+g['xoffset'],p(y)+g['yoffset']),glyph.getchannel('A'));xx+=g['xadvance']
        return width
    center=88 if mono else 130;dy=126 if mono else 187
    width=text(center,dy,'Small','TUE 09/22')
    if style:
        y=130 if mono else 194;edge=30 if mono else 48;half=width/scale/2
        for side in range(2):
            direction=-1 if side==0 else 1;inner=center+direction*(half+5);outer=edge if side==0 else center*2-edge
            if abs(outer-center)<=half+9:continue
            line((inner,y,outer,y))
            if style==1:line((inner,y+1,inner+direction*5,y+1))
            elif style==2:line((outer,y,outer-direction*3,y-3))
            else:
                x=outer-direction*2;d.polygon([(p(a),p(b)) for a,b in [(x,y-2),(x+2,y),(x,y+2),(x-2,y)]],fill=accent)
    for ops in layout(mono,style):
        for kind,args in ops:
            if kind=='line':line(args)
            elif kind=='rect':
                x,y,ww,hh=args;d.rectangle((p(x),p(y),p(x+ww)-1,p(y+hh)-1),fill=accent)
            else:d.polygon([(p(x),p(y)) for x,y in args],fill=accent)
    xs=[46,88,130] if mono else [79,130,181]
    for x,label,value in zip(xs,['STEP','BPM','KCAL'],['6840','80','520']):
        text(x,141 if mono else 206,'Label',label,accent if style==2 else 'black')
        text(x,152 if mono else 222,'Metric',value)
    return im.crop((0,p(121 if mono else 181),w,p(170 if mono else 247)))


if __name__=='__main__':
    dest=ROOT/'dist/evidence';dest.mkdir(parents=True,exist_ok=True)
    board=Image.new('RGB',(1220,980),'#10171c');d=ImageDraw.Draw(board)
    font=ImageFont.truetype(str(ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'),24)
    small=ImageFont.truetype(str(ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'),19)
    d.text((28,16),'ALPINE / DATA PANEL STUDIES',font=font,fill='white')
    d.text((28,49),'Shared drawing geometry + native font atlas. Design preview; simulator verification pending.',font=small,fill='#91a4af')
    d.text((28,84),'INSTINCT / 1-BIT / 3X',font=small,fill='#91a4af')
    d.text((635,84),'AMOLED / 1X',font=small,fill='#efb85b')
    for i,title in enumerate(['01 CLASSIC','02 SUMMIT WINGS / DEFAULT','03 CONTOUR CARDS','04 EXPEDITION']):
        yy=120+i*210;d.text((28,yy),title,font=font,fill='white')
        a=preview('instinct3solar45mm',i);b=preview('epix2',i)
        a.save(dest/f'panel-style-{i}-mono-design.png');b.save(dest/f'panel-style-{i}-amoled-design.png')
        board.paste(a.resize((a.width*3,a.height*3),Image.Resampling.NEAREST),(28,yy+34))
        board.paste(b,(635,yy+42))
    board.save(dest/'panel-styles-design.png')
    print(dest/'panel-styles-design.png')
