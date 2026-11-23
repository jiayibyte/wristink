"""Build each font at its target pixel dimensions from stroke and dot masters.

Every glyph is constructed on the target grid: integer strokes, stems on whole
pixels, symmetric rounded joins and even stairs. Grayscale screens run the same
construction at four times the size and area-sample it down, so their edges
are smooth instead of enlarged pixel steps. Nothing is scaled by a non-integer
factor after it has been rasterized.
"""
from functools import lru_cache
from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "moke/scripts"))
from pixel_glyphs import DOTS, SEGMENTS, Grid, caps, digit, latin
import icons

DIGITS = "0123456789"
TIME = DIGITS + ":"
VALUE_GLYPHS = DIGITS + "-.%°KCFMITd"
# Only the characters the face can draw are packed into each atlas.
LABEL_GLYPHS = "01 ABCDEFGHIKLMNOPRSTUVW"     # gauge ends, P, status words, units
DATE_GLYPHS = DIGITS + "ADEFHIMNORSTUW -'"    # weekdays and numeric dates
SYMBOLS = "bcdefghijklmnopqrs"
SUPERSAMPLE = 4
# Compact uppercase for small labels and the dot-matrix weekday, on a 5x7 grid.
CAPS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", (
    "0e11111f111111", "1e11111e11111e", "0f10101010100f", "1e11111111111e",
    "1f10101e10101f", "1f10101e101010", "0f10101711110f", "1111111f111111",
    "0e04040404040e", "0702020202120c", "11121418141211", "1010101010101f",
    "111b1515111111", "11191915131311", "0e11111111110e", "1e11111e101010",
    "0e11111115120d", "1e11111e141211", "0f10100e01011e", "1f040404040404",
    "1111111111110e", "11111111110a04", "11111115151b11", "11110a040a1111",
    "1111110a040404", "1f01020408101f",
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


def caps_rows(c):
    return [f"{int(CAPS[c][i:i+2], 16):05b}" for i in range(0, 14, 2)]


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


# --- Small type --------------------------------------------------------------

def weight(height, aa):
    """Stroke width: whole-pixel bands on 1-bit screens, about 11.5% of the
    height on grayscale ones (quarter pixels survive the supersampling)."""
    if aa:
        return max(1.0, round(height*.115*4)/4)
    return 1 if height <= 8 else 2 if height <= 18 else round(height*.11)


def build(draw, width, height, stroke, aa):
    """Run a grid-native builder at 1x, or 4x then area-sample for grayscale."""
    if not aa:
        return draw(width, height, max(1, round(stroke)))
    k = SUPERSAMPLE
    return draw(width*k, height*k, max(1, round(stroke*k))).resize((width, height), Image.Resampling.BOX)


def figure_width(height, stroke, narrow=False):
    """Tabular digit box. Counters keep at least two clear pixels."""
    return max(2*round(stroke)+2, int(height*(.47 if narrow else .54)+.5))


def ring(grid, x, y, size, stroke):
    """Closed rounded box, symmetric on the grid."""
    a = (stroke-1)/2
    radius = max(0, (size-stroke)/2*.9)
    grid.stroke([(x+a, y+a), (x+size-1-a, y+a), (x+size-1-a, y+size-1-a), (x+a, y+size-1-a)],
                stroke, radius, closed=True)


def degree(width, height, stroke):
    g = Grid(width, height)
    ring(g, 0, 0, width, stroke)
    return g.image()


def percent(width, height, stroke):
    g = Grid(width, height)
    size = max(3, round(width*.5))
    line = max(1, round(stroke*.75))
    ring(g, 0, 0, size, line)
    ring(g, width-size, height-size, size, line)
    g.slant(width-line, 0, 0, height-1, line)
    return g.image()


def value_glyph(c, height, aa, narrow=False, stroke=None):
    """Numerals and the few units a value can carry, on one stroke weight."""
    s = stroke or weight(height, aa)
    w = figure_width(height, s, narrow)
    if c in DIGITS:
        return build(lambda W, H, S: digit(c, W, H, stroke=S), w, height, s, aa)
    if c == "-":
        return build(_bar, w, height, s, aa)
    if c == ".":
        return build(_dot, max(2, round(s)), height, s, aa)
    if c == "%":
        return build(percent, w+2, height, s, aa)
    if c == "°":
        size = max(3, round(height*.3))
        line = 1 if not aa and height < 19 else max(1, s*.6)
        return _top(build(degree, size, size, line, aa), height)
    if c == "d":
        return build(lambda W, H, S: latin("d", W, H, S), w, height, s, aa)
    if c in "KM":
        w += 1
    elif c == "I":
        w = max(round(s)+2, w-2)
    return build(lambda W, H, S: caps(c, W, H, S), w, height, s, aa)


