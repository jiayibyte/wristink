"""Build each font at its target pixel dimensions from stroke and dot masters."""
from functools import lru_cache
from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "moke/scripts"))
from pixel_glyphs import DOTS, SEGMENTS, digit, latin

DIGITS = "0123456789"
TIME = DIGITS + ":"
VALUE_GLYPHS = DIGITS + "-.%KCFMITd"
# Compact uppercase for labels and dates, constructed on a 5x7 grid.
CAPS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", (
    "0e11111f111111", "1e11111e11111e", "0f10101010100f", "1e11111111111e",
    "1f10101e10101f", "1f10101e101010", "0f10101711110f", "1111111f111111",
    "0e04040404040e", "0702020202120c", "11121418141211", "1010101010101f",
    "111b1515111111", "11191915131311", "0e11111111110e", "1e11111e101010",
    "0e11111115120d", "1e11111e141211", "0f10100e01011e", "1f040404040404",
    "1111111111110e", "11111111110a04", "11111115151b11", "11110a040a1111",
    "1111110a040404", "1f01020408101f",
)))
# Data glyphs follow the public Garmin manual symbols recorded in README.
# Shapes are rebuilt on the target pixel grid so narrow counters stay open.
ICONS = dict(zip("abcdefghijklmnopqrs", (
    "00000/00000/00000/00000/00000/00000/00000",
    "01100110/11111111/11111111/01111110/00111100/00011000",
    "111111110/100000010/101110011/101110011/100000010/111111110",
    "000110000110/001111001111/001111001111/011110011110/011100011100/000000000000/110000110000/111000111000/110000110000",
    "000001000/001111000/011111000/011111100/111111110/111001111/110100111/110000011/010000010",
    "00000110/00000101/01110111/11010010/10010000/11110100/01110110/01100110/00001100",
    "001100/001010/001010/001010/001010/010011/010111/001110",
    "00111100/01111110/11111111/11111111/11111111/11111111/01111110/00111100/00100000",
    "000100000/001010000/001011000/010100100/010111100/100001010/100000001/111111111",
    "0001101111/0001101111/0010001100/0101111100/1001100000/1111100000/1111100000/1100000000/1000000000",
    "0011100/0001000/0011100/0100010/1001001/1001101/1000001/0100010/0011100",
    "0001000/0011100/0110110/0100010/0100010/1111111/0001000",
    "00101010/10101010/10101001/10101010/00101010",
    "0001001/0011010/1110100/1101100/1011000/0101000/1001000",
    "0011100/0110000/1100000/1100000/1100001/0110011/0011110",
    "11111110/10000010/10100011/10100011/10000010/11111110",
    "0011111/0010010/1010100/1011101/1010011/0100100/1001100",
    "1001110/0101010/0011000/0010100/0001100/0101010/0111001",
    "0001000/0011000/0110000/0111110/0001100/0011000/0010000",
)))


