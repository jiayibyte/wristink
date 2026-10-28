"""Decorative local-weather LCD skins; all share one geographic land mask."""
from PIL import Image

NAMES=[
 ('CLASSIC LCD','复古点阵'),('SOLID','旧版实心'),('COAST','极简海岸'),('STAR NIGHT','星夜反显'),
 ('DAWN','晨光横纹'),('DUSK','暮色斜纹'),('CLOUD DAY','白昼云纹'),('CLOUD NIGHT','云夜反显'),
 ('RAIN DAY','细雨点阵'),('RAIN NIGHT','夜雨斜纹'),('SNOW DAY','晴雪晶格'),('SNOW NIGHT','雪夜反显'),
 ('FOG','轻雾纬线'),('WIND','长风流纹'),('STORM DAY','雷暴线纹'),('STORM NIGHT','雷夜反显')]
INVERSE={3,7,9,11,15}

def bitmap(land,skin,night=False):
    reverse=skin in INVERSE
    image=Image.new('1',land.size,0 if reverse else 1)
    w,h=land.size
    def is_land(x,y):return 0<=x<w and 0<=y<h and land.getpixel((x,y))==0
    for y in range(h):
        for x in range(w):
            inside=is_land(x,y)
            edge=inside and any(not is_land(x+dx,y+dy) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)))
            if inside:
                pattern=(x%2==0 or y%2==0)
                if skin==1:pattern=True
                elif skin==2:pattern=edge or (x+3*y)%13==0
                elif skin in (4,10,11):pattern=(x+y)%3!=0
                elif skin==5:pattern=(x-y)%3!=0
                elif skin in (6,7):pattern=(x%3<2 or y%3==0)
                elif skin==12:pattern=(x+y)%2==0
                elif skin==13:pattern=y%3!=1
                elif skin in (14,15):pattern=(x+2*y)%4!=0
                if skin not in (0,1):pattern=pattern or edge
                if reverse and night and not edge:pattern=pattern and (x+y)%3!=1
                image.putpixel((x,y),(1 if pattern else 0) if reverse else (0 if pattern else 1))
            else:
                pattern=False
                if skin==3:pattern=(x*37+y*19)%173==0
                elif skin==4:pattern=y%6==3 and x%3==0
                elif skin==5:pattern=(x+2*y)%17==0
                elif skin in (6,7):pattern=(x//6+2*(y//4))%7==0 and x%6 in (1,2,3,4) and y%4 in (1,2)
                elif skin in (8,9):pattern=(x+2*y)%13==0 and y%4<2
                elif skin in (10,11):pattern=(x%13==4 and y%7 in (2,3,4)) or (y%7==3 and x%13 in (3,4,5))
                elif skin==12:pattern=y%7==3 and x%11<7
                elif skin==13:pattern=(y+(x//10)%3)%6==0 and x%17<12
                elif skin in (14,15):pattern=(x//4+2*(y//3))%11==0 and x%4 in (1,2) and y%3!=1
                if reverse:
                    if night:pattern=pattern and (x+y)%2==0
                    image.putpixel((x,y),1 if pattern else 0)
                else:
                    if night:pattern=pattern or (x%2==1 and y%2==1)
                    image.putpixel((x,y),0 if pattern else 1)
    # Exact old solid mask; the classic option restores the original graticule.
    if skin==0:
        for x in (15,29,44,59,73):
            for y in range(0,h,3):image.putpixel((x,y),0)
        for y in (7,21):
            for x in range(0,w,3):image.putpixel((x,y),0)
        for x in range(w):image.putpixel((x,14),0)
    return image

def select(kind,phase,minute):
    night=phase==0
    if kind==5:return 15 if night else 14
    if kind==3:return 9 if night else 8
    if kind==4:return 11 if night else 10
    if kind==6:return 12
    if kind==7:return 13
    if kind==2:return 7 if night else 6
    if phase==1:return 4
    if phase==3:return 5
    if night:return 3
    if kind==0:return 0
    if 600<=minute<720:return 1
    if 720<=minute<840:return 0
    return 2
