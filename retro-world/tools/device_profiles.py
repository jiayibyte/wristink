"""Generate native-size assets and profiles from Garmin's installed device packs.
No runtime image scaling; each build only contains its own layout/resources.
"""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import json,re,shutil,math,xml.etree.ElementTree as ET
from PIL import Image,ImageOps,ImageFilter,ImageDraw
import assets
from retro_style import GLYPHS, native as native_glyph
from garmin_weather import icon as garmin_icon
ROOT=Path(__file__).resolve().parents[1]
PACKS=ciq_env.DEVICES
NS='http://www.garmin.com/xml/connectiq';ET.register_namespace('iq',NS)
PAPER=0xE8EDDC;TEAL=0x63B6A4;AMBER=0xF2BD67;NIGHT=0x203F48
# Colour screens get one accent per data kind and coloured panel frames.
# MIP values come from the 64-colour panel palette so nothing is quantised.
PALETTES={
 'amoled':dict(PAPER=0xE8EDDC,TEAL=0x63B6A4,AMBER=0xF2BD67,RED=0xF07869,GREEN=0x9BD36A,SKY=0x7CC4F0,AOD_INK=0xB0B8B0),
 'mip':dict(PAPER=0xFFFFAA,TEAL=0x00AAAA,AMBER=0xFFAA00,RED=0xFF5555,GREEN=0x55FF55,SKY=0x55AAFF,AOD_INK=0xAAAAAA),
}
PAL=PALETTES['amoled']
def hexrgb(v):return ((v>>16)&255,(v>>8)&255,v&255)

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
        # Use the SDK LCD centre, not the decorative orange bezel. The 2.0
        # optical correction (-1,+2) appeared left/down on the user's watch.
        inset=2
    return dict(width=w,height=h,shape=shape,scale=scale,x=ox,y=oy,circle_scale=cs,circle_x=cx,circle_y=cy,circle_inset=inset,subscreen=bool(sub),analog=bool(s.get('analogHands')))

def native_image(im,size,color=False,map_image=False):
    im=im.convert('1').resize(size,Image.Resampling.NEAREST)
    if not color:return im
    # A fixed, small palette is shared with both runtime caches.
    out=Image.new('RGB',size);out.paste(hexrgb(PAL['PAPER']),(0,0,*size))
    ink=ImageOps.invert(im.convert('L'))
    out.paste(hexrgb(PAL['TEAL']) if map_image else (0,0,0),(0,0),ink)
    return out