def pixels(rows, w, h, gutter=0, rounded=False):
    """Draw directly into target cells with discrete, symmetric spacing."""
    im = Image.new("L", (w, h))
    draw = ImageDraw.Draw(im)
    for y, row in enumerate(rows):
        for x, bit in enumerate(row):
            if bit == "1":
                x0, x1 = round(x*w/len(row)), round((x+1)*w/len(row))-1
                y0, y1 = round(y*h/len(rows)), round((y+1)*h/len(rows))-1
                box = (x0, y0, max(x0, x1-gutter), max(y0, y1-gutter))
                if rounded:
                    draw.rounded_rectangle(box, radius=min((box[2]-x0)//3, (box[3]-y0)//3), fill=255)
                else:
                    draw.rectangle(box, fill=255)
    return im


def clock_mark(w, h, radius):
    im = Image.new("L", (w, h))
    draw = ImageDraw.Draw(im)
    for y in [h*3//10, h*7//10]:
        draw.rounded_rectangle((0, y-w//2, w-1, y+(w-1)//2), radius=radius, fill=255)
    return im


def segments(char, width, height, scale, thin=False, slanted=False):
    """Construct beveled segments directly on the selected raster grid."""
    im = Image.new("L", (width,height))
    draw = ImageDraw.Draw(im)
    lean = round(height*.093) if slanted else 0
    w = width-lean
    h = height
    stroke = max(scale, round(h*(.062 if thin else .114)))
    gap = max(scale, round(h*.023))
    cut = stroke//2
    middle = (h-stroke)//2

    def draw_segment(points):
        draw.polygon([(x + round(lean*(h-1-y)/(h-1)), y) for x,y in points],fill=255)

    for key in SEGMENTS[char]:
        if key in "agd":
            x0, x1 = cut+gap, w-1-cut-gap
            y = {"a": 0, "g": middle, "d": h-stroke}[key]
            draw_segment([(x0,y+cut), (x0+cut,y), (x1-cut,y), (x1,y+cut),
                          (x1-cut,y+stroke-1), (x0+cut,y+stroke-1)])
        else:
            x = w-stroke if key in "bc" else 0
            if char == "1" and slanted:
                x = (w-stroke)//2
            y0, y1 = ((cut+gap, middle+cut-gap) if key in "bf"
                      else (middle+cut+gap, h-1-cut-gap))
            draw_segment([(x+cut,y0), (x+stroke-1,y0+cut), (x+stroke-1,y1-cut),
                          (x+cut,y1), (x,y1-cut), (x,y0+cut)])
    return im


def mip_segments(char, width, height):
    """Upright integer stems and mirrored one-pixel bevels for MIP."""
    im = Image.new("L",(width,height))
    draw = ImageDraw.Draw(im)
    stroke = min(max(2,round(height*.124)),(width-3)//2)
    middle = (height-stroke)//2

    def bar(left,top,right,bottom):
        if min(right-left,bottom-top) < 2:
            draw.rectangle((left,top,right,bottom),fill=255)
            return
        draw.polygon([(left+1,top),(right-1,top),(right,top+1),
                      (right,bottom-1),(right-1,bottom),(left+1,bottom),
                      (left,bottom-1),(left,top+1)],fill=255)

    for key in SEGMENTS[char]:
        if key in "agd":
            y = {"a":0,"g":middle,"d":height-stroke}[key]
            bar(stroke,y,width-stroke-1,y+stroke-1)
        else:
            x = width-stroke if key in "bc" else 0
            if char == "1":
                x = (width-stroke)//2
            y0,y1 = ((stroke,middle-1) if key in "bf"
                     else (middle+stroke,height-stroke-1))
            bar(x,y0,x+stroke-1,y1)
    return im


def contour(char, w, h, scale):
    im = Image.new("L", (w, h))
    draw = ImageDraw.Draw(im)
    stroke = max(2*scale, round(h*.126))
    middle = (h-stroke)//2
    radius = max(1,round(stroke*.54))
    if char == "1":
        x = (w-stroke)//2
        draw.rounded_rectangle((x,0,x+stroke-1,h-1),radius,fill=255)
        draw.polygon([(x+stroke//2,0),(x+stroke//2,stroke),(x-stroke//2,stroke*2),
                      (x-stroke,stroke*3//2)],fill=255)
        return im
    for key in SEGMENTS[char]:
        if key in "agd":
            y0 = {"a": 0, "g": middle, "d": h-stroke}[key]
            draw.rounded_rectangle((0,y0,w-1,y0+stroke-1),radius,fill=255)
        else:
            x0 = w-stroke if key in "bc" else 0
            y0, y1 = (0, middle+stroke-1) if key in "bf" else (middle,h-1)
            draw.rounded_rectangle((x0,y0,x0+stroke-1,y1),radius,fill=255)
    return im


@lru_cache(maxsize=64)
def clock_fonts(size, aa):
    height = round(size*.176)
    width = round(size*.113)
    dot = max(3, round(height*.11))
    margin = max(2, round(size*.012))
    scale = 4 if aa else 1
    result = {}
    for label in ("Segment", "Contour", "Matrix"):
        items = {}
        for c in TIME:
            w = dot if c == ":" else width
            if c == ":":
                im = clock_mark(w*scale, height*scale, w*scale//4)
            elif label == "Segment":
                im = segments(c,w*scale,height*scale,scale,slanted=True) if aa else mip_segments(c,w,height)
            elif label == "Matrix":
                im = pixels(DOTS[c], w*scale, height*scale, scale*max(1, round(size*.006)), aa)
            else:
                # Grid-native continuous contours. Refine only their rounded
                # joints on displays with alpha support; never resize a 1-bit atlas.
                im = contour(c, w*scale, height*scale, scale)
            if aa:
                im = im.resize((w, height), Image.Resampling.BOX)
            items[c] = im, w+margin
        result[label] = items
    return result


def letter(c, h):
    if c == "'":
        im = Image.new("L",(max(2,h//4),h))
        ImageDraw.Draw(im).rectangle((im.width//2,0,im.width-1,max(1,h//4)),fill=255)
        return im
    if c in CAPS:
        rows = [f"{int(CAPS[c][i:i+2], 16):05b}" for i in range(0,14,2)]
        return pixels(rows, round(h*.76), h)
    if c == " ":
        return Image.new("L", (max(2, h//2), h))
    return latin(c, max(2, round(h*.64)), h, max(1, round(h*.135))) if c not in DIGITS else digit(c, max(3, round(h*.59)), h)


def data_heights(size):
    return {
        "Label": max(7, round(size*.031)), "Date": max(12, round(size*.077)),
        "Seconds": max(16, round(size*.114)), "Value": max(10, round(size*.057)),
        "Symbol": max(8, round(size*.041)),
    }


def native_segments(c, w, h, aa):
    if not aa:
        return mip_segments(c,w,h)
    return segments(c,w*4,h*4,4,slanted=True).resize((w,h),Image.Resampling.BOX)


def date_glyph(c, height, aa, compact):
    if c in DIGITS:
        width = max(7,round(height*.58)) if compact else max(8,round(height*.65))
        if not aa:
            return digit(c,width,height,stroke=2,style="square")
        return native_segments(c,width,height,aa)
    if c in CAPS:
        rows = [f"{int(CAPS[c][i:i+2],16):05b}" for i in range(0,14,2)]
        gutter = max(1,round(height*.048)) if aa else 0
        return pixels(rows,round(height*.79),height,gutter)
    return letter(c,height)


def symbol_glyph(c, height):
    rows = ICONS[c].split("/")
    im = pixels(rows,round(height*len(rows[0])/len(rows)),height)
    left,top,right,bottom = im.getbbox()
    result = Image.new("L",(right-left,height))
    result.paste(im.crop((left,top,right,bottom)),(0,(height-(bottom-top))//2))
    return result


def value_glyph(c, height):
    if c == "d":
        unit_height = max(6,round(height*.64))
        rows = ["0001","0001","0111","1001","1001","1001","0111"]
        unit = pixels(rows,max(4,round(unit_height*4/7)),unit_height)
        glyph = Image.new("L",(unit.width,height))
        glyph.paste(unit,(0,height-unit_height))
        return glyph
    return digit(c,max(4,round(height*.54)),height) if c in DIGITS else letter(c,height)


def window_heights(radius):
    return {"WindowValue":max(12,round(radius*.58)), "WindowSymbol":max(8,round(radius*.36))}


def window_fonts(radius):
    result = {}
    for name,height in window_heights(radius).items():
        chars,builder = (VALUE_GLYPHS,value_glyph) if name=="WindowValue" else ("bcdefghijk",symbol_glyph)
        result[name] = {}
        for c in chars:
            im = builder(c,height)
            result[name][c] = im,im.width+max(1,round(height*.105))
    return result


def data_fonts(size, aa):
    result = {}
    subsets = {
        "Label": DIGITS+"ABCDEFGHIJKLMNOPQRSTUVWXYZ -./%'",
        "Date": DIGITS+"ABCDEFGHIJKLMNOPQRSTUVWXYZ -/'",
        "Seconds": DIGITS,
        "Value": VALUE_GLYPHS,
        "Symbol": "bcdefghijklmnopqrs",
    }
    for name, height in data_heights(size).items():
        items = {}
        for c in subsets[name]:
            if name == "Symbol":
                im = symbol_glyph(c,height)
            elif name == "Seconds":
                im = native_segments(c,round(height*.63),height,aa)
            elif name == "Date":
                im = date_glyph(c,height,aa,size < 150)
            elif name == "Value":
                im = value_glyph(c,height)
            else:
                im = letter(c,height)
            items[c] = im, im.width + max(1,round(height*.105))
        result[name] = items
    return result


def aod_font(size):
    h, w = round(size*.089), round(size*.061)
    s = max(2, round(h*.085))
    items = {c: (segments(c,w,h,1,True), w+max(3,w//6)) for c in DIGITS}
    items[":"] = (clock_mark(s,h,0), s+max(3,w//6))
    return items


def write_atlas(path, glyphs):
    """BMFont atlas with one transparent guard pixel between ink boxes."""
    height = max(im.height for im, _ in glyphs.values())
    row_width = 480
    x = y = 0
    cells = []
    for c, (im, advance) in glyphs.items():
        if x + im.width > row_width:
            x, y = 0, y + height + 1
        cells.append((c, im, advance, x, y))
        x += im.width + 1
    width = max(x+im.width for _,im,_,x,_ in cells)
    atlas = Image.new("RGBA", (width, y+height))
    records = []
    for c, im, advance, x, y in cells:
        assert im.width < advance
        ink = Image.new("RGBA", im.size, (255,255,255,255))
        ink.putalpha(im)
        atlas.paste(ink, (x,y))
        records.append(f"char id={ord(c)} x={x} y={y} width={im.width} height={im.height} "
                       f"xoffset=0 yoffset=0 xadvance={advance} page=0 chnl=0")
    atlas.save(path.with_suffix(".png"))
    path.with_suffix(".fnt").write_text(
        f'info face="{path.stem}" size={height}\n'
        f'common lineHeight={height} base={height} scaleW={width} scaleH={atlas.height} pages=1 packed=0\n'
        f'page id=0 file="{path.stem}.png"\nchars count={len(records)}\n'+"\n".join(records)+"\n")
