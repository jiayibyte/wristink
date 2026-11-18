"""Selectable mountain backgrounds, original flat artwork drawn per native screen.

Scenes: 0 Summit (default), 1 Ranges, 2 Fuji, 3 Everest (the earlier artwork).
Flat colour planes keep each background small: the lite build must stay under
100,000 bytes per device with all four included. Monochrome screens get their
own line-and-snow compositions instead of a thresholded colour image.
Coordinates are fractions of the screen; the lower ~40% stays dark for the
clock and data.
"""
from PIL import Image, ImageDraw
import math

NAMES = [('Summit', '雪峰'), ('Ranges', '群峰'), ('Fuji', '富士'), ('Everest', '珠峰')]

MIP_LEVELS = (0, 85, 170, 255)


def mip(rgb):
    """Nearest colour of the 64-colour MIP panel palette."""
    return tuple(min(MIP_LEVELS, key=lambda v: abs(v - c)) for c in rgb)


def hexrgb(v):
    return ((v >> 16) & 255, (v >> 8) & 255, v & 255)


SUMMIT = [(-.05, .60), (.06, .53), (.16, .47), (.26, .40), (.33, .33), (.40, .26), (.45, .21), (.50, .15),
          (.55, .21), (.60, .25), (.66, .31), (.73, .38), (.82, .45), (.92, .52), (1.05, .60)]
SUMMIT_SNOW_LIT = [(.50, .15), (.45, .21), (.40, .26), (.36, .30), (.40, .30), (.43, .28), (.42, .34), (.47, .29),
                   (.49, .33), (.505, .27)]
SUMMIT_SNOW_SHADE = [(.50, .15), (.505, .27), (.52, .32), (.55, .28), (.58, .33), (.60, .29), (.64, .31), (.60, .25), (.55, .21)]
SUMMIT_FAR = [(-.05, .47), (.08, .41), (.17, .44), (.25, .37), (.31, .41), (.69, .41), (.76, .35), (.84, .40), (.93, .36), (1.05, .43)]

RANGES = [
    [(-.05, .40), (.06, .34), (.13, .37), (.22, .29), (.30, .35), (.38, .31), (.47, .36), (.58, .27), (.66, .33), (.75, .30), (.84, .36), (.93, .30), (1.05, .35)],
    [(-.05, .45), (.08, .40), (.18, .44), (.28, .37), (.40, .43), (.52, .38), (.63, .44), (.74, .39), (.86, .45), (1.05, .40)],
    [(-.05, .52), (.12, .46), (.24, .50), (.35, .45), (.48, .51), (.60, .47), (.72, .52), (.85, .47), (1.05, .53)],
    [(-.05, .59), (.14, .55), (.30, .58), (.46, .54), (.62, .58), (.78, .55), (1.05, .60)],
]
RANGE_TIPS = [(.22, .29), (.58, .27), (.93, .30)]

FUJI = [(-.05, .63), (.12, .58), (.24, .50), (.33, .40), (.40, .31), (.44, .25), (.47, .24), (.49, .245), (.51, .24),
        (.53, .245), (.56, .25), (.60, .31), (.67, .40), (.76, .50), (.88, .58), (1.05, .63)]
FUJI_SNOW = [(.44, .25), (.47, .24), (.49, .245), (.51, .24), (.53, .245), (.56, .25), (.60, .31), (.63, .35), (.605, .34),
             (.59, .38), (.565, .335), (.545, .37), (.52, .33), (.50, .38), (.48, .33), (.455, .37), (.435, .335),
             (.41, .38), (.395, .34), (.37, .35), (.40, .31)]

# name: (sky top, sky horizon, far, lit, shade, snow, snow shade, foreground, accent)
COLOURS = {
    0: dict(top=0x0B1630, bottom=0x4A7EA6, far=0x355A7E, lit=0x5D8CB4, shade=0x2E5276, snow=0xF4F8FC, snow2=0xB9D3E6, near=0x0E1B2E, mid=0x1A2D45),
    1: dict(top=0x2A1E4A, bottom=0xF0956A, sun=0xFFD08A, layers=[0xC98BA6, 0x8C5F8E, 0x553F72, 0x241E3D], snow=0xFFF1F0),
    2: dict(top=0x6FAEE0, bottom=0xF2C1C8, sun=0xE2453C, lit=0x3D5A8C, shade=0x2B4470, snow=0xFAFCFF, snow2=0xC8D8EE, lake=0x1B2E4D, near=0x0C1626),
}
MIP_COLOURS = {
    # Explicit sky bands from the MIP palette; interpolated bands picked greys and olives.
    0: dict(bands=[0x000000, 0x000055, 0x000055], far=0x005555, lit=0x55AAFF, shade=0x0055AA, snow=0xFFFFFF, snow2=0xAAFFFF, near=0x000000, mid=0x000055),
    1: dict(bands=[0x000055, 0x550055, 0xAA5555, 0xFFAA55], sun=0xFFFFAA, layers=[0xAA55AA, 0x550055, 0x000055, 0x000000], snow=0xFFFFFF),
    2: dict(bands=[0x55AAFF, 0xAAAAFF, 0xFFAAFF, 0xFFAAAA], sun=0xFF0000, lit=0x0055AA, shade=0x0000AA, snow=0xFFFFFF, snow2=0xAAAAFF, lake=0x000055, near=0x000000),
}


