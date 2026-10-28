"""Resource preview of the arrow change, retaining the white heart window."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('white',ROOT/'scripts/render-white-heart.py')
w=importlib.util.module_from_spec(sp);sp.loader.exec_module(w)
before=w.after;after=before.copy();d=ImageDraw.Draw(after);d.rectangle((81,7,95,21),fill='black')
f=w.three.m.Font('wind-arrow',ROOT/'resources/native');f.draw(after,81,7,'8',(255,255,255))
delta=ImageChops.difference(before,after).convert('L');mask=Image.new('L',(176,176));ImageDraw.Draw(mask).rectangle((81,7,95,21),fill=255)
assert ImageChops.multiply(delta,ImageChops.invert(mask)).getbbox() is None
out=ROOT/'bin/wind-arrow';out.mkdir(exist_ok=True);before.save(out/'before.png');after.save(out/'after.png')
board=Image.new('RGB',(800,510),'#202320');d=ImageDraw.Draw(board)
title=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',21,index=1);small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16,index=1)
d.text((32,16),'风向箭头 · 佳明官方方向指针轮廓',font=title,fill='white')
for image,x,label in [(before,32,'改前'),(after,416,'改后')]:
    d.text((x,57),label,font=small,fill='#c5cdc4');board.paste(image.resize((352,352),Image.Resampling.NEAREST),(x,87))
d.text((32,466),'实际单色资源2倍预览，非实表照片；箭头外区域像素一致。',font=small,fill='#c5cdc4')
board.save(out/'comparison.png');print(out/'comparison.png')
