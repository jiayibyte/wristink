"""Package signed per-device PRGs and actual simulator evidence for local review."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];E=R/'dist/evidence';D=R/'docs';version='1.0.1'
for name in ['instinct3-native','instinct2s-native','fenix7-native','epix2-native','epix2-night']:
 shutil.copy2(E/(name+'.png'),D/(name+'.png'))
board=Image.new('RGB',(1280,520),(14,19,23));draw=ImageDraw.Draw(board)
f=ImageFont.truetype(str(R/'assets/fonts/Rajdhani-SemiBold.ttf'),25);small=ImageFont.truetype(str(R/'assets/fonts/Rajdhani-SemiBold.ttf'),17)
for title,filename,left,width,scale in [('INSTINCT 3 SOLAR','instinct3-native',0,400,2),('AMOLED / DAY','epix2-native',416,416,1),('AMOLED / NIGHT','epix2-night',848,416,1)]:
 draw.text((left+18,14),title,font=f,fill='white');im=Image.open(E/(filename+'.png')).convert('RGB');im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
 board.paste(im,(left+(width-im.width)//2,55+(416-im.height)//2));draw.text((left+18,481),'SIMULATOR / DEMO DATA'+(' / 2X' if scale==2 else ' / 1X'),font=small,fill=(154,175,183))
board.save(D/'preview-board.png');board.save(D/'preview-details.png')
manifest=[]
for p in sorted((R/'bin').glob('*-live.prg')):
 target=R/'dist'/p.name;shutil.copy2(p,target);manifest.append({'file':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
assert len(manifest)==6
(R/'dist/SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in manifest))
(R/'dist/builds.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'dist/INSTALL.txt').write_text(f'''山境 Alpine {version} 本地修订版

选择与设备对应的 -live.prg，USB 连接手表，复制到 GARMIN/APPS/，安全断开后在表盘菜单选择山境。
instinct3solar45mm = 本能 3 Solar 45/50 mm
instinct2 / instinct2s / instinct2x = 本能 2 / 2S / 2X
fenix7 = fēnix 7；epix2 = epix Gen 2
这些文件不能跨机型安装。
本能圆窗默认心率；电池显示为系统预计剩余天数，缺失时为 --D。
只有编译和官方模拟器验证，未完成真机安装与长期续航测量，未上架商店。
''')
archive=R/f'dist/WristInk-Alpine-{version}-local.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((R/'dist').glob('*-live.prg')):z.write(p,p.name)
 for name in ['SHA256SUMS','INSTALL.txt','builds.json']:z.write(R/'dist'/name,name)
 z.write(D/'validation.md','validation.md');z.write(D/'preview-board.png','preview.png')
 for p in sorted(D.glob('*-native.png')):z.write(p,'screens/'+p.name)
print(archive)
