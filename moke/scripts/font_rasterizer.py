"""Native-size, grid-fitted Moke Soft digits and licensed Noto text glyphs.

The published advances/line boxes are frozen separately from glyph outlines.
Never enlarge a 1-bit font atlas: rasterize these outlines at the target size.
"""
from functools import lru_cache
from pathlib import Path
import json
import math
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
METRICS = json.loads((ROOT / 'assets/fonts/layout-metrics.json').read_text())
NOTO = ROOT / 'assets/fonts/NotoSansCJKsc-Regular.otf'
REFERENCE_MEDIUM = ROOT / 'assets/fonts/Rajdhani-Medium.ttf'
REFERENCE_SEMIBOLD = ROOT / 'assets/fonts/Rajdhani-SemiBold.ttf'


def reference_digit(char, width, height, weight=0, small=False, clock=False):
    """Rasterize the reference-style narrow, softly squared numeral outlines."""
    if char=='4' and not small:
        # The reference uses an upright open four, rather than a long diagonal.
        return digit(char,width,height,weight,small,clock)
    # Small labels already have one-pixel stems; retain their proven hinting.
    ss=4 if small or clock else 8
    path=REFERENCE_SEMIBOLD if weight==1 or clock else REFERENCE_MEDIUM
    font=ImageFont.truetype(str(path), max(16, round(height/.65))*ss)
    box=font.getbbox(char)
    source=Image.new('L',(max(1,box[2]-box[0]),max(1,box[3]-box[1])))
    ImageDraw.Draw(source).text((-box[0],-box[1]),char,font=font,fill=255)
    source=source.crop(source.getbbox())
    resample=Image.Resampling.LANCZOS if small or clock else Image.Resampling.BOX
    return source.resize((width,height),resample).point(lambda p:255 if p>=128 else 0)


def rounded_line(draw, points, radius, width):
    """Round joins in outline space, keeping the long stems pixel-aligned."""
    result = [points[0]]
    for i in range(1, len(points) - 1):
        a, b, c = points[i-1:i+2]
        ab, bc = math.dist(a, b), math.dist(b, c)
        if not ab or not bc:
            continue
        r = min(radius, ab / 2, bc / 2)
        start = tuple(b[j] + (a[j] - b[j]) * r / ab for j in (0, 1))
        end = tuple(b[j] + (c[j] - b[j]) * r / bc for j in (0, 1))
        result.append(start)
        for step in range(1, 13):
            t = step / 12
            result.append(tuple((1-t)**2*start[j] + 2*(1-t)*t*b[j] + t*t*end[j] for j in (0, 1)))
    result.append(points[-1])
    draw.line(result, fill=255, width=width, joint='curve')
    # Small terminal rounding; never soften a complete stem into gray pixels.
    r = max(0, width / 2 - .5)
    for x, y in (points[0], points[-1]):
        draw.ellipse((x-r, y-r, x+r, y+r), fill=255)


