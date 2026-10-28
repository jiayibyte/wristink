"""Code-generated 1-bit annular sectors; only occupied body-energy cells are drawn."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT/'resources/drawables'
ids=[[] for _ in range(4)]
offset_x=[[] for _ in range(4)];offset_y=[[] for _ in range(4)]
tree=ET.parse(folder/'drawables.xml');root=tree.getroot()
for item in list(root):
    if item.get('id','').startswith(('EnergySector','EnergyLevel')):root.remove(item)
for sector in range(8):
    image=Image.new('RGBA',(63,63),(255,255,255,0))
    for y in range(63):
        for x in range(63):
            dx,dy=x-31,y-31
            radius=math.hypot(dx,dy)
            angle=math.degrees(math.atan2(dx,-dy))%360
            local=angle-sector*45
            if not (20.5<=radius<=26.5 and 2.5<=local<=42.5):continue
            # Quiet concentric strokes replace the dense checkerboard texture.
            # Keep the same annulus, eight sectors, gaps and occupied counts.
            if radius>=25.5 or radius<=21.5 or 23<=radius<=24 or local<=4 or local>=41:
                image.putpixel((x,y),(255,255,255,255))
    image.save(folder/f'energy-sector-{sector}.png')
    for style in (0,1):
        for black in (False,True):
            out=Image.new('RGBA',(63,63),(0,0,0,0))
            for y in range(63):
                for x in range(63):
                    r=math.hypot(x-31,y-31);angle=math.degrees(math.atan2(x-31,31-y))%360-sector*45
                    if 20.5<=r<=26.5 and 2.5<=angle<=42.5 and (style==1 or image.getpixel((x,y))[3]):
                        out.putpixel((x,y),(0,0,0,255) if black else (255,255,255,255))
            key=style*2+int(black);ident=f'EnergySectorV{key}I{sector}';filename=f'energy-v{key}-{sector}.png'
            box=out.getbbox();offset_x[key].append(box[0]);offset_y[key].append(box[1])
            out.crop(box).save(folder/filename)
    # Retain IDs used by the existing source-derived preview generator.
# Cache one composite image for the occupied count rather than eight bitmap handles.
old_x,old_y=offset_x,offset_y
ids=[[] for _ in range(4)];offset_x=[[] for _ in range(4)];offset_y=[[] for _ in range(4)]
for key in range(4):
    combined=Image.new('RGBA',(63,63),(0,0,0,0))
    for sector in range(8):
        part=Image.open(folder/f'energy-v{key}-{sector}.png').convert('RGBA')
        combined.alpha_composite(part,(old_x[key][sector],old_y[key][sector]))
        box=combined.getbbox();offset_x[key].append(box[0]);offset_y[key].append(box[1])
        ident=f'EnergyLevelV{key}N{sector+1}';filename=f'energy-level-v{key}-n{sector+1}.png'
        combined.crop(box).save(folder/filename)
        ET.SubElement(root,'bitmap',id=ident,filename=filename);ids[key].append('Rez.Drawables.'+ident)
ET.indent(tree,space='    ');tree.write(folder/'drawables.xml',encoding='utf-8')
mc='// Generated sector palettes and textures, loaded only for the selected style.\nimport Toybox.Graphics;\nimport Toybox.WatchUi;\nimport Toybox.Lang;\nmodule EnergyCatalog {\n'
mc+='    function id(style,index) as ResourceId {switch(style*8+index){\n'
for style,row in enumerate(ids):
    for index,resource in enumerate(row):mc+='        case '+str(style*8+index)+':return '+resource+';\n'
mc+='    }return Rez.Drawables.EnergyLevelV0N1;}\n'
import json
assert all(row==offset_x[0] for row in offset_x)
assert all(row==offset_y[0] for row in offset_y)
mc+='    const X = '+json.dumps(offset_x[0])+';\n    const Y = '+json.dumps(offset_y[0])+';\n'
mc+='''    function load(style,count) as Graphics.BitmapReference {
        return WatchUi.loadResource(id(style,count-1)) as Graphics.BitmapReference;
    }
}
'''
(ROOT/'source/EnergyCatalog.mc').write_text(mc)
print('Generated 8 transparent body-battery sectors, with no empty-sector artwork.')
