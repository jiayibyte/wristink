"""Show actual compiled-background source PNGs, without pretending to be a simulator."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/'dist/evidence';dest.mkdir(parents=True,exist_ok=True)
board=Image.new('RGB',(930,1050),'#10171c');d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'),24)
small=ImageFont.truetype(str(ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'),18)
d.text((22,15),'ALPINE / FESTIVAL LANDSCAPES',font=font,fill='white')
d.text((22,45),'Actual background assets. Dynamic sky, clock and data are drawn separately.',font=small,fill='#9aabb6')
for i,name in enumerate(['SPRING FESTIVAL','CHRISTMAS','HALLOWEEN','MID-AUTUMN']):
    x=22+(i%2)*455;y=87+(i//2)*475
    d.text((x,y),name,font=font,fill='#f1ca79')
    # Night for Mid-Autumn, day for others; fair weather.
    key=i*20+(15 if i==3 else 5)+1
    color=Image.open(ROOT/f'generated/epix2/resources/drawables/festival-{key}.png').convert('RGB')
    mono=Image.open(ROOT/f'generated/instinct3solar45mm/resources/drawables/festival-{i*5+1}.png').convert('RGB')
    board.paste(color.crop((0,0,416,224)),(x,y+32))
    d.text((x,y+259),'INSTINCT / 1-BIT / 2X',font=small,fill='#9aabb6')
    board.paste(mono.crop((0,0,176,94)).resize((352,188),Image.Resampling.NEAREST),(x+32,y+282))
board.save(dest/'festival-landscapes-design.png')
print(dest/'festival-landscapes-design.png')
