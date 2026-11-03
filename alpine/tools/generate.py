"""Native geometry and font resources; all artwork is original vector geometry."""
from pathlib import Path
import json, math, uuid
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
PACKS=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Devices'
DEVICES=['instinct3solar45mm','instinct2','instinct2s','instinct2x','fenix7','epix2']
FONT=ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'

def font(out,name,height,chars,bold=False):
    size=height
    while ImageFont.truetype(str(FONT),size).getbbox('8')[3]-ImageFont.truetype(str(FONT),size).getbbox('8')[1]<height-2:size+=1
    f=ImageFont.truetype(str(FONT),size);stroke=1 if bold else 0
    glyphs=[]
    for ch in chars:
        box=f.getbbox(ch,stroke_width=stroke);w=max(1,box[2]-box[0]);h=max(1,box[3]-box[1])
        im=Image.new('RGBA',(w,h));ImageDraw.Draw(im).text((-box[0],-box[1]),ch,font=f,fill='white',stroke_width=stroke,stroke_fill='white')
        # MIP and AMOLED share grid-fitted fonts, regenerated at each native size.
        a=im.getchannel('A').point(lambda v:255 if v>=105 else 0);im.putalpha(a)
        glyphs.append((ch,im))
    cell=max(im.width for _,im in glyphs)+2;line=max(im.height for _,im in glyphs)
    atlas=Image.new('RGBA',(cell*len(chars),line))
    rows=[f'info face="Alpine Rajdhani" size={line} bold=1 italic=0 unicode=1 smooth=0 aa=1',f'common lineHeight={line} base={line} scaleW={atlas.width} scaleH={line} pages=1 packed=0',f'page id=0 file="{name}.png"',f'chars count={len(chars)}']
    for i,(ch,im) in enumerate(glyphs):
        y=line-im.height;atlas.paste(im,(cell*i,y))
        rows.append(f'char id={ord(ch)} x={cell*i} y=0 width={im.width} height={line} xoffset=0 yoffset=0 xadvance={im.width+max(1,round(height*.07))} page=0 chnl=15')
    atlas.save(out/(name+'.png'));(out/(name+'.fnt')).write_text('\n'.join(rows)+'\n')

