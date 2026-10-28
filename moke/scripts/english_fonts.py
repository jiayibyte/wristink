"""English data fonts retain all existing glyph geometry and append missing Latin glyphs."""
from pathlib import Path
import copy,re,xml.etree.ElementTree as ET
from font_rasterizer import METRICS,render_font,NOTO
from PIL import ImageFont

def generate(out,scale=1.0,circle_scale=None):
    out=Path(out);dest=out/'fonts';dest.mkdir(parents=True,exist_ok=True)
    resources=ET.Element('fonts')
    for name,original in list(METRICS.items()):
        if not name.startswith(('dataf','circlef')):continue
        spec=copy.deepcopy(original);header=spec['header']
        size=int(re.search(r'\bsize=(\d+)',header[0])[1]);width=int(re.search(r'scaleW=(\d+)',header[1])[1])
        zero=next(e for e in spec['chars'] if e['id']==48);height=zero['height'];cap=zero['ink'][3]-zero['ink'][1]
        existing={e['id'] for e in spec['chars']}
        font=ImageFont.truetype(str(NOTO),size)
        for char in (dict.fromkeys('SunMonTueWedThuFriSatAMPd') if name.startswith('data') else ['d']):
            if ord(char) in existing:continue
            box=font.getbbox(char);w=max(2,min(size,round(font.getlength(char))))
            e=dict(zero);e.update(id=ord(char),x=width,y=0,width=w+2,height=height,xoffset=-1,xadvance=w,ink=[1,zero['ink'][1],w+1,zero['ink'][1]+cap]);spec['chars'].append(e);width+=w+3
        header[1]=re.sub(r'scaleW=\d+','scaleW='+str(width),header[1]);METRICS[name]=spec
        try:render_font(name,dest,(circle_scale or scale) if name.startswith('circle') else scale)
        finally:METRICS[name]=original
        ident=re.sub(r'(data|circle)f(\d)s(\d+)',lambda m:m[1].title()+'F'+m[2]+'S'+m[3],name)
        ET.SubElement(resources,'font',id=ident,filename=name+'.fnt')
    ET.ElementTree(resources).write(dest/'fonts.xml',encoding='utf-8')
