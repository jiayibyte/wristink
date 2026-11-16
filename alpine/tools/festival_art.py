"""Original festival scenes, baked into one landscape bitmap per state.
Decorative light trails are artwork; the Sun and Moon are drawn by Sky at runtime.
"""
import math
from PIL import ImageDraw

PALETTES={
 1:(0xA01036,0xFFB35C,0xFFF8DC,0xFFC788,0xB74862,0x68284D),
 2:(0x063E69,0x30CEAE,0xFFFFFF,0xAAFFEE,0x278C98,0x124D67),
 3:(0x461C83,0xF88757,0xFFF4DC,0xEBC1FF,0x9C58BA,0x49276E),
 4:(0x142B78,0x83ACED,0xFFF5D7,0xDAE9FF,0x627AC4,0x273D88)}
MIP_PALETTES={
 1:(0xAA0055,0xFFAA55,0xFFFFFF,0xFFAAAA,0xAA5555,0xAA0055),
 2:(0x005555,0x55FFAA,0xFFFFFF,0xAAFFFF,0x00AAAA,0x005555),
 3:(0x5500AA,0xFFAA55,0xFFFFFF,0xFFAAFF,0xAA55AA,0x550055),
 4:(0x0000AA,0x55AAFF,0xFFFFAA,0xAAAAFF,0x5555AA,0x000055)}

class Brush:
    def __init__(self,im,holiday,mono):
        self.d=ImageDraw.Draw(im);self.mono=mono
        self.sx=im.width/(176 if mono else 260);self.sy=im.height/(176 if mono else 260)
        self.gold=1 if mono else '#ffe6a0'
        self.main=1 if mono else ['','#ff684f','#74ffcd','#ffad51','#ffe4a0'][holiday]
        self.dark=0 if mono else ['','#9b193c','#135967','#542166','#334b91'][holiday]
        self.white=1 if mono else '#fff9e8'
    def pt(self,x,y):return round(x*self.sx),round(y*self.sy)
    def line(self,points,c=None,w=1):
        self.d.line([self.pt(x,y) for x,y in points],fill=self.gold if c is None else c,width=max(1,round(w*self.sx)),joint='curve')
    def poly(self,points,c=None):self.d.polygon([self.pt(x,y) for x,y in points],fill=self.gold if c is None else c)
    def ellipse(self,box,c):self.d.ellipse((*self.pt(*box[:2]),*self.pt(*box[2:])),fill=c)
    def star(self,x,y,r=2,c=None):
        self.poly([(x,y-r),(x+1,y-1),(x+r,y),(x+1,y+1),(x,y+r),(x-1,y+1),(x-r,y),(x-1,y-1)],c)
    def burst(self,x,y,r):
        for i in range(12):
            a=i*math.pi/6
            self.line([(x+r*.45*math.cos(a),y+r*.45*math.sin(a)),(x+r*math.cos(a),y+r*math.sin(a))],self.main if i%2 else self.gold)
            self.ellipse((x+(r+3)*math.cos(a)-.5,y+(r+3)*math.sin(a)-.5,x+(r+3)*math.cos(a)+.5,y+(r+3)*math.sin(a)+.5),self.gold)
        self.star(x,y,2,self.white)
    def lantern(self,x,y,r):
        self.line([(x,y-r-14),(x,y-r-1)])
        self.ellipse((x-r,y-r,x+r,y+r),self.main)
        self.line([(x-r+2,y-r),(x+r-2,y-r)],self.gold,2)
        self.line([(x-r+2,y+r),(x+r-2,y+r)],self.gold,2)
        self.line([(x,y-r+2),(x,y+r-2)],self.gold)
        self.line([(x-r*.5,y-r+2),(x-r*.7,y),(x-r*.5,y+r-2)],self.dark)
        self.line([(x+r*.5,y-r+2),(x+r*.7,y),(x+r*.5,y+r-2)],self.dark)
        self.line([(x,y+r+1),(x,y+r+7)])
        self.line([(x-2,y+r+5),(x-2,y+r+8)])
        self.line([(x+2,y+r+5),(x+2,y+r+8)])


