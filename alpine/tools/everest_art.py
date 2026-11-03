"""Clean full-bleed Everest illustration, rasterized for each native screen.
Original artwork; references and stylization boundary: assets/everest/SOURCES.md.
"""
from PIL import Image,ImageDraw

RIDGE=[(-.08,.72),(.04,.62),(.14,.51),(.20,.445),(.25,.395),(.33,.377),(.40,.35),(.455,.303),(.48,.26),(.505,.235),(.53,.26),(.55,.294),(.585,.322),(.61,.35),(.65,.397),(.70,.44),(.75,.48),(.82,.565),(.92,.63),(1.08,.72)]

def monochrome(width,height,weather=0):
    """Independent ink composition: large solid snow planes, no grayscale conversion."""
    im=Image.new('1',(width,height),0);d=ImageDraw.Draw(im)
    def points(ps):return [(round(x*width/176),round(y*height/176)) for x,y in ps]
    def polygon(ps,white=True):d.polygon(points(ps),fill=1 if white else 0)
    def ridge(ps):d.line(points(ps),fill=1,width=1)
    # A continuous backdrop with distant summits separated from the foreground.
    ridge([(0,78),(10,68),(18,71),(28,57),(40,70),(51,62),(66,77),(87,67),(109,73),(126,62),(144,77),(160,68),(176,78)])
    polygon([(18,71),(28,57),(37,68),(31,65),(28,62),(23,70)])
    polygon([(149,78),(160,68),(169,78),(162,75),(159,72)])
    # Taller, broader Everest: summit pyramid and broad western shoulder.
    silhouette=[(0,94),(19,82),(30,69),(43,55),(58,51),(68,45),(76,31),(83,27),(90,35),(98,41),(108,46),(116,56),(126,64),(143,77),(161,89),(176,96),(176,176),(0,176)]
    polygon(silhouette,False)
    polygon([(83,27),(74,40),(67,47),(59,51),(43,56),(28,73),(42,66),(48,61),(44,71),(60,63),(55,75),(70,65),(65,79),(78,63),(79,51),(84,43)])
    polygon([(83,27),(90,35),(98,41),(101,49),(109,57),(111,66),(123,81),(108,73),(99,60),(93,54),(91,63),(84,73),(88,57),(86,45)])
    polygon([(103,46),(112,52),(122,63),(139,77),(127,71),(119,69),(117,63),(111,59),(111,55)])
    # Weather changes the snow/rock planes without adding dense texture.
    if weather in (1,2):
        polygon([(70,49),(66,61),(59,72),(64,58)],False)
        polygon([(93,44),(96,54),(106,69),(100,65)],False)
    elif weather==3:
        polygon([(52,59),(66,52),(60,65),(42,78),(47,66)])
        polygon([(98,55),(113,66),(126,83),(113,77),(104,68)])
    elif weather==4:
        polygon([(0,71),(29,67),(57,72),(91,68),(122,73),(176,68),(176,79),(0,79)],False)
        ridge([(0,74),(28,71),(55,75),(80,72)])
    return im

