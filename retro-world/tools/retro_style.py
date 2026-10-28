from pathlib import Path
from PIL import Image, ImageDraw
import math
ROOT=Path(__file__).resolve().parents[1]


GLYPHS = {
 '0':['111','101','101','101','111'], '1':['010','110','010','010','111'],
 '2':['111','001','111','100','111'], '3':['111','001','111','001','111'],
 '4':['101','101','111','001','001'], '5':['111','100','111','001','111'],
 '6':['111','100','111','101','111'], '7':['111','001','010','010','010'],
 '8':['111','101','111','101','111'], '9':['111','101','111','001','111'],
 'A':['010','101','111','101','101'], 'B':['110','101','110','101','110'],
 'C':['111','100','100','100','111'], 'D':['110','101','101','101','110'],
 'E':['111','100','110','100','111'], 'F':['111','100','110','100','100'],
 'G':['111','100','101','101','111'], 'H':['101','101','111','101','101'],
 'I':['111','010','010','010','111'], 'J':['001','001','001','101','111'],
 'K':['101','101','110','101','101'], 'L':['100','100','100','100','111'],
 'M':['10001','11011','10101','10001','10001'], 'N':['1001','1101','1011','1001','1001'],
 'O':['111','101','101','101','111'], 'P':['111','101','111','100','100'],
 'Q':['111','101','101','111','001'], 'R':['110','101','110','101','101'],
 'S':['111','100','111','001','111'], 'T':['111','010','010','010','010'],
 'U':['101','101','101','101','111'], 'V':['101','101','101','101','010'],
 'W':['10001','10001','10101','11011','10001'], 'X':['101','101','010','101','101'],
 'Y':['101','101','010','010','010'], 'Z':['111','001','010','100','111'],
 ' ':['0','0','0','0','0'], '-':['000','000','111','000','000'],
 '%':['101','001','010','100','101'], ':':['0','1','0','1','0'],
 '.':['0','0','0','0','1'], '/':['001','001','010','100','100'],
}

def text(im, x, y, s, color=0, sx=1, sy=1, center=False):
    width = sum((len(GLYPHS[c][0])+1)*sx for c in s)-sx
    if center: x -= width//2
    d=ImageDraw.Draw(im)
    for c in s:
        for row, bits in enumerate(GLYPHS[c]):
            for col, bit in enumerate(bits):
                if bit=='1': d.rectangle((x+col*sx,y+row*sy,x+(col+1)*sx-1,y+(row+1)*sy-1),fill=color)
        x += (len(GLYPHS[c][0])+1)*sx