def _canvas(width, height, ss):
    im = Image.new('RGB', (width * ss, height * ss))
    return im, ImageDraw.Draw(im)


def _sky(d, W, H, C, horizon, mipmode):
    end = max(1, round(H * horizon))
    if mipmode:
        # Flat bands at palette colours instead of a dithered gradient.
        steps = [hexrgb(c) for c in C['bands']];bands=len(steps)
        for k, c in enumerate(steps):
            d.rectangle((0, round(end * k / bands), W, round(end * (k + 1) / bands)), fill=c)
        d.rectangle((0, end, W, H), fill=steps[-1])
        return
    a, b = hexrgb(C['top']), hexrgb(C['bottom'])
    for y in range(H):
        k = min(1, y / end)
        d.line((0, y, W, y), fill=tuple(round(x + (z - x) * k) for x, z in zip(a, b)))


def render_colour(scene, width, height, amoled):
    ss = 4 if amoled else 1
    W, H = width * ss, height * ss
    im, d = _canvas(width, height, ss)
    C = (COLOURS if amoled else MIP_COLOURS)[scene]
    col = (lambda v: hexrgb(v)) if amoled else (lambda v: mip(hexrgb(v)))
    xy = lambda pts: [(round(x * W), round(y * H)) for x, y in pts]
    def poly(pts, c, close_to=1.2):
        d.polygon(xy(pts + [(pts[-1][0], close_to), (pts[0][0], close_to)]), fill=col(c))
    def shape(pts, c):
        d.polygon(xy(pts), fill=col(c))
    if scene == 0:
        _sky(d, W, H, C, .5, not amoled)
        for x, y, r in [(.12, .07, 1), (.24, .13, 1), (.36, .05, 1), (.70, .09, 1), (.83, .16, 1), (.62, .04, 1), (.18, .19, 1)]:
            rr = max(1, round(r * width / 260)) * ss
            d.ellipse((round(x * W) - rr, round(y * H) - rr, round(x * W) + rr, round(y * H) + rr), fill=(230, 238, 250))
        poly(SUMMIT_FAR, C['far'])
        poly(SUMMIT, C['lit'])
        # Shaded east face: from the summit down the right of the ridge.
        shape([(.50, .15), (.55, .21), (.60, .25), (.66, .31), (.73, .38), (.82, .45), (.92, .52), (1.05, .60), (1.05, 1.2), (.58, 1.2), (.56, .52), (.53, .34)], C['shade'])
        shape(SUMMIT_SNOW_LIT, C['snow'])
        shape(SUMMIT_SNOW_SHADE, C['snow2'])
        poly([(-.05, .57), (.15, .52), (.32, .56), (.50, .53), (.68, .57), (.86, .52), (1.05, .56)], C['mid'])
        poly([(-.05, .64), (.20, .60), (.42, .63), (.64, .60), (.85, .63), (1.05, .60)], C['near'])
    elif scene == 1:
        _sky(d, W, H, C, .55, not amoled)
        cx, cy, r = .30 * W, .38 * H, .075 * min(W, H)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col(C['sun']))
        for k, (pts, c) in enumerate(zip(RANGES, C['layers'])):
            poly(pts, c)
            if k == 0:
                for x, y in RANGE_TIPS:
                    shape([(x, y), (x - .03, y + .03), (x - .012, y + .024), (x, y + .035), (x + .014, y + .022), (x + .03, y + .028)], C['snow'])
        poly([(-.05, .66), (1.05, .66)], C['layers'][-1])
    else:
        _sky(d, W, H, C, .6, not amoled)
        cx, cy, r = .78 * W, .2 * H, .06 * min(W, H)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col(C['sun']))
        poly(FUJI, C['lit'])
        shape([(.51, .24), (.53, .245), (.56, .25), (.60, .31), (.67, .40), (.76, .50), (.88, .58), (1.05, .63), (1.05, 1.2), (.56, 1.2), (.53, .5)], C['shade'])
        shape(FUJI_SNOW, C['snow'])
        shape([(.51, .24), (.53, .245), (.56, .25), (.60, .31), (.63, .35), (.605, .34), (.59, .38), (.565, .335), (.545, .37), (.52, .33)], C['snow2'])
        poly([(-.05, .63), (1.05, .63)], C['lake'])
        for y in (.67, .70, .74):
            d.line((round(.30 * W), round(y * H), round(.70 * W), round(y * H)), fill=col(C['lit']), width=max(1, round(ss * width / 260)))
        poly([(-.05, .78), (.12, .74), (.22, .77), (.36, .73), (.50, .76), (.66, .72), (.82, .76), (1.05, .73)], C['near'])
    # The foregrounds are already dark under the clock; no extra overlay, so
    # the palette stays exactly the scene's own flat colours.
    if ss != 1:
        im = im.resize((width, height), Image.Resampling.LANCZOS)
    return im


