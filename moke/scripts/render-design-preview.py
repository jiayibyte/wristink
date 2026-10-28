"""Offline design preview using the project's real font atlases. NOT a simulator capture."""
from pathlib import Path
import io
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = dict((k, int(v)) for k, v in re.findall(r"const (\w+) = (\d+);", (ROOT / "source/FaceLayout.mc").read_text()))
demo = (ROOT / "preview/PreviewMode.mc").read_text()
VALUES = json.loads((ROOT / "config/preview-data.json").read_text())["values"]
HISTORY = json.loads(re.search(r"function history\(\).*?return (\[.*?\]);", demo).group(1))
MOVE_LEVEL = int(re.search(r"const MOVE_BAR_LEVEL = (\d+);",demo).group(1))
BODY_BATTERY = int(re.search(r"const BODY_BATTERY = (\d+);",demo).group(1))
INTENSITY_MINUTES = int(re.search(r"const INTENSITY_MINUTES = (\d+);",demo).group(1))
INTENSITY_GOAL = int(re.search(r"const INTENSITY_WEEK_GOAL = (\d+);",demo).group(1))/7
WEATHER_GLYPHS = [json.loads(values) for _, values in sorted(re.findall(r"case (\d+):return (\[.*?\]);", (ROOT / 'source/WeatherGlyphs.mc').read_text()),key=lambda item:int(item[0]))]


