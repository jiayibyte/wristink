"""Check real bitmap-font ink bounds against the watch's small layout regions."""
from pathlib import Path
import json
import math
import re
import runpy
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = dict((k, int(v)) for k, v in re.findall(r"const (\w+) = (\d+);", (ROOT / "source/FaceLayout.mc").read_text()))


def ink(name, text, x, y, centered=False):
    folder = ROOT / "resources/fonts"
    rows = (folder / f"{name}.fnt").read_text().splitlines()
    chars = {}
    for row in rows:
        if row.startswith("char id="):
            values = dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)", row))
            chars[values["id"]] = values
    width = sum(chars[ord(c)]["xadvance"] for c in text)
    pen = x - math.floor(width / 2) if centered else x
    atlas = Image.open(folder / f"{name}.png").getchannel("A")
    points = []
    for c in text:
        g = chars[ord(c)]
        for py in range(g["height"]):
            for px in range(g["width"]):
                if atlas.getpixel((g["x"] + px, g["y"] + py)):
                    points.append((pen + g["xoffset"] + px, y + g["yoffset"] + py))
        pen += g["xadvance"]
    return points


checks = []
weather_source=(ROOT/'source/WeatherGlyphs.mc').read_text()
weather_rows={int(i):json.loads(rows) for i,rows in re.findall(r'case (\d+):return (\[.*?\]);',weather_source)}
weather_generator=runpy.run_path(str(ROOT/'scripts/make-weather-icons.py'))['glyph']
for kind in range(11):
    image=weather_generator(kind)
    expected=[sum(1<<x for x in range(15) if image.getpixel((x,y))) for y in range(15)]
    assert weather_rows[kind]==expected
checks.append({'weather_icons':'All 11 lazy-loaded glyphs match their original 15 x 15 pixels', 'bounded':True})
catalog=(ROOT/'source/EnergyCatalog.mc').read_text()
energy_x=json.loads(re.search(r'const X = (\[.*?\]);',catalog).group(1))
energy_y=json.loads(re.search(r'const Y = (\[.*?\]);',catalog).group(1))
for variant in range(4):
    paper=(255,255,255,255) if variant%2 else (0,0,0,255)
    expected=Image.new('RGBA',(63,63),paper)
    for sector in range(8):
        box=Image.open(ROOT/f'resources/drawables/energy-sector-{sector}.png').getbbox()
        tile=Image.open(ROOT/f'resources/drawables/energy-v{variant}-{sector}.png').convert('RGBA')
        expected.alpha_composite(tile,(box[0],box[1]))
        actual=Image.new('RGBA',(63,63),paper)
        level=Image.open(ROOT/f'resources/drawables/energy-level-v{variant}-n{sector+1}.png').convert('RGBA')
        actual.alpha_composite(level,(energy_x[sector],energy_y[sector]))
        assert ImageChops.difference(expected,actual).getbbox() is None
checks.append({"energy_composites":"All 32 style/count images match the original individual-sector rendering pixel for pixel", "identical":True})
for family in range(3):
    for text in ['8608','128m','100%']:
        for size in [16,14,12,10,8]:
            name=f'dataf{family}s{size}'
            font=(ROOT/f'resources/fonts/{name}.fnt').read_text()
            advance={int(c):int(w) for c,w in re.findall(r'char id=(\d+).*?xadvance=(\d+)',font)}
            height=int(re.search(r'lineHeight=(\d+)',font)[1])
            if sum(advance[ord(c)] for c in text)<=34 and height<=22:break
        points=ink(name,text,144,26,centered=True)
        assert all(125<=x<163 and 26<=y<50 for x,y in points)
checks.append({'circle_long_values':'Four-character values use fitting data fonts in all three families','bounded':True})
for family in range(3):
    for size in [16,14,12,10,8]:
        font=(ROOT/f'resources/fonts/dataf{family}s{size}.fnt').read_text()
        if int(re.search(r'lineHeight=(\d+)',font)[1])<=13:break
    date_points=ink(f'dataf{family}s{size}','10/19',8,49)
    assert max(y for x,y in date_points)<63
