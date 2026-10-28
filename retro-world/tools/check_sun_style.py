"""Verify the native paired-sun row and keep unrelated pixels unchanged."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import io,json,zipfile
import assets
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist'
with zipfile.ZipFile(DIST/'RetroWorld-Instinct3-1.2.13.zip') as z:
    before=Image.open(io.BytesIO(z.read('RetroWorld-pixels.png'))).convert('1')
after=Image.open(DIST/'RetroWorld-pixels.png').convert('1')
for y in range(176):
    for x in range(176):
        if not (44<=x<=141 and 162<=y<=171):
            assert before.getpixel((x,y))==after.getpixel((x,y)),(x,y)
# Actual visible time ink centers surround the center sun with equal spacing.
bounds=[]
for left,right in ((49,80),(99,130)):
    pts=[(x,y) for y in range(163,172) for x in range(left,right) if after.getpixel((x,y))]
    bounds.append([min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)])
assert bounds==[[55,164,71,168],[105,164,121,168]],bounds
assert (bounds[0][0]+bounds[1][2])/2==88
mask=assets.sun_mask();assert mask.size==(13,8) and mask.mode=='1'
assert after.crop((82,163,95,171)).tobytes()==mask.tobytes()
assert before.crop((18,31,102,49)).tobytes()==after.crop((18,31,102,49)).tobytes()
report={'version':'1.2.14','source':json.loads((ROOT/'assets/garmin-sun/source.json').read_text()),'layout':'sunrise time / shared official half sun / sunset time','sun_cell':[82,163,13,8],'time_ink_bounds':bounds,'group_center_x':88,'unrelated_preview_pixels_unchanged':True,'step_kcal_left_alignment_preserved':True,'runtime_cost':'static dial bitmap only; same two cached sun-time text draws','limits':'Official source shape adapted to 13x8; not firmware pixel extraction; no physical-device test.'}
(DIST/'sun-style-validation.json').write_text(json.dumps(report,indent=2)+'\n')
panel=Image.new('RGB',(800,275),'#eeeeee');d=ImageDraw.Draw(panel)
f=ImageFont.truetype(str(ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'),22)
d.text((16,8),'GARMIN OFFICIAL REFERENCE',font=f,fill='black')
src=Image.open(ROOT/'assets/garmin-sun/official-sunrise-sunset.png').convert('RGBA');panel.paste(src,(32,40),src)
for y,label,face in ((118,'BEFORE',before),(196,'UPDATED',after)):
    d.text((16,y),label,font=f,fill='black')
    crop=face.crop((42,161,144,173)).convert('RGB').resize((612,72),Image.Resampling.NEAREST)
    panel.paste(crop,(182,y-6))
panel.save(DIST/'RetroWorld-sun-comparison.png')
print('Sun row checked: centered x=88, unchanged fonts and all unrelated pixels, STEP/KCAL preserved.')