class Font:
    def __init__(self, name, root=None):
        root = root or ROOT / "resources/fonts"
        self.atlas = Image.open(root / f"{name}.png").getchannel("A")
        self.chars = {}
        for row in (root / f"{name}.fnt").read_text().splitlines():
            if row.startswith("char id="):
                d = dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)", row))
                self.chars[d["id"]] = d

    def width(self, text):
        return sum(self.chars[ord(c)]["xadvance"] for c in text)

    def draw(self, image, x, y, text, color, center=False):
        x = int(x - self.width(text) // 2) if center else int(x)
        for c in text:
            g = self.chars[ord(c)]
            box = (g["x"], g["y"], g["x"] + g["width"], g["y"] + g["height"])
            image.paste(color, (x + g["xoffset"], int(y) + g["yoffset"]), self.atlas.crop(box))
            x += g["xadvance"]


FONTS = {name: Font(name) for name in ("compact", "data", "compact-small", "date", "time", "heart", "heart-small", "circle-value", "circle-value-small", "seconds", "days", "chart")}


def icon(d, kind, x, y, fg, bg):
    fg, bg = (fg,)*3, (bg,)*3
    if kind in (1,17):
        d.rectangle((x, y + 2, x + 11, y + 9), outline=fg)
        d.rectangle((x + 12, y + 4, x + 13, y + 7), fill=fg)
        d.rectangle((x + 2, y + 4, x + 7, y + 7), fill=fg)
    elif kind == 2:
        for cx, cy in ((x + 3, y + 4), (x + 9, y + 6)):
            d.ellipse((cx - 2, cy - 4, cx + 2, cy + 4), fill=fg)
            d.ellipse((cx - 1, cy + 6, cx + 1, cy + 8), fill=fg)
    elif kind == 5:
        d.polygon([(x + 7, y), (x + 12, y + 7), (x + 11, y + 12), (x + 5, y + 14), (x + 1, y + 10), (x + 2, y + 6), (x + 5, y + 8)], fill=fg)
        d.ellipse((x + 5, y + 9, x + 9, y + 13), fill=bg)
    elif kind == 6:
        d.ellipse((x + 1, y + 1, x + 7, y + 7), fill=fg)
        d.ellipse((x + 7, y + 1, x + 13, y + 7), fill=fg)
        d.polygon([(x + 1, y + 5), (x + 13, y + 5), (x + 7, y + 13)], fill=fg)
    elif kind == 7:
        # Same rain glyph as the full-data native preview build.
        for row,bits in enumerate(WEATHER_GLYPHS[4]):
            for col in range(15):
                if bits & (1<<col): d.point((x+col,y+row),fill=fg)
    elif kind == 16:
        d.ellipse((x + 4, y + 7, x + 10, y + 13), outline=fg)
        d.rectangle((x + 6, y, x + 8, y + 9), outline=fg)
        d.line((x + 10, y + 2, x + 13, y + 2), fill=fg)
        d.line((x + 10, y + 5, x + 12, y + 5), fill=fg)
    elif kind == 18:
        d.polygon([(x+12,y+5),(x+10,y+7),(x+6,y+2),(x,y+12),(x+16,y+12)],fill=fg)


def card(kind):
    image = Image.new("RGBA", (28, 13))
    d = ImageDraw.Draw(image)
    if kind == "beijing":
        d.rounded_rectangle((0, 0, 27, 12), radius=2, fill="black", outline="white")
        svg = ET.parse(ROOT / "resources/drawables/beijing-card.svg").getroot()
        for rect in svg.findall(".//{http://www.w3.org/2000/svg}g[@fill='#fff']/{http://www.w3.org/2000/svg}rect"):
            x, y, w, h = (int(rect.get(k)) for k in ("x", "y", "width", "height"))
            d.rectangle((x, y, x + w - 1, y + h - 1), fill="white")
        d.arc((12, 5, 30, 21), 180, 330, fill="white")
        d.arc((15, 8, 29, 22), 180, 330, fill="white")
    else:
        d.rounded_rectangle((0, 0, 27, 12), radius=2, fill="white", outline="black")
        def xy(p): return (5.8 + p[0] * .8, 1.1 + p[1] * .8)
        def curve(a, b, c, e):
            return [xy(((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*e[0], (1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*e[1])) for t in (i/30 for i in range(31))]
        for a,b in [((9,0),(9,5)),((3,2.5),(15,2.5)),((2,5.5),(14,5.5))]: d.line([xy(a),xy(b)],fill="black",width=1)
        for ps in [((14,5.5),(12,9),(7,12),(3.2,11.7)),((3.2,11.7),(-.6,11.4),(0,8.2),(3.4,8.3)),((3.4,8.3),(8.6,8.3),(13.9,12.4),(19.7,13.4))]: d.line(curve(*ps),fill="black",width=1)
    return image


def render(dark, seconds=False):
    fg, bg = (255, 0) if dark else (0, 255)
    image = Image.new("RGB", (176, 176), (bg,)*3)
    d = ImageDraw.Draw(image)
    def metric(kind,x,y,fixed_font=None):
        icon(d,kind,x,y+(0 if y>=120 else 3),fg,bg)
        font=fixed_font or FONTS["data"]
        width=(LAYOUT["LOWER_LEFT_WIDTH"] if x<80 else LAYOUT["LOWER_RIGHT_WIDTH"]) if y>=120 else 74
        if y==LAYOUT["LOWER_Y"] and x==LAYOUT["STEP_X"]:width=LAYOUT["STEP_WIDTH"]
        if y>=LAYOUT["FOOTER_Y"] and x>=80:width=LAYOUT["FOOTER_RIGHT_WIDTH"]
        text_offset=LAYOUT["LOWER_TEXT_OFFSET"] if y>=120 else 17
        available=width-text_offset
        if fixed_font is None and font.width(VALUES[kind]) > available:font=FONTS["compact-small"]
        font.draw(image,x+text_offset,y+1,VALUES[kind],(fg,)*3)
    metric(7,34,5)
    d.line((83,14,94,14),fill=(fg,)*3,width=2)
    d.line((94,14,90,10),fill=(fg,)*3,width=2)
    d.line((94,14,90,18),fill=(fg,)*3,width=2)
    metric(17,10,LAYOUT["POWER_ROW_Y"])
    mx,my=LAYOUT["MOON_X"],LAYOUT["MOON_Y"]
    d.ellipse((mx-7,my-7,mx+7,my+7),outline=(fg,)*3,fill=(fg,)*3)
    d.pieslice((mx-6,my-6,mx+6,my+6),270,90,fill=(bg,)*3)
    d.ellipse((113,0,175,62),fill="black")
    count=min(8,max(0,__import__('math').ceil(BODY_BATTERY*8/100)))
    for i in range(count):
        tile=Image.open(ROOT/f'resources/drawables/energy-sector-{i}.png')
        image.paste(tile,(113,0),tile)
    ratio=min(1,max(0,INTENSITY_MINUTES/INTENSITY_GOAL)) if INTENSITY_GOAL>0 else 0
    if ratio:d.arc((115,2,173,60),-90,-90+360*ratio,fill="white",width=2)
    icon(d,6,137,LAYOUT["HEART_ICON_Y"],255,0)
    FONTS["circle-value"].draw(image,144,LAYOUT["HEART_VALUE_Y"],VALUES[6],(255,255,255),center=True)
    FONTS["data"].draw(image,8,49,"10/19 一",(fg,)*3)
    x,y=LAYOUT["MOVE_X"],LAYOUT["MOVE_Y"]
    d.ellipse((x+3,y,x+5,y+2),fill=(fg,)*3)
    for line in ((x+4,y+4,x+4,y+8),(x+1,y+7,x+4,y+4),(x+4,y+4,x+7,y+7),
                 (x+4,y+8,x+2,y+12),(x+4,y+8,x+6,y+12)):
        d.line(line,fill=(fg,)*3)
    for i in range(5):
        left=x+12+i*5
        d.rectangle((left,y+4,left+3,y+9),outline=(fg,)*3)
        if i<MOVE_LEVEL:d.rectangle((left+1,y+5,left+2,y+8),fill=(fg,)*3)
    FONTS["time"].draw(image,9,LAYOUT["TIME_Y"],"18:58",(fg,)*3)
    if seconds:
        FONTS["seconds"].draw(image,LAYOUT["SECONDS_X"],LAYOUT["SECONDS_Y"],"48",(fg,)*3,center=True)
    else:
        for kind,y in (("beijing",LAYOUT["CARD_TOP_Y"]),("alipay",LAYOUT["CARD_BOTTOM_Y"])):
            tile=card(kind);image.paste(tile,(LAYOUT["CARD_X"],y),tile)
    metric(2,LAYOUT["STEP_X"],LAYOUT["LOWER_Y"])
    left,top=LAYOUT["GRAPH_X"],LAYOUT["GRAPH_Y"]
    px,py,w,h=left+18,top+1,LAYOUT["GRAPH_WIDTH"]-20,LAYOUT["GRAPH_HEIGHT"]-LAYOUT["GRAPH_BOTTOM_INSET"]
    low,high=min(HISTORY),max(HISTORY)
    FONTS["chart"].draw(image,left+15-FONTS["chart"].width(str(high)),top,str(high),(fg,)*3)
    FONTS["chart"].draw(image,left+15-FONTS["chart"].width(str(low)),top+LAYOUT["GRAPH_LOW_LABEL_OFFSET"],str(low),(fg,)*3)
    points=[(round(px+i*w/(len(HISTORY)-1)),round(py+h-(v-low)*h/(high-low))) for i,v in enumerate(HISTORY)]
    d.line((px,py,px,py+h),fill=(fg,)*3)
    d.line((px,py+h,px+w,py+h),fill=(fg,)*3);d.line(points,fill=(fg,)*3)
    footer_font=FONTS["data"]
    if footer_font.width(VALUES[5])>LAYOUT["LOWER_LEFT_WIDTH"]-LAYOUT["LOWER_TEXT_OFFSET"] or footer_font.width(VALUES[18])>LAYOUT["FOOTER_RIGHT_WIDTH"]-LAYOUT["LOWER_TEXT_OFFSET"]:
        footer_font=FONTS["compact-small"]
    metric(5,LAYOUT["LOWER_LEFT_X"],LAYOUT["FOOTER_Y"],footer_font);metric(18,LAYOUT["LOWER_RIGHT_X"],LAYOUT["FOOTER_Y"],footer_font)
    return image


if __name__ == "__main__":
    folder=ROOT/"bin";folder.mkdir(exist_ok=True)
    for dark in (True,False):render(dark).save(folder/("design-dark.png" if dark else "design-light.png"))
    board=Image.new("RGB",(1152,674),"#e9e9e6")
    labels=ImageDraw.Draw(board)
    face=ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc",22,index=1)
    small=ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc",17,index=1)
    for dark,x,label in ((True,24,"黑底 · 演示数据"),(False,600,"白底 · 演示数据")):
        labels.text((x,18),label,font=face,fill="#222")
        board.paste(render(dark).resize((528,528),Image.Resampling.NEAREST),(x,60))
    labels.text((24,619),"静态设计预览，依据源码布局与实际字形生成；非佳明模拟器截图。",font=small,fill="#555")
    board.save(folder/"design-comparison.png")
    print("Saved offline design previews (not simulator screenshots).")
