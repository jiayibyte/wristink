"""Rasterize the Garmin forum's shared standard icon outlines for Instinct 3."""
from pathlib import Path
import xml.etree.ElementTree as ET
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.svgLib.path import parse_path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'assets/icons'
out = ROOT/'resources/native'
out.mkdir(exist_ok=True)
glyphs = {'.notdef': TTGlyphPen(None).glyph()}
cmap = {}
for el in ET.parse(source/'garmin-connect-icons.svg').getroot().iter():
    if not el.tag.endswith('glyph') or not el.get('unicode'):
        continue
    name = el.get('path-name')
    pen = TTGlyphPen(None)
    parse_path(el.get('d'), Cu2QuPen(pen, 1.0, reverse_direction=False))
    glyphs[name] = pen.glyph()
    cmap[ord(el.get('unicode'))] = name
fb = FontBuilder(512, isTTF=True)
fb.setupGlyphOrder(list(glyphs))
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics({name:(320,0) for name in glyphs})
fb.setupHorizontalHeader(ascent=448, descent=-64)
fb.setupNameTable({'familyName':'Garmin Forum Standard Icons','styleName':'Regular',
                  'uniqueFontIdentifier':'MokeForumIcons20261027',
                  'fullName':'Garmin Forum Standard Icons','psName':'MokeForumIcons'})
fb.setupOS2(sTypoAscender=448,sTypoDescender=-64,usWinAscent=448,usWinDescent=64)
fb.setupPost()
fb.save(source/'forum-standard-icons.ttf')

chosen = {'steps':'Ä','calories':'X','heart':'l','floors':'e','intensity':'o',
          'distance':'Q','notifications':'Â','goal':'g','stress':'È','humidity':'Í',
          'recovery':'R','move':'r','body':'A','sunrise':'b','sunset':'c'}
atlas = Image.new('RGBA',(len(chosen)*17,16),(255,255,255,0))
entries=[]

def topology(im):
    pts={(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))}
    spurs=sum(sum((x+dx,y+dy) in pts for dx in [-1,0,1] for dy in [-1,0,1] if dx or dy)<=1 for x,y in pts)
    unseen=set(pts);parts=0
    while unseen:
        stack=[unseen.pop()];parts+=1
        while stack:
            x,y=stack.pop()
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    p=(x+dx,y+dy)
                    if p in unseen:unseen.remove(p);stack.append(p)
    return len(pts),spurs,parts

for i,(name,char) in enumerate(chosen.items()):
    for size in range(30,7,-1):
        font=ImageFont.truetype(str(source/'forum-standard-icons.ttf'),size)
        b=font.getbbox(char)
        im=Image.new('L',(max(1,b[2]-b[0]),max(1,b[3]-b[1])))
        ImageDraw.Draw(im).text((-b[0],-b[1]),char,font=font,fill=255)
        box=im.getbbox()
        if not box:raise ValueError(name)
        im=im.crop(box)
        if im.width<=14 and im.height<=14:break
    # Preserve the approved ink box, re-rasterizing the source outline at 8x
    # before one area-coverage conversion. Avoid thresholding a tiny raster.
    hinted=im.point(lambda p:255 if p>=112 else 0);box=hinted.getbbox()
    target=(box[2]-box[0],box[3]-box[1]);offset=((16-im.width)//2+box[0],(16-im.height)//2+box[1])
    hi=ImageFont.truetype(str(source/'forum-standard-icons.ttf'),48*8);hb=hi.getbbox(char)
    vector=Image.new('L',(hb[2]-hb[0],hb[3]-hb[1]));ImageDraw.Draw(vector).text((-hb[0],-hb[1]),char,font=hi,fill=255)
    # Keep thin official outline details above the one-pixel visibility floor.
    cutoff=112 if char in 'XloRÍÈ' else 128
    vector=vector.crop(vector.getbbox()).resize(target,Image.Resampling.BOX).point(lambda p:255 if p>=cutoff else 0)
    previous=hinted.crop(box);old_stats=topology(previous);new_stats=topology(vector)
    # Keep the native hint if area resampling loses a head/toe or introduces
    # endpoints. One-pixel pictograms must stay readable, not merely thinner.
    if new_stats[1]>old_stats[1] or new_stats[2]!=old_stats[2] or new_stats[0]>old_stats[0]:
        vector=previous
    tile=Image.new('L',(16,16));tile.paste(vector,offset)
    rgba=Image.new('RGBA',(16,16),(255,255,255,0));rgba.putalpha(tile)
    atlas.paste(rgba,(i*17,0))
    entries.append(f'char id={ord(char)} x={i*17} y=0 width=16 height=16 xoffset=0 yoffset=0 xadvance=16 page=0 chnl=15')
atlas.save(out/'garmin-icons.png')
(out/'garmin-icons.fnt').write_text('\n'.join([
    'info face="Garmin Forum Standard Icons" size=16 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1',
    f'common lineHeight=16 base=16 scaleW={atlas.width} scaleH=16 pages=1 packed=0',
    'page id=0 file="garmin-icons.png"',f'chars count={len(entries)}',*entries])+'\n')
(out/'fonts.xml').write_text('<fonts><font id="GarminStandardIcons" filename="garmin-icons.fnt" /></fonts>\n')
print(f'Generated {len(chosen)} Garmin forum standard icons.')
