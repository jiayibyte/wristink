"""Package final live PRGs, native configuration screenshots and instructions."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];E=R/'dist/evidence';D=R/'docs';version='1.3.1'
frames=[('本能 · 山景数据默认隐藏','headers-hidden-instinct3.png',2),('彩屏 · 三处数据位默认隐藏','headers-hidden-epix2.png',1)]
f=ImageFont.truetype(str(R.parent/'moke/assets/fonts/NotoSansCJKsc-Regular.otf'),22);small=ImageFont.truetype(str(R.parent/'moke/assets/fonts/NotoSansCJKsc-Regular.otf'),15)
board=Image.new('RGB',(864,520),(14,19,23));draw=ImageDraw.Draw(board)
for i,(title,name,scale) in enumerate(frames):
 im=Image.open(E/name).convert('RGB');assert im.size in [(176,176),(416,416)]
 shutil.copy2(E/name,D/name);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
 draw.text((i*432+14,14),title,font=f,fill='white');board.paste(im,(i*432+(432-im.width)//2,54+(416-im.height)//2))
 draw.text((i*432+14,482),'实际模拟器 · 演示数据',font=small,fill=(154,175,183))
board.save(D/'preview-hidden-headers.png');board.save(D/'preview-board.png')
shutil.copy2(E/'headers-hidden-instinct3.png',D/'instinct3-native.png');shutil.copy2(E/'headers-hidden-epix2.png',D/'epix2-native.png')
manifest=[]
for p in sorted((R/'bin').glob('*-live.prg')):
 target=R/'dist'/p.name;shutil.copy2(p,target);manifest.append({'file':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
assert len(manifest)==6
(R/'dist/SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in manifest));(R/'dist/builds.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'dist/INSTALL.txt').write_text(f'''山境 Alpine {version}

选择对应设备的 -live.prg，USB 连接手表后复制到 GARMIN/APPS/，安全断开，在表盘菜单选择山境。
instinct3solar45mm = 本能 3 Solar 45/50 mm；instinct2 / instinct2s / instinct2x = 本能 2 / 2S / 2X；fenix7 = fēnix 7；epix2 = epix Gen 2。不能跨机型安装。

自定义：进入这款表盘的「设置 / 自定义」→「数据位」，选择圆窗、顶部/侧边或底部位置，再选择指标。选中自动保存，BACK 返回后生效；固件入口名称可能略有不同。
顶部和山景左右三个数据位默认隐藏。右上圆窗默认天气图标与温度，底部默认步数/心率/热量。可以独立换成心率、步数、热量、海拔、剩余天数、距离、天气温度、压力、通知、日出、日落或隐藏。

太阳月亮与天气联动保持原有功能。有位置时计算近似升落，无位置时为时段示意；天气与温度读取系统缓存。仅完成编译与官方模拟器验证，未做真机验收或上架商店。
''')
archive=R/f'dist/WristInk-Alpine-{version}-local.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((R/'dist').glob('*-live.prg')):z.write(p,p.name)
 for name in ['SHA256SUMS','INSTALL.txt','builds.json']:z.write(R/'dist'/name,name)
 z.write(R/'assets/astronomy/LICENSE-SunCalc.txt','licenses/LICENSE-SunCalc.txt');z.write(R/'assets/fonts/OFL-Rajdhani.txt','licenses/OFL-Rajdhani.txt')
 z.write(D/'validation.md','validation.md');z.write(D/'preview-hidden-headers.png','preview.png')
 for _,name,_ in frames:z.write(E/name,'screens/'+name)

print(archive)
