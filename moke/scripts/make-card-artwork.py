"""Small, original pixel card artwork; only the two selected images load at runtime."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
NAMES=['北京公交卡','支付宝','聊天气泡','地铁','公交车','门禁钥匙','银行卡','音乐','咖啡','跑步','骑行','山峰','飞机','猫爪','笑脸','星空','相机','游戏机','露营','爱心']

def artwork(kind,light=False):
    paper=255 if light else 0;ink=255-paper
    image=Image.new('L',(28,13),paper);d=ImageDraw.Draw(image)
    d.rounded_rectangle((0,0,27,12),radius=2,outline=ink)
    def line(points):d.line(points,fill=ink,width=1)
    if kind==1:
        svg=ET.parse(ROOT/'resources/drawables/beijing-card.svg').getroot()
        for r in svg.findall(".//{http://www.w3.org/2000/svg}g[@fill='#fff']/{http://www.w3.org/2000/svg}rect"):
            x,y,w,h=(int(r.get(k)) for k in ('x','y','width','height'));d.rectangle((x,y,x+w-1,y+h-1),fill=ink)
        d.arc((12,5,30,21),180,330,fill=ink);d.arc((15,8,29,22),180,330,fill=ink)
    elif kind==2:
        def xy(p):return (6+p[0]*.8,1+p[1]*.8)
        for a,b in [((9,0),(9,5)),((3,2.5),(15,2.5)),((2,5.5),(14,5.5))]:line([xy(a),xy(b)])
        for a,b,c,e in [((14,5.5),(12,9),(7,12),(3.2,11.7)),((3.2,11.7),(-.6,11.4),(0,8.2),(3.4,8.3)),((3.4,8.3),(8.6,8.3),(13.9,12.4),(19.7,13.4))]:
            line([xy(((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*e[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*e[1])) for t in (i/30 for i in range(31))])
    elif kind==3:
        d.rounded_rectangle((5,2,15,8),2,outline=ink);line([(7,8),(6,10),(10,8)])
        d.rounded_rectangle((13,5,23,10),2,fill=paper,outline=ink);line([(20,10),(22,11)])
        d.point([(8,5),(12,5),(16,7),(20,7)],fill=ink)
    elif kind==4:
        d.rounded_rectangle((8,2,19,9),2,outline=ink);d.rectangle((10,3,17,5),outline=ink)
        d.point([(10,7),(17,7)],fill=ink);line([(10,10),(8,11)]);line([(17,10),(19,11)])
    elif kind==5:
        d.rounded_rectangle((6,2,21,9),1,outline=ink);line([(8,4),(19,4)])
        line([(13,2),(13,4)]);d.rectangle((8,6,10,7),fill=ink);d.rectangle((17,6,19,7),fill=ink)
        d.point([(8,10),(19,10)],fill=ink)
    elif kind==6:
        d.ellipse((6,3,12,9),outline=ink);line([(12,6),(22,6),(22,9)]);line([(18,6),(18,8)])
    elif kind==7:
        d.rectangle((5,3,22,9),outline=ink);line([(6,5),(21,5)])
        line([(8,7),(11,7)]);line([(16,7),(19,7)])
    elif kind==8:
        line([(11,9),(11,3),(19,2),(19,8)]);line([(12,5),(18,4)])
        d.ellipse((7,8,11,10),fill=ink);d.ellipse((15,7,19,9),fill=ink)
    elif kind==9:
        d.rectangle((8,5,17,9),outline=ink);d.arc((16,5,21,9),270,90,fill=ink)
        line([(7,11),(20,11)]);line([(10,2),(9,3)]);line([(15,2),(14,3)])
    elif kind==10:
        d.ellipse((15,2,17,4),fill=ink);line([(14,5),(11,8),(16,9),(18,11)])
        line([(14,5),(18,7),(21,6)]);line([(12,6),(8,6),(7,8)]);line([(12,8),(9,11),(6,11)])
    elif kind==11:
        d.ellipse((4,6,11,11),outline=ink);d.ellipse((17,6,24,11),outline=ink)
        line([(7,9),(11,4),(15,9),(7,9)]);line([(15,9),(20,9),(17,3),(20,3)])
        line([(10,4),(13,4)])
    elif kind==12:
        d.polygon([(4,10),(11,2),(16,8),(20,4),(25,10)],fill=ink)
        line([(9,5),(11,3),(13,5)]);d.point((11,4),fill=paper)
    elif kind==13:
        d.polygon([(4,7),(12,5),(14,2),(16,2),(16,5),(23,7),(23,8),(16,7),(16,10),(18,11),(14,10),(10,11),(12,9),(12,7),(4,8)],fill=ink)
    elif kind==14:
        d.ellipse((10,6,18,10),fill=ink)
        for box in [(6,4,9,7),(10,2,13,5),(15,2,18,5),(19,4,22,7)]:d.ellipse(box,fill=ink)
    elif kind==15:
        d.ellipse((9,2,19,11),outline=ink);d.point([(12,5),(16,5)],fill=ink)
        line([(12,8),(13,9),(15,9),(16,8)])
    elif kind==16:
        line([(7,2),(7,6)]);line([(5,4),(9,4)]);line([(18,5),(18,10)]);line([(16,7),(20,7)])
        d.point([(13,3),(22,3),(4,9),(11,9),(23,10)],fill=ink)
    elif kind==17:
        d.rectangle((6,4,22,10),outline=ink);d.rectangle((10,2,15,3),outline=ink)
        d.ellipse((11,5,17,9),outline=ink);d.point((20,5),fill=ink)
    elif kind==18:
        d.rounded_rectangle((5,3,23,10),2,outline=ink);line([(9,5),(9,8)]);line([(7,6),(11,6)])
        d.point([(18,5),(20,7)],fill=ink)
    elif kind==19:
        d.polygon([(5,10),(13,2),(22,10)],outline=ink);line([(13,2),(13,10),(17,10),(13,5)])
        line([(4,11),(24,11)]);d.point((22,3),fill=ink)
    elif kind==20:
        d.ellipse((8,3,14,8),fill=ink);d.ellipse((14,3,20,8),fill=ink)
        d.polygon([(8,6),(20,6),(14,11)],fill=ink)
    return image

def main():
    folder=ROOT/'resources/drawables';tree=ET.parse(folder/'drawables.xml');el=tree.getroot()
    for item in list(el):
        if item.get('id','').startswith('CardArt'):el.remove(item)
    entries=[]
    mc='// A single theme atlas holds the optional artwork; crop with Dc.setClip on MIP.\nimport Toybox.Lang;\nmodule CardArtwork {\n    function resource(kind,light) as ResourceId {\n        if(kind==1){return Rez.Drawables.BeijingCard;}\n        if(kind==2){return Rez.Drawables.AlipayCard;}\n        return light ? Rez.Drawables.CardArtAtlasLight : Rez.Drawables.CardArtAtlasDark;\n    }\n}\n'
    for kind,name in enumerate(NAMES,1):
        entries.append({'id':kind,'label':name,'width':28,'height':13,'theme_aware':kind>2})
    for light in (False,True):
        atlas=Image.new('L',(28*18,13),255 if light else 0)
        suffix='light' if light else 'dark'
        for kind in range(3,21):atlas.paste(artwork(kind,light),((kind-3)*28,0))
        filename=f'card-art-atlas-{suffix}.png';atlas.convert('1').save(folder/filename)
        ET.SubElement(el,'bitmap',id='CardArtAtlas'+suffix.title(),filename=filename)
    (ROOT/'source/CardArtwork.mc').write_text(mc)
    ET.indent(tree,space='    ');tree.write(folder/'drawables.xml',encoding='utf-8')
    (ROOT/'config/card-artwork.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
    sheet=Image.new('RGB',(840,700),'#f1f1ee');d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20,index=1)
    title=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26,index=1)
    d.text((28,20),'20 款黑白小卡片 · 上下两处可独立选择',font=title,fill='#202020')
    for i,name in enumerate(NAMES):
        x=24+(i%4)*202;y=76+(i//4)*116
        d.rounded_rectangle((x,y,x+188,y+102),12,fill='white')
        tile=artwork(i+1,(i+1)%2==0).convert('RGB').resize((112,52),Image.Resampling.NEAREST)
        sheet.paste(tile,(x+38,y+9));d.text((x+94,y+72),name,font=font,fill='#202020',anchor='mm')
    d.text((26,674),'原生像素图案放大展示；装饰用途，无刷卡或支付功能。',font=font,fill='#555555')
    (ROOT/'bin').mkdir(exist_ok=True);sheet.save(ROOT/'bin/card-artwork-gallery.png')
    print('Generated 20 card choices in two compact theme atlases and a contact sheet.')

if __name__=='__main__':main()
