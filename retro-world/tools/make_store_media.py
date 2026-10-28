"""Frame actual SDK screen captures; never redraw or invent watch readings."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];STORE=ROOT/'store';OUT=STORE/'images';OUT.mkdir(exist_ok=True)
FONT=ROOT.parent/'moke/assets/fonts/NotoSansCJKsc-Regular.otf'
def font(size):return ImageFont.truetype(str(FONT),size)
def text(im,xy,value,size,fill='#182721'):
 ImageDraw.Draw(im).text(xy,value,font=font(size),fill=fill)
def screen(name):return Image.open(STORE/'screenshots'/name).convert('RGB')
def place(im,source,box,round_face=False):
 x,y,w,h=box;ratio=min(w/source.width,h/source.height)
 if source.width<=176 and source.height<=176:ratio=float(max(1,int(ratio)))
 size=(round(source.width*ratio),round(source.height*ratio))
 scaled=source.resize(size,Image.Resampling.NEAREST if ratio.is_integer() else Image.Resampling.LANCZOS)
 xx=x+(w-size[0])//2;yy=y+(h-size[1])//2
 if round_face:
  mask=Image.new('L',size,0);ImageDraw.Draw(mask).ellipse((0,0,size[0]-1,size[1]-1),fill=255);im.paste(scaled,(xx,yy),mask)
 else:im.paste(scaled,(xx,yy))
 return {'source_size':source.size,'display_size':size}
items=[('instinct3-active.png','mip','MIP 黑白复古','MIP / classic monochrome',False),('venu3-active.png','amoled','AMOLED 柔和配色','AMOLED / soft colour',True),('venusq2-active.png','rectangle','方屏原生布局','Native rectangular layout',False),('venu3-aod.png','aod','低亮常亮时间','Dim always-on time',True)]
records=[]
for source,key,zh,en,circle in items:
 src=screen(source)
 for locale in ('zh','en'):
  im=Image.new('RGB',(500,620),'#EEF0E8');d=ImageDraw.Draw(im)
  text(im,(30,22),'寰游时刻' if locale=='zh' else 'Retro World',30)
  text(im,(30,68),zh if locale=='zh' else en,18,'#4A665B')
  d.rounded_rectangle((30,116,470,556),radius=28,fill='#D9DFD5')
  meta=place(im,src,(48,134,404,404),circle)
  text(im,(30,576),'模拟器示例数据 · 功能依机型而异' if locale=='zh' else 'Simulator sample data · Features vary',12,'#56665F')
  dest=OUT/f'{key}-{locale}.png';im.save(dest,optimize=True)
  records.append(dict(source=source,source_sha256=hashlib.sha256((STORE/'screenshots'/source).read_bytes()).hexdigest(),file=dest.name,bytes=dest.stat().st_size,**meta))
  assert dest.stat().st_size<150*1024,dest
cover=Image.new('RGB',(500,500),'#EEF0E8');place(cover,screen('venu3-active.png'),(30,30,440,440),True);cover.save(OUT/'cover-500.png',optimize=True)
for locale in ('zh','en'):
 im=Image.new('RGB',(1440,720),'#EEF0E8');d=ImageDraw.Draw(im)
 text(im,(62,52),'寰游时刻' if locale=='zh' else 'Retro World',62)
 text(im,(65,143),'复古数字，腕上世界。' if locale=='zh' else 'Retro time. A living world.',27,'#4A665B')
 for i,line in enumerate((['16 种自动地图皮肤','天气 · 日出日落 · 每日数据','MIP 黑白 / AMOLED 彩色','免费 · 无广告'] if locale=='zh' else ['16 automatic map skins','Weather, sun times and daily data','Monochrome MIP / colour AMOLED','Free. No ads.'])):
  d.ellipse((67,231+i*54,75,239+i*54),fill='#488774');text(im,(93,214+i*54),line,22)
 place(im,screen('venu3-active.png'),(635,95,650,565),True)
 text(im,(65,625),'模拟器示例数据；可用功能依设备而异。' if locale=='zh' else 'Simulator sample data. Availability varies by device.',17,'#56665F')
 im.save(OUT/f'hero-{locale}-1440x720.png',optimize=True)
(STORE/'media-validation.json').write_text(json.dumps({'screenshots':records,'artwork':'Actual SDK captures framed with text; no Garmin casing or logo','cover':[500,500],'hero':[1440,720]},indent=2,ensure_ascii=False)+'\n')
print('Prepared cover, two hero images and eight localized screenshots.')