def aurora(im,mono):
    """Offline decorative light ribbons, shared by the standalone skin and Christmas."""
    b=Brush(im,2,mono)
    ribbons=[(0,37,24,10),(5,53,18,8),(2,65,17,5)] if mono else [(0,64,37,18),(6,85,28,15),(3,102,24,12)]
    for i,(start,y,amplitude,width) in enumerate(ribbons):
        points=[(start+x,y-amplitude*math.sin((x+18+i*7)*math.pi/(140 if mono else 215))) for x in range(0,176 if mono else 261,3)]
        if mono:b.line(points,b.main)
        else:
            for thickness,c in [(width+5,'#126a83'),(width,'#209fa7'),(width*.6,'#40d9bb'),(1,'#aaffdd')]:b.line(points,c,thickness)
    return im


def backdrop(im,holiday,mono):
    if not holiday:return im
    b=Brush(im,holiday,mono)
    if holiday==1:
        for x,y,r in ([(31,29,12),(99,18,8)] if mono else [(53,62,23),(204,57,20),(85,37,10)]):b.burst(x,y,r)
        b.line([(10,46),(36,39),(56,43)],b.gold)
    elif holiday==2:
        # Aurora ribbons, not falling snow. Snow remains driven by real weather.
        aurora(im,mono)
        for x,y in ([(32,27),(99,18)] if mono else [(47,45),(92,33),(207,45),(224,76)]):b.star(x,y,3,b.white)
    elif holiday==3:
        # Luminous purple ribbons and a bat swarm; no decorative fake moon.
        if not mono:
            for i,c in enumerate(['#6334a1','#8a4fb5','#ab65c6']):
                b.line([(4,88+i*4),(28,69+i*3),(68,63+i*3),(99,50+i*3)],c,3-i*.6)
                b.line([(172,48+i*4),(204,55+i*4),(237,81+i*3),(260,92+i*2)],c,3-i*.6)
        bats=[(29,31,8),(53,23,6),(99,20,5)] if mono else [(44,66,14),(77,47,9),(212,64,13),(184,38,7)]
        for x,y,r in bats:
            b.poly([(x-r,y-r*.45),(x-r*.5,y-r*.3),(x-r*.16,y),(x,y-r*.35),(x+r*.16,y),(x+r*.5,y-r*.3),(x+r,y-r*.45),(x+r*.65,y+r*.35),(x+r*.3,y+r*.15),(x,y+r*.45),(x-r*.3,y+r*.15),(x-r*.65,y+r*.35)],b.main if mono else '#24154f')
            if not mono:b.ellipse((x-1,y,x+1,y+1),b.gold)
    else:
        # Golden wind/cloud scrolls frame the actual astronomical moon.
        for offset in (0,6):
            points=[(x,54+offset+8*math.sin((x-22)*math.pi/66)) for x in range(11,86,2)]
            b.line(points,b.gold,1 if mono else 1.4)
        if not mono:
            for offset in (0,6):b.line([(189,66+offset),(204,58+offset),(222,61+offset),(238,76+offset)],b.gold,1.2)
        for x,y in ([(30,29),(54,24),(99,18)] if mono else [(42,53),(76,40),(217,47),(193,31)]):b.star(x,y,2,b.gold)
    return im


