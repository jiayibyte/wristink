"""Frame verified SDK screen captures for the store; never repaint the watch UI."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
R=Path(__file__).resolve().parents[1];font=R/'assets/fonts/NotoSansCJKsc-Regular.otf'
items=[('instinct3-1.1.0-cn.png','screen-1.1.0-cn-dark.png','墨刻','简体中文 · 深色','预览数值为演示数据',False),('instinct3-1.1.0-en.png','screen-1.1.0-en-dark.png','Moke','English · Dark','Preview values are simulated',False),('instinct3-1.1.0-white.png','screen-1.1.0-cn-light.png','墨刻','简体中文 · 浅色','预览数值为演示数据',True)]
records=[]
for source,target,title,subtitle,note,light in items:
 path=R/'store/screenshots'/source;screen=Image.open(path).convert('RGB');assert screen.size==(176,176),path
 out=Image.new('RGB',(500,620),'#f2f1ed');d=ImageDraw.Draw(out)
 def text(x,y,value,size,fill='#171d19'):d.text((x,y),value,font=ImageFont.truetype(str(font),size),fill=fill)
 text(42,25,title,32);text(407,40,'1.1.0',13,'#626c65')
 text(42,77,'Instinct 3 Solar · 45 / 50 mm',16,'#626c65');text(42,108,subtitle,15)
 d.rounded_rectangle((44,150,456,562),radius=30,fill='white' if light else 'black')
 # Integer scaling leaves every original MIP pixel intact.
 out.paste(screen.resize((352,352),Image.Resampling.NEAREST),(74,180))
 text(42,583,note,12,'#626c65')
 dest=R/'store/images'/target;out.save(dest,optimize=True);assert dest.stat().st_size<150*1024
 records.append({'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output':str(dest),'size':dest.stat().st_size,'source_pixels_unchanged':True,'integer_scale':2})
(R/'bin/store-screenshot-validation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('Prepared 3 store screenshots from native SDK captures.')