checks.append({'12h_date':'Large short dates leave room above the Chinese AM/PM marker','bounded':True})
for family,size in [(0,22),(1,22),(2,22),(2,26),(2,28)]:
    for value in ["9","99","100","199","299","--"]:
        points=ink(f"liveheartf{family}s{size}",value,144,27 if len(value)==3 else 26,centered=True)
        assert min(x for x,y in points)>=126 and max(x for x,y in points)<162
        assert min(y for x,y in points)>=25 and max(y for x,y in points)<50
    checks.append({"live_heart_font":f"family {family}, size {size}","two_three_digit_and_missing_values_fit_partial_clip":True})
for name,values,y in [("circle-value",("00","60","80","96","99"),LAYOUT["HEART_VALUE_Y"]),
                      ("circle-value-small",("100","128","199","240"),LAYOUT["HEART_SMALL_VALUE_Y"])]:
    for value in values:
        points = ink(name, value, 144, y, centered=True)
        assert all((x - 144) ** 2 + (py - 31) ** 2 <= 20 ** 2 for x, py in points), value
        assert min(py for x,py in points)>=23
        assert max(py for x,py in points)<=51
        checks.append({"heart_rate": value, "clear_of_icon_and_body_battery_sectors": True})
for i in range(8):
    alpha=Image.open(ROOT/f'resources/drawables/energy-sector-{i}.png').getchannel('A')
    points=[(x,y) for y in range(63) for x in range(63) if alpha.getpixel((x,y))]
    assert points and all(20.5<=math.hypot(x-31,y-31)<=26.5 for x,y in points)
    assert all(i*45+2.5<=(math.degrees(math.atan2(x-31,31-y))%360)<=i*45+42.5 for x,y in points)
checks.append({"body_battery":"8 disjoint annular sectors; no central or missing-sector pixels", "bounded":True})

for value in ("00:00", "18:58", "23:59"):
    points = ink("time", value, 9, LAYOUT["TIME_Y"])
    assert max(x for x, y in points) <= LAYOUT["CARD_X"] - 6, value
    assert max(y for x, y in points) < LAYOUT["LOWER_Y"], value
    checks.append({"time": value, "clear_of_cards_and_lower_data": True})

for name, text, x, y, right, bottom in [
    ("data", "12 106", LAYOUT["STEP_X"] + LAYOUT["LOWER_TEXT_OFFSET"], LAYOUT["LOWER_Y"] + 1, 96, 149),
    ("data", "9.7km", LAYOUT["LOWER_RIGHT_X"] + LAYOUT["LOWER_TEXT_OFFSET"], LAYOUT["LOWER_Y"] + 1, 168, 149),
    ("data", "1688", LAYOUT["LOWER_LEFT_X"]+LAYOUT["LOWER_TEXT_OFFSET"], LAYOUT["FOOTER_Y"]+1, 96, 169),
    ("data", "128m", LAYOUT["LOWER_RIGHT_X"]+LAYOUT["LOWER_TEXT_OFFSET"], LAYOUT["FOOTER_Y"]+1, 154, 169),
]:
    points = ink(name, text, x, y)
    assert max(px for px, py in points) < right, text
    assert max(py for px, py in points) < bottom, text
    checks.append({"text": text, "bounded": True})

assert LAYOUT["CARD_X"] + 28 <= 168
assert LAYOUT["WIND_X"] + 7 <= 96
assert LAYOUT["MOON_X"] + 7 <= 112
assert 10+LAYOUT['POWER_ROW_WIDTH'] <= LAYOUT['MOON_X']-8
assert LAYOUT["LOWER_LEFT_X"] >= 20
assert LAYOUT["STEP_X"]+1==min(x for x,y in ink("time","18:58",9,LAYOUT["TIME_Y"]))
assert LAYOUT["STEP_X"]+LAYOUT["STEP_WIDTH"]<=LAYOUT["LOWER_RIGHT_X"]-4
checks.append({"steps":"Icon left edge matches the main time; separate safe footer inset", "aligned":True})
for value in ("00", "58", "59"):
    points = ink("seconds", value, LAYOUT["SECONDS_X"], LAYOUT["SECONDS_Y"], centered=True)
    assert min(x for x, y in points) >= LAYOUT["SECONDS_LEFT"]
    assert max(x for x, y in points) < 168
    checks.append({"seconds": value, "right_margin_at_least_8px": True})
checks.append({"cards": "28 x 13", "right_margin_at_least_8px": True})
assert LAYOUT["LOWER_LEFT_X"]+LAYOUT["LOWER_LEFT_WIDTH"]<=LAYOUT["LOWER_RIGHT_X"]-4
assert LAYOUT["GRAPH_X"]==LAYOUT["LOWER_RIGHT_X"]
for label in ("12 106","605","128m"):
    points=ink("data",label,0,1)
    text_center=(min(y for x,y in points)+max(y for x,y in points))/2
    assert abs(text_center-7)<=1
