"""Generate grid-fitted Moke Soft font resources and the Monkey C catalog."""
from pathlib import Path
from font_rasterizer import METRICS, render_font

ROOT = Path(__file__).resolve().parents[1] / 'resources/fonts'
info_chars = '0123456789 .:-/%°kmifthPaCF年月日周一二三四五六天上午下午'
info_metrics = info_chars
info_font = str(ROOT.parents[1]/'assets/fonts/NotoSansCJKsc-Regular.otf')


def build(name, size, chars, **kwargs):
    # Geometry is a compatibility contract; only outlines change.
    render_font(name, ROOT)


for name in METRICS:
    render_font(name, ROOT)

# Load these by family/size on demand; changing settings releases the previous cache.
import xml.etree.ElementTree as ET
catalog={}; extra=[]
for group,sizes in [('Data',[8,10,12,14,16]),('Time',[54,58,64,68]),('Circle',[18,22,26,28]),('LiveHeart',[18,22,26,28]),('Second',[18,22,26,28])]:
    matrix=[]
    for family in range(3):
        row=[]
        for size in sizes:
            ident=f'{group}F{family}S{size}';filename=ident.lower()
            if group in ('Circle','LiveHeart') and family!=2 and size>22:
                row.append(f'Rez.Fonts.{group}F{family}S22');continue
            if group=='Data':
                build(filename,size,info_chars,ratio=.86 if family==2 else 1,stroke=1 if family==1 else 0,font_path=info_font,font_index=1,metrics_chars=info_metrics)
            else:
                content='0123456789:.- %km°hPaCFft/i' if group=='Circle' else ('0123456789-' if group=='LiveHeart' else '0123456789:. ')
                path=info_font if family==1 else None
                ratio=(.76 if group=='Time' else (.8 if group=='Second' else .72)) if family!=2 else (.67 if group=='Time' else (.72 if group=='Second' else .66))
                build(filename,size,content,ratio=ratio,stroke=1 if family==0 and group!='Second' else 0,font_path=path,font_index=1 if path else 0,metrics_chars='0123456789:.- %km°hPaCFft/i' if group=='LiveHeart' else None)
            row.append('Rez.Fonts.'+ident);extra.append((ident,filename+'.fnt'))
        matrix.append(row)
    catalog[group.upper()]=matrix
tree=ET.parse(ROOT/'fonts.xml');el=tree.getroot()
for old in list(el):
    if old.get('id')!='Chart':el.remove(old)
for ident,filename in extra:ET.SubElement(el,'font',id=ident,filename=filename)
ET.indent(tree,space='    ');tree.write(ROOT/'fonts.xml',encoding='utf-8')
mc='// Generated font families; keep renderer and resource IDs in sync.\nimport Toybox.Graphics;\nimport Toybox.WatchUi;\nimport Toybox.Lang;\nmodule FontCatalog {\n'
mc+='    (:extendedCode)\n    function id(group,family,size) as ResourceId {\n'
for name,matrix in catalog.items():
    key={'DATA':'data','TIME':'time','CIRCLE':'circle','LIVEHEART':'liveheart','SECOND':'seconds'}[name]
    mc+='        if(group.equals("'+key+'")){switch(family*'+str(len(matrix[0]))+'+size){\n'
    for family,row in enumerate(matrix):
        for size,resource in enumerate(row):mc+='            case '+str(family*len(row)+size)+':return '+resource+';\n'
    mc+='        }}\n'
mc+='        return Rez.Fonts.DataF0S14;\n    }\n'
mc+='''    var _ids as Array<ResourceId> = [];
    var _fonts as Array = [];
    function reset() { _ids = []; _fonts = []; }
    function load(id as ResourceId) {
        for(var i=0;i<_ids.size();i++){if(_ids[i]==id){return _fonts[i];}}
        if(_ids.size()>=1){_ids.remove(_ids[0]);_fonts.remove(_fonts[0]);}
        var font=WatchUi.loadResource(id) as Graphics.FontType;
        _ids.add(id);_fonts.add(font);return font;
    }
    function data(family,size) { return load(id("data",family,size)); }
    function fit(dc,group,family,size,text,width,height) {
        for (var i=size;i>=0;i--) {
            var font=load(id(group,family,i));
            if (dc.getTextWidthInPixels(text,font)<=width && dc.getFontHeight(font)<=height) { return font; }
            font=null; // Release a rejected size before loading the next bitmap font.
        }
        return load(id(group,family,0));
    }
}
'''
(ROOT.parents[1]/'source/FontCatalog.mc').write_text(mc)
print(f'Generated {len(extra)} configurable font resources (loaded on demand).')
