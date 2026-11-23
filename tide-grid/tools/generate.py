"""Generate English settings, native device layouts, and compact BMFont resources."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
WEATHER = REPO / "retro-world/assets/garmin-weather"
sys.path.append(str(REPO / "tools")); import ciq_env
PACKS = ciq_env.DEVICES
OUT = ROOT / "generated"
sys.path.insert(0, str(REPO / "moke/scripts"))
from pixel_glyphs import Grid, _flatten, caps, digit, stroke_for
sys.path.insert(0, str(REPO / "retro-world/tools"))
from garmin_weather import icon as garmin_icon
sys.path.insert(0, str(REPO / "signal-lcd/tools"))
import icons as pictograms

METRICS = [
    ("OFF", "Hidden"), ("DATE", "Date"), ("BAT", "Battery"), ("STP", "Steps"),
    ("HR", "Heart rate"), ("TMP", "Weather temperature"), ("DST", "Distance"),
    ("CAL", "Calories"), ("ALT", "Elevation"), ("FLR", "Floors climbed"),
    ("NTF", "Notifications"), ("HI", "Next high tide"), ("LO", "Next low tide"),
    ("UP", "Sunrise"), ("DN", "Sunset"), ("DAY", "Day of week"),
    ("HC", "Next high tide height"), ("LC", "Next low tide height"),
    ("MD", "Moon age"), ("DC", "Weekday and date"), ("TC", "Tide cycle"),
]
CHARTS = ["Hidden", "Tide forecast · selected port", "Steps · 7 days", "Heart rate · 2 hours",
          "Distance · 7 days", "Calories · 7 days"]
THEMES = ["Deep Sea", "Ember", "Glacier", "Kelp", "Ink", "Paper",
          "Amber LCD", "Ultraviolet", "Signal Red", "Lime Phosphor", "Rose Quartz", "Polar Light"]
MONO_THEMES = (4, 5)
# Theme colors per screen family: background, dial, border, main ink, quiet
# ink, accent, secondary accent. Each device carries only its own family, as
# one hex string in Panel.PALETTE.
AMOLED_PALETTES = [
    "071518 10272B 28464B EDF6E8 9CB9B6 61E8C9 F5BB71", "190C10 2F1A1C 5F3433 FFF1DD D0A99D FF8A69 F1CC83",
    "0B1421 152640 325071 EFF5FF A1BCD7 93C7FF CFB3F4", "101710 1D2A1B 394D32 F4F2DB AFC0A0 BCE881 F0CA8B",
    "080B0C 191E22 47515A F3F5F6 BDC7CE E4E9EC A8B4BE", "F4EBD6 E6DBC2 B9AB8F 172522 425954 00685E 923B20",
    "000000 1B1103 78591D FFEBC1 D0AB62 FFB942 FFED97", "10091E 241639 603780 F5ECFF C4AADF B8A4FF FF84D4",
    "08090C 221015 842A3A FFF2F3 D4A0AA FF6077 FFBF79", "020900 112010 437133 E7FFCC A9CC92 C4FF4D 63E4AB",
    "F7E7E8 F1D7DA 9E6B79 321723 683E4E 9B2D57 514678", "EAF5F8 CEDFEE 7792A6 122837 3C5767 136A83 593B8F",
]
MIP_PALETTES = [
    "000000 005555 00AAAA FFFFFF AAAAAA 55FFFF FFAA00", "000000 550000 AA5500 FFFFAA AAAAAA FFAA55 FFFF00",
    "000000 000055 0055AA FFFFFF AAAAAA 55FFFF AAAAFF", "000000 005500 55AA00 FFFFAA AAAAAA AAFF55 FFAA55",
    "000000 000000 555555 FFFFFF AAAAAA FFFFFF AAAAAA", "FFFFAA FFAAAA AA5555 000000 555555 005555 AA0000",
    "000000 555500 AA5500 FFFFAA FFAA55 FFAA00 FFFF55", "000000 550055 AA55AA FFFFFF FFAAFF AAAAFF FF55FF",
    "000000 550000 AA0000 FFFFFF FFAAAA FF5555 FFAA55", "000000 005500 55AA00 FFFFAA AAFFAA AAFF00 55FFAA",
    "FFAAFF FFAAAA AA55AA 550000 550055 AA0055 5500AA", "AAFFFF AAAAFF 5555AA 000055 005555 0055AA 5500AA",
]
# Ink (theme 4) and Paper (theme 5) on 1-bit and 8-color screens.
MONO_PALETTES = ["000000 000000 FFFFFF FFFFFF FFFFFF FFFFFF FFFFFF",
                 "FFFFFF FFFFFF 000000 000000 000000 000000 000000"]
assert len(AMOLED_PALETTES) == len(MIP_PALETTES) == len(THEMES)
TIDE_PORTS = json.loads((ROOT / "assets/tide-ports.json").read_text())
FONTS = {"Harbor": "round", "Dock": "lcd", "Beacon": "segment"}
# Normalized ink from the licensed Casio module 3482 TIME+TIDE ALL example.
# The source time in the manual is 10:58. These are only individual glyph
# masks, so all time and instrument data remain live.
# CASIO figure 3482_53_Info, screen ink y=265..302 inclusive.
LCD_SAMPLE = {
    "1": (14, "3ff fff fff 3fff 3fff 3fff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff"),
    "0": (27, "7ffff8 1fffffc 1fffffc 7ffffff 7ffffff 7ffffff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7f801ff 7ffffff 7ffffff 7ffffff 1fffffc 1fffffc 7ffff8"),
    ":": (10, "0 0 0 70 70 1fc 1fc 1fc 1fc 1fc 1fc 70 70 0 0 0 0 0 0 0 0 0 0 0 0 70 70 1fc 1fc 1fc 1fc 1fc 1fc 70 70 0 0 0"),
    "5": (26, "3ffffff 3ffffff 3ffffff 3ffffff 3ffffff 3ffffff 3fc0000 3fc0000 3fc0000 3fc0000 3fc0000 3fc0000 3fc0000 3ffffff 3ffffff 3ffffff 3ffffff 3ffffff 3ffffff 3ffffff 3fc01ff 3fc01ff 1ff 1ff 1ff 1ff 1ff 1ff 3fc01ff 3fc01ff 3fc01ff 3fc01ff 3ffffff 3ffffff 3ffffff fffffc fffffc 7ffff8"),
    "8": (26, "7ffff8 1fffffe 1fffffe 3ffffff 3ffffff 3ffffff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3ffffff 3ffffff 1fffffe 1fffffe 1fffffe 3ffffff 3ffffff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3fc00ff 3ffffff 3ffffff 3ffffff 1fffffe 1fffffe 7ffff8"),
}

SLOTS = {"HeaderLeft": 13, "HeaderRight": 14, "CircleTop": 11, "CircleBottom": 16,
         "ChartLeft": 18, "ChartRight": 20, "TimeAux": 19,
         "FooterLeft": 3, "FooterCenter": 4, "FooterRight": 2,
         "Heading": 21, "ClockCaption": 22, "SecondsSlot": 23}
SPECIAL_SLOTS = {"Heading": "Automatic (port or chart name)",
                 "ClockCaption": "HOME (local time)",
                 "SecondsSlot": "Seconds while awake"}


def slot_options(key):
    options = list(range(len(METRICS)))
    return options + [SLOTS[key]] if key in SPECIAL_SLOTS else options


APP_ID = "3f5ca29b55614e16a7d5028093314aec"
NS = "http://www.garmin.com/xml/connectiq"
ET.register_namespace("iq", NS)

# Seven-row pixel masters. Native size is an integer partition of the target cell.
LETTERS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", """
0e11111f111111 1e11111e11111e 0f10101010100f 1e11111111111e
1f10101e10101f 1f10101e101010 0f10101711110f 1111111f111111
0e04040404040e 0702020202120c 11121418141211 1010101010101f
111b1515111111 11191513111111 0e11111111110e 1e11111e101010
0e11111115120d 1e11111e141211 0f10100e01011e 1f040404040404
1111111111110e 11111111110a04 1111111515150a 11110a040a1111
11110a04040404 1f01020408101f
""".split(), strict=True))
PUNCT = {"-": "0000001f000000", ":": "00040400040400", ".": "00000000000404",
         "/": "01010204081010", "%": "19190204081313", "+": "0004041f040400",
         "°": "06090906000000", "_": "0000000000001f", " ": "00000000000000"}

# Original compact symbols where Garmin exposes values without shareable native glyphs.
ICONS = {
    "c": "00001e13131e00",
    "d": "020606080c1018", "e": "000a1f1f0e0400",
    "g": "0011111f101000", "h": "04060e0f1f0e00", "i": "00040a111f0000",
    "j": "010107041c1000", "k": "040e0e0e1f0400", "l": "040e1504041f00",
    "m": "040404150e1f00",
    "p": "041f1115151f00",
}


def write_xml(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def settings(preview=False, fixture="tide", theme=0, font=0, mono=False):
    mode = "preview" if preview else "live"
    path = OUT / (mode+"-mono-resources" if mono else mode+"-resources")
    strings = ET.Element("strings")
    props = ET.Element("properties")
    fields = ET.Element("settings")

    def label(key, value):
        scope = {} if key == "AppName" else {"scope": "settings"}
        ET.SubElement(strings, "string", id=key, **scope).text = value

    def setting(key, title, default, options=None, type_="number", values=None, **attrs):
        label(key, title)
        ET.SubElement(props, "property", id=key, type=type_).text = str(default)
        field = ET.SubElement(fields, "setting", propertyKey="@Properties." + key, title="@Strings." + key)
        editor = ET.SubElement(field, "settingConfig", type="list" if options else "alphaNumeric", **attrs)
        for value, name_key in zip(values if values is not None else range(len(options or [])), options or [], strict=True):
            ET.SubElement(editor, "listEntry", value=str(value)).text = "@Strings." + name_key

    label("AppName", "Tide Grid")
    for prefix, names in (("Metric", [name for _, name in METRICS]), ("ChartOption", CHARTS),
                          ("ThemeOption", THEMES), ("FontOption", FONTS),
                          ("FormatOption", ["System", "12-hour", "24-hour"])):
        for i, name in enumerate(names):
            key = f"{prefix}{i}"
            label(key, name)
    theme_choices = MONO_THEMES if mono else range(len(THEMES))
    fallback_theme = MONO_THEMES[0] if mono else 0
    setting("Theme", "Theme", theme if theme in theme_choices else fallback_theme,
            [f"ThemeOption{i}" for i in theme_choices], values=theme_choices)
    setting("TimeFont", "Clock font", font if preview else 1, [f"FontOption{i}" for i in range(len(FONTS))])
    setting("ClockFormat", "Clock format", 0, [f"FormatOption{i}" for i in range(3)])
    setting("Chart", "Chart", {"tide": 1, "steps": 2, "heart": 3, "distance": 4, "calories": 5}.get(fixture, 2)
            if preview else 1, [f"ChartOption{i}" for i in range(len(CHARTS))])
    label("TidePlace0", "Automatic (near Garmin location)")
    for i, port in enumerate(TIDE_PORTS["stations"], 1):
        label(f"TidePlace{i}", port["name"] + " · " + port["region"])
    setting("TidePlace", "Tide location", 0, [f"TidePlace{i}" for i in range(len(TIDE_PORTS["stations"])+1)])
    # Keep the property for existing installations without exposing station IDs.
    ET.SubElement(props, "property", id="TideStation", type="string").text = ""
    label("WristSeconds", "Seconds while awake")
    ET.SubElement(props, "property", id="WristSeconds", type="boolean").text = "true"
    ET.SubElement(ET.SubElement(fields, "setting", propertyKey="@Properties.WristSeconds",
                               title="@Strings.WristSeconds"), "settingConfig", type="boolean")
    for key, default in SLOTS.items():
        title = {"HeaderLeft": "Upper left · top", "HeaderRight": "Upper left · bottom",
                 "CircleTop": "Upper right · top", "CircleBottom": "Upper right · bottom",
                 "ChartLeft": "Left of chart", "ChartRight": "Right of chart",
                 "TimeAux": "Right of time · top", "SecondsSlot": "Right of time · bottom",
                 "FooterLeft": "Bottom left", "FooterCenter": "Bottom center", "FooterRight": "Bottom right",
                 "Heading": "Top title", "ClockCaption": "Above main time"}[key]
        if key in SPECIAL_SLOTS:
            label(f"Metric{default}", SPECIAL_SLOTS[key])
        choices = slot_options(key)
        setting(key, title, default, [f"Metric{i}" for i in choices], values=choices)
    write_xml(strings, path / "strings.xml")
    write_xml(props, path / "properties.xml")
    write_xml(fields, path / "settings.xml")
    return path.relative_to(ROOT).as_posix()


def font_file(folder, fonts, name, height, glyphs, antialias=False):
    width = sum(g.width for _, g, _ in glyphs)
    atlas = Image.new("L", (width, height))
    entries = []
    x = 0
    for char, glyph, advance in sorted(glyphs):
        assert glyph is not None and glyph.height == height
        assert glyph.getbbox() is None or glyph.getbbox()[2] < advance
        atlas.paste(glyph, (x, 0))
        entries.append(f"char id={ord(char)} x={x} y=0 width={glyph.width} height={height} "
                       f"xoffset=0 yoffset=0 xadvance={advance} page=0 chnl=15")
        x += glyph.width
    if antialias:
        # Grayscale coverage on opaque black survives CIQ's grayscale importer.
        atlas.convert("RGB").save(folder / f"{name}.png")
    else:
        image = Image.new("RGBA", atlas.size, "white")
        image.putalpha(atlas)
        image.save(folder / f"{name}.png")
    (folder / f"{name}.fnt").write_text(
        f'info face="{name}" size={height} bold=0 italic=0 charset="" unicode=1 stretchH=100 '
        'smooth=1 aa=1 padding=0,0,0,0 spacing=0,0 outline=0\n'
        f'common lineHeight={height} base={height} scaleW={width} scaleH={height} pages=1 packed=0\n'
        f'page id=0 file="{name}.png"\nchars count={len(entries)}\n' + "\n".join(entries) + "\n"
    )
    ET.SubElement(fonts, "font", id=name, filename=f"{name}.fnt", antialias=str(antialias).lower())


class CoverageGrid(Grid):
    """Rasterize the common digit paths as high-resolution filled strokes."""
    def __init__(self, width, height):
        super().__init__(width, height)
        self.coverage = Image.new("L", (width, height))
        self.draw = ImageDraw.Draw(self.coverage)

    def stroke(self, points, width, rho=0, closed=False):
        unique = []
        for point in points:
            if not unique or point[:2] != unique[-1][:2]:
                unique.append(point)
        segments = _flatten(tuple(unique), rho, closed and len(unique) > 2)
        radius = (width - 1) / 2
        joints = set()
        for x1, y1, x2, y2 in segments:
            length = math.hypot(x2-x1, y2-y1)
            joints.update(((x1, y1), (x2, y2)))
            if length:
                u = (y2-y1) / length * radius
                v = (x1-x2) / length * radius
                self.draw.polygon(((x1+u, y1+v), (x2+u, y2+v), (x2-u, y2-v), (x1-u, y1-v)), fill=255)
        for x, y in joints:
            self.draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)

    def image(self):
        return ImageChops.lighter(super().image(), self.coverage)


def lcd_glyph(char, width, height, antialias):
    factor = 3 if antialias else 1
    if char in LCD_SAMPLE:
        source_width, rows = LCD_SAMPLE[char]
        source = Image.new("L", (source_width, 38))
        pixels = [255 if int(row, 16) & (1 << shift) else 0
                  for row in rows.split() for shift in reversed(range(source_width))]
        source.putdata(pixels)
        method = Image.Resampling.BOX if antialias else Image.Resampling.NEAREST
        return source.resize((width, height), method)
    # Rebuild the remaining numerals using the reference stroke/width ratio.
    # Their final dimensions are rasterized independently for each screen.
    w, h = width*factor, height*factor
    s = max(1, round(height*.203)) * factor
    canvas = Image.new("L", (w, h))
    d = ImageDraw.Draw(canvas)
    mid = (h-s)//2
    radius = max(1, round(h*.09))
    segments = {"2": "abged", "3": "abgcd", "4": "fgbc", "6": "afgecd",
                "7": "abc", "9": "abfgcd"}[char]
    for part, (x,y,x2,y2) in {
        "a": (0,0,w-1,s-1), "g": (0,mid,w-1,mid+s-1), "d": (0,h-s,w-1,h-1),
        "f": (0,0,s-1,mid+s-1), "b": (w-s,0,w-1,mid+s-1),
        "e": (0,mid,s-1,h-1), "c": (w-s,mid,w-1,h-1),
    }.items():
        if part in segments:
            d.rectangle((x,y,x2,y2), fill=255)
    for x,y,dx,dy in ((0,0,1,1),(w-1,0,-1,1),(0,h-1,1,-1),(w-1,h-1,-1,-1)):
        if canvas.getpixel((x,y)):
            d.polygon(((x,y),(x+dx*(radius-1),y),(x,y+dy*(radius-1))), fill=0)
    return canvas.resize((width,height), Image.Resampling.BOX)


def clock_glyph(char, width, height, style, antialias):
    if style == "lcd":
        return lcd_glyph(char, width, height, antialias)
    factor = 4 if antialias else 1
    if char == ":":
        edge = width * factor
        image = Image.new("L", (edge, height * factor))
        draw = ImageDraw.Draw(image)
        dot = max(2 * factor, round(edge * 0.65))
        for y in (round(height * factor * .31), round(height * factor * .68)):
            box = ((edge - dot) // 2, y - dot // 2, (edge + dot) // 2 - 1, y + dot // 2 - 1)
            (draw.ellipse if style == "round" else draw.rectangle)(box, fill=255)
    else:
        stroke = round(height * .106) if style == "segment" else stroke_for(width, height) + (height > 50)
        if char == "7" and antialias and style != "segment":
            # One continuous stroke removes the gap between the horizontal
            # cap and diagonal present when they are sampled separately.
            w, h, size = width * factor, height * factor, stroke * factor
            a = (size-1)/2
            grid = CoverageGrid(w, h)
            grid.stroke([(a,a), (w-1-a,a), (round(w*.32),h-1-a)], size)
            image = grid.image()
        else:
            image = digit(char, width * factor, height * factor, stroke=stroke * factor, style=style,
                          grid_type=CoverageGrid if antialias else Grid)
    return image.resize((width, height), Image.Resampling.BOX)


def grid(rows, width, height):
    out = Image.new("L", (width, height))
    draw = ImageDraw.Draw(out)
    for y, row in enumerate(bytes.fromhex(rows)):
        for x in range(5):
            if row & (16 >> x):
                draw.rectangle((x * width // 5, y * height // 7,
                                (x+1) * width // 5 - 1, (y+1) * height // 7 - 1), fill=255)
    return out


def font_resources(folder, clock_height, small, antialias):
    folder.mkdir(parents=True, exist_ok=True)
    fonts = ET.Element("fonts")
    for name, style in FONTS.items():
        width = round(clock_height * (.69 if style == "lcd" else .76))
        gap = max(2, round(clock_height * (.145 if style == "lcd" else .08)))
        colon = max(3, round(clock_height * (.22 if style == "lcd" else .25)))
        glyphs = []
        for c in "0123456789:":
            cell = colon if c == ":" else round(width*.52) if c == "1" and style == "lcd" else width
            glyphs.append((c, clock_glyph(c, cell, clock_height, style, antialias), cell+gap))
        font_file(folder, fonts, name, clock_height, glyphs, antialias)
    sub_height = max(10, round(clock_height * .66))
    sub_width = round(sub_height * .82)
    sub_gap = max(1, round(sub_height * .14))
    glyphs = [(c, lcd_glyph(c, sub_width, sub_height, antialias), sub_width+sub_gap) for c in "0123456789"]
    glyphs += [("-", grid(PUNCT["-"], sub_width, sub_height), sub_width+sub_gap)]
    font_file(folder, fonts, "Seconds", sub_height, glyphs, antialias)

    width = max(5, round(small * .69))
    gap = max(1, round(small * .13))
    stroke = text_stroke(small, antialias)
    glyphs = [(c, small_glyph(c, width, small, stroke, antialias), width+gap)
              for c in LETTERS | PUNCT if c != " "]
    glyphs.append((" ", Image.new("L", (max(1,width//2), small)), max(1,width//2)+gap))
    icon_width = max(7, width+1)
    for c, rows in ICONS.items():
        # Bottom-align optical ink (including the battery and footsteps),
        # using the same baseline as the numerical readout.
        ink = pictogram(c, rows, icon_width, small, antialias)
        ink = ink.crop(ink.getbbox())
        cell = Image.new("L", (max(icon_width, ink.width), small))
        cell.paste(ink, ((cell.width-ink.width)//2, small-ink.height))
        glyphs.append((c, cell, cell.width+gap))
    glyphs += [(c, build(lambda W, H, S, c=c: digit(c, W, H, stroke=S), width, small, stroke, antialias), width+gap)
               for c in "0123456789"]
    # Garmin support weather pictograms, already pinned and checked by WristInk.
    for i in range(13):
        source = weather_ink(i, icon_width, small, antialias)
        cell = Image.new("L", (icon_width, small))
        cell.paste(source, ((icon_width-source.width)//2, small-source.height))
        glyphs.append((chr(0x100+i), cell, icon_width+gap))
    glyphs.append(("f", next(g[1] for g in glyphs if g[0] == chr(0x10a)), icon_width+gap))
    # The public Garmin support symbol represents both sunrise and sunset.
    for char, direction in (("n", 1), ("o", -1)):
        glyphs.append((char, sun_glyph(direction, icon_width, small, antialias), icon_width+gap))
    font_file(folder, fonts, "Instrument", small, glyphs, antialias)
    write_xml(fonts, folder / "fonts.xml")


SUPERSAMPLE = 4


def text_stroke(small, antialias):
    """Whole pixels on MIP, matching the numerals; proportional on AMOLED."""
    return max(1.0, round(small*.12*4)/4) if antialias else max(1, round(small*.13))


def build(draw, width, height, stroke, antialias):
    """Run a grid-native builder at 1x, or 4x and area-sample for grayscale."""
    if not antialias:
        return draw(width, height, max(1, round(stroke)))
    k = SUPERSAMPLE
    return draw(width*k, height*k, max(1, round(stroke*k))).resize((width, height), Image.Resampling.BOX)


def small_glyph(c, width, small, stroke, antialias):
    """Letters and punctuation. At 7px the 5x7 masters are exactly native;
    larger sizes are stroked on their own grid instead of being stretched."""
    rows = LETTERS.get(c) or PUNCT[c]
    if small <= 7 and width == 5 and not antialias:
        return grid(rows, width, small)
    if c in LETTERS:
        return build(lambda W, H, S: caps(c, W, H, S), width, small, stroke, antialias)

    def punct(W, H, S):
        g = Grid(W, H)
        mid = (H-S)//2
        if c == "-":
            g.rect(0, mid, W-1, mid+S-1)
        elif c == "_":
            g.rect(0, H-S, W-1, H-1)
        elif c == "+":
            g.rect(0, mid, W-1, mid+S-1)
            g.rect((W-S)//2, (H-W)//2+S//2, (W-S)//2+S-1, (H+W)//2-1-S//2)
        elif c in ":.":
            x = (W-S)//2
            rows_at = [H-S] if c == "." else [round(H*.28), round(H*.72)-S+1]
            for y in rows_at:
                g.rect(x, y, x+S-1, y+S-1)
        elif c == "/":
            g.slant(W-S, 0, 0, H-1, S)
        elif c == "%":
            ring = max(3, W//2+1)
            a = (S-1)/2
            for x0, y0 in ((0, 0), (W-ring, H-ring)):
                g.stroke([(x0+a, y0+a), (x0+ring-1-a, y0+a), (x0+ring-1-a, y0+ring-1-a), (x0+a, y0+ring-1-a)],
                         S, max(0, (ring-S)/2*.9), closed=True)
            g.slant(W-S, 0, 0, H-1, S)
        elif c == "°":
            ring = min(W, max(3, round(H*.5)))
            a = (S-1)/2
            x0 = (W-ring)//3
            g.stroke([(x0+a, a), (x0+ring-1-a, a), (x0+ring-1-a, ring-1-a), (x0+a, ring-1-a)],
                     S, max(0, (ring-S)/2*.9), closed=True)
        return g.image()
    return build(punct, width, small, stroke, antialias)


def traced(mask, size, antialias):
    """Smooth outline of a small 1-bit master at `size`. The master is
    magnified, softened by under half a master pixel and cut at half coverage:
    stairs become straight edges and corners become arcs."""
    zoom = 16
    big = mask.resize((mask.width*zoom, mask.height*zoom), Image.Resampling.NEAREST)
    canvas = Image.new("L", (big.width+2*zoom, big.height+2*zoom))
    canvas.paste(big, (zoom, zoom))
    shape = canvas.filter(ImageFilter.GaussianBlur(zoom*.42)).point(lambda v: 255 if v >= 128 else 0)
    shape = shape.crop((zoom, zoom, zoom+big.width, zoom+big.height)).resize(size, Image.Resampling.BOX)
    return shape if antialias else shape.point(lambda v: 255 if v >= 128 else 0)


# Grayscale screens trace the shared 11px pictogram masters (signal-lcd/tools/icons.py).
TRACED = {"c": "c", "d": "d", "e": "b", "g": "f", "h": "e", "i": "i", "j": "j", "k": "h",
          "l": "H", "m": "L", "p": "W"}


def pictogram(c, rows, icon_width, small, antialias):
    if antialias:
        # Nine tenths of the text height sits level with the capitals.
        return pictograms.smooth(TRACED[c], round(small*.9))
    if small <= 9:
        # The 5x7 master is the native drawing at this size: never stretch it.
        return grid(rows, 5, 7)
    return grid(rows, icon_width, small)


def weather_ink(i, icon_width, small, antialias):
    if not antialias:
        source = garmin_icon(i, small).convert("L").point(lambda v: 255-v)
        source = source.crop(source.getbbox())
        source.thumbnail((icon_width, small), Image.Resampling.NEAREST)
        return source
    # Area-sample the pinned source pictogram itself: no 1-bit intermediate.
    meta = json.loads((WEATHER / "sources.json").read_text())["icons"][i]
    path = WEATHER / meta["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"], path
    ink = ImageOps.invert(Image.open(path).convert("L")).point(lambda v: 0 if v < 40 else v)
    ink = ink.crop(ink.getbbox())
    scale = min(icon_width/ink.width, small/ink.height)
    return ink.resize((max(1, round(ink.width*scale)), max(1, round(ink.height*scale))), Image.Resampling.BOX)


def sun_glyph(direction, icon_width, small, antialias):
    sun_dir = REPO / "retro-world/assets/garmin-sun"
    sun_meta = json.loads((sun_dir / "source.json").read_text())
    sun_path = sun_dir / "official-sunrise-sunset.png"
    assert hashlib.sha256(sun_path.read_bytes()).hexdigest() == sun_meta["sha256"]
    source = Image.open(sun_path).convert("RGBA")
    base = Image.new("RGBA", source.size, "white")
    base.alpha_composite(source)
    k = SUPERSAMPLE if antialias else 1
    ink = base.convert("L").point(lambda v: 255 if v < 145 else 0)
    ink = ink.crop(ink.getbbox())
    ink.thumbnail((icon_width*k, (small-2)*k), Image.Resampling.BOX)
    cell = Image.new("L", (icon_width*k, small*k))
    cell.paste(ink if antialias else ink.point(lambda v: 255 if v >= 88 else 0),
               ((icon_width*k-ink.width)//2, small*k-ink.height))
    center = icon_width//2
    y = 1 if direction == 1 else 0
    # Chevron above the horizon: up for sunrise, down for sunset.
    ImageDraw.Draw(cell).line([((center-1)*k+k//2, y*k+k//2), (center*k+k//2, (y-direction)*k+k//2),
                               ((center+1)*k+k//2, y*k+k//2)], fill=255, width=k)
    return cell.resize((icon_width, small), Image.Resampling.BOX) if antialias else cell


def manifest(path, devices, preview, preview_key=""):
    root = ET.Element(f"{{{NS}}}manifest", version="3")
    app_id = hashlib.md5((APP_ID + preview_key).encode()).hexdigest() if preview else APP_ID
    app = ET.SubElement(root, f"{{{NS}}}application", id=app_id, type="watchface", name="@Strings.AppName",
                        entry="TideGridApp", launcherIcon="@Drawables.LauncherIcon", minApiLevel="3.2.0")
    for section, element, items in (
        ("products", "product", devices),
        ("permissions", "uses-permission", ["Positioning", "ComplicationSubscriber"]),
        ("languages", "language", ["eng"]),
    ):
        group = ET.SubElement(app, f"{{{NS}}}{section}")
        for value in items:
            node = ET.SubElement(group, f"{{{NS}}}{element}")
            if section == "languages":
                node.text = value
            else:
                node.set("id", value)
    ET.SubElement(app, f"{{{NS}}}barrels")
    write_xml(root, path)


def device_specs():
    for filename in sorted(PACKS.glob("*/compiler.json")):
        c = json.loads(filename.read_text())
        sfile = filename.with_name("simulator.json")
        if not sfile.exists():
            continue
        s = json.loads(sfile.read_text())
        if not s.get("display") or s.get("analogHands"):
            continue
        capacities = {v["type"]: v["memoryLimit"] for v in c["appTypes"]}
        if capacities.get("watchFace", 0) < 65536 or capacities.get("background", 0) < 32768:
            continue
        versions = [p.get("connectIQVersion", "") for p in c["partNumbers"]]
        if not versions or any(not v or tuple(map(int, v.split("."))) < (3, 2, 0) for v in versions):
            continue
        w, h = (c["resolution"][k] for k in ("width", "height"))
        shape = s["display"]["shape"]
        sub = s.get("subscreen")
        if min(w, h) < 148 or shape not in {"round", "semi-octagon", "rectangle"} or (shape == "semi-octagon" and not sub):
            continue
        if max(w/h, h/w) > 1.43:
            continue
        yield c, s, versions, capacities


def launcher(folder, dims):
    w, h = dims
    image = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, w-1, h-1), radius=w//5, fill="#102b31")
    for i, fraction in enumerate((.30, .55, .74, .58, .32)):
        x = round(w * (.18 + i * .135))
        y = round(h * (.78-fraction*.75))
        draw.rounded_rectangle((x, y, x+max(1, w//12), int(h*.78)), radius=max(1, w//28), fill="#58efd2")
    folder.mkdir(parents=True, exist_ok=True)
    image.save(folder / "launcher.png")
    assets = ET.Element("drawables")
    ET.SubElement(assets, "bitmap", id="LauncherIcon", filename="launcher.png", compress="true")
    write_xml(assets, folder / "launcher.xml")


def tide_resources():
    dest = OUT / "tides"
    dest.mkdir(parents=True, exist_ok=True)
    lines = ["// Generated from the licensed station subset in assets/tide-ports.json.",
             "import Toybox.Lang;", "", "module TideCatalog {", "    const PORTS = ["]
    for port in TIDE_PORTS["stations"]:
        # Each harmonic occupies three ASCII characters. It carries nine
        # bits of amplitude (half-cm increments) and nine bits of phase.
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        values = port["amplitudeTenthCM_phaseHundredthDeg"]
        packed = ""
        for amplitude, phase in zip(values[::2], values[1::2], strict=True):
            half_cm = round(amplitude/5)
            assert 0 <= half_cm <= 511
            code = (half_cm << 9) | (round(phase*512/36000) & 511)
            packed += "".join(alphabet[(code>>shift)&63] for shift in (12,6,0))
        # One record string per station costs about a third less than a
        # five-element array of constants in the PRG data section.
        fields = [port["name"], str(round(port["lat"]*1000)), str(round(port["lon"]*1000)),
                  packed, port.get("legacyNoaa", "")]
        assert not any("|" in field for field in fields)
        lines.append("        " + json.dumps("|".join(fields)) + ",")
    lines += ["    ];",
              "    // [name, latitude, longitude, harmonics, legacy NOAA id]; degrees.",
              "    function port(i as Number) as Array {",
              "        var text = PORTS[i] as String;",
              "        var parts = [] as Array<String>;",
              "        for (var k = 0; k < 4; k++) {",
              "            var bar = text.find(\"|\") as Number;",
              "            parts.add(text.substring(0, bar) as String);",
              "            text = text.substring(bar+1, text.length()) as String;",
              "        }",
              "        return [parts[0], (parts[1].toNumber() as Number)/1000.0,",
              "                (parts[2].toNumber() as Number)/1000.0, parts[3], text];",
              "    }",
              f"    const EPOCH_DAY = {TIDE_PORTS['epochUnixDay']};",
              "    const NODE = " + json.dumps(TIDE_PORTS["lunarNode"]) + ";",
              "    const TERMS = ["]
    for term in TIDE_PORTS["constituents"]:
        values = [term[k] for k in ("phase", "driftPerDay", "advance1800", "f0", "f1", "u1")]
        lines.append("        " + json.dumps(values) + ",")
    lines += ["    ];", "}"]
    (dest / "TideCatalog.mc").write_text("\n".join(lines) + "\n")


def generate(preview_device=None, fixture="tide", theme=0, font=0, test=False):
    tide_resources()
    previews = preview_device is not None
    spec = list(device_specs())
    if previews:
        spec = [parts for parts in spec if parts[0]["deviceId"] == preview_device]
    assert spec, "No compatible device packs"
    configs = []
    cached = set()
    mode = "preview" if previews else "live"
    if test:
        mode += ";tests"
    settings_paths = {mono: settings(previews, fixture, theme, font, mono) for mono in (False, True)}
    manifest_path = ROOT / ("generated/preview-manifest.xml" if previews else "manifest.xml")
    jungle = [f"project.manifest = {manifest_path.relative_to(ROOT)}"]
    for c, s, api, capacities in spec:
        name = c["deviceId"]
        w, h = (c["resolution"][k] for k in ("width", "height"))
        q = min(w, h)
        lcd = s["display"]["location"]
        shape = s["display"]["shape"]
        amoled = c["displayType"] in {"amoled", "microled"}
        # The Instinct 3 AMOLED window is part of the stock dial artwork.
        sub = None if name.startswith("instinct3amoled") else s.get("subscreen")
        bpp = c["bitsPerPixel"]
        mono = bpp == 1
        aa = amoled and c.get("alphaBlendingSupport", False)
        small = max(7, round(q*.040))
        clock = round(q * .141)
        cx, cy, r = 0, 0, 0
        if sub:
            rect = sub["location"]
            cx = round(rect["x"] - lcd["x"] + rect["width"]/2 - max(0, lcd["width"]-w))
            cy = round(rect["y"] - lcd["y"] + rect["height"]/2)
            r = min(rect["width"], rect["height"])//2 - 2
        icon_size = (c["launcherIcon"]["width"], c["launcherIcon"]["height"])
        key = f"{clock}-{small}-{int(aa)}-{icon_size[0]}x{icon_size[1]}"
        assets = OUT / "profiles" / key
        if key not in cached:
            font_resources(assets / "fonts", clock, small, aa)
            launcher(assets / "launch", icon_size)
            cached.add(key)
        profile = dict(W=w, H=h, CLOCK_H=clock, SMALL=small, ROUND=shape == "round", SUB=bool(sub),
                       CX=cx, CY=cy, R=r, MONO=mono, AMOLED=amoled, LOW_COLOR=bpp < 6 and not amoled)
        code = OUT / "devices" / name
        code.mkdir(parents=True, exist_ok=True)
        values = "\n".join(f"    const {k} = {str(v).lower()};" for k, v in profile.items())
        family = (MONO_PALETTES if mono or profile["LOW_COLOR"] else
                  AMOLED_PALETTES if amoled else MIP_PALETTES)
        values += '\n    const PALETTE = "' + "".join(family).replace(" ", "") + '";'
        (code / "Panel.mc").write_text("module Panel {\n"+values+"\n}\n")
        paths = assets.relative_to(ROOT)
        jungle.extend([f"{name}.sourcePath = source;{mode};{code.relative_to(ROOT)};generated/tides",
                       f"{name}.resourcePath = {settings_paths[mono or profile['LOW_COLOR']]};{paths}",
                       f"{name}.excludeAnnotations = " + ("liveOnly" if previews else "demo")])
        configs.append({"device": name, "display": c["displayName"], "hardwareVariants": len(c["partNumbers"]),
                        "minAPI": min(api, key=lambda v: tuple(map(int,v.split(".")))), "watchFaceRAM": capacities["watchFace"],
                        "maxPrgFileSpace": c.get("maxPrgFilespace"), "antialias": aa, "fontResources": key, **profile})
    manifest(manifest_path, [p["device"] for p in configs], previews,
             f"{preview_device}/{fixture}/{theme}/{font}/{test}")
    jungle_path = ROOT / ("preview.jungle" if previews else "monkey.jungle")
    jungle_path.write_text("\n".join(jungle)+"\n")
    if not previews:
        (OUT / "device-matrix.json").write_text(json.dumps(configs, indent=2)+"\n")
    print(f"{len(configs)} SDK targets, {sum(p['hardwareVariants'] for p in configs)} hardware variants")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview-device")
    parser.add_argument("--fixture", choices=("tide","steps","heart","distance","calories"), default="tide")
    parser.add_argument("--theme", type=int, choices=range(len(THEMES)), default=0)
    parser.add_argument("--font", type=int, choices=range(len(FONTS)), default=0)
    args = parser.parse_args()
    generate(args.preview_device, args.fixture, args.theme, args.font)
