"""Named palettes for AMOLED, 64-color MIP, and 8-color MIP targets."""
import math

# Role order: outside background, LCD fill, LCD text, outside text, data icons, LCD frame.
# Theme IDs are persistent Connect IQ property values. Append new themes.
_THEMES = (
    ("Blue LCD",          "091019 AAB597 19241C FFFFFF F3C383 2B6CBC", "000000 AAAAAA 000000 FFFFFF FFAA55 0055AA", "000000 FFFF00 000000 FFFFFF FFFF00 00FFFF"),
    ("Amber Night",       "080A0A 161B1D DCC09C FFFFFF C5AC8F 8D8F89", "000000 000000 FFDDAA FFFFFF FFFFAA AAAAAA", "000000 000000 FFFFFF FFFFFF FFFF00 FFFFFF"),
    ("Moss",              "0E1812 1F3020 EDF6D2 FFFFFF F8CC80 537548", "000000 005500 FFFFAA FFFFFF FFFF55 55AA55", "000000 000000 FFFF00 FFFFFF 00FF00 00FF00"),
    ("Orchid",            "18121F 302039 F4EAFF FFFFFF FFADCB 795989", "000000 550055 FFFFFF FFFFFF FFAA55 AA55AA", "000000 000000 FFFFFF FFFFFF FF00FF FF00FF"),
    ("Silver",            "101419 262D36 EEF4FA FFFFFF B9CAD7 526777", "000000 555555 FFFFFF FFFFFF FFAAAA AAAAAA", "000000 0000FF FFFFFF FFFFFF FFFFFF FFFFFF"),
    ("Light LCD",         "E5EADB BCC7AE 172A24 172A24 823D23 79958A", "FFFFFF FFFFAA 000000 000000 AA0000 555555", "FFFFFF FFFF00 000000 000000 FF0000 000000"),
    ("Ice Blue",          "080F18 142A38 9EDFFF E4F4FF 74C7FD 497C9D", "000000 000055 AAFFFF FFFFFF 55AAFF 5555AA", "000000 0000FF 00FFFF FFFFFF 00FFFF 00FFFF"),
    ("Phosphor Green",    "090F0B 15231B A3F568 DDFCD2 91DB66 557B42", "000000 005500 55FF55 FFFFFF 55FF55 55AA55", "000000 000000 00FF00 FFFFFF 00FF00 00FF00"),
    ("Copper",            "140D09 301C14 FFAD76 FFE8D8 E9A177 9C6144", "000000 550000 FFAA55 FFFFFF FFAA55 AA5500", "000000 000000 FFFF00 FFFFFF FF0000 FF0000"),
    ("Crimson",           "130C11 321822 FFA0B8 FFE6EC F691A9 A64B69", "000000 550000 FFAAAA FFFFFF FFAAAA AA5555", "000000 000000 FF0000 FFFFFF FF00FF FF0000"),
    ("Ocean Teal",        "081618 112D2B 79E8CE DDF9F2 EAC48A 528F85", "000000 005555 AAFFFF FFFFFF FFAA55 55AAAA", "000000 000000 00FFFF FFFFFF FFFF00 00FFFF"),
    ("Rose Quartz",       "1A1118 DAAFC2 492236 FFF0F7 F4ACCB AB718F", "000000 FFAAAA 550055 FFFFFF FFAAFF AA55AA", "000000 FF00FF 000000 FFFFFF FF00FF FFFFFF"),
    ("Sepia Paper",       "E6D6B7 F7E9CC 493020 523625 864326 A57E54", "FFFFAA FFFFFF 552200 553300 AA0000 AA5500", "FFFF00 FFFFFF 000000 000000 FF0000 000000"),
    ("Signal Yellow",     "10151E 1D2433 FFE070 FFF3CF 84CAD2 68768B", "000000 000055 FFFF55 FFFFFF 55FFFF 55AAAA", "000000 0000FF FFFF00 FFFFFF 00FFFF FFFF00"),
)

THEME_NAMES = tuple(row[0] for row in _THEMES)


def _colors(row):
    return [int(color,16) for color in row.split()]


def rgb(n):
    return (n >> 16, (n >> 8) & 255, n & 255)


def _luminance(color):
    parts = [channel/255 for channel in rgb(color)]
    linear = [p/12.92 if p <= .04045 else ((p+.055)/1.055)**2.4 for p in parts]
    return sum(p*w for p,w in zip(linear,(.2126,.7152,.0722)))


def contrast(a,b):
    dark,light = sorted((_luminance(a),_luminance(b)))
    return (light+.05)/(dark+.05)


def display_palettes(compiler, mono, amoled):
    if mono:
        return []
    if amoled:
        return [_colors(row[1]) for row in _THEMES]

    colors = [int(c,16) for c in compiler.get("palette",{}).get("colors",[]) if c != "TRANSPARENT"]
    if not colors:
        # Standard ARGB2222 RGB channel values for 64-color Garmin MIP.
        levels = (0,85,170,255)
        colors = [r<<16 | g<<8 | b for r in levels for g in levels for b in levels]
    variant = 3 if len(colors) <= 8 else 2
    result = []
    for row in _THEMES:
        name = row[0]
        mapped = [min(colors,key=lambda p:math.dist(rgb(p),rgb(n))) for n in _colors(row[variant])]
        bg,lcd,ink,body,icon,frame = mapped
        if contrast(lcd,ink)<3.5 or contrast(bg,body)<3.5 or icon==bg:
            raise ValueError(f"Insufficient palette contrast for {name} on {compiler['deviceId']}")
        result.append(mapped)
    return result
