"""Store layouts from actual Garmin framebuffer captures, never concept faces.
Preserve raw PNGs; composed JPEG panels respect Garmin's 150 KB image limit.
"""
from pathlib import Path
import hashlib,json,math,unicodedata
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];OUT=R/'store/images';OUT.mkdir(parents=True,exist_ok=True)
LOCALES=json.loads((R/'store/localizations.json').read_text());records=[]
LATIN=Path('/System/Library/Fonts/Supplemental/Arial.ttf');BOLD=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
CJK=R.parent/'moke/assets/fonts/NotoSansCJKsc-Regular.otf'

def font(size,locale='en',bold=False):
 path=CJK if locale in ['zh_CN','zh_TW','ja','ko'] else (Path('/System/Library/Fonts/Supplemental/Thonburi.ttc') if locale=='th' else (Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf') if locale=='iw' else BOLD if bold else LATIN))
 return ImageFont.truetype(str(path),size,layout_engine=ImageFont.Layout.RAQM)
def canvas(w,h):
 im=Image.new('RGB',(w,h));d=ImageDraw.Draw(im)
 for y in range(h):
  t=y/max(1,h-1);d.line((0,y,w,y),fill=(round(9+7*t),round(22+15*t),round(38+17*t)))
 return im

def text(im,xy,value,size=28,color='#f4f8f5',locale='en',bold=False,anchor='la'):
 ImageDraw.Draw(im).text(xy,value,font=font(size,locale,bold),fill=color,anchor=anchor,direction='rtl' if locale=='iw' else 'ltr')
def lines(value,f,maxwidth):
 words=value.split(' ');result=[];line=''
 for word in words:
  test=(line+' '+word).strip()
  if f.getlength(test)<=maxwidth:line=test;continue
  if line:result.append(line);line=''
  if f.getlength(word)<=maxwidth:line=word;continue
  part=''
  for ch in word:
   if f.getlength(part+ch)>maxwidth and part and not unicodedata.combining(ch):result.append(part);part=''
   part+=ch
  line=part
 if line:result.append(line)
 return result

def face(im,path,x,y,size=None,roundscreen=True):
 src=Image.open(path).convert('RGB');original=src.size
 if size:
  src=src.resize((size,round(src.height*size/src.width)),Image.Resampling.NEAREST if original[0]<=260 else Image.Resampling.LANCZOS)
 if roundscreen:
  mask=Image.new('L',src.size);ImageDraw.Draw(mask).ellipse((0,0,src.width-1,src.height-1),fill=255);im.paste(src,(x,y),mask)
 else:im.paste(src,(x,y))
 return {'file':str(Path(path).relative_to(R)),'nativeSize':list(original),'displaySize':list(src.size),'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}

def save(im,name,limit):
 path=OUT/name
 if path.suffix=='.jpg':
  for quality in [92,88,84,80,76,72,68,64,60]:
   im.save(path,quality=quality,optimize=True,progressive=True)
   if path.stat().st_size<limit:break
 else:im.save(path,optimize=True)
 assert path.stat().st_size<limit,(name,path.stat().st_size)
 return path
def main():
 DAY=R/'docs/verified-release/epix2-day-birds-plane.png';NIGHT=R/'docs/verified-release/epix2-aurora-birds-plane.png'
 # A single 500px cover, with a true 416px colour framebuffer.
 cover=canvas(500,500);sources=[face(cover,DAY,42,8)]
 text(cover,(250,438),'ALPINE',36,anchor='ma',bold=True);text(cover,(250,480),'MOUNTAIN SKINS',12,color='#9edbcc',anchor='ma')
 save(cover,'cover-500.png',300000)
 records.append({'file':'cover-500.png','sources':sources})
 # Every storefront language gets its own 1440 x 720 headline/banner.
 for key,item in LOCALES.items():
  im=canvas(1440,720);rtl=key=='iw';tx=1370 if rtl else 70;anchor='ra' if rtl else 'la'
  text(im,(tx,56),item['title'],25,color='#9edbcc',locale=key,anchor=anchor)
  headline=lines(item['headline'],font(52,key,True),670)
  for i,line in enumerate(headline):text(im,(tx,132+i*76),line,52,locale=key,bold=True,anchor=anchor)
  y=144+len(headline)*76
  for i,line in enumerate(lines(item['tagline'],font(26,key),650)):text(im,(tx,y+i*40),line,26,color='#c5d7df',locale=key,anchor=anchor)
  sources=[face(im,DAY,70 if rtl else 900,118)]
  text(im,(tx,600),'12/24H  ·  MIP  ·  AMOLED',22,color='#9edbcc',anchor=anchor)
  for i,line in enumerate(lines(item['demoCaption'],font(17,key),670)):
   text(im,(tx,636+i*25),line,17,color='#a8b9c5',locale=key,anchor=anchor)
  path=save(im,f'hero-{key}-1440x720.jpg',2000000);records.append({'file':path.name,'locale':key,'sources':sources})
 # Five global screenshot slots: several native scenes in each panel.
 PANELS=[
  ('01-displays.jpg','A mountain for every display','Original art, bold time, independent monochrome and colour layouts',[
   ('AMOLED / DAY','docs/verified-release/epix2-day-birds-plane.png',True),('AMOLED / NIGHT','docs/verified-release/epix2-aurora-birds-plane.png',True),('COLOUR MIP / FENIX 7','docs/verified-release/fenix7-day-birds-plane.png',True),('MONOCHROME MIP / INSTINCT','docs/verified-release/instinct2s-snow-birds-plane.png',False)]),
  ('02-backgrounds.jpg','18 backgrounds. Your choice stays.','Automatic weather, or pin your favourite. Birds and airplane are optional.',[
   ('AURORA','docs/verified-release/epix2-aurora-birds-plane.png',True),('RAIN SKIN','docs/verified-sky/epix2-rain.png',True),('SNOW SKIN','docs/verified-sky/epix2-snow.png',True),('DAWN','docs/sky-sunrise.png',True)]),
  ('03-festivals.jpg','Four festivals, any time of year','Spring Festival · Christmas · Halloween · Mid-Autumn',[
   ('SPRING FESTIVAL','docs/verified-bright/epix2-spring.png',True),('CHRISTMAS','docs/verified-bright/epix2-christmas.png',True),('HALLOWEEN','docs/verified-bright/epix2-halloween.png',True),('MID-AUTUMN / NIGHT','docs/verified-bright/epix2-mid-autumn-night.png',True)]),
  ('04-your-data.jpg','Your data. Your layout.','6 Instinct / 7 colour data positions · 12 choices · 4 panel styles',[
   ('CLASSIC','docs/verified/verified-instinct3-classic.png',False),('CONTOUR','docs/verified/verified-instinct3-contour.png',False),('EXPEDITION','docs/verified/verified-instinct3-expedition.png',False),('SUMMIT WINGS','docs/verified/verified-instinct3-wings.png',False)]),
  ('05-everyday.jpg','Built for everyday use','12/24-hour time · Awake seconds · Moving Sun/Moon · Low-brightness AMOLED clock',[
   ('12-HOUR / COLOUR','docs/verified-bright/epix2-day-bright.png',True),('24-HOUR / COLOUR','docs/verified-release/epix2-day-birds-plane.png',True),('AMOLED / ALWAYS-ON','docs/verified-release/epix2-aod-native.png',True),('ON-WATCH SETTINGS','docs/verified-bright/instinct2s-time24-menu.png',False)])]
 for name,title,subtitle,items in PANELS:
  im=canvas(1440,1280);text(im,(60,44),'ALPINE',24,color='#9edbcc',bold=True);text(im,(60,90),title,49,bold=True)
  for i,line in enumerate(lines(subtitle,font(24),1310)):text(im,(60,166+34*i),line,24,color='#c5d7df')
  cols=3 if len(items)>4 else 2;cellw=1440//cols;sources=[]
  for i,(label,relative,rounded) in enumerate(items):
   path=R/relative
   if not path.exists():raise FileNotFoundError(path)
   source=Image.open(path);size=416 if source.width>=416 else 352 if source.width==176 else 326 if source.width==163 else 364
   x=i%cols*cellw+(cellw-size)//2;y=254+i//cols*470
   sources.append(face(im,path,x,y,size,rounded));text(im,(i%cols*cellw+cellw//2,y+size+12),label,20,color='#a5e9db',anchor='ma',bold=True)
  footer='Native simulator captures · Demo data · Manual skins do not change actual weather data'
  text(im,(60,1230),footer,19,color='#a8b9c5')
  path=save(im,name,148000);records.append({'file':name,'sources':sources,'historicalNativeCaptures':any('verified-release' not in s['file'] for s in sources),'freshCaptureReview':'Source 301136a: fresh display-family, aurora and always-on captures; retained native festival and configuration examples.'})
 (OUT/'media-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 print('Prepared',len(records),'media assets: cover + 28 localized banners + 5 rich screenshot panels')

if __name__=="__main__":main()
