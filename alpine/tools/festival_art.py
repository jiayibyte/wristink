"""Original, sparse seasonal ornaments. Never draw a fake moon or weather cloud."""
from PIL import Image,ImageDraw

PALETTES={
 1:(0x8A1829,0xEEAD66,0xFFF0C2,0xE3B493,0x6D3B52,0x36273C),
 2:(0x123F3E,0x3A8874,0xF2FFF2,0xAFD9CA,0x2B6566,0x143B46),
 3:(0x6A3048,0xEFB56B,0xFFF0D5,0xDFC0A1,0x6E5162,0x312A43),
 4:(0x162956,0x536E9D,0xFFF1CF,0xBBCFE1,0x3F5F80,0x172E49)}

def decorate(im,holiday,mono):
    if not holiday:return im
    d=ImageDraw.Draw(im);sx=im.width/(176 if mono else 260);sy=im.height/(176 if mono else 260)
    gold=1 if mono else '#f3cb77';main=1 if mono else ['','#df524b','#86c9aa','#f3a45c','#e5d6a5'][holiday]
    dark=0 if mono else ['','#7a2633','#154e49','#553651','#243a63'][holiday]
    def pt(x,y):return (round(x*sx),round(y*sy))
    def line(points,c=gold):d.line([pt(x,y) for x,y in points],fill=c,width=max(1,round(sx)))
    def poly(points,c=gold):d.polygon([pt(x,y) for x,y in points],fill=c)
    def ellipse(box,c):d.ellipse((*pt(*box[:2]),*pt(*box[2:])),fill=c)
    def star(x,y,r=2):
        poly([(x,y-r),(x+1,y-1),(x+r,y),(x+1,y+1),(x,y+r),(x-1,y+1),(x-r,y),(x-1,y-1)])
    def lantern(x,y,r=5):
        line([(x,y-9),(x,y-r-1)])
        ellipse((x-r,y-r,x+r,y+r),main)
        line([(x-r+1,y-r),(x+r-1,y-r)])
        line([(x-r+1,y+r),(x+r-1,y+r)])
        line([(x,y-r+2),(x,y+r-2)],dark)
        line([(x,y+r+1),(x,y+r+5)])
    if holiday==1:
        lantern(28 if mono else 43,29 if mono else 54,5 if mono else 7)
        if not mono:lantern(216,47,6)
        for x,y in ([(48,23),(57,36),(94,20)] if mono else [(69,42),(189,58),(230,68)]):star(x,y)
        # A small festive pennant on the shoulder, away from the summit.
        x,y=(49,59) if mono else (64,112)
        line([(x,y),(x,y-9)]);poly([(x,y-9),(x+7,y-7),(x,y-4)],main)
    elif holiday==2:
        # Ornament balls are suspended, so they cannot be confused with snowfall.
        for x,y in ([(30,28),(53,34)] if mono else [(42,48),(70,58),(217,48)]):
            line([(x,y-9),(x,y-4)]);ellipse((x-3,y-3,x+3,y+3),main);line([(x-1,y-1),(x+1,y+1)],dark)
        star(94 if mono else 190,22 if mono else 47,3)
        x,y=(148,78) if mono else (226,128)
        poly([(x,y-13),(x-4,y-7),(x-2,y-7),(x-6,y),(x+6,y),(x+2,y-7),(x+4,y-7)],main)
        line([(x,y),(x,y+3)]);star(x,y-15,1)
    elif holiday==3:
        for x,y in ([(34,30),(59,25)] if mono else [(46,53),(80,45),(217,51)]):
            poly([(x-6,y-3),(x-3,y-2),(x-1,y),(x,y-2),(x+1,y),(x+3,y-2),(x+6,y-3),(x+4,y+2),(x+2,y+1),(x,y+3),(x-2,y+1),(x-4,y+2)],main)
        x,y=(21,77) if mono else (32,132)
        ellipse((x-5,y-4,x+5,y+4),main);line([(x,y-4),(x+1,y-7)])
        poly([(x-3,y),(x-2,y-2),(x-1,y)],dark);poly([(x+1,y),(x+2,y-2),(x+3,y)],dark)
        line([(x-2,y+2),(x+2,y+2)],dark)
    else:
        # Osmanthus blossom motifs; astronomical moon stays entirely dynamic.
        for x,y in ([(32,29),(54,24),(94,21)] if mono else [(43,53),(75,42),(214,52)]):
            for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:ellipse((x+dx-1,y+dy-1,x+dx+1,y+dy+1),gold)
            ellipse((x,y,x,y),dark)
        x,y=(149,77) if mono else (226,128)
        # Small rabbit silhouette in the valley, separate from the snow planes.
        ellipse((x-4,y-3,x+3,y+2),main);ellipse((x+1,y-6,x+5,y-2),main)
        line([(x+2,y-5),(x+1,y-10)]);line([(x+4,y-5),(x+5,y-10)])
    return im
