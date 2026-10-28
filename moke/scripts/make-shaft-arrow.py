"""Polish the original shafted arrow: larger chevron, clean joins, same anchor."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'resources/native'
stroke=2.0;h=stroke/2;length=math.hypot(4,5)
nx,ny=5/length,4/length
tip=5+length*h/5;inside=5-length*h/5;join=inside-4*h/5
# A proper shaft plus open chevron, not a navigation triangle.
outline=[(-5,-h),(join,-h),(1-nx*h,-5+ny*h),(1+nx*h,-5-ny*h),(tip,0),
         (1+nx*h,5+ny*h),(1-nx*h,5-ny*h),(join,h),(-5,h)]
atlas=Image.new('RGBA',(32*16,15),(255,255,255,0));rows=[];codes='0123456789ABCDEFGHIJKLMNOPQRSTUV'
for i,char in enumerate(codes):
    a=(i*360/32-90)*math.pi/180;co,si=math.cos(a),math.sin(a);ss=8
    # Optical grid fitting gives cardinal shafts a consistent two-pixel weight.
    cx=7.5+.5*abs(si);cy=7.5+.5*abs(co)
    poly=[(round((cx+x*co-y*si)*ss),round((cy+x*si+y*co)*ss)) for x,y in outline]
    im=Image.new('L',(15*ss,15*ss));d=ImageDraw.Draw(im);d.polygon(poly,fill=255)
    for x,y in [(-5,0),(1,-5),(1,5)]:
        tx,ty=cx+x*co-y*si,cy+x*si+y*co
        d.ellipse(((tx-h)*ss,(ty-h)*ss,(tx+h)*ss,(ty+h)*ss),fill=255)
    im=im.resize((15,15),Image.Resampling.LANCZOS).point(lambda p:255 if p>=112 else 0)
    px,py=round(cx-.5+tip*co),round(cy-.5+tip*si)
    im.putpixel((max(0,min(14,px)),max(0,min(14,py))),255)
    tile=Image.new('RGBA',(15,15),(255,255,255,0));tile.putalpha(im);atlas.paste(tile,(i*16,0))
    rows.append(f'char id={ord(char)} x={i*16} y=0 width=15 height=15 xoffset=0 yoffset=0 xadvance=15 page=0 chnl=15')
atlas.save(OUT/'shaft-wind.png')
(OUT/'shaft-wind.fnt').write_text('\n'.join([
    'info face="Moke Shafted Direction Arrow" size=15 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1',
    'common lineHeight=15 base=15 scaleW=512 scaleH=15 pages=1 packed=0',
    'page id=0 file="shaft-wind.png"','chars count=32',*rows])+'\n')
tree=ET.parse(OUT/'fonts.xml');root=tree.getroot()
for el in list(root):
    if el.get('id')=='ShaftWindArrow':root.remove(el)
ET.SubElement(root,'font',id='ShaftWindArrow',filename='shaft-wind.fnt');ET.indent(tree,space='    ');tree.write(OUT/'fonts.xml',encoding='utf-8')
print('Generated 32 shafted-arrow orientations with a larger chevron head.')
