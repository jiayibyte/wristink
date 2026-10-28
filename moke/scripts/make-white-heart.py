"""Bigger, tabular heart-rate numerals inside the existing white 63px window."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
from font_rasterizer import reference_digit,NOTO

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'resources/native'
tree=ET.parse(OUT/'fonts.xml');root=tree.getroot()
for el in list(root):
    if el.get('id','').startswith('WhiteHeart'):root.remove(el)
catalog=[]
for family in range(3):
    for size,height in enumerate([22,26,28]):
        cell=14 if family==2 else 16;width=cell-2;chars='0123456789-'
        name=f'white-heart-f{family}-s{height}';ident=f'WhiteHeartF{family}S{height}'
        atlas=Image.new('RGBA',((cell+1)*len(chars),height),(255,255,255,0));rows=[]
        for i,char in enumerate(chars):
            tile=Image.new('L',(cell,height))
            if char=='-':
                ImageDraw.Draw(tile).rounded_rectangle((3,height//2-1,cell-4,height//2+1),radius=1,fill=255)
            else:
                w=width//2 if char=='1' else width
                if family==1:
                    font=ImageFont.truetype(str(NOTO),round(height/.72)*8);b=font.getbbox(char)
                    im=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(im).text((-b[0],-b[1]),char,font=font,fill=255)
                    ink=im.crop(im.getbbox()).resize((w,height),Image.Resampling.BOX).point(lambda p:255 if p>=128 else 0)
                else:ink=reference_digit(char,w,height,family,False)
                tile.paste(ink,((cell-w)//2,0))
            rgba=Image.new('RGBA',tile.size,(255,255,255,0));rgba.putalpha(tile);atlas.paste(rgba,(i*(cell+1),0))
            rows.append(f'char id={ord(char)} x={i*(cell+1)} y=0 width={cell} height={height} xoffset=0 yoffset=0 xadvance={cell} page=0 chnl=15')
        atlas.save(OUT/(name+'.png'))
        (OUT/(name+'.fnt')).write_text('\n'.join([
            f'info face="Moke White Heart {family}" size={height} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1',
            f'common lineHeight={height} base={height} scaleW={atlas.width} scaleH={height} pages=1 packed=0',
            f'page id=0 file="{name}.png"',f'chars count={len(chars)}',*rows])+'\n')
        ET.SubElement(root,'font',id=ident,filename=name+'.fnt');catalog.append((family*3+size,ident))
ET.indent(tree,space='    ');tree.write(OUT/'fonts.xml',encoding='utf-8')
mc='// Generated white-heart fonts; load only the chosen family/size.\nimport Toybox.Graphics;\nimport Toybox.WatchUi;\nmodule WhiteHeartFonts {function load(family,size){var id=Rez.Fonts.WhiteHeartF0S26;switch(family*3+size){\n'
for n,ident in catalog:mc+=f'case {n}:id=Rez.Fonts.{ident};break;\n'
mc+='}return WatchUi.loadResource(id) as Graphics.FontType;}}\n'
(ROOT/'source/WhiteHeartFonts.mc').write_text(mc)
print('Generated 9 white-heart styles; a single selected font stays resident.')