def decorate(im,holiday,mono):
    if not holiday:return im
    b=Brush(im,holiday,mono)
    if holiday==1:
        if mono:b.lantern(30,37,7);b.lantern(103,28,5)
        else:b.lantern(39,77,11);b.lantern(219,75,10);b.lantern(81,48,6)
        x,y=(50,60) if mono else (64,116)
        b.line([(x,y),(x,y-11)]);b.poly([(x,y-11),(x+9,y-8),(x,y-4)],b.main)
        # Warm edge lights continue into the valley, clear of the clock/data.
        if not mono:
            for x,y in [(9,119),(17,126),(241,120),(249,115)]:b.star(x,y,2,b.gold)
    elif holiday==2:
        def tree(x,y,h):
            b.poly([(x,y-h),(x-h*.18,y-h*.65),(x-h*.09,y-h*.65),(x-h*.33,y-h*.32),(x-h*.19,y-h*.32),(x-h*.46,y),(x+h*.46,y),(x+h*.19,y-h*.32),(x+h*.33,y-h*.32),(x+h*.09,y-h*.65),(x+h*.18,y-h*.65)],b.main)
            b.line([(x,y),(x,y+3)],b.gold,2);b.star(x,y-h-2,2,b.gold)
            if not mono:
                b.line([(x-h*.17,y-h*.57),(x+h*.18,y-h*.42),(x-h*.28,y-h*.23),(x+h*.32,y-h*.08)],b.gold)
                for dx,dy in [(-.1,-.45),(.12,-.25),(-.19,-.15)]:b.ellipse((x+h*dx-1,y+h*dy-1,x+h*dx+1,y+h*dy+1),'#ff8877')
        tree(148 if mono else 230,80 if mono else 133,19 if mono else 37)
        if not mono:tree(12,133,23);tree(247,129,24)
        for x,y in ([(31,32),(55,38)] if mono else [(42,64),(79,51),(214,54)]):
            b.line([(x,y-13),(x,y-5)]);b.ellipse((x-4,y-4,x+4,y+4),b.main);b.line([(x-2,y-2),(x+2,y+2)],b.gold)
    elif holiday==3:
        x,y=(20,77) if mono else (24,128);r=6 if mono else 11
        b.ellipse((x-r,y-r*.7,x+r,y+r*.7),b.main)
        b.line([(x,y-r*.7),(x+2,y-r)],b.gold,2)
        b.poly([(x-r*.6,y),(x-r*.35,y-r*.4),(x-r*.12,y)],b.dark)
        b.poly([(x+r*.12,y),(x+r*.35,y-r*.4),(x+r*.6,y)],b.dark)
        b.line([(x-r*.4,y+r*.3),(x-r*.16,y+r*.48),(x,y+r*.3),(x+r*.2,y+r*.48),(x+r*.45,y+r*.25)],b.dark,1 if mono else 2)
        if not mono:
            b.line([(242,133),(238,111),(240,94),(236,84)],'#3b215c',3)
            b.line([(238,114),(227,106),(225,95)],'#3b215c',2)
            b.line([(239,106),(250,99),(253,89)],'#3b215c',2)
    else:
        # Osmanthus branches and rabbit; never force a full moon for Mid-Autumn.
        for x,y in ([(21,50),(35,45),(45,52)] if mono else [(13,95),(25,87),(38,82),(48,94)]):
            b.line([(x-9,y+8),(x,y),(x+6,y-4)],b.gold)
            for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:b.ellipse((x+dx-1,y+dy-1,x+dx+1,y+dy+1),b.gold)
        x,y=(149,78) if mono else (231,131)
        b.ellipse((x-6,y-4,x+4,y+3),b.white);b.ellipse((x+1,y-9,x+7,y-3),b.white)
        b.line([(x+3,y-7),(x+2,y-16)],b.white,2);b.line([(x+5,y-7),(x+8,y-15)],b.white,2)
        b.ellipse((x+5,y-7,x+5.7,y-6),b.dark)
        if not mono:
            # A miniature pavilion sits on the opposite ridge.
            b.poly([(11,126),(24,119),(37,126),(30,125),(18,125)],b.gold)
            b.line([(17,126),(17,134),(31,134),(31,126)],b.gold)
            b.line([(24,125),(24,134)],b.gold)
    return im
