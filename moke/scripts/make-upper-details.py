"""Native 1-bit upper-panel details; retain the existing 176px layout boxes."""
from pathlib import Path
import math
import json
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resources/native'
OUT.mkdir(exist_ok=True)
MOON_REFERENCE=json.loads((ROOT/'assets/icons/garmin-moon-reference.json').read_text())


def moon(phase):
    """Garmin manual's circular outline and filled phase, at native 15px size."""
    ss=8;im=Image.new('L',(15*ss,15*ss));pixels=im.load()
    radius=MOON_REFERENCE['circle_radius'];stroke=MOON_REFERENCE['outline_width']
    scale=15/(2*radius+stroke)
    inner=(radius-stroke/2)*scale;face=radius*scale
    edge=math.cos(phase*2*math.pi)
    for y in range(im.height):
        dy=(y+.5)/ss-7.5
        for x in range(im.width):
            dx=(x+.5)/ss-7.5;r=math.hypot(dx,dy)
            if r>7.5:continue
            lit=r>=inner
            if not lit:
                span=math.sqrt(max(0,face**2-dy**2))
                # The existing epoch is a NEW moon. Its old rendering inverted
                # illumination; match the official new/quarter/full symbols.
                lit=dx>=edge*span if phase<.5 else dx<=-edge*span
            if lit:pixels[x,y]=255
    return im.resize((15,15),Image.Resampling.BOX).point(lambda p:255 if p>=128 else 0)


def glyph(char,width,height):
    # Render the original Garmin forum vector outline with a single final
    # conversion to native pixels; do not enlarge an existing small bitmap.
    ss=8;font=ImageFont.truetype(str(ROOT/'assets/icons/forum-standard-icons.ttf'),48*ss)
    b=font.getbbox(char);im=Image.new('L',(b[2]-b[0],b[3]-b[1]))
    ImageDraw.Draw(im).text((-b[0],-b[1]),char,font=font,fill=255)
    im=im.crop(im.getbbox());scale=min(width/im.width,height/im.height)
    return im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.BOX).point(lambda p:255 if p>=120 else 0)


def save_font(name,tiles,line):
    width=sum(im.width+1 for _,im in tiles)
    atlas=Image.new('RGBA',(width,line),(255,255,255,0));rows=[];x=0
    for char,im in tiles:
        tile=Image.new('RGBA',im.size,(255,255,255,0));tile.putalpha(im);atlas.paste(tile,(x,0))
        rows.append(f'char id={ord(char)} x={x} y=0 width={im.width} height={im.height} xoffset=0 yoffset=0 xadvance={im.width} page=0 chnl=15')
        x+=im.width+1
    atlas.save(OUT/(name+'.png'))
    (OUT/(name+'.fnt')).write_text('\n'.join([
        f'info face="Moke Upper {name}" size={line} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1',
        f'common lineHeight={line} base={line} scaleW={width} scaleH={line} pages=1 packed=0',
        f'page id=0 file="{name}.png"',f'chars count={len(rows)}',*rows])+'\n')


codes='0123456789ABCDEFGHIJKLMNOPQRSTUV'
save_font('upper-moon',[(c,moon(i/32)) for i,c in enumerate(codes)],15)
details=[]
for char,w,h,cell in [('Q',8,13,(9,13)),('l',11,10,(12,12)),('m',11,10,(12,12))]:
    ink=glyph(char,w,h);im=Image.new('L',cell)
    im.paste(ink,((cell[0]-ink.width)//2,(cell[1]-ink.height)//2));details.append((char,im))
for level in range(9):
    ss=8;im=Image.new('L',(14*ss,12*ss));d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,2*ss,12*ss-1,10*ss-1),radius=2*ss,outline=255,width=ss)
    d.rounded_rectangle((12*ss,4*ss,14*ss-1,8*ss-1),radius=ss,fill=255)
    if level:
        box=(2*ss,4*ss,(2+level)*ss-1,8*ss-1)
        if level<3:d.rectangle(box,fill=255)
        else:d.rounded_rectangle(box,radius=ss,fill=255)
    im=im.resize((14,12),Image.Resampling.BOX).point(lambda p:255 if p>=128 else 0)
    details.append((str(level),im))
save_font('upper-details',details,13)
tree=ET.parse(OUT/'fonts.xml');root=tree.getroot()
for item in list(root):
    if item.get('id') in ['UpperMoon','UpperDetails']:root.remove(item)
ET.SubElement(root,'font',id='UpperMoon',filename='upper-moon.fnt')
ET.SubElement(root,'font',id='UpperDetails',filename='upper-details.fnt')
ET.indent(tree,space='    ');tree.write(OUT/'fonts.xml',encoding='utf-8')
print('Generated 32 native moon phases and Garmin standard walking/heart details.')
