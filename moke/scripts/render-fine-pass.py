"""Honest native-size and enlarged views of the same monochrome watch assets."""
from pathlib import Path
import importlib.util,json,re
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1];BEFORE=ROOT/'releases/instinct3-before-fine-pass-2026-10-27'
sp=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
base_icon=m.icon
names={'data':'dataf0s14','compact-small':'dataf0s12','time':'timef0s64','circle-value':'liveheartf0s22','seconds':'secondf0s26'}
mapping={2:'Ä',3:'Q',4:'e',5:'X',6:'l',8:'c',9:'b',10:'Í',11:'Â',12:'g',15:'l',19:'A',20:'o',21:'o',22:'o',23:'o',24:'r',25:'R',26:'È'}

def render(after,dark=True):
    root=ROOT if after else BEFORE;m.ROOT=root
    for k,n in names.items():m.FONTS[k]=m.Font(n,root/'resources/fonts')
    m.WEATHER_GLYPHS=[json.loads(v) for _,v in sorted(re.findall(r'case (\d+):return (\[.*?\]);',(root/'source/WeatherGlyphs.mc').read_text()),key=lambda p:int(p[0]))]
    standard=m.Font('garmin-icons',root/'resources/native');upper=m.Font('upper-details',root/'resources/native');moon=m.Font('upper-moon',root/'resources/native')
    heart=m.Font('white-heart-f0-s26',root/'resources/native');arrow=m.Font('shaft-wind',root/'resources/native')
    def icon(d,kind,x,y,fg,bg):
        if kind in (1,17):upper.draw(d._image,x,y,'6',(fg,)*3)
        elif kind in mapping:standard.draw(d._image,x,y,mapping[kind],(fg,)*3)
        else:base_icon(d,kind,x,y,fg,bg)
    m.icon=icon;im=m.render(dark);d=ImageDraw.Draw(im)
    fg,bg=((255,)*3,(0,)*3) if dark else ((0,)*3,(255,)*3)
    mx,my=m.LAYOUT['MOON_X'],m.LAYOUT['MOON_Y'];d.rectangle((mx-7,my-7,mx+7,my+7),fill=bg);moon.draw(im,mx-7,my-7,'8',fg)
    x,y=m.LAYOUT['MOVE_X'],m.LAYOUT['MOVE_Y'];d.rectangle((x,y,x+8,y+12),fill=bg);upper.draw(im,x,y,'Q',fg)
    d.rectangle((81,7,95,21),fill=bg);arrow.draw(im,81,7,'8',fg)
    d.ellipse((113,0,175,62),fill='white');upper.draw(im,138,11,'m',(0,0,0));heart.draw(im,144,25,'96',(0,0,0),center=True)
    return im

if __name__=='__main__':
    out=ROOT/'bin/fine-pass';out.mkdir(exist_ok=True);before=render(False);after=render(True)
    before.save(out/'before-native.png');after.save(out/'after-native.png');render(True,False).save(out/'after-light-native.png')
    title=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',21,index=1);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16,index=1)
    board=Image.new('RGB',(800,520),'#202320');d=ImageDraw.Draw(board)
    d.text((32,16),'保留粗体主时间 · 细化图标与边缘',font=title,fill='white')
    for im,x,label in [(before,32,'改前'),(after,416,'改后')]:
        d.text((x,57),label,font=small,fill='#c5cdc4');board.paste(im.resize((352,352),Image.Resampling.NEAREST),(x,87))
    d.text((32,463),'原生176×176单色资源放大2倍；像素边缘真实保留，非实表照片。',font=small,fill='#c5cdc4')
    d.text((32,491),'粗体时间、大箭头与原布局保持；细化心率数字和图标边缘。',font=small,fill='#c5cdc4')
    board.save(out/'comparison.png');print(out/'comparison.png')
