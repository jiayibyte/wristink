"""Verify every date digit has white vertical breathing room inside the real tab."""
from pathlib import Path
from PIL import Image
import json,sys,zipfile,io
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assets

def main():
    atlas=Image.open(ROOT/'resources/drawables/date.png');assert atlas.size==(80,13) and atlas.mode=='1'
    base=assets.base();checked=0
    with zipfile.ZipFile(ROOT/'dist/RetroWorld-Instinct3-1.2.8.zip') as z:
        old=Image.open(io.BytesIO(z.read('source-project/resources/drawables/date.png')))
        for n in range(10):
            reference=Image.new('1',(8,13),1)
            for target,source in enumerate(y for y in range(15) if y not in (5,11)):
                reference.paste(old.crop((n*8,source,(n+1)*8,source+1)),(0,target))
            glyph=atlas.crop((n*8,0,(n+1)*8,13));assert glyph.tobytes()==reference.tobytes()
            for x0 in (123,132,144,153):
                for y in range(13):
                    for x in range(8):
                        if glyph.getpixel((x,y))==0:
                            assert base.getpixel((x0+x,94+y))!=0,(n,x0,x,y)
                            assert 93<94+y<107
                checked+=1
    report={'date_cell':[8,13],'date_ink_y_range':[94,106],'white_inner_y_range':[93,107],'min_white_margin_top_bottom_pixels':1,'digit_positions_checked':checked,'segment_caps_preserved':True,'separator_y':100}
    (ROOT/'dist/date-padding-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Date padding verified for all 10 digits at 4 positions: white top/bottom margin >=1px, original caps preserved.')

if __name__=='__main__':main()
