"""Build monochrome glyphs from Garmin's published inReach Mini 2 images.
No firmware extraction and no runtime downloads. See assets/garmin-weather/SOURCE.md.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/garmin-weather'
NAMES=['Clear day','Clear night','Cloudy','Fog','Hail','Partly cloudy day','Partly cloudy night','Rain','Snow','Thunderstorm','Unknown','Wind','Wintry mix']
COARSE=[10,0,2,7,8,9,3,11]
@lru_cache()
def icon(kind,size=9):
    meta=json.loads((SOURCE/'sources.json').read_text())['icons'][kind]
    p=SOURCE/meta['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256'],p
    ink=ImageOps.invert(Image.open(p).convert('L')).point(lambda v:255 if v>=128 else 0)
    ink=ink.crop(ink.getbbox());scale=min(size/ink.width,size/ink.height)
    dimensions=(round(ink.width*scale),round(ink.height*scale))
    mask=ink.resize(dimensions,Image.Resampling.BOX).point(lambda v:255 if v>=96 else 0).convert('1')
    tile=Image.new('1',(size,size),1)
    tile.paste(0,((size-mask.width)//2,(size-mask.height)//2),mask)
    return tile

def generate(out,dist):
    for size,name in ((9,'weather-small'),(11,'weather')):
        atlas=Image.new('1',(13*size,size),1)
        glyphs=[icon(k,size) for k in range(13)]
        assert len({im.tobytes() for im in glyphs})==13,'weather states collapsed'
        for k,im in enumerate(glyphs):atlas.paste(im,(k*size,0))
        atlas.save(out/(name+'.png'))
    sheet=Image.new('RGB',(880,480),'#eeeeee');d=ImageDraw.Draw(sheet)
    d.text((16,10),'GARMIN OFFICIAL SOURCE  /  9px WATCH ADAPTATION (8x view)',fill='black')
    for k,name in enumerate(NAMES):
        x=16+k%4*220;y=40+k//4*110
        d.text((x,y),name,fill='black')
        src=Image.open(SOURCE/f'official-{k:02d}.jpg').convert('RGB');sheet.paste(src,(x,y+25))
        sheet.paste(icon(k).convert('RGB').resize((72,72),Image.Resampling.NEAREST),(x+90,y+23))
    sheet.save(dist/'RetroWorld-official-weather-icons.png')
    (dist/'weather-icons-validation.json').write_text(json.dumps({'count':13,'unique_9px_icons':13,'cell':[9,9],'source':json.loads((SOURCE/'sources.json').read_text()),'raster':'aspect-fit, BOX coverage threshold 96/255, 1-bit; no runtime scaling'},indent=2)+'\n')