def fonts(dest,scale):
    for f in (ROOT/'resources/fonts').glob('*.fnt'):
        # A 3x5 digit must not shrink to 2x4: 0 and 8 would become identical.
        glyph_scale=max(1,scale) if f.stem=='tiny' else scale
        text=f.read_text();png=Image.open(f.with_suffix('.png'));glyphs=[]
        for line in text.splitlines():
            if not line.startswith('char id='):continue
            v={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
            glyph=png.crop((v['x'],v['y'],v['x']+v['width'],v['y']+v['height']))
            size=(n(v['width'],glyph_scale),n(v['height'],glyph_scale))
            # Construct each glyph at its final size. Enlarging the 176px
            # bitmap by a fractional factor gives columns of uneven width.
            base_stroke=1 if f.stem=='tiny' else 2
            # Keep a 2px counter: at 4px wide a 2px stroke fills 0 and 8 into the same block.
            stroke=min(max(1,round(base_stroke*glyph_scale)),max(1,(size[0]-2)//2))
            fresh=native_glyph(chr(v['id']),size[0],size[1],stroke)
            if fresh is not None and chr(v['id'])!=' ':
                glyph=Image.new('RGBA',size,(255,255,255,0));glyph.putalpha(fresh)
                glyphs.append((v,glyph));continue
            glyph=glyph.resize(size,Image.Resampling.NEAREST)
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

def write_font(folder,name,glyphs):
    """BMFont from (char, ink mask) pairs; drawn in whatever ink the dc sets."""
    w=max(m.width for _,m in glyphs);h=max(m.height for _,m in glyphs)
    atlas=Image.new('RGBA',(len(glyphs)*(w+1),h),(255,255,255,0));lines=[]
    for i,(ch,mask) in enumerate(glyphs):
        tile=Image.new('RGBA',mask.size,(255,255,255,0));tile.putalpha(mask);atlas.paste(tile,(i*(w+1),0))
        lines.append(f'char id={ord(ch)} x={i*(w+1)} y=0 width={mask.width} height={mask.height} xoffset=0 yoffset=0 xadvance={mask.width} page=0 chnl=15')
    atlas.save(folder/f'{name}.png')
    (folder/f'{name}.fnt').write_text(f'info face="Retro {name}" size={h} bold=0 italic=0 unicode=1 smooth=0 aa=1\ncommon lineHeight={h} base={h} scaleW={atlas.width} scaleH={h} pages=1 packed=0\npage id=0 file="{name}.png"\nchars count={len(lines)}\n'+'\n'.join(lines)+'\n')
    return name

def ink(im):
    """Ink mask (255) of a two-tone sprite whose ink is black."""
    return im.convert('L').point(lambda v:255 if v<128 else 0)

def cells(path,count):
    im=Image.open(path).convert('L');w=im.width//count
    return [ink(im.crop((k*w,0,(k+1)*w,im.height))) for k in range(count)]

def sprite_fonts(folder,out,scale):
    """Two-tone sprites become fonts, so one set of glyphs serves every colour theme."""
    made=[]
    made.append(write_font(folder,'Seg',list(zip('0123456789',cells(out/'large.png',10)))))
    made.append(write_font(folder,'SegDate',list(zip('0123456789',cells(out/'date.png',10)))))
    made.append(write_font(folder,'SegSec',[(str(k),ink(Image.open(out/f'second-{k}.png'))) for k in range(10)]))
    made.append(write_font(folder,'Caps',list(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',cells(out/'letters.png',26)))))
    made.append(write_font(folder,'Days',list(zip('0123456',cells(out/'weekdays.png',7)))))
    made.append(write_font(folder,'WxIcon',list(zip('abcdefghijklm',cells(out/'weather-small.png',13)))))
    # Dial face: 'D' is the disc (paper), 'M' the ticks and numerals (ink).
    face=Image.open(out/'circle.png').convert('L');w,h=face.size
    outside=Image.new('L',(w,h),0);dark=[[face.getpixel((x,y))<128 for x in range(w)] for y in range(h)]
    stack=[(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)];seen=set()
    while stack:
        x,y=stack.pop()
        if (x,y) in seen or not (0<=x<w and 0<=y<h) or not dark[y][x]:continue
        seen.add((x,y));outside.putpixel((x,y),255);stack+=[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    disc=outside.point(lambda v:0 if v else 255)
    marks=Image.composite(ink(face),Image.new('L',(w,h),0),disc)
    made.append(write_font(folder,'Face',[('D',disc),('M',marks)]))
    sun=assets.sun_mask().resize((n(13,scale),n(8,scale)),Image.Resampling.NEAREST).convert('L')
    made.append(write_font(folder,'Icons',[('S',sun)]))
    for skin in range(len(assets.SKIN_NAMES)):
        made.append(write_font(folder,f'MapSkin{skin}',[('d',ink(Image.open(out/f'map-skin-{skin}-0.png'))),('n',ink(Image.open(out/f'map-skin-{skin}-1.png')))]))
    tree=ET.parse(folder/'fonts.xml');root=tree.getroot()
    for name in made:ET.SubElement(root,'font',id=name,filename=name+'.fnt')
    tree.write(folder/'fonts.xml',encoding='utf-8')
    # The PNG sprites themselves are no longer packaged.
    for path in out.glob('*.png'):
        if path.name not in ('dial.png','aod.png','icon.png'):path.unlink()

def resource_set(key,g,color,icon,pal=None):
    global PAL
    PAL=pal or PALETTES['amoled']
    dest=ROOT/'generated'/key/'resources';dest.mkdir(parents=True,exist_ok=True)
    for folder in ('drawables','fonts','strings'):(dest/folder).mkdir(exist_ok=True)
    scale=g['scale'];cs=g['circle_scale'];out=dest/'drawables'
    atlas={'large.png':(10,22,35),'date.png':(10,8,13),'letters.png':(26,6,10),'weekdays.png':(7,32,10),'weather.png':(13,11,11),'weather-small.png':(13,9,9)}
    for p in (ROOT/'resources/drawables').glob('*.png'):
        if p.name in ('dial.png','icon.png'):continue
        im=assets.circle_face(g["circle_inset"]) if p.name=="circle.png" else Image.open(p)
        sc=cs if p.name=='circle.png' else scale
        if p.name=='circle.png' and (sc!=1 or not g['subscreen']):
            # Only the 62px hardware window keeps the approved 63px master as is.
            size=n(63,sc)
            result=native_image(assets.circle_face_native(size,sc,g['subscreen']),(size,size),False)
        elif p.name in atlas:
            count,w,h=atlas[p.name];nw,nh=n(w,sc),n(h,sc)
            result=Image.new('1',(nw*count,nh),1)
            for k in range(count):
                tile=im.crop((k*w,0,(k+1)*w,h))
                # The approved 176px sprites stay byte-identical; every other
                # size is drawn from the same generators at its own resolution.
                if p.name=='weather-small.png' and not g['subscreen']:
                    # Full screens use the larger weather panel; same resource id.
                    size=n(15,sc);tile=garmin_icon(k,size)
                    if k==0:result=Image.new('1',(size*count,size),1)
                    result.paste(native_image(tile,(size,size),False),(k*size,0));continue
                if sc!=1 and p.name in ('weather.png','weather-small.png'):tile=garmin_icon(k,nw)
                elif sc!=1 and p.name in ('large.png','date.png'):tile=assets.digit(k,nw,nh)
                elif sc!=1 and p.name=='letters.png':tile=assets.letter_tile(chr(65+k),nw,nh,max(1,round(sc)))
                elif sc!=1 and p.name=='weekdays.png':tile=assets.weekday_tile(assets.WEEKDAYS[k],nw,nh,sc)
                result.paste(native_image(tile,(nw,nh),False),(k*nw,0))
        elif sc!=1 and p.stem.startswith('second-'):
            result=native_image(assets.digit(int(p.stem[7:]),n(im.width,sc),n(im.height,sc)),(n(im.width,sc),n(im.height,sc)),False)
        else:result=native_image(im,(n(im.width,sc),n(im.height,sc)),False)
        result.save(out/p.name)
    # Entire frame is native-sized. Remove the original embedded circle then
    # position its native-size replacement at the device's actual sub-screen.
    if color:
        # Colour screens draw their panels as vectors in the chosen theme.
        face=Image.new('RGB',(1,1),0)
    else:
        face=Image.new('1',(g['width'],g['height']),0)
        if scale==1 and g['subscreen']:
            # The approved Instinct background stays byte-identical.
            logical=assets.base();ImageDraw.Draw(logical).rectangle((113,0,175,62),fill=0)
        else:logical=assets.base_native(scale,not g['subscreen'])
        face.paste(native_image(logical,(n(176,scale),n(176,scale)),False),(coord(g['x']),coord(g['y'])))
        face.paste(Image.open(out/'circle.png'),(coord(g['circle_x']+113*cs),coord(g['circle_y'])))
    face.save(out/'dial.png')
    # AOD outline digits keep the same seven-segment outline; no bright panels.
    aw,ah=n(22,scale),n(35,scale);aod=Image.new('RGB' if color else '1',(aw*10,ah),0)
    for k in range(10):
        ink=ImageOps.invert(assets.digit(k,aw,ah).convert('L'))
        border=ImageChops_subtract(ink,ink.filter(ImageFilter.MinFilter(5)))
        aod.paste(hexrgb(PAL['AOD_INK']) if color else 1,(k*aw,0),border)
    aod.save(out/'aod.png')
    # Keep original native fonts exactly on the user's original Instinct target.
    if scale==1:
        shutil.copytree(ROOT/'resources/fonts',dest/'fonts',dirs_exist_ok=True)
    else:fonts(dest/'fonts',scale)
    shutil.copytree(ROOT/'resources/strings',dest/'strings',dirs_exist_ok=True)
    shutil.copytree(ROOT/'resources/settings',dest/'settings',dirs_exist_ok=True)
    sprite_fonts(dest/'fonts',out,scale)
    preview=native_image(assets.render(),(n(176,scale),n(176,scale)),color)
    # The icon uses actual face artwork on a neutral, non-branded background.
    preview.resize((icon['width'],icon['height']),Image.Resampling.NEAREST).save(out/'icon.png')
    keep={'Dial':'dial.png','Aod':'aod.png','LauncherIcon':'icon.png'}
    root=ET.Element('drawables')
    for ident,filename in keep.items():
        bitmap=ET.SubElement(root,'bitmap',id=ident,filename=filename,dithering='none',compress='false' if ident=='LauncherIcon' else 'true')
        colors=sorted(set(Image.open(out/filename).convert('RGB').getdata()))
        palette=ET.SubElement(bitmap,'palette',disableTransparency='true')
        for value in colors:ET.SubElement(palette,'color').text=''.join(f'{v:02X}' for v in value)
    ET.ElementTree(root).write(out/'drawables.xml',encoding='utf-8')
    return dest

def ImageChops_subtract(a,b):
    from PIL import ImageChops
    return ImageChops.subtract(a,b)

def main():
    import settings
    settings.generate();assets.main();rows=[];excluded=[];groups={}
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
        g=geometry(c,s);amoled=c['displayType'] in ('amoled','microled');color=amoled or c.get('bitsPerPixel',1)>1;pal=PALETTES['amoled' if amoled else 'mip']
        key=c['deviceFamily']+'-'+c['displayType']+('-'+c['deviceId'] if g['subscreen'] or g['analog'] else '')+('-c' if color and not amoled else '')+f"-i{c['launcherIcon']['width']}"
        if key not in groups:groups[key]=resource_set(key,g,color,c['launcherIcon'],pal)
        profile=ROOT/'generated/profiles'/c['deviceId'];profile.mkdir(parents=True,exist_ok=True)
        text='module DeviceProfile {\n'
        for k,v in g.items():
            if isinstance(v,str):continue
            text+=f' const {k.upper()}={str(v).lower() if isinstance(v,bool) else round(v,6)};\n'
        text+=f' const COLOR={str(color).lower()};\n const AMOLED={str(amoled).lower()};\n'
        mono=dict(PAPER=0xFFFFFF,TEAL=0x000000,AMBER=0xFFFFFF,RED=0xFFFFFF,GREEN=0xFFFFFF,SKY=0xFFFFFF,AOD_INK=0xB0B8B0)
        for name,value in (pal if color else mono).items():text+=f' const {name}={hex(value)};\n'
        text+='}\n'
        (profile/'DeviceProfile.mc').write_text(text)
        rows.append({'id':c['deviceId'],'name':c['displayName'],'api':'.'.join(map(str,api)),'memory':types['watchFace'],'parts':len(c['partNumbers']),'color':color,'display':c['displayType'],'profile':key,'geometry':g})
    for demo,manifest,jungle in ((False,'manifest.xml','monkey.jungle'),(True,'preview/manifest.xml','preview.jungle')):
        tree=ET.parse(ROOT/'manifest.xml');app=tree.getroot().find(f'{{{NS}}}application');app.set('minApiLevel','3.2.0');app.set('id','d2fd1f269ea4491f9bf5c77046e0e302' if demo else 'd2fd1f269ea4491f9bf5c77046e0e301')
        products=app.find(f'{{{NS}}}products');products.clear()
        for row in rows:ET.SubElement(products,f'{{{NS}}}product',id=row['id'])
        tree.write(ROOT/manifest,encoding='utf-8',xml_declaration=True)
        mode='preview' if demo else 'live'
        lines=[f'project.manifest = {manifest}','base.excludeAnnotations = diagnostic',f'base.sourcePath = source;{mode};generated/profiles/instinct3solar45mm','base.resourcePath = generated/semioctagon-176x176-mip-instinct3solar45mm-i62/resources','base.lang.zhs = resources-zhs']
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