def legacy_digit(n,w,h):
    # Seven separated, bevelled segments, with the LCD's slight rightward slant.
    im=Image.new('1',(w,h),1);d=ImageDraw.Draw(im)
    t=max(1,round(w*.18)); slant=max(1,round(w*.09));left=0;right=w-1-slant;mid=h//2
    def skew(p):
        return [(round(x+slant*(1-y/(h-1))),round(y)) for x,y in p]
    def horiz(y):
        return [(left+t/2,y),(right-t/2,y),(right,y+t/2),(right-t/2,y+t),(left+t/2,y+t),(left,y+t/2)]
    def vert(x,y1,y2):
        return [(x+t/2,y1),(x+t,y1+t/2),(x+t,y2-t/2),(x+t/2,y2),(x,y2-t/2),(x,y1+t/2)]
    polys=[horiz(0),vert(right-t,2,mid-1),vert(right-t,mid+1,h-2),horiz(h-t-1),vert(left,mid+1,h-2),vert(left,2,mid-1),horiz(mid-t//2)]
    segments=['abcdef','bc','abdeg','abcdg','bcfg','acdfg','acdefg','abc','abcdefg','abcdfg'][n]
    for i,k in enumerate('abcdefg'):
        if k in segments:d.polygon(skew(polys[i]),fill=0)
    return im

def digit(n,w,h):
    """Refine only raster edges of the original slanted segment outlines.

    Keep metrics, segment selection, bevels, slant and inclusive stroke weight.
    Tiny date cells receive only one-pixel notch fills at the end caps.
    All work happens at asset-build time; the watch still draws 1-bit bitmaps.
    """
    original=legacy_digit(n,w,h)
    if w<12:
        result=original.copy()
        for y in (1,h-2):
            for x in range(w):
                if original.getpixel((x,y))==0:continue
                neighbours=sum(0<=xx<w and 0<=yy<h and original.getpixel((xx,yy))==0
                               for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
                if neighbours>=3:result.putpixel((x,y),0)
        return result
    ss=8
    mask=Image.new('L',(w*ss,h*ss),0);d=ImageDraw.Draw(mask)
    t=max(1,round(w*.18));slant=max(1,round(w*.09));left=0;right=w-1-slant;mid=h//2
    def project(points):
        return [(round((x+slant*(1-y/(h-1))+.5)*ss),round((y+.5)*ss)) for x,y in points]
    def horiz(y):
        return [(left+t/2,y),(right-t/2,y),(right,y+t/2),(right-t/2,y+t),(left+t/2,y+t),(left,y+t/2)]
    def vert(x,y1,y2):
        return [(x+t/2,y1),(x+t,y1+t/2),(x+t,y2-t/2),(x+t/2,y2),(x,y2-t/2),(x,y1+t/2)]
    polys=[horiz(0),vert(right-t,2,mid-1),vert(right-t,mid+1,h-2),horiz(h-t-1),vert(left,mid+1,h-2),vert(left,2,mid-1),horiz(mid-t//2)]
    segments=['abcdef','bc','abdeg','abcdg','bcfg','acdfg','acdefg','abc','abcdefg','abcdfg'][n]
    for key,poly in zip('abcdefg',polys):
        if key in segments:
            points=project(poly);d.polygon(points,fill=255)
            # Half a native pixel around the outline matches PIL's original
            # inclusive polygon edges without rounding vertices prematurely.
            d.line(points+[points[0]],fill=255,width=ss,joint='curve')
    coverage=mask.resize((w,h),Image.Resampling.BOX)
    return coverage.point(lambda v:0 if v>=128 else 255).convert('1')

def fonts():
    folder=ROOT/'resources/fonts';folder.mkdir(exist_ok=True)
    for name,scale in [('tiny',1),('medium',2)]:
        chars=sorted(GLYPHS);cell=6*scale;h=5*scale
        atlas=Image.new('RGBA',(len(chars)*cell,h),(0,0,0,0))
        rows=[f'info face="Retro Data" size={h} bold=0 italic=0 unicode=1 smooth=0 aa=1',
              f'common lineHeight={h} base={h} scaleW={atlas.width} scaleH={h} pages=1 packed=0',
              f'page id=0 file="{name}.png"',f'chars count={len(chars)}']
        for i,c in enumerate(chars):
            mask=Image.new('1',(cell,h),0);text(mask,0,0,c,1,sx=scale,sy=scale)
            atlas.paste((255,255,255,255),(i*cell,0),mask)
            w=len(GLYPHS[c][0])*scale
            rows.append(f'char id={ord(c)} x={i*cell} y=0 width={w} height={h} xoffset=0 yoffset=0 xadvance={w+scale} page=0 chnl=15')
        atlas.save(folder/(name+'.png'));(folder/(name+'.fnt')).write_text('\n'.join(rows)+'\n')
    # Same 3x5 master as the existing temperature lettering, grid-fitted to 5x8.
    chars='-0123456789C';cell=6;h=8;atlas=Image.new('RGBA',(len(chars)*cell,h),(0,0,0,0))
    rows=['info face="Retro Data" size=8 bold=0 italic=0 unicode=1 smooth=0 aa=1',
          f'common lineHeight=8 base=8 scaleW={atlas.width} scaleH=8 pages=1 packed=0',
          'page id=0 file="weather-small.png"',f'chars count={len(chars)}']
    for i,c in enumerate(chars):
        mask=weather_glyph(c);atlas.paste((255,255,255,255),(i*cell,0),mask)
        rows.append(f'char id={ord(c)} x={i*cell} y=0 width=5 height=8 xoffset=0 yoffset=0 xadvance=6 page=0 chnl=15')
    atlas.save(folder/'weather-small.png');(folder/'weather-small.fnt').write_text('\n'.join(rows)+'\n')
    (folder/'fonts.xml').write_text('<fonts><font id="Tiny" filename="tiny.fnt"/><font id="Medium" filename="medium.fnt"/><font id="WeatherSmall" filename="weather-small.fnt"/></fonts>\n')

def weather_glyph(char):
    mask=Image.new('1',(5,8),0);d=ImageDraw.Draw(mask)
    for row,bits in enumerate(GLYPHS[char]):
        for col,bit in enumerate(bits):
            if bit=='1':d.rectangle((round(col*5/3),round(row*8/5),round((col+1)*5/3)-1,round((row+1)*8/5)-1),fill=1)
    return mask
