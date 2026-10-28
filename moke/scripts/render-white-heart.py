"""Whole-face comparison of the requested plain white heart window."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw,ImageFont,ImageChops

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('three',ROOT/'scripts/render-three-details.py')
three=importlib.util.module_from_spec(spec);spec.loader.exec_module(three)
before=three.render(True);after=before.copy();d=ImageDraw.Draw(after)
d.ellipse((113,0,175,62),fill='white')
icons=three.m.Font('upper-details',ROOT/'resources/native')
font=three.m.Font('white-heart-f0-s26',ROOT/'resources/native')
icons.draw(after,138,11,'m',(0,0,0));font.draw(after,144,25,'96',(0,0,0),center=True)
assert ImageChops.difference(before.crop((0,64,176,176)),after.crop((0,64,176,176))).getbbox() is None
mask=Image.new('L',(176,176));ImageDraw.Draw(mask).ellipse((113,0,175,62),fill=255)
delta=ImageChops.difference(before,after).convert('L');assert ImageChops.multiply(delta,ImageChops.invert(mask)).getbbox() is None
out=ROOT/'bin/white-heart';out.mkdir(exist_ok=True);before.save(out/'before.png');after.save(out/'after.png')
board=Image.new('RGB',(800,510),'#202320');d=ImageDraw.Draw(board)
title=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',21,index=1)
small=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',16,index=1)
d.text((32,16),'右上心率窗 · 白底黑字 · 移除两圈进度',font=title,fill='white')
for image,x,label in [(before,32,'改前'),(after,416,'改后')]:
    d.text((x,57),label,font=small,fill='#c5cdc4');board.paste(image.resize((352,352),Image.Resampling.NEAREST),(x,87))
d.text((32,466),'实际单色资源2倍预览，非实表照片；其他区域像素一致。',font=small,fill='#c5cdc4')
board.save(out/'comparison.png');print(out/'comparison.png')
