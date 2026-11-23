"""Native geometry and font resources; all artwork is original vector geometry."""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import json, math, uuid, shutil
from PIL import Image, ImageDraw, ImageFont
from everest_art import generate_resources
import mountain_art
from typography import build_fonts
from sky_ornaments import generate as generate_ornaments
ROOT=Path(__file__).resolve().parents[1]
PACKS=ciq_env.DEVICES
DEVICES=json.loads((ROOT/'config/devices.json').read_text())
FONT=ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'

def skyless(scene,w,h,amoled):
    """The mountain with a transparent sky: the face paints the sky, sun, Moon
    and stars for the real time and weather behind it. Rendered once on a black
    and once on a white sky; pixels that change are sky (or a blended edge)."""
    from PIL import ImageChops
    if scene==3:
        from everest_art import render as everest
        draw=lambda sky: everest(w,h,2,False,amoled,0,skyfill=sky)
    else:
        draw=lambda sky: mountain_art.render_colour(scene,w,h,amoled,sky=sky)
    a=draw((0,0,0)).convert('RGB');b=draw((255,255,255)).convert('RGB')
    mask=ImageChops.difference(a,b).convert('L').point(lambda v:255 if v<24 else 0)
    if amoled:
        # 15 (Everest 11) flat colours plus the transparent sky: 4 bits per pixel.
        counts={}
        for px,m in zip(a.getdata(),mask.getdata()):
            if m:counts[px]=counts.get(px,0)+1
        base=a.copy();base.paste(max(counts,key=counts.get),(0,0,w,h),ImageChops.invert(mask))
        a=base.quantize(15 if scene<3 else 11,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
    out=a.convert('RGBA');out.putalpha(mask)
    return out

def generate():
    from panels import generate as generate_panels
    from festivals import generate as generate_festivals
    # Lite release: one classic mountain, no bundled seasonal backgrounds.
    jungle=['project.manifest = manifest.xml','base.sourcePath = source;live','base.resourcePath = resources']
    profiles=[];resource_families={}
    for device in DEVICES:
        c=json.loads((PACKS/device/'compiler.json').read_text());s=json.loads((PACKS/device/'simulator.json').read_text())
        w,h=map(int,c['deviceFamily'].split('-')[-1].split('x'));mono=c['bitsPerPixel']==1;scale=h/176 if mono else w/260
        out=ROOT/'generated'/device;res=out/'resources';fonts=res/'fonts';fonts.mkdir(parents=True,exist_ok=True)
        family=(w,h,mono,c['bitsPerPixel'])
        reuse=resource_families.get(family)
        if reuse:shutil.copytree(reuse,res,dirs_exist_ok=True)
        generate_panels(out,mono,scale)
        if not reuse:build_fonts(fonts,scale,mono,c['bitsPerPixel']==16)
        loc=s['display']['location'];sub=s.get('subscreen');cx=cy=radius=0
        if sub:
            q=sub['location'];cx=q['x']-loc['x']+q['width']/2;cy=q['y']-loc['y']+q['height']/2;radius=q['width']/2-3
        constants={'W':w,'H':h,'S':scale,'MONO':mono,'AMOLED':c['bitsPerPixel']==16,'CX':round(cx),'CY':round(cy),'CR':round(radius)}
        icons=res/'drawables';icons.mkdir(exist_ok=True)
        iw=c['launcherIcon']['width'];ih=c['launcherIcon']['height']
        (icons/'icon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{iw}" height="{ih}" viewBox="0 0 40 40"><rect width="40" height="40" fill="black"/><path d="M3 31 L18 8 L25 18 L29 13 L38 31 Z" fill="white"/><path d="M12 27 L18 13 L21 21 L18 19 Z" fill="black"/></svg>')
        # Four selectable mountains. Flat colour planes compress to a few KB, so
        # every device carries all four and stays under the 100,000-byte limit.
        amoled=c['bitsPerPixel']==16;entries=[]
        for scene in range(len(mountain_art.NAMES)):
            filename=f'mountain-{scene}.png'
            if not reuse:
                if mono:
                    # 1-bit art stays opaque (a transparent slot would double it in the
                    # 64 KB Instinct 2 heap); the face draws the sky objects over the sky.
                    if scene==3:
                        from everest_art import render
                        image=render(w,h,2,mono,amoled,0)
                    else:image=mountain_art.render(scene,w,h,mono,amoled)
                else:image=skyless(scene,w,h,amoled)
                image.save(icons/filename,optimize=True)
            palette=''
            if amoled:
                # An explicit palette (opaque colours + transparency) keeps four
                # backgrounds inside the 100,000-byte binary; the art is flat planes.
                image=Image.open(icons/filename).convert('RGBA')
                colors=sorted(set(px[:3] for px in image.getdata() if px[3]))
                palette='<palette disableTransparency="false">'+''.join('<color>'+''.join(f'{v:02X}' for v in color)+'</color>' for color in colors)+'</palette>'
            entries.append(f'<bitmap id="Mountain{scene}" filename="{filename}" dithering="none" compress="true"'+(' automaticPalette="false"' if amoled else '')+'>'+palette+'</bitmap>')
        (icons/'drawables.xml').write_text('<drawables><bitmap id="LauncherIcon" filename="icon.svg"/>'+''.join(entries)+'</drawables>')
        (out/'LandscapeArt.mc').write_text('module LandscapeArt {function id(key){switch(key){case 1:return Rez.Drawables.Mountain1;case 2:return Rez.Drawables.Mountain2;case 3:return Rez.Drawables.Mountain3;}return Rez.Drawables.Mountain0;}}\n')
        (out/'Device.mc').write_text('import Toybox.Lang;\nmodule Device {\n'+''.join(f' const {k}={str(v).lower()};\n' for k,v in constants.items())+'}\n')
        jungle += [f'{device}.sourcePath = $(base.sourcePath);generated/{device}',f'{device}.resourcePath = $(base.resourcePath);generated/{device}/resources',f'{device}.lang.zhs = resources-zhs']
        profiles.append(dict(device=device,**constants,minimumApi='.'.join(map(str,min(tuple(map(int,p['connectIQVersion'].split('.'))) for p in c['partNumbers'])))))
    (ROOT/'monkey.jungle').write_text('\n'.join(jungle)+'\n')
    for mode in ['preview','tests']:
        lines=[l.replace('project.manifest = manifest.xml',f'project.manifest = {mode}/manifest.xml').replace('base.sourcePath = source;live','base.sourcePath = source;'+('preview' if mode=='preview' else 'live;tests')) for l in jungle]
        if mode=='preview':lines=[l.replace('base.resourcePath = resources','base.resourcePath = resources;preview/resources').replace('.lang.zhs = resources-zhs','.lang.zhs = resources-zhs;preview/resources-zhs') for l in lines]
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
            ident=uuid.uuid5(uuid.NAMESPACE_DNS,f'wristink.alpine.sky2.{mode}.{device}').hex
            source=(ROOT/mode/'manifest.xml').read_text()
            old='bb71078cce15417aa5425aa350817002' if mode=='preview' else 'bb71078cce15417aa5425aa350817003'
            (ROOT/rel).write_text(source.replace(old,ident))
            (ROOT/f'{mode}-{device}.jungle').write_text((ROOT/f'{mode}.jungle').read_text().replace(f'project.manifest = {mode}/manifest.xml',f'project.manifest = {rel}'))
    d=ROOT/'resources/drawables';d.mkdir(exist_ok=True)
    # Original logo: no assets are extracted from the reference or its branding.
    (d/'icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><rect width="40" height="40" fill="black"/><path d="M3 31 L18 8 L25 18 L29 13 L38 31 Z" fill="white"/><path d="M12 27 L18 13 L21 21 L18 19 Z" fill="black"/></svg>')
    (d/'drawables.xml').write_text('<drawables><bitmap id="LauncherIcon" filename="icon.svg"/></drawables>')

if __name__=='__main__':generate()
