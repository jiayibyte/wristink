"""Whole-face resource preview for weather, battery and date refinements."""
from pathlib import Path
import importlib.util,json,re
from PIL import Image,ImageDraw,ImageFont,ImageChops

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'releases/instinct3-before-three-details-2026-10-27'
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base_icon=m.icon
names={'data':'dataf0s14','compact-small':'dataf0s12','time':'timef0s64','circle-value':'liveheartf0s22','seconds':'secondf0s26'}
mapping={2:'Ä',3:'Q',4:'e',5:'X',6:'l',8:'c',9:'b',10:'Í',11:'Â',12:'g',15:'l',19:'A',20:'o',21:'o',22:'o',23:'o',24:'r',25:'R',26:'È'}


def render(after,dark=True):
    root=ROOT if after else BEFORE;m.ROOT=root
    for key,name in names.items():m.FONTS[key]=m.Font(name,root/'resources/fonts')
    m.WEATHER_GLYPHS=[json.loads(v) for _,v in sorted(re.findall(r'case (\d+):return (\[.*?\]);',(root/'source/WeatherGlyphs.mc').read_text()),key=lambda p:int(p[0]))]
    standard=m.Font('garmin-icons',root/'resources/native');upper=m.Font('upper-details',root/'resources/native');moon=m.Font('upper-moon',root/'resources/native')
    def icon(d,kind,x,y,fg,bg):
        if after and kind in (1,17):upper.draw(d._image,x,y,'6',(fg,)*3)
        elif kind==6 and x==137 and y==m.LAYOUT['HEART_ICON_Y']:upper.draw(d._image,138,y,'l',(fg,)*3)
        elif kind in mapping:standard.draw(d._image,x,y,mapping[kind],(fg,)*3)
        else:base_icon(d,kind,x,y,fg,bg)
    m.icon=icon;im=m.render(dark)
    fg,bg=((255,)*3,(0,)*3) if dark else ((0,)*3,(255,)*3)
    mx,my=m.LAYOUT['MOON_X'],m.LAYOUT['MOON_Y'];d=ImageDraw.Draw(im)
    d.rectangle((mx-7,my-7,mx+7,my+7),fill=bg);moon.draw(im,mx-7,my-7,'8',fg)
    x,y=m.LAYOUT['MOVE_X'],m.LAYOUT['MOVE_Y'];d.rectangle((x,y,x+8,y+12),fill=bg);upper.draw(im,x,y,'Q',fg)
    return im


if __name__=='__main__':
    out=ROOT/'bin/three-details';out.mkdir(exist_ok=True)
    before,after=render(False),render(True)
    assert ImageChops.difference(before.crop((0,64,176,176)),after.crop((0,64,176,176))).getbbox() is None
    before.save(out/'before-dark.png');after.save(out/'after-dark.png');render(True,False).save(out/'after-light.png')
    board=Image.new('RGB',(800,530),'#202320');d=ImageDraw.Draw(board)
    title=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',21,index=1)
    text=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16,index=1)
    d.text((32,16),'天气 · 续航 · 日期：统一细节与字形比例',font=title,fill='#f1f3ee')
    for image,x,label in [(before,32,'改前'),(after,416,'改后')]:
        d.text((x,57),label,font=text,fill='#c5cdc4');board.paste(image.resize((352,352),Image.Resampling.NEAREST),(x,87))
    d.text((32,460),'原生 176×176 单色资源放大 2 倍；非实表照片。',font=text,fill='#c5cdc4')
    d.text((32,490),'保留原功能、布局和大时间；下半区域像素一致。',font=text,fill='#c5cdc4')
    board.save(out/'comparison.png');print(out/'comparison.png')