def _bar(width, height, stroke):
    g = Grid(width, height)
    top = (height-stroke)//2
    g.rect(0, top, width-1, top+stroke-1)
    return g.image()


def _dot(width, height, stroke):
    g = Grid(width, height)
    g.rect((width-stroke)//2, height-stroke, (width-stroke)//2+stroke-1, height-1)
    return g.image()


def _top(mark, height):
    cell = Image.new("L", (mark.width, height))
    cell.paste(mark, (0, 0))
    return cell


def label_glyph(c, height, aa):
    if c == " ":
        return Image.new("L", (max(2, height//2), height))
    if c in DIGITS:
        if height <= 7 and not aa:
            return digit(c, max(3, round(height*.59)), height)
        s = weight(height, aa)
        return build(lambda W, H, S: digit(c, W, H, stroke=S), max(3, round(height*.59)), height, s, aa)
    width = round(height*.76)
    if height <= 7 and not aa:
        # Exactly one pixel per master cell: the 5x7 grid is already native.
        return pixels(caps_rows(c), width, height)
    s = weight(height, aa)
    return build(lambda W, H, S: caps(c, W, H, S), width, height, s, aa)


def date_figure_width(height, compact):
    return max(7, round(height*.58)) if compact else max(8, round(height*.65))


def date_glyph(c, height, aa, compact):
    if c in DIGITS or c == " ":
        width = date_figure_width(height, compact)
        if c == " ":
            # A blank figure cell: one-digit months keep the LCD's column.
            return Image.new("L", (width, height))
        if not aa:
            return digit(c, width, height, stroke=2)
        return native_segments(c, width, height, aa)
    if c in CAPS:
        if not aa:
            return caps(c, round(height*.79), height, 2)
        gutter = max(1, round(height*.048))
        return pixels(caps_rows(c), round(height*.79), height, gutter)
    if c == "'":
        im = Image.new("L", (max(2, height//4), height))
        ImageDraw.Draw(im).rectangle((im.width//2, 0, im.width-1, max(1, height//4)), fill=255)
        return im
    return latin(c, max(2, round(height*.64)), height, max(1, round(height*.135)))


def native_segments(c, w, h, aa):
    if not aa:
        return mip_segments(c,w,h)
    return segments(c,w*4,h*4,4,slanted=True).resize((w,h),Image.Resampling.BOX)


def data_heights(size, window=False, aa=False):
    # Instinct windows: bolder, larger readouts beside the aperture.
    value = round(size*.084) if window else max(10, round(size*.057))
    return {
        "Label": max(7, round(size*.031)), "Date": max(12, round(size*.077)),
        "Seconds": max(16, round(size*.114)), "Value": value,
        # MIP pictograms are drawn natively on an 11px grid; grayscale
        # screens trace them at four fifths of the numeral height.
        "Symbol": max(12, round(value*.8)) if aa else icons.GRID,
    }


def window_heights(radius):
    return {"WindowValue": max(12, int(radius*.66+.5))}


def window_fonts(radius):
    height = window_heights(radius)["WindowValue"]
    stroke = 3 if height >= 17 else 2
    items = {}
    for c in VALUE_GLYPHS:
        im = value_glyph(c, height, False, stroke=stroke)
        items[c] = im, im.width+max(1, round(height*.105))
    return {"WindowValue": items}


def data_fonts(size, aa, window=False):
    result = {}
    subsets = {
        "Label": LABEL_GLYPHS,
        "Date": DATE_GLYPHS,
        "Seconds": DIGITS,
        "Value": VALUE_GLYPHS,
        "Symbol": SYMBOLS,
    }
    for name, height in data_heights(size, window, aa).items():
        items = {}
        for c in subsets[name]:
            if name == "Symbol":
                im = icons.glyph(c, height, aa)
            elif name == "Seconds":
                im = native_segments(c,round(height*.63),height,aa)
            elif name == "Date":
                im = date_glyph(c,height,aa,size < 150)
            elif name == "Value":
                im = value_glyph(c, height, aa, narrow=window)
            else:
                im = label_glyph(c, height, aa)
            items[c] = im, im.width + max(1,round(height*.105))
        result[name] = items
    return result


def aod_font(size):
    h, w = round(size*.089), round(size*.061)
    s = max(2, round(h*.085))
    k = SUPERSAMPLE
    gap = max(3, w//6)
    items = {c: (segments(c, w*k, h*k, k, True).resize((w, h), Image.Resampling.BOX), w+gap) for c in DIGITS}
    items[":"] = (clock_mark(s*k, h*k, 0).resize((s, h), Image.Resampling.BOX), s+gap)
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
