"""Package only final live PRGs and explicitly selected native evidence."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];E=R/'dist/evidence';D=R/'docs';version='1.2.0'
frames=[('本能 · 晴天正午','sky-noon-instinct3.png',2),('日出 · 04:50','sky-sunrise.png',1),('晴天正午 · 12:00','noon.png',1),('本能 · 雪天','sky-snow-instinct2s.png',2),('近满月 · 23:00','sky-fullmoon.png',1),('雪天 · 云层与积雪','sky-snow.png',1)]
font_path=R.parent/'moke/assets/fonts/NotoSansCJKsc-Regular.otf'
f=ImageFont.truetype(str(font_path),23);small=ImageFont.truetype(str(font_path),15)
board=Image.new('RGB',(1280,1040),(14,19,23));draw=ImageDraw.Draw(board)
for i,(title,name,scale) in enumerate(frames):
 col=i%3;row=i//3;left=[0,416,848][col];width=400 if col==0 else 416;top=row*520
 im=Image.open(E/name).convert('RGB');assert im.size in [(176,176),(163,156),(416,416)]
 shutil.copy2(E/name,D/('sky-noon.png' if name=='noon.png' else name))
 im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
 draw.text((left+16,top+12),title,font=f,fill='white')
 board.paste(im,(left+(width-im.width)//2,top+54+(416-im.height)//2))
 draw.text((left+16,top+483),'模拟器 · 演示日期与天气'+(' · 2×' if scale==2 else ' · 原生尺寸'),font=small,fill=(154,175,183))
board.save(D/'preview-weather.png');board.save(D/'preview-board.png')
for source,target in [('noon.png','epix2-native.png'),('sky-fullmoon.png','epix2-night.png'),('sky-noon-instinct3.png','instinct3-native.png'),('sky-snow-instinct2s.png','instinct2s-native.png')]:shutil.copy2(E/source,D/target)
manifest=[]
for p in sorted((R/'bin').glob('*-live.prg')):
 target=R/'dist'/p.name;shutil.copy2(p,target);manifest.append({'file':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
assert len(manifest)==6
(R/'dist/SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in manifest));(R/'dist/builds.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'dist/INSTALL.txt').write_text(f'''山境 Alpine {version}

选择对应设备的 -live.prg，USB 连接手表，复制到 GARMIN/APPS/，安全断开后在表盘菜单选择山境。
instinct3solar45mm = 本能 3 Solar 45/50 mm
instinct2 / instinct2s / instinct2x = 本能 2 / 2S / 2X
fenix7 = fēnix 7；epix2 = epix Gen 2
不能跨机型安装。

日月按分钟更新；有有效缓存位置时使用近似天文计算，无位置时采用本地时段/月相示意。正常同步天气或让手表已有定位可提供位置，本表盘不主动启动 GPS。
晴天零云，多云、阴雨雪雾改变天空与山体；天气读取系统缓存。圆窗默认心率，电池为系统预计剩余天数，缺失时显示 --D。
已做编译、数值与模拟器验证，未完成真机安装、当地实际升落对照和长期续航测量；未上架商店。
''')
archive=R/f'dist/WristInk-Alpine-{version}-local.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((R/'dist').glob('*-live.prg')):z.write(p,p.name)
 for name in ['SHA256SUMS','INSTALL.txt','builds.json']:z.write(R/'dist'/name,name)
 z.write(R/'assets/astronomy/LICENSE-SunCalc.txt','licenses/LICENSE-SunCalc.txt');z.write(R/'assets/fonts/OFL-Rajdhani.txt','licenses/OFL-Rajdhani.txt')
 z.write(R/'assets/astronomy/SOURCES.md','astronomy-sources.md');z.write(D/'validation.md','validation.md');z.write(D/'preview-weather.png','preview.png')
 for _,name,_ in frames:z.write(E/name,'screens/'+name)
print(archive)
