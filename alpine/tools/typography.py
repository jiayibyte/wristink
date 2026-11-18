"""Native typography: continuous instrument numerals and hand-fitted small caps.
MIP receives binary native pixels; AMOLED retains coverage alpha for real font AA.
Rounded-stroke construction is adapted from this repository's Moke rasterizer.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
import pixel_glyphs as pg
FONT=Path(__file__).resolve().parents[1]/'assets/fonts/Rajdhani-SemiBold.ttf'
CAPS={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['111','010','010','010','010','010','111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10001','10001','10001','10001','01110'],
'1':['010','110','010','010','010','010','111'],
'2':['01110','10001','00001','00110','01000','10000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
':':['0','1','1','0','1','1','0'],'.':['0','0','0','0','0','0','1'],
'-':['000','000','000','111','000','000','000'],
'/':['00001','00001','00010','00100','01000','10000','10000'],
'%':['11001','11010','00100','00100','01000','10110','00110'],
' ':['00']*7}


def smooth_path(d,points,radius,stroke):
    path=[points[0]]
    for a,b,c in zip(points,points[1:],points[2:]):
        ab=math.dist(a,b);bc=math.dist(b,c)
        if not ab or not bc:continue
        r=min(radius,ab/2,bc/2)
        start=tuple(b[j]+(a[j]-b[j])*r/ab for j in (0,1));end=tuple(b[j]+(c[j]-b[j])*r/bc for j in (0,1))
        path.append(start)
        for i in range(1,13):
            t=i/12;path.append(tuple((1-t)**2*start[j]+2*(1-t)*t*b[j]+t*t*end[j] for j in (0,1)))
    path.append(points[-1]);d.line(path,fill=255,width=stroke,joint='curve')
    r=max(0,stroke/2-.5)
    for x,y in (points[0],points[-1]):d.ellipse((x-r,y-r,x+r,y+r),fill=255)


def instrument(char,w,h,stroke,aa):
    ss=8;im=Image.new('L',(w*ss,h*ss));d=ImageDraw.Draw(im)
    half=(stroke-1)/2;l=half;r=w-1-half;t=half;b=h-1-half;m=round((h-stroke)/2)+half
    radius=max(1,round(min(w*.20,h*.085)))
    paths={
      '1':[[(l,t+(b-t)*.14),(l+(r-l)*.58,t),(l+(r-l)*.58,b)]],
      '2':[[(l,t+radius),(l,t),(r,t),(r,m),(l,m),(l,b),(r,b)]],
      '3':[[(l,t),(r,t),(r,b),(l,b)],[(l+(r-l)*.12,m),(r,m)]],
      '4':[[(l,t),(l,m),(r,m)],[(r,t),(r,b)]],
      '5':[[(r,t),(l,t),(l,m),(r,m),(r,b),(l,b)]],
      '6':[[(r,t),(l,t),(l,b),(r,b),(r,m),(l,m)]],
      '7':[[(l,t),(r,t),(l+(r-l)*.33,b)]],
      '9':[[(r,m),(l,m),(l,t),(r,t),(r,b),(l,b)]]}
    def rect(box,rad,fill):d.rounded_rectangle(tuple(round(v*ss) for v in box),radius=rad*ss,fill=fill)
    if char in '08':
        rect((0,0,w-1/ss,h-1/ss),radius+half,255)
        if char=='0':rect((stroke,stroke,w-stroke-1/ss,h-stroke-1/ss),max(.5,radius-half),0)
        else:
            mid=h//2;rect((stroke,stroke,w-stroke-1/ss,mid-(stroke+1)//2-1/ss),max(.5,radius-half),0)
            rect((stroke,mid+stroke//2,w-stroke-1/ss,h-stroke-1/ss),max(.5,radius-half),0)
    else:
        for path in paths[char]:smooth_path(d,[((x+.5)*ss,(y+.5)*ss) for x,y in path],radius*ss,stroke*ss)
    im=im.resize((w,h),Image.Resampling.BOX)
    return im if aa else im.point(lambda v:255 if v>=128 else 0)


def pixel_text(ch,height):
    rows=CAPS[ch]
    # Extend vertical stems, retaining one-pixel horizontal strokes and open counters.
    if height>=9:rows=rows[:2]+[rows[1]]+rows[2:6]+[rows[5]]+rows[6:]
    im=Image.new('L',(len(rows[0]),height))
    y0=(height-len(rows))//2
    for y,row in enumerate(rows):
        for x,v in enumerate(row):
            if v=='1':im.putpixel((x,y+y0),255)
    return im


def outline_text(ch,h,aa):
    if ch==' ':return Image.new('L',(max(2,round(h*.28)),h))
    ss=4;size=1
    while True:
        f=ImageFont.truetype(str(FONT),(size+1)*ss);box=f.getbbox('H')
        if box[3]-box[1]>h*ss:break
        size+=1
    f=ImageFont.truetype(str(FONT),size*ss);box=f.getbbox(ch);w=max(1,box[2]-box[0]);hh=max(1,box[3]-box[1]);im=Image.new('L',(w,hh));ImageDraw.Draw(im).text((-box[0],-box[1]),ch,font=f,fill=255)
    box=im.getbbox()
    if not box:return Image.new('L',(2,h))
    im=im.crop(box);im=im.resize((max(1,round(im.width/ss)),min(h,max(1,round(im.height/ss)))),Image.Resampling.BOX)
    out=Image.new('L',(im.width,h));out.paste(im,(0,h-im.height))
    return out if aa else out.point(lambda v:255 if v>=128 else 0)


def make_font(dest,name,height,mono,aa):
    chars='0123456789:-' if name in ('Time','Aod') else ('0123456789:-.CFDKM' if name=='Circle' else ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-:.%/')
    glyphs=[];gap=max(1,round(height*.055))
    for ch in chars:
        if mono and name in ('Small','Label'):
            glyph=pixel_text(ch,height)
        elif ch.isdigit():
            ratio=.60 if mono else .64
            w=round(height*ratio)
            if name=='Metric':w=max(5,round(height*.58))
            stroke=max(1,round(height*(.105 if name in ('Time','Aod') else .12 if name=='Circle' else .09)))
            stroke=min(stroke,max(1,(w-1)//3))
            # Two-colour pixels (MIP) get numerals built on the pixel grid; a
            # thresholded rounded path leaves uneven stems and stepped diagonals.
            glyph=instrument(ch,w,height,stroke,aa) if aa else pg.digit(ch,w,height,0,stroke)
        elif ch in ':-.':
            w=max(2,round(height*(.16 if ch!='-' else .35)));glyph=Image.new('L',(w,height));d=ImageDraw.Draw(glyph)
            dot=max(1,round(height*.09))
            if ch=='-':d.rectangle((0,(height-dot)//2,w-1,(height+dot)//2-1),fill=255)
            else:
                for y in ([round(height*.28),round(height*.68)] if ch==':' else [height-dot]):d.rectangle(((w-dot)//2,y,(w-dot)//2+dot-1,min(height-1,y+dot-1)),fill=255)
        elif mono and name=='Metric':glyph=pixel_text(ch,height)
        elif not aa and (ch in pg.CAPS or ch in '%/'):
            # Same advance as the outline letter, drawn on the grid instead of thresholded.
            width=outline_text(ch,height,False).width
            stroke=1 if height<13 else max(2,round(height*.12))
            glyph=pg.caps(ch,width,height,stroke) if ch in pg.CAPS else pg.latin(ch,width,height,stroke)
        else:glyph=outline_text(ch,height,aa)
        if ch=='1' and name in ('Time','Circle','Aod'):
            bounds=glyph.getbbox()
            if bounds:glyph=glyph.crop((0,0,bounds[2],height))
        glyphs.append((ch,glyph))
    # Tabular small numerals; a natural narrow one sits within the same cell.
    cell=max(g.width for _,g in glyphs)+gap;atlas=Image.new('RGBA',(cell*len(glyphs),height),(255,255,255,0));entries=[]
    for i,(ch,g) in enumerate(glyphs):
        im=Image.new('RGBA',g.size,(255,255,255,0));im.putalpha(g);atlas.paste(im,(i*cell,0))
        entries.append(f'char id={ord(ch)} x={i*cell} y=0 width={g.width} height={height} xoffset=0 yoffset=0 xadvance={g.width+gap} page=0 chnl=15')
    atlas.save(dest/f'{name}.png')
    (dest/f'{name}.fnt').write_text(f'info face="Alpine Instrument" size={height} bold=0 italic=0 unicode=1 smooth={int(aa)} aa=1\ncommon lineHeight={height} base={height} scaleW={atlas.width} scaleH={height} pages=1 packed=0\npage id=0 file="{name}.png"\nchars count={len(glyphs)}\n'+'\n'.join(entries)+'\n')
    return {ch:dict(width=g.width,advance=g.width+gap,height=height) for ch,g in glyphs}


def build_fonts(dest,scale,mono,amoled):
    sizes={'Time':round((39 if mono else 49)*scale),'Circle':round(20*scale),'Small':9 if mono else round(13*scale),'Label':7 if mono else round(11*scale),'Metric':round((11 if mono else 15)*scale),'Aod':round(21*scale)}
    # The 2S uses shorter numerals; label masters retain their full 5x7 counters.
    if mono and scale<1:sizes['Small']=7;sizes['Metric']=10
    metrics={name:make_font(dest,name,h,mono,amoled) for name,h in sizes.items()}
    (dest/'fonts.xml').write_text('<fonts>'+''.join(f'<font id="{name}" filename="{name}.fnt" antialias="{str(amoled).lower()}"/>' for name in sizes)+'</fonts>\n')
    (dest/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