def generate():
    jungle=['project.manifest = manifest.xml','base.sourcePath = source;live','base.resourcePath = resources']
    profiles=[]
    for device in DEVICES:
        c=json.loads((PACKS/device/'compiler.json').read_text());s=json.loads((PACKS/device/'simulator.json').read_text())
        w,h=map(int,c['deviceFamily'].split('-')[-1].split('x'));mono=c['bitsPerPixel']==1;scale=h/176 if mono else w/260
        out=ROOT/'generated'/device;res=out/'resources';fonts=res/'fonts';fonts.mkdir(parents=True,exist_ok=True)
        sizes={'Time':round(35*scale if mono else 49*scale),'Small':max(7,round(9*scale if mono else 13*scale)),'Data':round(13*scale if mono else 19*scale),'Circle':round(20*scale),'Aod':round(21*scale)}
        for name,height in sizes.items():font(fonts,name,height,'0123456789:-' if name in ('Time','Circle','Aod') else ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-:.%/',name in ('Time','Circle'))
        (fonts/'fonts.xml').write_text('<fonts>'+''.join(f'<font id="{n}" filename="{n}.fnt"/>' for n in sizes)+'</fonts>')
        loc=s['display']['location'];sub=s.get('subscreen');cx=cy=radius=0
        if sub:
            q=sub['location'];cx=q['x']-loc['x']+q['width']/2;cy=q['y']-loc['y']+q['height']/2;radius=q['width']/2-3
        constants={'W':w,'H':h,'S':scale,'MONO':mono,'AMOLED':c['bitsPerPixel']==16,'CX':round(cx),'CY':round(cy),'CR':round(radius)}
        icons=res/'drawables';icons.mkdir(exist_ok=True)
        iw=c['launcherIcon']['width'];ih=c['launcherIcon']['height']
        (icons/'icon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{iw}" height="{ih}" viewBox="0 0 40 40"><rect width="40" height="40" fill="black"/><path d="M3 31 L18 8 L25 18 L29 13 L38 31 Z" fill="white"/><path d="M12 27 L18 13 L21 21 L18 19 Z" fill="black"/></svg>')
        (icons/'drawables.xml').write_text('<drawables><bitmap id="LauncherIcon" filename="icon.svg"/></drawables>')
        (out/'Device.mc').write_text('module Device {\n'+''.join(f' const {k}={str(v).lower()};\n' for k,v in constants.items())+'}\n')
        jungle += [f'{device}.sourcePath = $(base.sourcePath);generated/{device}',f'{device}.resourcePath = $(base.resourcePath);generated/{device}/resources',f'{device}.lang.zhs = resources-zhs']
        profiles.append(dict(device=device,**constants,minimumApi=min(p['connectIQVersion'] for p in c['partNumbers'])))
    (ROOT/'monkey.jungle').write_text('\n'.join(jungle)+'\n')
    for mode in ['preview','tests']:
        lines=[l.replace('project.manifest = manifest.xml',f'project.manifest = {mode}/manifest.xml').replace('base.sourcePath = source;live','base.sourcePath = source;'+('preview' if mode=='preview' else 'live;tests')) for l in jungle]
        (ROOT/(mode+'.jungle')).write_text('\n'.join(lines)+'\n')
    (ROOT/'generated/profiles.json').write_text(json.dumps(profiles,indent=2)+'\n')
    for mode,ident in [('live','bb71078cce15417aa5425aa350817001'),('preview','bb71078cce15417aa5425aa350817002'),('tests','bb71078cce15417aa5425aa350817003')]:
        xml='<?xml version="1.0"?><iq:manifest xmlns:iq="http://www.garmin.com/xml/connectiq" version="3"><iq:application id="'+ident+'" type="watchface" name="@Strings.AppName" entry="AlpineApp" launcherIcon="@Drawables.LauncherIcon" minApiLevel="3.2.0"><iq:products>'+''.join(f'<iq:product id="{d}"/>' for d in DEVICES)+'</iq:products><iq:permissions><iq:uses-permission id="SensorHistory"/><iq:uses-permission id="Positioning"/></iq:permissions><iq:languages><iq:language>eng</iq:language><iq:language>zhs</iq:language></iq:languages><iq:barrels/></iq:application></iq:manifest>'
        (ROOT/('manifest.xml' if mode=='live' else mode+'/manifest.xml')).write_text(xml+'\n')
    # The simulator caches bitmap fonts by app ID across device switches.
    # Isolate preview/test IDs per target; the production app ID stays stable.
    for mode in ['preview','tests']:
        for device in DEVICES:
            rel=f'generated/{device}/{mode}-manifest.xml'
            ident=uuid.uuid5(uuid.NAMESPACE_DNS,f'wristink.alpine.{mode}.{device}').hex
            source=(ROOT/mode/'manifest.xml').read_text()
            old='bb71078cce15417aa5425aa350817002' if mode=='preview' else 'bb71078cce15417aa5425aa350817003'
            (ROOT/rel).write_text(source.replace(old,ident))
            (ROOT/f'{mode}-{device}.jungle').write_text((ROOT/f'{mode}.jungle').read_text().replace(f'project.manifest = {mode}/manifest.xml',f'project.manifest = {rel}'))
    d=ROOT/'resources/drawables';d.mkdir(exist_ok=True)
    # Original logo: no assets are extracted from the reference or its branding.
    (d/'icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><rect width="40" height="40" fill="black"/><path d="M3 31 L18 8 L25 18 L29 13 L38 31 Z" fill="white"/><path d="M12 27 L18 13 L21 21 L18 19 Z" fill="black"/></svg>')
    (d/'drawables.xml').write_text('<drawables><bitmap id="LauncherIcon" filename="icon.svg"/></drawables>')

if __name__=='__main__':generate()