def render(width,height,scene,mono=False,amoled=False,weather=0):
    if mono:return monochrome(width,height,weather)
    ss=4 if amoled else 1;W,H=width*ss,height*ss
    im=Image.new('RGB',(W,H));d=ImageDraw.Draw(im);night=scene in (4,9)
    def rgb(c):return ((c>>16)&255,(c>>8)&255,c&255)
    def xy(points):return [(round(x*W),round(y*H)) for x,y in points]
    def poly(points,c):d.polygon(xy(points),fill=rgb(c))
    def line(points,c,w=1):d.line(xy(points),fill=rgb(c),width=max(1,round(w*ss*width/260)),joint='curve')
    if night:top,bottom=0x07172F,0x32738B;snow,ice,shade,rock=0xE6F3EF,0x9ECAD9,0x28536D,0x102B43
    elif scene==1:top,bottom=0x6C6496,0xEAC7BC;snow,ice,shade,rock=0xFFF2DC,0xCBCDDD,0x626881,0x263B55
    elif scene in (3,6):top,bottom=0x805E78,0xE9B27E;snow,ice,shade,rock=0xFFF1D6,0xD7C2B6,0x70627A,0x28374E
    elif scene in (5,7):top,bottom=0x284858,0x98B8BF;snow,ice,shade,rock=0xE2E9E2,0xA5C4CE,0x506C7D,0x263E51
    else:top,bottom=0x287D9E,0xAFDDE0;snow,ice,shade,rock=0xFAFFF4,0xABD3DE,0x346783,0x163D58
    def tint(c,target,amount):
        a=rgb(c);b=rgb(target);v=[round(x*(1-amount)+y*amount) for x,y in zip(a,b)]
        return (v[0]<<16)|(v[1]<<8)|v[2]
    if weather:
        target=(0x354C60 if night else 0x768D96)
        if weather==2:target=0x223B50 if night else 0x486574
        if weather==3:target=0x567589 if night else 0xB4D0D7
        if weather==4:target=0x4E6375 if night else 0xACBCBF
        amount=0.65 if weather==4 else 0.45
        top=tint(top,target,amount);bottom=tint(bottom,target,amount)
        shade=tint(shade,target,amount);rock=tint(rock,target,amount*.7);ice=tint(ice,target,amount)
        if weather==4:snow=tint(snow,target,.38)
    for y in range(H):
        k=min(1,y/(H*.62));a=rgb(top);b=rgb(bottom)
        color=tuple(round(v*(1-k)+z*k) for v,z in zip(a,b))
        if mono:color=(0,0,0) if night else (255,255,255)
        d.line((0,y,W,y),fill=color)
    # Distant silhouettes, softened on colour screens and clean contours on MIP.
    far=[(-.1,.64),(.04,.43),(.10,.47),(.165,.37),(.23,.46),(.30,.41),(.39,.50),(.50,.43),(.59,.47),(.69,.37),(.74,.42),(.82,.35),(.89,.44),(1.1,.49),(1.1,1),(-.1,1)]
    poly(far,0 if mono else (0x23445E if night else 0x7DAAB8))
    if mono:line(far[:14],0xFFFFFF if night else 0,1)
    for x,y in [(.165,.37),(.69,.37),(.82,.35)]:
        poly([(x-.026,y+.040),(x,y),(x+.032,y+.045),(x+.01,y+.03),(x-.002,y+.022)],0xFFFFFF if mono else (0x7599AC if night else 0xD2E3E1))
    # Everest's summit pyramid and broad western shoulder, extended to the screen edge.
    poly(RIDGE+[(1.1,1.1),(-.1,1.1)],0 if mono else rock)
    poly([(.505,.235),(.53,.26),(.55,.294),(.585,.322),(.61,.35),(.65,.397),(.70,.44),(.75,.48),(.82,.565),(.92,.63),(1.08,.72),(1.08,1),(.68,1),(.62,.65),(.58,.49),(.55,.37)],0 if mono else shade)
    bright=0xFFFFFF if mono else snow;cool=0xFFFFFF if mono else ice
    # Few large, deliberate snow planes retain a strong silhouette at 176 pixels.
    poly([(.505,.235),(.53,.263),(.545,.29),(.573,.315),(.536,.301),(.516,.282),(.49,.30),(.464,.329),(.48,.274)],bright)
    poly([(.46,.31),(.405,.357),(.33,.384),(.25,.404),(.20,.459),(.264,.43),(.298,.434),(.276,.479),(.35,.438),(.375,.42),(.356,.482),(.422,.427),(.416,.469),(.452,.419),(.473,.365)],bright)
    poly([(.495,.302),(.515,.303),(.53,.342),(.56,.38),(.559,.42),(.614,.509),(.548,.456),(.518,.404),(.488,.44),(.446,.511),(.458,.448),(.486,.367)],bright)
    poly([(.58,.334),(.612,.36),(.646,.408),(.676,.435),(.638,.418),(.62,.388),(.594,.381)],cool)
    poly([(.70,.468),(.73,.489),(.768,.533),(.806,.582),(.766,.557),(.744,.531),(.716,.517)],cool)
    if weather==3:
        poly([(.29,.44),(.37,.403),(.35,.46),(.26,.525),(.275,.47)],bright)
        poly([(.55,.411),(.61,.48),(.67,.57),(.60,.532),(.565,.47)],bright)
    # A thin, single ridge separates the two main snow faces without hairline scratches.
    if not mono:line([(.505,.249),(.502,.284),(.514,.322),(.52,.344)],0xFFFFFF,1)
    # Foreground glacier valley and rock walls continue behind the clock/data.
    glacier=[(.62,.56),(.67,.58),(.70,.68),(.61,.79),(.58,.88),(.71,1.06),(.43,1.06),(.52,.86),(.56,.74)]
    poly(glacier,0 if mono else (0x15364D if night else 0x305D73))
    left=[(-.1,.57),(.03,.55),(.16,.65),(.28,.73),(.40,.85),(.46,1.1),(-.1,1.1)]
    right=[(1.1,.59),(.96,.61),(.88,.70),(.78,.80),(.68,.91),(.68,1.1),(1.1,1.1)]
    poly(left,0 if mono else 0x0A2337);poly(right,0 if mono else 0x102D42)
    # Sparse contour accents at the edges, not a texture carpet under the numerals.
    if mono:
        line([(.0,.58),(.07,.63),(.13,.71)],0xFFFFFF,1)
        line([(1,.63),(.95,.67),(.9,.74)],0xFFFFFF,1)
    else:
        line([(.0,.58),(.11,.68),(.23,.83),(.28,1)],0x1B3D53,1.5)
        line([(1,.64),(.90,.75),(.81,.87),(.76,1)],0x285069,1.4)
        line([(.64,.68),(.59,.79),(.55,.88),(.59,1)],0x426E80,1.2)
        line([(.66,.7),(.62,.80),(.59,.87)],0x21495F,1)
    # Gentle darkness for text contrast, preserving the full-bleed foreground.
    if not mono:
        layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer)
        for y in range(H):
            k=max(0,min(1,(y/H-.46)/.48));alpha=round(115*k*k*(3-2*k))
            ld.line((0,y,W,y),fill=(0,5,13,alpha))
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    if ss!=1:im=im.resize((width,height),Image.Resampling.LANCZOS)
    if mono:return im.convert('1',dither=Image.Dither.NONE)
    if not amoled:
        palette=Image.new('P',(1,1))
        palette.putpalette([0,0,0,85,85,85,170,170,170,255,255,255,85,170,170]+[0,0,0]*251)
        return im.quantize(palette=palette,dither=Image.Dither.NONE)
    return im


