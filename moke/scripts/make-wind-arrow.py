"""Adapt Garmin's official direction pointer to the existing wind-arrow area."""
from pathlib import Path
import json,math
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'resources/native'
ref=json.loads((ROOT/'assets/icons/garmin-wind-reference.json').read_text())
points=ref['outer_polygon'];cx=(min(p[0] for p in points)+max(p[0] for p in points))/2
cy=(min(p[1] for p in points)+max(p[1] for p in points))/2
scale=7/max(math.hypot(x-cx,y-cy) for x,y in points)
atlas=Image.new('RGBA',(32*16,15),(255,255,255,0));entries=[];codes='0123456789ABCDEFGHIJKLMNOPQRSTUV'
for i,char in enumerate(codes):
    a=i*2*math.pi/32;co,si=math.cos(a),math.sin(a);ss=8
    poly=[]
    for x,y in points:
        dx,dy=(x-cx)*scale,(y-cy)*scale
        poly.append((round((7.5+dx*co-dy*si)*ss),round((7.5+dx*si+dy*co)*ss)))
    im=Image.new('L',(15*ss,15*ss));ImageDraw.Draw(im).polygon(poly,fill=255)
    im=im.resize((15,15),Image.Resampling.LANCZOS).point(lambda p:255 if p>=112 else 0)
    dx,dy=(points[0][0]-cx)*scale,(points[0][1]-cy)*scale
    im.putpixel((round(7+dx*co-dy*si),round(7+dx*si+dy*co)),255)
    tile=Image.new('RGBA',(15,15),(255,255,255,0));tile.putalpha(im);atlas.paste(tile,(i*16,0))
    entries.append(f'char id={ord(char)} x={i*16} y=0 width=15 height=15 xoffset=0 yoffset=0 xadvance=15 page=0 chnl=15')
atlas.save(OUT/'wind-arrow.png')
(OUT/'wind-arrow.fnt').write_text('\n'.join([
    'info face="Garmin Direction Pointer Adaptation" size=15 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1',
    f'common lineHeight=15 base=15 scaleW={atlas.width} scaleH=15 pages=1 packed=0',
    'page id=0 file="wind-arrow.png"','chars count=32',*entries])+'\n')
tree=ET.parse(OUT/'fonts.xml');root=tree.getroot()
for el in list(root):
    if el.get('id')=='WindArrow':root.remove(el)
ET.SubElement(root,'font',id='WindArrow',filename='wind-arrow.fnt');ET.indent(tree,space='    ');tree.write(OUT/'fonts.xml',encoding='utf-8')
print('Generated official direction-pointer silhouette in 32 native orientations.')
