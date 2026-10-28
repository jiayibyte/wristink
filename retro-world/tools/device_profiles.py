"""Generate native-size assets and profiles from Garmin's installed device packs.
No runtime image scaling; each build only contains its own layout/resources.
"""
from pathlib import Path
import json,re,shutil,math,xml.etree.ElementTree as ET
from PIL import Image,ImageOps,ImageFilter,ImageDraw
import assets
from retro_style import GLYPHS
ROOT=Path(__file__).resolve().parents[1]
PACKS=Path.home()/'Library/Application Support/Garmin/ConnectIQ/Devices'
NS='http://www.garmin.com/xml/connectiq';ET.register_namespace('iq',NS)
PAPER=0xE8EDDC;TEAL=0x63B6A4;AMBER=0xF2BD67;NIGHT=0x203F48

def n(v,scale):return max(1,math.floor(v*scale+.5))
def coord(v):return math.floor(v+.5)
def geometry(c,s):
    w,h=map(int,c['deviceFamily'].split('-')[-1].split('x'))
    loc=s['display']['location'];shape=s['display']['shape'];sub=s.get('subscreen')
    # Device family is the actual framebuffer; simulator location may include bezel overlap.
    if 'semioctagon' in c['deviceFamily']:
        scale=min(w,h)/176*(1 if sub else .78);ox=(w-176*scale)/2;oy=(h-176*scale)/2
    elif shape=='round':
        scale=min(w,h)/230;ox=w/2-88*scale;oy=h/2-88*scale
    else:
        scale=min((w-20)/176,(h-24)/176);ox=w/2-88*scale;oy=h/2-88*scale
    cs=scale;cx=ox;cy=oy
    if sub:
        rect=sub['location'];cs=rect['width']/62
        cx=rect['x']-loc['x']+rect['width']/2-144*cs
        cy=rect['y']-loc['y']+rect['height']/2-31*cs
        # The small Instinct 2S visible panel includes a 7px bezel extension.
        if loc['width']!=w:cx-=loc['width']-w
    inset=0
    if c["deviceId"]=="instinct3solar45mm":
        # Measured orange bezel centre (244,191) in Garmin's official skin.
        # Inset 2 keeps every white pixel inside the actual LCD alpha aperture.
        cx-=1;cy+=2;inset=2
    return dict(width=w,height=h,shape=shape,scale=scale,x=ox,y=oy,circle_scale=cs,circle_x=cx,circle_y=cy,circle_inset=inset,subscreen=bool(sub),analog=bool(s.get('analogHands')))

def native_image(im,size,color=False,map_image=False):
    im=im.convert('1').resize(size,Image.Resampling.NEAREST)
    if not color:return im
    # A fixed, small palette is shared with both runtime caches.
    rgb=Image.new('RGB',size);rgb.paste((232,237,220),(0,0,*size))
    ink=ImageOps.invert(im.convert('L'))
    rgb.paste((99,182,164) if map_image else (0,0,0),(0,0),ink)
    return rgb