def digit(char, width, height, weight=0, small=False, clock=False):
    """Continuous rounded instrument numerals, without segment gaps."""
    if width < 4 or height < 7:
        # Extremely small secondary regions use a hinted 3 x 5 master.
        rows = TINY[char]
        im = Image.new('L', (width, height))
        for y in range(height):
            for x in range(width):
                if rows[min(4, y*5//height)][min(2, x*3//width)] == '1':
                    im.putpixel((x, y), 255)
        return im
    # Supersampling is used only before the FINAL 1-bit conversion at native size.
    ss = 8
    im = Image.new('L', (width*ss, height*ss))
    d = ImageDraw.Draw(im)
    stroke = max(1, round(height * (.13 if weight == 1 else (.105 if clock else .09))))
    if small:
        stroke = max(1, round(height * (.15 if weight == 1 else .095)))
    stroke = min(stroke, max(1, (width-1)//3))
    half = (stroke-1)/2
    l, r, t, b = half, width-1-half, half, height-1-half
    m = round((height-stroke)/2)+half
    radius = max(1, round(min(width*.22, height*.095)))
    paths = {
        '2': [[(l, t+radius), (l, t), (r, t), (r, m), (l, m), (l, b), (r, b)]],
        '3': [[(l, t), (r, t), (r, b), (l, b)], [(l+(r-l)*.12, m), (r, m)]],
        '4': [[(l, t), (l, m), (r, m)], [(r, t), (r, b)]],
        '5': [[(r, t), (l, t), (l, m), (r, m), (r, b), (l, b)]],
        '6': [[(r, t), (l, t), (l, b), (r, b), (r, m), (l, m)]],
        '7': [[(l, t), (r, t), (l+(r-l)*.32, b)]],
        '9': [[(r, m), (l, m), (l, t), (r, t), (r, b), (l, b)]],
        '1': [[(l, t+(b-t)*.13), (l+(r-l)*.62, t), (l+(r-l)*.62, b)]],
    }
    def rect(box, rad, fill):
        d.rounded_rectangle(tuple(round(v*ss) for v in box), radius=rad*ss, fill=fill)
    if char in '08':
        rect((0, 0, width-1/ss, height-1/ss), radius+half, 255)
        if char == '0':
            rect((stroke, stroke, width-stroke-1/ss, height-stroke-1/ss), max(1, radius-half), 0)
        else:
            mid = round(height/2)
            rect((stroke, stroke, width-stroke-1/ss, mid-(stroke+1)//2-1/ss), max(1, radius-half), 0)
            rect((stroke, mid+stroke//2, width-stroke-1/ss, height-stroke-1/ss), max(1, radius-half), 0)
    else:
        for path in paths[char]:
            # Pixel centers, rather than integer corners, give symmetric stems.
            points = [((x+.5)*ss, (y+.5)*ss) for x, y in path]
            rounded_line(d, points, radius*ss, stroke*ss)
    resample=Image.Resampling.LANCZOS if clock else Image.Resampling.BOX
    return im.resize((width, height), resample).point(lambda p: 255 if p >= 128 else 0)


@lru_cache(maxsize=128)
def noto(size):
    return ImageFont.truetype(str(NOTO), max(1, size))


def text_glyph(char, width, height, size, bold=False):
    """Fit the source outline, never squeeze the raster to a new aspect ratio."""
    stroke = 1 if bold and height >= 12 else 0
    while True:
        font = noto(size)
        box = font.getbbox(char, stroke_width=stroke)
        source = Image.new('L', (max(1, box[2]-box[0]), max(1, box[3]-box[1])))
        draw = ImageDraw.Draw(source)
        draw.fontmode = '1'
        draw.text((-box[0], -box[1]), char, font=font,
                  fill=255, stroke_width=stroke, stroke_fill=255)
        ink = source.getbbox()
        if ink is None:
            return Image.new('L', (width, height))
        source = source.crop(ink)
        if (source.width <= width and source.height <= height) or size <= 1:
            break
        size -= 1
    im = Image.new('L', (width, height))
    im.paste(source, ((width-source.width)//2, (height-source.height)//2))
    return im.point(lambda p: 255 if p >= 112 else 0)


def render_font(name, dest, scale=1.0):
    """Preserve per-device advance/clip geometry and rasterize at native pixels."""
    spec = METRICS[name]
    header = list(spec['header'])
    number = lambda v: round(v*scale)
    dims = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', header[1])}
    atlas = Image.new('RGBA', (max(1, number(dims['scaleW'])), max(1, number(dims['scaleH']))), (255, 255, 255, 0))
    source_size = int(re.search(r'\bsize=(\d+)', header[0])[1])
    family = re.search(r'f(\d)s', name)
    weight = int(family[1]) if family else 0
    small = name.startswith(('data', 'compact', 'date', 'days'))
    entries = []
    zero = next((e for e in spec['chars'] if e['id'] == 48), None)
    for original in spec['chars']:
        e = {k: v for k, v in original.items() if k != 'ink'}
        for key in ('x', 'y', 'xoffset', 'yoffset', 'xadvance'):
            e[key] = number(original[key])
        e['width'] = max(1, number(original['x']+original['width'])-e['x'])
        e['height'] = max(1, number(original['y']+original['height'])-e['y'])
        tile = Image.new('L', (e['width'], e['height']))
        char = chr(e['id'])
        ink = original['ink']
        if ink is None and not char.isspace():
            # Some old tiny unit glyphs were already blank. Restore them using
            # the available line box instead of propagating missing characters.
            ink = (1, 1, max(2, original['width']-1), max(2, original['height']-1))
        if ink:
            bounds = ink
            if char in '0123456789' and zero and name != 'chart':
                bounds = zero['ink']
            if char in ':.' and zero and not small:
                bounds = (ink[0], zero['ink'][1], ink[2], zero['ink'][3])
            if ord(char) >= 0x4e00:
                # Chinese uses its full em box; old per-glyph squeezing could
                # reduce e.g. 午 to half height and make it unreadable.
                bounds = (1, 1, original['width']-1, original['height']-2)
                if small and zero and source_size>=12:
                    # Match Chinese units/weekday labels to the numeral cap
                    # height; the old full-em 天 was three pixels taller.
                    cap=min(original['height']-2,zero['ink'][3]-zero['ink'][1]+1)
                    cw=min(original['width']-2,cap)
                    bx=(original['width']-cw)//2;by=(original['height']-cap)//2
                    bounds=(bx,by,bx+cw,by+cap)
            if small and zero and char==':':
                bounds=(ink[0],zero['ink'][1],ink[2],zero['ink'][3])
            if small and source_size>=12 and char=='/' and ink[3]-ink[1]>=9:
                bounds=(ink[0],ink[1]+1,ink[2],ink[3]-1)
            left, top, right, bottom = map(number, bounds)
            # Published one has an intentional left inset shared with the step icon.
            if char == '1' and name.startswith('time'):
                left = max(left, number(original['ink'][0]))
            right = min(right, e['width'])
            bottom = min(bottom, e['height'])
            w, h = max(1, right-left), max(1, bottom-top)
            if name == 'chart':
                # Tiny plot labels retain their hand-hinted 4 x 7 design.
                rows = CHART[char]
                raw = Image.new('L', (4, 7))
                for y, row in enumerate(rows):
                    for x, pixel in enumerate(row):
                        if pixel == '1': raw.putpixel((x, y), 255)
                glyph = raw.resize((w, h), Image.Resampling.NEAREST)
            elif char in '0123456789':
                if char=='1':
                    # Preserve a natural narrow one, rather than stretching it
                    # across the full tabular advance of the other numerals.
                    right=min(right,number(original['ink'][2]))
                    w=max(1,right-left)
                glyph = reference_digit(char, w, h, weight, small,name.startswith('time'))
                if glyph.getbbox() is None:
                    glyph = digit(char,w,h,weight,True,False)
            elif char in ':.':
                glyph = Image.new('L', (w, h))
                draw = ImageDraw.Draw(glyph)
                dot = max(1, min(w, round(h*.10))) if not small else min(w, max(1, round(scale)))
                # Colon dots sit on the optical thirds, rather than on the baseline.
                for cy in ([round(h*.3), round(h*.7)] if char == ':' else [h-dot]):
                    x = (w-dot)//2
                    box = (x, min(h-1, cy), x+dot-1, min(h-1, cy+dot-1))
                    if dot < 3: draw.rectangle(box, fill=255)
                    else: draw.rounded_rectangle(box, radius=dot//4, fill=255)
            elif char == '-':
                glyph = Image.new('L', (w, h), 255)
            elif char == '°':
                glyph = Image.new('L', (w, h))
                ImageDraw.Draw(glyph).ellipse((0, 0, w-1, min(w, h)-1), outline=255,
                                             width=max(1, round(scale)))
            else:
                glyph = text_glyph(char, w, h, number(source_size), weight == 1 and small)
                if char == 'F' and glyph.getbbox() is None:
                    # The narrowest Fahrenheit unit is two pixels wide. A
                    # native stencil keeps it legible when Noto drops its stem.
                    draw = ImageDraw.Draw(glyph)
                    draw.line((0, 0, 0, h-1), fill=255)
                    draw.line((0, 0, w-1, 0), fill=255)
                    draw.line((0, h//2, w-1, h//2), fill=255)
            tile.paste(glyph, (left, top))
        rgba = Image.new('RGBA', tile.size, (255, 255, 255, 0))
        rgba.putalpha(tile)
        atlas.paste(rgba, (e['x'], e['y']))
        entries.append('char '+' '.join(f'{k}={v}' for k, v in e.items()))
    header[0] = re.sub(r'face="[^"]+"', f'face="Moke Reference {name}"', header[0])
    for i, line in enumerate(header):
        for key in ('size', 'lineHeight', 'base', 'scaleW', 'scaleH'):
            line = re.sub(r'\b'+key+r'=(-?\d+)', lambda m: key+'='+str(number(int(m[1]))), line)
        header[i] = line
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    atlas.save(dest / (name+'.png'))
    (dest / (name+'.fnt')).write_text('\n'.join(header+entries)+'\n')


CHART = {
    '0': ['0110','1001','1001','1001','1001','1001','0110'],
    '1': ['0010','0110','0010','0010','0010','0010','0111'],
    '2': ['0110','1001','0001','0010','0100','1000','1111'],
    '3': ['1110','0001','0001','0110','0001','0001','1110'],
    '4': ['0010','0110','1010','1010','1111','0010','0010'],
    '5': ['1111','1000','1000','1110','0001','0001','1110'],
    '6': ['0110','1000','1000','1110','1001','1001','0110'],
    '7': ['1111','0001','0010','0010','0100','0100','0100'],
    '8': ['0110','1001','1001','0110','1001','1001','0110'],
    '9': ['0110','1001','1001','0111','0001','0001','0110'],
    '-': ['0000','0000','0000','1111','0000','0000','0000'],
}

TINY = dict(zip('0123456789', [
    ['111','101','101','101','111'], ['010','110','010','010','111'],
    ['110','001','010','100','111'], ['110','001','010','001','110'],
    ['101','101','111','001','001'], ['111','100','110','001','110'],
    ['011','100','111','101','111'], ['111','001','010','010','010'],
    ['111','101','111','101','111'], ['111','101','111','001','110'],
]))
