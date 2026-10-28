"""Resource-based before/after preview; not a simulator or real-watch capture."""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BEFORE=ROOT/'releases/instinct3-before-upper-style-2026-10-27'
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/render-design-preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for key,name in {'data':'dataf0s14','compact-small':'dataf0s12','time':'timef0s64','circle-value':'liveheartf0s22','seconds':'secondf0s26'}.items():m.FONTS[key]=m.Font(name)
standard=m.Font('garmin-icons',ROOT/'resources/native')
upper=m.Font('upper-details',ROOT/'resources/native')
moon=m.Font('upper-moon',ROOT/'resources/native')
old_icon=m.icon
mapping={2:'Ä',3:'Q',4:'e',5:'X',6:'l',8:'c',9:'b',10:'Í',11:'Â',12:'g',15:'l',19:'A',20:'o',21:'o',22:'o',23:'o',24:'r',25:'R',26:'È'}


def render(after,dark=True):
    m.ROOT=ROOT if after else BEFORE
    def icon(d,kind,x,y,fg,bg):
        if after and kind==6 and x==137 and y==m.LAYOUT['HEART_ICON_Y']:
            upper.draw(d._image,138,y,'l',(fg,)*3)
        elif kind in mapping:standard.draw(d._image,x,y,mapping[kind],(fg,)*3)
        else:old_icon(d,kind,x,y,fg,bg)
    m.icon=icon
    im=m.render(dark)
    if after:
        fg,bg=((255,)*3,(0,)*3) if dark else ((0,)*3,(255,)*3)
        mx,my=m.LAYOUT['MOON_X'],m.LAYOUT['MOON_Y']
        ImageDraw.Draw(im).rectangle((mx-7,my-7,mx+7,my+7),fill=bg)
        moon.draw(im,mx-7,my-7,'8',fg) # Same half-phase as the original preview.
        x,y=m.LAYOUT['MOVE_X'],m.LAYOUT['MOVE_Y']
        ImageDraw.Draw(im).rectangle((x,y,x+8,y+12),fill=bg)
        upper.draw(im,x,y,'Q',fg)
    return im


if __name__=='__main__':
    out=ROOT/'bin/upper-style';out.mkdir(exist_ok=True)
    before,after=render(False),render(True)
    assert ImageChops.difference(before.crop((0,64,176,176)),after.crop((0,64,176,176))).getbbox() is None
    before.save(out/'before-dark.png');after.save(out/'after-dark.png');render(True,False).save(out/'after-light.png')
    board=Image.new('RGB',(800,500),'#202320');d=ImageDraw.Draw(board)
    title=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22,index=1)
    text=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16,index=1)
    d.text((32,18),'上方细节优化 · 原功能与布局',font=title,fill='#f1f3ee')
    for image,x,label in [(before,32,'改前'),(after,416,'改后')]:
        d.text((x,58),label,font=text,fill='#c5cdc4')
        board.paste(image.resize((352,352),Image.Resampling.NEAREST),(x,88))
    d.text((32,462),'实际单色资源放大 2 倍；非实表截图。下半区域像素完全一致。',font=text,fill='#c5cdc4')
    board.save(out/'comparison.png')
    print(out/'comparison.png')