def fonts(dest,scale):
    for f in (ROOT/'resources/fonts').glob('*.fnt'):
        # A 3x5 digit must not shrink to 2x4: 0 and 8 would become identical.
        glyph_scale=max(1,scale) if f.stem=='tiny' else scale
        text=f.read_text();png=Image.open(f.with_suffix('.png'));glyphs=[]
        for line in text.splitlines():
            if not line.startswith('char id='):continue
            v={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
            glyph=png.crop((v['x'],v['y'],v['x']+v['width'],v['y']+v['height']))
            glyph=glyph.resize((n(v['width'],glyph_scale),n(v['height'],glyph_scale)),Image.Resampling.NEAREST)
            if f.stem=='weather-small' and scale<1:
                # Re-rasterize the same 3x5 master at the native size; a second
                # nearest-neighbour resize would erase the middle bar of 8.
                glyph=Image.new('RGBA',glyph.size,(0,0,0,0));draw=ImageDraw.Draw(glyph)
                rows=GLYPHS[chr(v['id'])]
                for yy,bits in enumerate(rows):
                    for xx,bit in enumerate(bits):
                        if bit=='1':draw.rectangle((round(xx*glyph.width/3),round(yy*glyph.height/5),round((xx+1)*glyph.width/3)-1,round((yy+1)*glyph.height/5)-1),fill=(255,255,255,255))
            glyphs.append((v,glyph))
        width=sum(g.width+1 for _,g in glyphs);height=max(g.height for _,g in glyphs)
        out=Image.new('RGBA',(width,height),(0,0,0,0));x=0;lines=[]
        for v,g in glyphs:
            out.paste(g,(x,0));advance=n(v['xadvance'],glyph_scale)
            lines.append(f"char id={v['id']} x={x} y=0 width={g.width} height={g.height} xoffset=0 yoffset=0 xadvance={advance} page=0 chnl=15")
            x+=g.width+1
        out.save(dest/f.with_suffix('.png').name)
        (dest/f.name).write_text(f'info face="Retro Native" size={height} bold=0 italic=0 unicode=1 smooth=0 aa=1\ncommon lineHeight={height} base={height} scaleW={width} scaleH={height} pages=1 packed=0\npage id=0 file="{f.stem}.png"\nchars count={len(lines)}\n'+'\n'.join(lines)+'\n')
    shutil.copy(ROOT/'resources/fonts/fonts.xml',dest/'fonts.xml')

def resource_set(key,g,color,icon):
    dest=ROOT/'generated'/key/'resources';dest.mkdir(parents=True,exist_ok=True)
    for folder in ('drawables','fonts','strings'):(dest/folder).mkdir(exist_ok=True)
    scale=g['scale'];cs=g['circle_scale'];out=dest/'drawables'
    atlas={'large.png':(10,22,35),'date.png':(10,8,13),'letters.png':(26,6,10),'weekdays.png':(7,32,10),'weather.png':(13,11,11),'weather-small.png':(13,9,9)}
    for p in (ROOT/'resources/drawables').glob('*.png'):
        if p.name in ('dial.png','icon.png'):continue
        im=assets.circle_face(g["circle_inset"]) if p.name=="circle.png" else Image.open(p)
        sc=cs if p.name=='circle.png' else scale
        if p.name in atlas:
            count,w,h=atlas[p.name];nw,nh=n(w,sc),n(h,sc)
            result=Image.new('RGB' if color else '1',(nw*count,nh),(232,237,220) if color else 1)
            for k in range(count):result.paste(native_image(im.crop((k*w,0,(k+1)*w,h)),(nw,nh),color),(k*nw,0))
        else:result=native_image(im,(n(im.width,sc),n(im.height,sc)),color,p.stem.startswith('map'))
        result.save(out/p.name)
    # Entire frame is native-sized. Remove the original embedded circle then
    # position its native-size replacement at the device's actual sub-screen.
    logical=assets.base();ImageDraw.Draw(logical).rectangle((113,0,175,62),fill=0)
    face=Image.new('RGB' if color else '1',(g['width'],g['height']),0)
    scaled=native_image(logical,(n(176,scale),n(176,scale)),color)
    face.paste(scaled,(coord(g['x']),coord(g['y'])))
    circle=Image.open(out/'circle.png')
    face.paste(circle,(coord(g['circle_x']+113*cs),coord(g['circle_y'])))
    if color:
        # Small warm accents, leaving the approved monochrome lettering intact.
        d=ImageDraw.Draw(face);d.line((coord(g['x']+16*scale),coord(g['y']+151*scale),coord(g['x']+159*scale),coord(g['y']+151*scale)),fill=(242,189,103),width=max(1,n(1,scale)))
        mask=assets.sun_mask().resize((n(13,scale),n(8,scale)),Image.Resampling.NEAREST)
        face.paste((242,189,103),(coord(g['x']+82*scale),coord(g['y']+163*scale)),mask)
    face.save(out/'dial.png')
    # AOD outline digits keep the same seven-segment outline; no bright panels.
    aw,ah=n(22,scale),n(35,scale);aod=Image.new('RGB' if color else '1',(aw*10,ah),0)
    for k in range(10):
        ink=ImageOps.invert(assets.digit(k,22,35).convert('L')).resize((aw,ah),Image.Resampling.NEAREST)
        border=ImageChops_subtract(ink,ink.filter(ImageFilter.MinFilter(5)))
        aod.paste((176,184,176) if color else 1,(k*aw,0),border)
    aod.save(out/'aod.png')
    # Keep original native fonts exactly on the user's original Instinct target.
    if scale==1:
        shutil.copytree(ROOT/'resources/fonts',dest/'fonts',dirs_exist_ok=True)
    else:fonts(dest/'fonts',scale)
    shutil.copytree(ROOT/'resources/strings',dest/'strings',dirs_exist_ok=True)
    tree=ET.parse(ROOT/'resources/drawables/drawables.xml');ET.SubElement(tree.getroot(),'bitmap',id='Aod',filename='aod.png')
    for bitmap in tree.getroot():
        bitmap.set('dithering','none');bitmap.set('compress','false')
        image=Image.open(out/bitmap.get('filename')).convert('RGB') if bitmap.get('filename')!='icon.png' else face.convert('RGB')
        colors=sorted(set(image.getdata()))
        palette=ET.SubElement(bitmap,'palette',disableTransparency='true')
        for rgb in colors:ET.SubElement(palette,'color').text=''.join(f'{v:02X}' for v in rgb)
    tree.write(out/'drawables.xml',encoding='utf-8')
    preview=native_image(assets.render(),(n(176,scale),n(176,scale)),color)
    # The icon uses actual face artwork on a neutral, non-branded background.
    preview.resize((icon['width'],icon['height']),Image.Resampling.NEAREST).save(out/'icon.png')
    return dest

def ImageChops_subtract(a,b):
    from PIL import ImageChops
    return ImageChops.subtract(a,b)

def main():
    assets.main();rows=[];excluded=[];groups={}
    for p in sorted(PACKS.glob('*/compiler.json')):
        c=json.loads(p.read_text());types={v['type']:v['memoryLimit'] for v in c['appTypes']}
        if 'watchFace' not in types:continue
        s=json.loads((p.parent/'simulator.json').read_text())
        api=min(tuple(map(int,v['connectIQVersion'].split('.'))) for v in c['partNumbers'])
        recent_exception=c['deviceId'] in ('instinct2','instinct2s','descentg1')
        reason=None
        if api<(3,3,0) and not recent_exception:reason='Older than API 3.3 compatibility baseline'
        elif types['watchFace']<65536:reason='Watch-face memory below 64 KiB'
        if reason:excluded.append({'id':c['deviceId'],'name':c['displayName'],'reason':reason});continue
        g=geometry(c,s);color=c['displayType'] in ('amoled','microled')
        key=c['deviceFamily']+'-'+c['displayType']+('-'+c['deviceId'] if g['subscreen'] or g['analog'] else '')+f"-i{c['launcherIcon']['width']}"
        if key not in groups:groups[key]=resource_set(key,g,color,c['launcherIcon'])
        profile=ROOT/'generated/profiles'/c['deviceId'];profile.mkdir(parents=True,exist_ok=True)
        text='module DeviceProfile {\n'
        for k,v in g.items():
            if isinstance(v,str):continue
            text+=f' const {k.upper()}={str(v).lower() if isinstance(v,bool) else round(v,6)};\n'
        text+=f' const COLOR={str(color).lower()};\n const PAPER={hex(PAPER) if color else "0xFFFFFF"};\n const TEAL={hex(TEAL) if color else "0x000000"};\n const AMBER={hex(AMBER) if color else "0xFFFFFF"};\n const AOD_INK=0xB0B8B0;\n}}\n'
        (profile/'DeviceProfile.mc').write_text(text)
        rows.append({'id':c['deviceId'],'name':c['displayName'],'api':'.'.join(map(str,api)),'memory':types['watchFace'],'parts':len(c['partNumbers']),'color':color,'display':c['displayType'],'profile':key,'geometry':g})
    for demo,manifest,jungle in ((False,'manifest.xml','monkey.jungle'),(True,'preview/manifest.xml','preview.jungle')):
        tree=ET.parse(ROOT/'manifest.xml');app=tree.getroot().find(f'{{{NS}}}application');app.set('minApiLevel','3.2.0');app.set('id','d2fd1f269ea4491f9bf5c77046e0e302' if demo else 'd2fd1f269ea4491f9bf5c77046e0e301')
        products=app.find(f'{{{NS}}}products');products.clear()
        for row in rows:ET.SubElement(products,f'{{{NS}}}product',id=row['id'])
        tree.write(ROOT/manifest,encoding='utf-8',xml_declaration=True)
        mode='preview' if demo else 'live'
        lines=[f'project.manifest = {manifest}','base.excludeAnnotations = diagnostic',f'base.sourcePath = source;{mode};generated/profiles/instinct3solar45mm','base.resourcePath = generated/semioctagon-176x176-mip-instinct3solar45mm-i62/resources']
        for row in rows:
            lines.extend([f"{row['id']}.sourcePath = source;{mode};generated/profiles/{row['id']}",f"{row['id']}.resourcePath = generated/{row['profile']}/resources"])
        (ROOT/jungle).write_text('\n'.join(lines)+'\n')
    # Diagnostic/test artifacts have independent application IDs and explicit
    # build exclusions, so benchmark classes never enter the store binary.
    for filename,mode,manifest in [('diagnostic.jungle','diagnostics','diagnostics/manifest.xml'),('tests.jungle','live;tests','tests/manifest.xml')]:
        j=(ROOT/'monkey.jungle').read_text().replace('project.manifest = manifest.xml','project.manifest = '+manifest).replace('source;live;','source;'+mode+';')
        if mode=='diagnostics':j=j.replace('base.excludeAnnotations = diagnostic','base.excludeAnnotations = release')
        (ROOT/filename).write_text(j)
    report={'baseline':'API >=3.3, >=64KiB; Instinct 2/2S and Descent G1 include regional API 3.2.7','devices':rows,'excluded':excluded,'profiles':len(groups)}
    (ROOT/'dist/device-matrix.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('Targets',len(rows),'hardware variants',sum(r['parts'] for r in rows),'native resource profiles',len(groups))
if __name__=='__main__':main()