def render_mono(scene, width, height):
    """Clean 1-bit compositions: black planes, white ridges and solid snow."""
    im = Image.new('1', (width, height), 0); d = ImageDraw.Draw(im)
    # Instinct's clock starts at ~55% of the height: lift the whole composition
    # so no ridge line crosses the digits (the colour layouts sit lower).
    P = lambda pts: [(round(x * width), round((.05 + y * .78) * height)) for x, y in pts]
    line = lambda pts: d.line(P(pts), fill=1, width=1)
    if scene == 0:
        for x, y in [(.12, .07), (.24, .13), (.36, .05), (.18, .19), (.30, .21)]:
            d.point(P([(x, y)])[0], fill=1)
        line(SUMMIT_FAR[:5] + [(.36, .41)])
        d.polygon(P(SUMMIT + [(1.05, 1.1), (-.05, 1.1)]), fill=0)
        line(SUMMIT)
        d.polygon(P(SUMMIT_SNOW_LIT), fill=1)
        d.polygon(P(SUMMIT_SNOW_SHADE), fill=1)
    elif scene == 1:
        cx, cy, r = .30 * width, (.05 + .38 * .78) * height, .075 * width
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=1)
        for k, pts in enumerate(RANGES[:3]):
            d.polygon(P(pts + [(1.05, 1.1), (-.05, 1.1)]), fill=0)
            line(pts)
        for x, y in RANGE_TIPS:
            d.polygon(P([(x, y), (x - .03, y + .03), (x - .012, y + .024), (x, y + .035), (x + .014, y + .022), (x + .03, y + .028)]), fill=1)
    else:
        cx, cy, r = .24 * width, (.05 + .16 * .78) * height, .06 * width
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=1)
        d.polygon(P(FUJI + [(1.05, 1.1), (-.05, 1.1)]), fill=0)
        line(FUJI)
        d.polygon(P(FUJI_SNOW), fill=1)
    return im


def amoled_palette(scene, size=16):
    """The scene's own flat colours first (snow, sun, ridges), sky steps after.

    A generic 16-colour quantiser spends every slot on the sky gradient and
    drops the snow and the sun."""
    C = COLOURS[scene]
    keys = []
    for name, value in C.items():
        if name in ('top', 'bottom'):
            continue
        for v in (value if isinstance(value, list) else [value]):
            if hexrgb(v) not in keys:
                keys.append(hexrgb(v))
    a, b = hexrgb(C['top']), hexrgb(C['bottom']); n = max(2, size - len(keys))
    sky = [tuple(round(x + (y - x) * k / (n - 1)) for x, y in zip(a, b)) for k in range(n)]
    return (keys + sky)[:size]


def render(scene, width, height, mono=False, amoled=False):
    if mono:
        return render_mono(scene, width, height)
    im = render_colour(scene, width, height, amoled)
    if amoled:
        palette = Image.new('P', (1, 1))
        flat = [c for color in amoled_palette(scene) for c in color]
        palette.putpalette(flat + [0] * (768 - len(flat)))
        return im.quantize(palette=palette, dither=Image.Dither.NONE)
    if not amoled:
        palette = Image.new('P', (1, 1))
        flat = [c for r in MIP_LEVELS for g in MIP_LEVELS for b in MIP_LEVELS for c in (r, g, b)]
        palette.putpalette(flat + [0] * (768 - len(flat)))
        return im.quantize(palette=palette, dither=Image.Dither.NONE)
    return im
