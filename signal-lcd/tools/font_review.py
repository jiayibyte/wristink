"""Render the complete native glyph repertoire and a legibility sheet."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build import ROOT, glyphs, profile

NAVY = "#0D151B"
CARD = "#18252F"
INK = "#E8F3DD"
SOFT = "#A9B9BF"
ACCENT = "#8DCBF4"


def run(text, font):
    masks = [font[c] for c in text]
    width = sum(advance for _,advance in masks) - (masks[-1][1]-masks[-1][0].width)
    strip = Image.new("L", (width,masks[0][0].height))
    x = 0
    for mask, advance in masks:
        strip.paste(mask,(x,0))
        x += advance
    return strip


def draw_run(canvas, text, font, xy, color, zoom=1):
    strip = run(text,font)
    if zoom != 1:
        strip = strip.resize((strip.width*zoom,strip.height*zoom),Image.Resampling.NEAREST)
    canvas.paste(color,xy,strip)


def validate(fonts, aa):
    for name, font in fonts.items():
        if "0" in font:
            digits = [font[c][0].tobytes() for c in "0123456789"]
            assert len(set(digits)) == 10, f"colliding digits in {name}"
        for c, (im, advance) in font.items():
            assert im.width < advance, (name,c)
            assert c == " " or im.getbbox() is not None, (name,c)
            if not aa or name not in ("Segment","Contour","Matrix","Date","Seconds"):
                assert set(im.getdata()) <= {0,255}, (name,c)
        if aa and name in ("Segment","Contour","Matrix","Date","Seconds"):
            assert any(0 < v < 255 for im,_ in font.values() for v in im.getdata()), name


def sheet(out, devices):
    title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf",46)
    ui = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf",23)
    detail = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf",21)
    canvas = Image.new("RGB",(1560,1120),NAVY)
    pen = ImageDraw.Draw(canvas)
    pen.text((44,33),"Signal LCD   /   Time fonts",font=title,fill=INK)
    pen.text((46,95),"Native glyphs, rendered from the same atlases used by the watch face",font=detail,fill=SOFT)
    positions = [220,720,1120]
    for d, x in zip(devices,positions):
        pen.text((x,150),f"{d['id'].upper()}  ·  {d['size']} PX",font=ui,fill=ACCENT)
    for i, name in enumerate(("Segment","Contour","Matrix")):
        y = 191 + i*276
        pen.rounded_rectangle((38,y,1522,y+249), radius=18,fill=CARD)
        pen.text((57,y+37),name,font=ui,fill=INK)
        for d, x, zoom in zip(devices,positions,(1,1,2)):
            font = glyphs(d["size"],d["aa"],d["lcd_size"])[name]
            draw_run(canvas,"10:58",font,(x,y+30),INK,zoom)
            draw_run(canvas,"23:59",font,(x,y+141),ACCENT,zoom)
        if i == 0:
            pen.text((1134,y+230),"2× nearest neighbor",font=detail,fill=SOFT)
    pen.text((46,1043),"Segment uses beveled bars. Contour joins the strokes. Matrix uses a 5 × 7 grid.",font=detail,fill=SOFT)
    canvas.save(out/"time-fonts.png")


def full_set(out,d):
    fonts = glyphs(d["size"],d["aa"],d["lcd_size"])
    if not d["amoled"]:
        fonts = {key: f for key, f in fonts.items() if key != "AlwaysOn"}
    title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf",25)
    text = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf",18)
    y = 78
    canvas = Image.new("RGB",(1100,860),NAVY)
    pen = ImageDraw.Draw(canvas)
    pen.text((30,24),d["name"] + "  /  all glyphs",font=title,fill=INK)
    for name,font in fonts.items():
        pen.text((30,y+4),name,font=text,fill=ACCENT)
        if name == "Label":
            lines = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789 -./%\'"]
        elif name == "Date":
            lines = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789 -/\'"]
        elif name == "Symbol":
            lines = ["".join(font)]
        else:
            lines = ["".join(font)]
        for line in lines:
            draw_run(canvas,line,font,(160,y),INK)
            y += next(iter(font.values()))[0].height+9
        y += 16
    canvas.crop((0,0,1100,y+16)).save(out/f"glyphs-{d['id']}.png")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("out",type=Path)
    args = cli.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    devices = [profile(id) for id in json.loads((ROOT/"devices.json").read_text())]
    unique = {(d["size"],d["aa"],d["lcd_size"]) for d in devices}
    for size,aa,lcd_size in unique:
        validate(glyphs(size,aa,lcd_size),aa)
    print(f"Font checks passed across {len(unique)} native raster profiles.")
    selected = [profile(id) for id in ("epix2","fenix7","instinct3solar45mm")]
    sheet(args.out,selected)
    for d in selected:
        full_set(args.out,d)


if __name__ == "__main__":
    main()
