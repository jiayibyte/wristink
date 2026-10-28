"""Native-pixel monochrome assets. Fonts are rasterized at target size, never enlarged.
Natural Earth public-domain land polygons use the same equirectangular projection as the marker.
"""
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import json
import math
import shutil
from retro_style import digit as retro_digit, text as retro_text, fonts as retro_fonts, weather_glyph
from garmin_weather import icon as garmin_icon, generate as generate_weather, COARSE
from map_skins import NAMES as SKIN_NAMES, bitmap as skin_bitmap, select as select_skin

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resources/drawables'
OUT.mkdir(parents=True,exist_ok=True)
FONT=ROOT/'assets/fonts/Rajdhani-SemiBold.ttf'

@lru_cache()
def font(size):return ImageFont.truetype(str(FONT),size)

def text(im,x,y,value,color=0,size=11,center=False):
    scale=2 if size>=13 else 1
    retro_text(im,x,y,value,color,sx=scale,sy=scale,center=center)

def digit(n,w,h):
    return retro_digit(n,w,h)

def date_digit(n):
    # Keep the existing segment caps/bevels exactly; shorten one straight row
    # in each vertical half instead of changing typeface or scaling the raster.
    original=digit(n,8,15);result=Image.new('1',(8,13),1)
    for target,source in enumerate(y for y in range(15) if y not in (5,11)):
        result.paste(original.crop((0,source,8,source+1)),(0,target))
    return result

