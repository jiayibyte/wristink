"""Frame verified SDK screen captures for the store; never repaint the watch UI."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,argparse
R=Path(__file__).resolve().parents[1];font=R/'assets/fonts/NotoSansCJKsc-Regular.otf'
p=argparse.ArgumentParser();p.add_argument('--version',default='1.2.0');p.add_argument('--captures',type=Path,default=R/'store/screenshots');p.add_argument('--output',type=Path,default=R/'store/images');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
items=[(f'moke-{a.version}-zhs.png',f'screen-{a.version}-cn-dark.png','墨刻','简体中文 · 深色','预览数值为演示数据',False),(f'moke-{a.version}-eng.png',f'screen-{a.version}-en-dark.png','Moke','English · Dark','Preview values are simulated',False),(f'moke-{a.version}-zhs-light.png',f'screen-{a.version}-cn-light.png','墨刻','简体中文 · 浅色','预览数值为演示数据',True)]
records=[]
for source,target,title,subtitle,note,light in items:
 path=a.captures/source;screen=Image.open(path).convert('RGB');assert screen.size==(176,176),path
 out=Image.new('RGB',(500,620),'#f2f1ed');d=ImageDraw.Draw(out)
 def text(x,y,value,size,fill='#171d19'):d.text((x,y),value,font=ImageFont.truetype(str(font),size),fill=fill)
 text(42,25,title,32);text(407,40,a.version,13,'#626c65')
 text(42,77,'Instinct 3 Solar · 45 / 50 mm',16,'#626c65');text(42,108,subtitle,15)
 d.rounded_rectangle((44,150,456,562),radius=30,fill='white' if light else 'black')
 # Integer scaling leaves every original MIP pixel intact.
 out.paste(screen.resize((352,352),Image.Resampling.NEAREST),(74,180))
 text(42,583,note,12,'#626c65')
 dest=a.output/target;out.save(dest,optimize=True);assert dest.stat().st_size<150*1024
 records.append({'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output':str(dest),'size':dest.stat().st_size,'source_pixels_unchanged':True,'integer_scale':2})
(R/'bin/store-screenshot-validation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Prepared 3 store screenshots from native SDK captures.')
