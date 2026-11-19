"""Audit native display bounds and adjacent data regions across the device matrix."""
import argparse
import json
import math
from pathlib import Path

from font_review import load
from generate import FONTS, OUT


def px(size, fraction):
    return int(size * fraction + .5)


def boxes_for(panel):
    w, h, small = (panel[k] for k in ("W", "H", "SMALL"))
    round_screen = panel["ROUND"]
    hardware = panel["SUB"] and not round_screen
    if panel["SUB"]:
        cx, cy, radius = (panel[k] for k in ("CX", "CY", "R"))
    else:
        cx, cy, radius = 0, 0, 0
    graph_top = max(px(h, .397 if hardware else .369), cy+radius+8 if panel["SUB"] else 0)
    graph_bottom = px(h, .600)
    graph_width = px(w, .552)
    graph_left = (w-graph_width)//2
    clock_x, clock_y = px(w, .157), px(h, .677)
    aux_x = px(w, .785)
    aux_width = px(w, .180)
    foot_y = px(h, .884)
    foot_span = px(w, .169 if round_screen else .204)
    foot_width = px(w, .165 if round_screen else .195)
    fonts = OUT / "profiles" / panel["fontResources"] / "fonts"
    seconds = load(fonts / "Seconds.fnt")
    clock_width = max(sum(load(fonts / f"{face}.fnt")[c][1] for c in "00:00") for face in FONTS)
    seconds_width = 2*seconds["0"][1]
    seconds_height = seconds["0"][0].height
    seconds_y = clock_y+small+2
    result = {
        "graph": [graph_left, graph_top, graph_left+graph_width-1, graph_bottom-3],
        "clock": [clock_x, clock_y, clock_x+clock_width-1, clock_y+panel["CLOCK_H"]-1],
        "aux": [aux_x-aux_width//2, clock_y, aux_x+aux_width//2, clock_y+small-1],
        "seconds": [aux_x-seconds_width//2-1, seconds_y, aux_x+seconds_width//2+1, seconds_y+seconds_height-1],
    }
    for i in range(3):
        x = w//2+(i-1)*foot_span
        result[f"footer{i+1}"] = [x-foot_width//2, foot_y, x+foot_width//2, foot_y+small-1]
    return result, graph_bottom, (cx,cy,radius)


def check(panel):
    w, h, small = (panel[k] for k in ("W", "H", "SMALL"))
    boxes, baseline, (cx, cy, r) = boxes_for(panel)
    if panel["device"].startswith("instinct3amoled"):
        assert panel["ROUND"] and panel["AMOLED"] and not panel["SUB"]
    assert boxes["graph"][3] - boxes["graph"][1] >= 9
    assert baseline+3+small <= boxes["clock"][1]
    assert boxes["clock"][2] < min(boxes["aux"][0], boxes["seconds"][0]), boxes
    assert max(boxes["clock"][3], boxes["seconds"][3]) < boxes["footer2"][1]
    assert boxes["footer1"][2] < boxes["footer2"][0] < boxes["footer2"][2] < boxes["footer3"][0]
    if panel["SUB"]:
        assert cx-r >= 0 and cy-r >= 0 and cx+r < w and cy+r < h
        half = (r*8//5)/2
        assert math.hypot(half, small+1) < r
        assert boxes["graph"][1] > cy+r
        if panel["ROUND"]:
            assert math.hypot(cx-w/2, cy-h/2)+r <= min(w,h)/2
    for region, (left, top, right, bottom) in boxes.items():
        assert 0 <= left < right < w and 0 <= top < bottom < h, (region, boxes[region])
        if panel["ROUND"]:
            assert all(math.hypot(x-w/2, y-h/2) < min(w,h)/2
                       for x in (left,right) for y in (top,bottom)), (region, boxes[region])
    return {"device": panel["device"], "width": w, "height": h, "subscreen": [cx,cy,r], "bounds": boxes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    rows = []
    for panel in json.loads((OUT / "device-matrix.json").read_text()):
        try:
            rows.append(check(panel))
        except AssertionError as issue:
            raise AssertionError(panel["device"], issue.args) from issue
    args.report.write_text(json.dumps(rows, indent=2)+"\n")
    print(f"{len(rows)} device layouts passed screen, circle, and adjacent-region tests")


if __name__ == "__main__":
    main()
