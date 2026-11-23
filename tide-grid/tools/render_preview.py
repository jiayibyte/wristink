"""Draw marked design previews with the compiled project's native font atlases."""
from pathlib import Path
import argparse
import json

from PIL import Image, ImageDraw

from check_layout import boxes_for, px
from font_review import load
from generate import OUT

DEEP_SEA = ("#071518", "#10272b", "#28464b", "#edf6e8", "#9cb9b6", "#61e8c9", "#f5bb71")
INK = ("#000000", "#000000", "#ffffff", "#ffffff", "#ffffff", "#ffffff", "#ffffff")


def emit(panel, filename):
    w, h, small = (panel[k] for k in ("W", "H", "SMALL"))
    hardware = panel["SUB"] and not panel["ROUND"]
    bg, surface, border, ink, quiet, accent, secondary = INK if panel["MONO"] else DEEP_SEA
    canvas = Image.new("RGB", (w,h), bg)
    d = ImageDraw.Draw(canvas)
    bay = OUT / "profiles" / panel["fontResources"] / "fonts"
    ui, clock, seconds = (load(bay / f"{v}.fnt") for v in ("Instrument", "Dock", "Seconds"))

    def measure(s, font=ui):
        return sum(font[c][1] for c in s)

    def label(x, y, s, color=ink, font=ui, side="center"):
        if side == "center":
            x -= measure(s,font)//2
        elif side == "right":
            x -= measure(s,font)
        for c in s:
            glyph, advance = font[c]
            canvas.paste(color, (x,y,x+glyph.width,y+glyph.height), glyph)
            x += advance

    def pair(x, y, value, icon="", color=ink):
        if icon:
            gap = 2 if panel["SUB"] else px(w, .009)
            left = x - (measure(icon) + measure(value) + gap)//2
            label(left, y, icon, quiet, side="left")
            label(left+measure(icon)+gap,y,value,color,side="left")
        else:
            label(x,y,value,color)

    regions, graph_bottom, (cx, cy, radius) = boxes_for(panel)
    left = px(w, .343 if hardware else .313)
    y_header = px(h, .105 if hardware else .137)
    label(left if hardware else w//2, y_header, "CAPE TOWN", quiet)
    upper = px(h, .198 if hardware else .225)
    lower = upper + small + px(h, .014)
    pair(left, upper, "6:18", "n")
    pair(left, lower, "6:26P", "o")
    if panel["SUB"]:
        d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius), fill=surface, outline=border)
        pair(cx, cy-small-1, "3:03", "l", accent)
        pair(cx, cy+2, "196CM", color=secondary)
    else:
        x_tide = px(w,.734)
        pair(x_tide, upper, "3:03", "l", accent)
        pair(x_tide, lower, "196CM", color=quiet)

    x_graph, top, right, axis = regions["graph"]
    width = right-x_graph+1
    values = [28,46,66,87,102,113,120,122,120,114,105,93,79,65,51,38,27,21,19,22,29,42,54,62,73]
    gap = max(1,px(w,.004))
    for i,v in enumerate(values):
        x = x_graph+width*i//len(values)
        right_edge = x_graph+width*(i+1)//len(values)-gap-1
        bar_height = 1+px(axis-top-1,(v-min(values))/(max(values)-min(values)))
        if panel["MONO"] and i != 6:
            for y in range(axis-1,axis-bar_height-1,-2):
                d.line((x,y,right_edge,y), fill=accent)
        else:
            d.rectangle((x,axis-bar_height,right_edge,axis-1), fill=secondary if i==6 else accent)

    mx, my, r = px(w,.132), top+px(graph_bottom-top,.38), px(w,.047)
    d.ellipse((mx-r,my-r,mx+r,my+r),outline=quiet)
    label(mx,my+r+2,"1.0",quiet)
    gx, gy, size = px(w,.844), my+r, r+1
    d.arc((gx-size,gy-size,gx+size,gy+size),178,351,fill=quiet,width=max(1,w//176))
    d.line((gx,gy,gx+size-1,gy-size//2), fill=quiet, width=max(1,w//176))
    label(gx+size//2,my-small//2,"L",quiet)
    rail = px(w,.409)
    d.line((w//2-rail,graph_bottom,w//2+rail,graph_bottom),fill=quiet)
    label(px(w,.343),graph_bottom+3,"HOME",quiet)

    tx, ty = regions["clock"][:2]
    label(tx-3,ty+(panel["CLOCK_H"]-small)*2//3,"P",side="right")
    label(tx,ty,"10:58",font=clock,side="left")
    right_x = px(w,.785)
    date = "SUN 30" if measure("SUN 30") <= px(w,.180) else "SUN30"
    label(right_x,ty,date,quiet)
    label(right_x,ty+small+2,"50",font=seconds)

    for i,(value,icon,color) in enumerate((("8426","d",accent),("74","e",ink),("86%","c",accent)),1):
        left, y, right, _ = regions[f"footer{i}"]
        if measure(value)+measure(icon)+(2 if hardware else px(w,.009)) > right-left+1:
            icon = ""
        pair((left+right)//2,y,value,icon,color)
    canvas.save(filename)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("out", type=Path)
    args = cli.parse_args()
    config = json.loads((OUT / "device-matrix.json").read_text())
    for row in config:
        if row["device"] in ("fenix847mm","instinct3solar45mm"):
            emit(row,args.out/f"layout-preview-{row['device']}.png")