def land_mask():
    im=Image.new('1',(89,29),1);d=ImageDraw.Draw(im)
    data=json.loads((ROOT/'assets/ne_110m_land.geojson').read_text())
    def xy(ring):return [(round((lon+180)*88/360),round((90-lat)*28/180)) for lon,lat,*_ in ring]
    for feature in data['features']:
        geom=feature['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        for polygon in polys:
            d.polygon(xy(polygon[0]),fill=0)
            for hole in polygon[1:]:d.polygon(xy(hole),fill=1)
    return im

def world(night=False):
    return skin_bitmap(land_mask(),0,night)

def phased_world(utc_hour=8,day_of_year=301,skin=0):
    land=land_mask();day=skin_bitmap(land,skin,False);night=skin_bitmap(land,skin,True);im=day.copy()
    dec=math.radians(23.44*math.sin((day_of_year-80)*2*math.pi/365.2422))
    sun_lon=180-utc_hour*15
    for y in range(29):
        lat=math.radians(90-y*180/28)
        for x in range(89):
            lon=-180+x*360/88
            elevation=math.sin(lat)*math.sin(dec)+math.cos(lat)*math.cos(dec)*math.cos(math.radians(lon-sun_lon))
            if elevation<0:im.putpixel((x,y),night.getpixel((x,y)))
    return im

def weather_icon(kind,size=11):
    return garmin_icon(COARSE[kind],size)

@lru_cache()
def sun_mask():
    # Garmin-published filled sun/horizon symbol; one shared icon between times,
    # matching the native Instinct paired sunrise/sunset field. Build time only.
    source=ROOT/'assets/garmin-sun/official-sunrise-sunset.png'
    import hashlib
    metadata=json.loads((source.parent/'source.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==metadata['sha256']
    # Native-pixel tracing of the official six separate ink components.
    # Uniform downsampling joins the rays to the sun at this size; preserve
    # a full pixel of negative space instead of changing the official silhouette.
    rows=["......#......", "..#...#...#..", "...#.....#...", ".............",
          ".....###.....", "....#####....", "...#######...", "##.#######.##"]
    mask=Image.new('1',(13,8),0)
    for y,row in enumerate(rows):
        for x,pixel in enumerate(row):
            if pixel=='#':mask.putpixel((x,y),1)
    return mask

def sun_icon(im,x,y,color=1):
    im.paste(color,(x,y),sun_mask())

def circle_face(inset=0):
    im=Image.new('1',(63,63),0);d=ImageDraw.Draw(im)
    # Restore the substantial instrument-dial character, fitted inside the
    # physical 62px aperture rather than doubling the edge on its outer boundary.
    if inset:
        d.ellipse((inset,inset,62-inset,62-inset),fill=1)
        d.ellipse((inset+1,inset+1,61-inset,61-inset),outline=0)
    else:
        d.ellipse((-1,-1,63,63),fill=1)
        d.ellipse((1,1,60,60),outline=0)
    for i in range(60):
        a=math.radians(i*6-90)
        inner=25 if i%5==0 else 27
        d.line((round(31+inner*math.cos(a)),round(31+inner*math.sin(a)),round(31+28*math.cos(a)),round(31+28*math.sin(a))),fill=0)
    for x,y,s in ((31,7,'12'),(51,29,'3'),(31,50,'6'),(11,29,'9')):text(im,x,y,s,size=8,center=True)
    # The physical sub-screen is 62x62. Do not leave white pixels on the
    # final atlas row/column, which can be part of the adjacent main display.
    d.line((0,62,62,62),fill=0);d.line((62,0,62,62),fill=0)
    return im

def base():
    im=Image.new('1',(176,176),0);d=ImageDraw.Draw(im)
    d.rounded_rectangle((16,31,109,49),radius=4,fill=1);d.line((18,40,107,40),fill=0)
    d.rounded_rectangle((13,52,109,88),radius=4,outline=1)
    d.rounded_rectangle((15,54,107,86),radius=2,fill=1);im.paste(world(),(17,56))
    im.paste(circle_face(),(113,0))
    # Independent weather LCD below the hardware circle, above the date tab.
    d.rounded_rectangle((123,74,165,86),radius=3,fill=1)
    d.rounded_rectangle((10,106,165,150),radius=5,outline=1);d.rounded_rectangle((13,109,162,147),radius=3,fill=1)
    d.rounded_rectangle((79,90,165,110),radius=4,outline=1);d.rounded_rectangle((82,93,162,112),radius=2,fill=1)
    d.rectangle((82,105,161,112),fill=1);d.line((83,108,161,108),fill=0);d.line((119,94,119,107),fill=0)
    sun_icon(im,82,163)
    return im

def marker(im,lat,lon):
    x=17+round((lon+180)*88/360);y=56+round((90-lat)*28/180)
    d=ImageDraw.Draw(im);d.ellipse((x-3,y-3,x+3,y+3),fill=1)
    d.ellipse((x-2,y-2,x+2,y+2),outline=0);d.point((x,y),fill=0)

def render(hour=22,minute=8,second=36,day=30,month=6,dow='SUN',mode24=False,weather=3,location=True,utc_hour=8,skin=0):
    im=base();d=ImageDraw.Draw(im);h=hour if mode24 else (hour%12 or 12)
    im.paste(phased_world(utc_hour,skin=skin),(17,56))
    for i,n in enumerate(f'{h:02}{minute:02}'):im.paste(digit(int(n),22,35),([24,47,79,102][i],111))
    d.rectangle((72,122,74,124),fill=0);d.rectangle((72,133,74,135),fill=0)
    for i,n in enumerate(f'{second:02}'):im.paste(digit(int(n),13,24),(132+i*14,122))
    if not mode24:text(im,15,113,'PM' if hour>=12 else 'AM',size=8)
    text(im,100,96,dow,size=13,center=True)
    for i,n in enumerate(f'{month:02}{day:02}'):
        if i==0 and month<10:continue
        im.paste(date_digit(int(n)),([123,132,144,153][i],94))
    d.line((140,100,142,100),fill=0)
    for a,r,w in ((hour%12*30+minute*.5,11,3),(minute*6,16,2),(second*6,18,1)):
        a=math.radians(a-90);d.line((144,31,144+int(r*math.cos(a)),31+int(r*math.sin(a))),fill=0,width=w)
    d.ellipse((142,29,146,33),fill=0)
    text(im,67,6,'HR 76',1,size=16,center=True);text(im,63,21,'BAT 24.3D',1,center=True)
    text(im,42,33,'STEP 8608');text(im,42,43,'KCAL 1688')
    text(im,45,98,'ALT 128M',1,center=True);text(im,88,154,'DIST 6.42KM',1,center=True)
    # Match the native centered 31px time cells, not left-aligned preview labels.
    text(im,55,164,'06:04',1);text(im,105,164,'17:18',1)
    im.paste(weather_icon(weather,9),(129,76))
    for i,c in enumerate('24C'):im.paste(0,(143+i*6,77),weather_glyph(c))
    if location:marker(im,39.9,116.4)
    # Preview the actual main-screen aperture beside the circular hardware bezel.
    # The installable background itself is unchanged; the watch provides this mask.
    right_edges=(100,100,100,100,100,100,100,100,101,101,101,101,102,102,102,103,103,103,104)
    for y,right in enumerate(right_edges,31):d.line((right+1,y,109,y),fill=0)
    aperture=Image.new('1',(63,63),0);ImageDraw.Draw(aperture).ellipse((0,0,61,61),fill=1)
    for y in range(63):
        for x in range(63):
            if not aperture.getpixel((x,y)):im.putpixel((113+x,y),0)
    return im

def fonts():
    retro_fonts()

def main():
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    if (dist/'RetroWorld-preview.png').exists() and not (dist/'RetroWorld-before-1.2.1.png').exists():shutil.copy(dist/'RetroWorld-preview.png',dist/'RetroWorld-before-1.2.1.png')
    im=base();im.save(OUT/'dial.png');im.crop((113,0,176,63)).save(OUT/'circle.png');world().save(OUT/'map.png');world(True).save(OUT/'map-night.png');fonts()
    land=land_mask()
    for skin in range(len(SKIN_NAMES)):
        for night in (False,True):skin_bitmap(land,skin,night).save(OUT/f'map-skin-{skin}-{int(night)}.png')
    code='// Generated bitmap resource lookup; only the selected two bitmaps are loaded.\nmodule MapSkinResources {\nfunction get(skin,night) {switch(skin) {\n'
    for skin in range(len(SKIN_NAMES)):code+=f'case {skin}:return night ? Rez.Drawables.MapSkin{skin}Night : Rez.Drawables.MapSkin{skin}Day;\n'
    code+='}return night ? Rez.Drawables.MapSkin0Night : Rez.Drawables.MapSkin0Day;}\n}\n'
    (ROOT/'source/MapSkinResources.mc').write_text(code)
    for name,w,h in [('large',22,35),('date',8,13)]:
        atlas=Image.new('1',(10*w,h),1)
        for i in range(10):atlas.paste(date_digit(i) if name=='date' else digit(i,w,h),(i*w,0))
        atlas.save(OUT/(name+'.png'))
    for n in range(10):digit(n,13,24).save(OUT/f'second-{n}.png')
    weekdays=Image.new('1',(7*32,10),1)
    for i,s in enumerate(('SUN','MON','TUE','WED','THU','FRI','SAT')):text(weekdays,i*32+16,0,s,size=13,center=True)
    weekdays.save(OUT/'weekdays.png')
    letters=Image.new('1',(26*6,10),1)
    for i,c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):retro_text(letters,i*6,0,c,sy=2)
    letters.save(OUT/'letters.png')
    generate_weather(OUT,dist)
    render().resize((62,62),Image.Resampling.NEAREST).save(OUT/'icon.png')
    entries=[('Dial','dial'),('Circle','circle'),('Map','map'),('MapNight','map-night'),('Weather','weather'),('WeatherSmall','weather-small'),('Large','large'),('Date','date'),('Letters','letters'),('Weekdays','weekdays'),('LauncherIcon','icon')]+[(f'Sec{n}',f'second-{n}') for n in range(10)]
    entries += [(f'MapSkin{s}{"Night" if n else "Day"}',f'map-skin-{s}-{n}') for s in range(len(SKIN_NAMES)) for n in (0,1)]
    (OUT/'drawables.xml').write_text('<drawables>\n'+''.join(f'<bitmap id="{name}" filename="{file}.png"/>\n' for name,file in entries)+'</drawables>\n')
    image=render();image.save(dist/'RetroWorld-pixels.png');image.resize((704,704),Image.Resampling.NEAREST).save(dist/'RetroWorld-preview.png')
    sheet=Image.new('RGB',(3*352,2*384),'#eeeeee');d=ImageDraw.Draw(sheet)
    for i,kind in enumerate((1,2,3,4,5,6)):
        x=i%3*352;y=i//3*384;d.text((x+12,y+6),['','SUN','CLOUD','RAIN','SNOW','STORM','FOG'][kind],font=font(22),fill='black');sheet.paste(render(weather=kind).convert('RGB').resize((352,352),Image.Resampling.NEAREST),(x,y+32))
    sheet.save(dist/'RetroWorld-weather-designs.png')
    phases=Image.new('RGB',(930,390),'#e9e9e9');pd=ImageDraw.Draw(phases)
    for i,utc in enumerate((0,6,12,18)):
        x=10+i%2*465;y=10+i//2*195
        pd.text((x,y),f'UTC {utc:02d}:00 / UTC+8 {(utc+8)%24:02d}:00',font=font(23),fill='black')
        phase=phased_world(utc).convert('RGB').resize((445,145),Image.Resampling.NEAREST)
        phases.paste(phase,(x,y+32))
    phases.save(dist/'RetroWorld-map-daylight.png')
    gallery=Image.new('RGB',(1148,568),'#e9e9e9');gd=ImageDraw.Draw(gallery)
    caption_path=ROOT.parent/'assets/fonts/NotoSansCJKsc-Regular.otf'
    caption=ImageFont.truetype(str(caption_path),20) if caption_path.exists() else font(22)
    for skin,(name,cn) in enumerate(SKIN_NAMES):
        x=16+skin%4*283;y=10+skin//4*138
        label=f'{skin+1:02d} {cn if caption_path.exists() else name}'
        gd.text((x,y),label,font=caption,fill='black')
        gallery.paste(skin_bitmap(land,skin).convert('RGB').resize((267,87),Image.Resampling.NEAREST),(x,y+31))
    gallery.save(dist/'RetroWorld-map-skins.png')
    (dist/'map-skins.json').write_text(json.dumps([{'id':i,'name':n,'label':cn} for i,(n,cn) in enumerate(SKIN_NAMES)],ensure_ascii=False,indent=2)+'\n')
    print('Original retro lettering preserved; generated same-style refined digits and georeferenced map.')

if __name__=='__main__':main()