checks.append({"lower_grid":"Shared right-column anchors and vertically centered icon/text pairs", "aligned":True})
points = ink("data", "10/19 一", 8, 49)
assert min(y for x, y in points) > LAYOUT["MOON_Y"] + 7
checks.append({"date": "10/19 一", "clear_of_moon_above": True})
assert max(x for x,y in points)<LAYOUT["MOVE_COMPACT_X"]-3
assert LAYOUT["MOVE_X"]+LAYOUT["MOVE_WIDTH"]<=112
assert LAYOUT["MOVE_Y"]+LAYOUT["MOVE_HEIGHT"]<LAYOUT["TIME_Y"]-6
assert LAYOUT["MOVE_COMPACT_X"]+12+5*3<=102-7
checks.append({"move_bar":"Date-right position clears date/time/heart window, compact variant clears optional moon", "bounded":True})
points=ink("data","24°",51,6)
assert max(x for x,y in points)<LAYOUT["WIND_X"]-7
assert max(y for x,y in points)<28
checks.append({"temperature":"24°","clear_of_wind_and_battery_row":True})
assert 'bold=0' in (ROOT/'resources/fonts/data.fnt').read_text().splitlines()[0]
for label, y in (("240",LAYOUT["GRAPH_Y"]),("60",LAYOUT["GRAPH_Y"]+LAYOUT["GRAPH_LOW_LABEL_OFFSET"])):
    points=ink("chart",label,LAYOUT["GRAPH_X"]+15, y, centered=False)
    # Labels are right-justified in the native drawing; subtract the advance here.
    advances=dict((int(m[0]),int(m[1])) for m in re.findall(r'char id=(\d+).*?xadvance=(\d+)',(ROOT/'resources/fonts/chart.fnt').read_text()))
    shift=sum(advances[ord(c)] for c in label)
    points=[(x-shift,py) for x,py in points]
    assert min(x for x,py in points)>=LAYOUT["GRAPH_X"]
    assert max(x for x,py in points)<LAYOUT["GRAPH_X"]+18
    assert max(py for x,py in points)<LAYOUT["GRAPH_Y"]+LAYOUT["GRAPH_HEIGHT"]-2
    checks.append({"heart_axis_label":label,"clear_of_plot_and_footer":True})
for label in ("28天","100天"):
    points=ink("data",label,27,LAYOUT["POWER_ROW_Y"]+1)
    assert max(x for x,y in points)<LAYOUT["MOON_X"]-8
    assert max(y for x,y in points)<49
    center=(min(y for x,y in points)+max(y for x,y in points))/2
    assert abs(center-LAYOUT["MOON_Y"])<=1
    checks.append({"battery_days":label,"clear_of_moon_and_date":True})
assert abs((LAYOUT["POWER_ROW_Y"]+8.5)-LAYOUT["MOON_Y"])<=1
checks.append({"power_row":"Battery outline, remaining-days text and moon share an optical center", "aligned":True})
assert LAYOUT["CARD_TOP_Y"] >= 80
assert LAYOUT["CARD_BOTTOM_Y"] - LAYOUT["CARD_TOP_Y"] - 13 >= 6
assert LAYOUT["CARD_BOTTOM_Y"] + 13 <= LAYOUT["GRAPH_Y"] - 6
assert LAYOUT["CARD_TOP_Y"] <= LAYOUT["SECONDS_Y"]
assert LAYOUT["SECONDS_Y"] + 21 <= LAYOUT["CARD_BOTTOM_Y"] + 13
assert abs((LAYOUT["CARD_TOP_Y"]+LAYOUT["CARD_BOTTOM_Y"]+13)/2-(LAYOUT["CARD_SINGLE_Y"]+6.5)) <= .5
assert LAYOUT["SECONDS_Y"] + 21 <= LAYOUT["GRAPH_Y"]
checks.append({"side_panel":"Cards and seconds share an exclusive centered area; lowered cards clear the heart bezel and chart", "bounded":True})

result = {"method": "Bitmap font ink geometry; not a simulator screenshot", "checks": checks}
(ROOT / "bin/layout-geometry-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(f"Passed {len(checks)} bitmap-font layout checks.")