def skyline(width,height,mono):
    if mono:
        main=[(0,94),(19,82),(30,69),(43,55),(58,51),(68,45),(76,31),(83,27),(90,35),(98,41),(108,46),(116,56),(126,64),(143,77),(161,89),(176,96)]
        far=[(0,78),(10,68),(18,71),(28,57),(40,70),(51,62),(66,77),(87,67),(109,73),(126,62),(144,77),(160,68),(176,78)]
        main=[(x/176,y/176) for x,y in main];far=[(x/176,y/176) for x,y in far]
    else:
        main=RIDGE
        far=[(-.1,.64),(.04,.43),(.10,.47),(.165,.37),(.23,.46),(.30,.41),(.39,.50),(.50,.43),(.59,.47),(.69,.37),(.74,.42),(.82,.35),(.89,.44),(1.1,.49)]
    def edge(profile,x):
        for (x0,y0),(x1,y1) in zip(profile,profile[1:]):
            if x0<=x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
        return 1
    return [round(min(edge(main,x/width),edge(far,x/width))*height) for x in range(width)]


def generate_resources(folder,width,height,mono,amoled):
    from pathlib import Path
    import hashlib
    folder.mkdir(exist_ok=True)
    digest=hashlib.sha256(Path(__file__).read_bytes()+str((width,height,mono,amoled)).encode()).hexdigest()
    cache=folder/'sky-art.sha256'
    if cache.exists() and cache.read_text()==digest and all((folder/f'sky-{i}.png').exists() for i in range(1,21)) and (folder/'sky-front.png').exists():return
    for light in range(1,5):
        for weather in range(5):
            key=(light-1)*5+weather+1
            render(width,height,light,mono,amoled,weather).save(folder/f'sky-{key}.png')
    # Only the top 48 logical pixels can overlap cloud primitives on Instinct.
    # A 2-bit transparent foreground mask is much smaller than a full-frame overlay.
    if mono:
        foreground=monochrome(width,height).convert('RGBA');edge=skyline(width,height,True)
        height_top=round(48*height/176);foreground=foreground.crop((0,0,width,height_top));alpha=Image.new('L',foreground.size,0)
        ap=alpha.load()
        for x in range(width):
            for y in range(max(0,edge[x]),height_top):ap[x,y]=255
        foreground.putalpha(alpha)
    else:foreground=Image.new('RGBA',(1,1),(0,0,0,0))
    foreground.save(folder/'sky-front.png')
    cache.write_text(digest)
