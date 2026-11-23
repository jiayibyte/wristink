"""Build deterministic native assets/source profiles from Garmin's installed device packs."""
from pathlib import Path
import sys; sys.path.append(str(Path(__file__).resolve().parents[2]/'tools')); import ciq_env
import argparse,json,re,shutil,math
import xml.etree.ElementTree as ET
from PIL import Image
from font_rasterizer import render_font

ROOT=Path(__file__).resolve().parents[1]
DEVICES=ciq_env.DEVICES
NS={'iq':'http://www.garmin.com/xml/connectiq'}
ET.register_namespace('iq',NS['iq'])

# Modern round screens: the Instinct layout fills 86% of the diameter instead of
# 76%. The rows that would reach the bezel move in (weather +8, status/date +6,
# footer narrower) and the heart window moves inward on its own transform.
ROUND_LAYOUT=dict(side=.86,circle_cx=136,circle_cy=38,circle_r=25,weather_shift=8,upper_shift=6,footer_left_width=56,footer_right_x=88,footer_right_width=56,lower_right_width=60)
def geometry(c,s,round_layout=False):
    location=s['display']['location'];w,h=location['width'],location['height']
    family=c['deviceFamily'];shape=s['display']['shape']
    roundish=shape in ['round','semi-round','semiround','semi-octagon'] or 'round' in family
    tuned=round_layout and roundish and not s.get('subscreen') and not s.get('analogHands')
    if 'semioctagon' in family and 'subscreen' in s:side=min(w,h)
    elif tuned:side=min(w,h)*ROUND_LAYOUT['side']
    elif roundish:side=min(w,h)*.76
    else:side=min(w,h)-8
    scale=round(side/176,6)
    g=dict(width=w,height=h,shape=shape,scale=scale,x=round((w-side)/2),y=round((h-side)/2),analog=bool(s.get('analogHands')))
    g.update(circle_scale=scale,circle_x=g['x'],circle_y=g['y'],time_scale=round(scale*(.92 if g['analog'] else 1),6))
    g.update(weather_shift=0,upper_shift=0,footer_left_width=64,footer_right_x=98,footer_right_width=58,lower_right_width=68)
    if tuned:
        L=ROUND_LAYOUT;cs=round(scale*L['circle_r']/31,6)
        g.update(circle_scale=cs,circle_x=round(g['x']+scale*L['circle_cx']-144*cs,6),circle_y=round(g['y']+scale*L['circle_cy']-31*cs,6))
        g.update({k:L[k] for k in ('weather_shift','upper_shift','footer_left_width','footer_right_x','footer_right_width','lower_right_width')})
    if s.get('subscreen'):
        sub=s['subscreen']['location'];cs=round(sub['width']/62,6)
        g.update(circle_scale=cs,circle_x=round(sub['x']-location['x']+sub['width']/2-144*cs,6),circle_y=round(sub['y']-location['y']+sub['height']/2-31*cs,6))
    return g

def scaled_assets(key,g,icon,noclip=False,compact=False,amoled=False):
    dest=ROOT/'generated/assets'/key/'resources'
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(ROOT/'resources',dest)
    if amoled:
        # A white heart window is a large always-lit area on AMOLED: default to black there.
        props=dest/'settings/properties.xml';text=props.read_text()
        text,n=re.subn(r'(<property id="circleBackground" type="number">)\d(</property>)',r'\g<1>0\g<2>',text)
        assert n==1,'circleBackground default not found';props.write_text(text)
    scale=g['scale']
    if noclip:
        tree=ET.parse(dest/'drawables/drawables.xml')
        for theme in ['dark','light']:
            with Image.open(dest/f'drawables/card-art-atlas-{theme}.png') as atlas:
                for kind in range(3,21):
                    filename=f'card-single-{theme}-{kind}.png';atlas.crop(((kind-3)*28,0,(kind-2)*28,13)).save(dest/'drawables'/filename)
                    ET.SubElement(tree.getroot(),'bitmap',id=f'CardSingle{theme.title()}{kind}',filename=filename)
        tree.write(dest/'drawables/drawables.xml',encoding='utf-8')
    if noclip:
        tree=ET.parse(dest/'drawables/drawables.xml')
        for item in tree.getroot():item.attrib.pop('compress',None)
        tree.write(dest/'drawables/drawables.xml',encoding='utf-8')
    def n(v):return round(int(v)*scale)
    for path in (dest/'drawables').glob('*.png'):
        scale=g['circle_scale'] if path.name.startswith('energy-') else g['scale']
        with Image.open(path) as im:out=im.resize((max(1,n(im.width)),max(1,n(im.height))),Image.Resampling.NEAREST)
        out.save(path)
    for path in (dest/'drawables').glob('*.svg'):
        scale=g['scale']
        text=path.read_text()
        for attr in ['width','height']:
            text=re.sub(r'(?<= )'+attr+r'="(\d+)"',lambda m:attr+'="'+str(icon[attr] if path.stem=='launcher' else max(1,n(m[1])))+'"',text,count=1)
        path.write_text(text)
    # Re-rasterize outlines at the native target resolution. Scaling a 1-bit
    # atlas with NEAREST duplicates columns and creates uneven, jagged stems.
    for path in (dest/'fonts').glob('*.fnt'):
        font_scale = g['circle_scale'] if path.stem.startswith(('circle','liveheart')) else (g['time_scale'] if path.stem.startswith('time') else g['scale'])
        render_font(path.stem, dest/'fonts', font_scale)
    from english_fonts import generate
    english=dest.parent/'resources-eng'
    shutil.copytree(ROOT/'resources-eng',english,dirs_exist_ok=True)
    # One Latin-extended font set for both languages (see generate-english.py).
    generate(dest,g['scale'],g['circle_scale'],shared=True)
    shutil.rmtree(english/'fonts',ignore_errors=True)
    if compact:
        # These 48KB API-1.4 models use vector rings and phone-only settings.
        tree=ET.parse(dest/'drawables/drawables.xml')
        for item in list(tree.getroot()):
            if item.get('id','').startswith('EnergyLevel'):tree.getroot().remove(item)
        tree.write(dest/'drawables/drawables.xml',encoding='utf-8')
        for resource in [dest,english]:
            path=resource/'strings/strings.xml';tree=ET.parse(path)
            for item in list(tree.getroot()):
                if item.get('id','').startswith('Menu'):tree.getroot().remove(item)
            tree.write(path,encoding='utf-8',xml_declaration=True)
        mapping=dict(zip('年月日周一二三四五六天上午下','!#$&()*+;<=>?@'))
        for fonts in [dest/'fonts',english/'fonts']:
            for path in fonts.glob('data*.fnt'):
                text=path.read_text()
                text=re.sub(r'char id=(\d+)',lambda m:'char id='+str(ord(mapping.get(chr(int(m[1])),chr(int(m[1]))))),text)
                path.write_text(text)
    return dest

def legacy_core():
    dest=ROOT/'generated/legacy-core'
    if dest.exists():shutil.rmtree(dest)
    dest.mkdir(parents=True,exist_ok=True)
    for name in ['FaceLayout','FaceFormat','SidePanel','PrefsDefaults','CardArtwork','LiveHeart','FaceLocale']:
        shutil.copy2(ROOT/f'source/{name}.mc',dest/f'{name}.mc')
    dest.joinpath('NativeStyle.mc').write_text('module NativeStyle {function enabled(){return false;}}\n')
    groups={}
    for group,sizes in [('data',[8,12,14,16]),('time',[54,58,64]),('liveheart',[18,22])]:
        prefix={'data':'Data','time':'Time','liveheart':'LiveHeart'}[group]
        groups[group]=[f'Rez.Fonts.{prefix}F{f}S{size}' for f in range(3) for size in sizes]
    source='import Toybox.Lang;\nimport Toybox.WatchUi;\nmodule FontCatalog {\n'
    # Resource lookup arrays are only needed during a full frame. Keeping all
    # 27 IDs resident starves incoming phone-settings deserialization on 2S.
    for key,values in groups.items():source+=f'    function {key.upper()}(i) {{var ids=['+','.join(values)+'];return ids[i];}\n'
    source+='''    var _id;var _font;
    function reset(){_id=null;_font=null;}
    function load(id){if(_id!=id || _font==null){_font=null;_id=id;_font=WatchUi.loadResource(id);}return _font;}
    function id(group,family,size){
        if(group.equals("time")){return TIME(family*3+(size>2 ? 2 : size));}
        if(group.equals("liveheart")){return LIVEHEART(family*2+(size>0 ? 1 : 0));}
        return DATA(family*4+(size<2 ? 0 : (size>4 ? 3 : size-1)));
    }
    function data(family,size){return load(id("data",family,size));}
    function fit(dc,group,family,size,text,width,height){
        for(var i=size;i>=0;i--){var font=load(id(group,family,i));if(dc.getTextWidthInPixels(text,font)<=width && dc.getFontHeight(font)<=height){return font;}font=null;}
        return load(id(group,family,0));
    }
}
'''
    dest.joinpath('FontCatalog.mc').write_text(source)

def legacy_extras(folder,api,analog,native_menu,memory,g):
    drawing=(ROOT/'source/DeviceDrawing.mc').read_text().replace('_dc.getTextWidthInPixels(text,font)','_dc.getTextWidthInPixels(LegacyText.encode(text),font)').replace('_dc.drawText(px(x),py(y),font,text,justify)','_dc.drawText(px(x),py(y),font,LegacyText.encode(text),justify)')
    if all(g[k]==v for k,v in dict(scale=1,x=0,y=0,circle_scale=1,circle_x=0,circle_y=0).items()):
        drawing='module DeviceDrawing {function target(dc){return dc;}function circleTarget(dc){return dc;}}\n'
    if api>=(2,3):
        drawing=drawing.replace('if(Math has :round){return Math.round(v);}var shifted=v+0.5;var n=shifted.toNumber();return shifted<n ? n-1 : n;', 'return Math.round(v);')
        drawing=drawing.replace('if(_dc has :clearClip){_dc.clearClip();}', '_dc.clearClip();')
        drawing=drawing.replace('if(_dc has :setClip){_dc.setClip(px(x),py(y),px(x+w)-px(x),py(y+h)-py(y));}', '_dc.setClip(px(x),py(y),px(x+w)-px(x),py(y+h)-py(y));')
    folder.joinpath('DeviceDrawing.mc').write_text(drawing)
    if memory<65536:
        folder.joinpath('LegacyText.mc').write_text('module LegacyText {var _last;var _encoded;function encode(text){if(_last!=null && _last.equals(text)){return _encoded;}var chinese="年月日周一二三四五六天上午下";var codes="!#$&()*+;<=>?@";var out=null;for(var i=0;i<text.length();i++){var char=text.substring(i,i+1);var index=chinese.find(char);if(index!=null){if(out==null){out=text.substring(0,i);}out+=codes.substring(index,index+1);}else if(out!=null){out+=char;}}if(out==null){return text;}_last=text;_encoded=out;return out;}}\n')
    else:folder.joinpath('LegacyText.mc').write_text('module LegacyText {function encode(text){return text;}}\n')
    keys=[r['key'] for r in json.loads(ROOT.joinpath('config/settings-catalog.json').read_text())['settings']]
    width=max(map(len,keys))+1;packed=''.join(k.ljust(width) for k in keys)
    index='function index(key){var n=KEYS.find(key+" ");return n==null ? null : (n/WIDTH).toNumber();}'
    folder.joinpath('LegacyPrefsIndex.mc').write_text('module LegacyPrefsIndex {const COUNT='+str(len(keys))+';const WIDTH='+str(width)+';var KEYS='+json.dumps(packed)+';'+index+'function key(i){var word=KEYS.substring(i*WIDTH,(i+1)*WIDTH);return word.substring(0,word.find(" "));}}\n')

    face=ROOT.joinpath('compat/legacy/LegacyFace.mc').read_text()
    if memory<=65536:
        folder.joinpath('LegacyPrefsIndex.mc').unlink()
        start=face.index('(:classicPrefs)');end=face.index('class InstinctFaceApp',start)
        face=face[:start]+'''(:classicPrefs)
module FacePrefs {
var revision=0;function prepare(){}function reload(){revision+=1;}
function raw(key){FontCatalog.reset();var v=null;try{v=Application.getApp().getProperty(key);}catch(e){}return v;}
function num(v){if(v instanceof String || v instanceof Float || v instanceof Long || v instanceof Double){return v.toNumber();}return v;}
function get(key){var v=num(raw(key));return v instanceof Number && v>=0 && v<=PrefsDefaults.max(key) ? v : PrefsDefaults.value(key);}
function flag(key){var v=raw(key);if(v instanceof String){v=v.equals("true") ? true : v.equals("false") ? false : num(v);}if(v instanceof Number){v=v!=0;}return v instanceof Boolean ? v : PrefsDefaults.flag(key);}
function fontFamily(key){var n=get(key+"Font");return n==0 ? get("dataFont") : n-1;}
function fontSize(key){var n=get(key+"Size");return n==0 ? get("dataSize") : n-1;}
}
'''+face[end:]
    if api<(1,3):
        catalog=json.loads(ROOT.joinpath('config/settings-catalog.json').read_text())['settings']
        entries=[[r['key'],r['default'],r['type'],r['max']] for r in catalog]
        fast='module FacePrefs {var revision=0;var _cache;const ENTRIES='+json.dumps(entries,ensure_ascii=False)+';'
        fast+='function reload(){revision+=1;_cache=null;}function prepare(){if(_cache!=null){return;}_cache={};var app=Application.getApp();for(var i=0;i<ENTRIES.size();i++){var row=ENTRIES[i];var value=app.getProperty(row[0]);if(value instanceof String && row[2]==1){value=value.equals("true") ? true : value.equals("false") ? false : value.toNumber();}else if(value instanceof String || value instanceof Float || value instanceof Long){value=value.toNumber();}if(row[2]==1){if(value instanceof Number){value=value!=0;}value=value instanceof Boolean ? value : row[1];}else{value=value instanceof Number && value>=0 && value<=row[3] ? value : row[1];}_cache[row[0]]=value;}}'
        fast+='function get(key){var v=_cache[key];return v instanceof Number ? v : 0;}function flag(key){var v=_cache[key];return v instanceof Boolean ? v : PrefsDefaults.flag(key);}function fontFamily(key){var n=get(key+"Font");return n==0 ? get("dataFont") : n-1;}function fontSize(key){var n=get(key+"Size");return n==0 ? get("dataSize") : n-1;}}\n'
        start=face.index('(:classicPrefs)');end=face.index('class InstinctFaceApp',start)
        face=face[:start]+fast+face[end:]
        folder.joinpath('LegacyPrefsIndex.mc').unlink(missing_ok=True)
    if not analog:
        start=face.index('    function analog(');end=face.index('    function card(',start);face=face[:start]+face[end:]
        face=face.replace('if(DeviceProfile.ANALOG){analog(dc,now);return;}','')
    if api<(1,3):
        face=face.replace('Math.floor(', 'CompatMath.floor(').replace('Math.ceil(', 'CompatMath.ceil(')
        folder.joinpath('CompatMath.mc').write_text('module CompatMath {function floor(v){var n=v.toNumber();return v<n ? n-1 : n;}function ceil(v){var n=v.toNumber();return v>n ? n+1 : n;}}\n')
    if memory<=65536:
        # Keep phone-setting deserialization headroom. These targets already
        # have a vector fallback; do not retain the 32-entry bitmap catalog.
        a=face.index('        if(_cells!=null && _cells>0 && _cellsStyle!=2)')
        b=face.index('cells(dc);',a)+len('cells(dc);')
        face=face[:a]+'        cells(dc);'+face[b:]
        face=face.replace('        else if(_energy!=null){dc.drawBitmap(113+EnergyCatalog.X[_energyCount-1],EnergyCatalog.Y[_energyCount-1],_energy);}', '')
        face=face.replace('var _energy;var _energyKey=-1;var _energyCount=0;', '')
        face=face.replace('_energy=null;_energyKey=-1;', '')
    folder.joinpath('LegacyFace.mc').write_text(face)
    icons=ROOT.joinpath('compat/legacy/LegacyIcons.mc').read_text()
    if api<(3,2):
        start=icons.index('    function weather(');end=icons.index('    function moon(',start)
        icons=icons[:start]+'    function weather(dc,x,y,condition){dc.drawLine(x+4,y+7,x+10,y+7); }\n'+icons[end:]
    else:
        glyphs={int(k):json.loads(v) for k,v in re.findall(r'case (\d+):return (\[.*?\]);',ROOT.joinpath('source/WeatherGlyphs.mc').read_text())}
        packed='module WeatherGlyphs {function pixels(kind){var text="";switch(kind){'
        for k,values in glyphs.items():packed+='case '+str(k)+':text='+json.dumps(''.join(chr(v+32) for v in values))+';break;'
        packed+='default:text='+json.dumps(chr(32)*15)+';}var chars=text.toCharArray();var rows=[];for(var i=0;i<chars.size();i++){rows.add(chars[i].toNumber()-32);}return rows;}}\n'
        folder.joinpath('WeatherGlyphs.mc').write_text(packed)
    if memory<65536:
        # Keep the requested common pictograms on 48 KB watches; less common
        # metrics use short ASCII labels instead of a large vector icon catalog.
        moon=icons[icons.index('    function moon('):icons.index('    function sun(')]
        weather=icons[icons.index('    function weather('):icons.index('    function moon(')]
        cases=[]
        for match in re.finditer(r'((?:\s*case \d+:)+)(.*?)(?=\s*case \d+:|\n        }\n    }\n})',icons,re.S):
            kinds=set(map(int,re.findall(r'case (\d+):',match[1])))
            if kinds & {1,2,3,5,6,7,14,18}:cases.append(match[0])
        icons='import Toybox.Graphics;\nimport Toybox.Math;\nmodule LegacyIcons {\n'+weather+moon+'function draw(dc,kind,x,y,ink,paper,battery,condition){dc.setColor(ink,paper);switch(kind){'+''.join(cases)+'default:var text=kind==4 ? "F" : (kind==10 || kind==12 || kind==22 || kind==23 ? "%" : (kind==11 || kind==24 ? "!" : (kind==16 ? "T" : (kind==19 ? "B" : (kind==20 || kind==21 ? "M" : (kind==26 ? "S" : (kind==28 ? "P" : (kind==29 ? "L" : "R"))))))));dc.drawText(x,y,Graphics.FONT_XTINY,text,Graphics.TEXT_JUSTIFY_LEFT);break;}}}\n'
        icons=re.sub(r'case 5:.*?break;', 'case 5:dc.fillEllipse(x+7,y+9,4,5);for(var i=0;i<7;i++){dc.drawLine(x+7-i*.5,y+i,x+7+i*.4,y+i);}dc.setColor(paper,paper);dc.fillCircle(x+7,y+11,1);dc.setColor(ink,paper);break;',icons,flags=re.S)
        icons=re.sub(r'case 6:.*?break;', 'case 6:dc.fillCircle(x+4,y+4,3);dc.fillCircle(x+10,y+4,3);for(var i=0;i<9;i++){dc.drawLine(x+1+i*.75,y+5+i,x+13-i*.75,y+5+i);}break;',icons,flags=re.S)
        icons=re.sub(r'case 18:.*?break;', 'case 18:for(var i=0;i<11;i++){dc.drawLine(x+6-i*.6,y+2+i,x+6+i,y+2+i);}break;',icons,flags=re.S)
        icons=re.sub(r'case 3:.*?break;', 'case 3:dc.drawCircle(x+6,y+4,4);for(var i=0;i<8;i++){dc.drawLine(x+2+i*.5,y+7+i,x+10-i*.5,y+7+i);}break;',icons,flags=re.S)
    if api<(1,3):icons=icons.replace('Math.floor(', 'CompatMath.floor(').replace('Math.ceil(', 'CompatMath.ceil(')
    if memory==65536:
        from compact_icons import compact
        icons=compact(icons)
    folder.joinpath('LegacyIcons.mc').write_text(icons)
    shutil.copy2(ROOT/'compat/legacy/FitnessProgress.mc',folder/'FitnessProgress.mc')
    card='import Toybox.Lang;\nmodule LegacyCardArtwork {function resource(kind,light) as ResourceId {'
    if api<(2,3):
        card+='if(kind==1){return Rez.Drawables.BeijingCard;}if(kind==2){return Rez.Drawables.AlipayCard;}'
        for k in range(3,21):card+=f'if(kind=={k}){{return light ? Rez.Drawables.CardSingleLight{k} : Rez.Drawables.CardSingleDark{k};}}'
        card+='return Rez.Drawables.BeijingCard;'
    else:card+='return CardArtwork.resource(kind,light);'
    folder.joinpath('LegacyCardArtwork.mc').write_text(card+'}}\n')
    if api>=(2,1):shutil.copy2(ROOT/'source/TrendData.mc',folder/'TrendData.mc')
    if api>=(3,0) and memory>65536:
        energy=ROOT.joinpath('source/EnergyCatalog.mc').read_text().replace(' as Graphics.BitmapReference','')
        folder.joinpath('EnergyCatalog.mc').write_text(energy)
    elif memory>65536:
        folder.joinpath('EnergyCatalog.mc').write_text('module EnergyCatalog {const X=[0,0,0,0,0,0,0,0];const Y=[0,0,0,0,0,0,0,0];function load(style,count){return null;}}\n')
    if native_menu:
        folder.joinpath('FaceSettings.mc').write_text(ROOT.joinpath('source/FaceSettings.mc').read_text().replace('(:extendedCode)',''))
        folder.joinpath('SettingsCatalog.mc').write_text(ROOT.joinpath('source/SettingsCatalog.mc').read_text().replace('(:extendedCode)',''))
    source='import Toybox.Time;\nimport Toybox.Time.Gregorian;\n'
    if api>=(3,2):source+='import Toybox.Weather;\n'
    if api>=(3,3):source+='import Toybox.SensorHistory;\n'
    source+='module LegacyExtras {\n    function body(){'
    if api>=(3,3):source+='if(SensorHistory has :getBodyBatteryHistory){var s=SensorHistory.getBodyBatteryHistory({:period=>1,:order=>SensorHistory.ORDER_NEWEST_FIRST}).next();if(s!=null && s.data!=null && s.data>=0 && s.data<=100){return s.data;}}'
    source+='return null;}\n    function weather(now){'
    if api>=(3,2):
        source+='var w=Weather.getCurrentConditions();if(w!=null){var sunrise="--:--";var sunset="--:--";'
        if api>=(3,3):source+='if((Weather has :getSunrise) && (Weather has :getSunset) && w.observationLocationPosition!=null){sunrise=clock(Weather.getSunrise(w.observationLocationPosition,now));sunset=clock(Weather.getSunset(w.observationLocationPosition,now));}'
        source+='return [w.temperature,w.relativeHumidity,w.windSpeed!=null ? w.windSpeed*3.6 : null,w.feelsLikeTemperature,w.windBearing,WeatherIcons.category(w.condition),sunrise,sunset];}'
        weather_source=(ROOT/'source/WeatherIcons.mc').read_text()
        if memory<=65536:
            table=json.loads((ROOT/'config/weather-condition-categories.json').read_text())
            begin=weather_source.index('    function category(');finish=weather_source.index('    function draw(',begin)
            packed=''.join(str(v) if v<10 else 'A' for v in table)
            weather_source=weather_source[:begin]+'    const CATEGORIES='+json.dumps(packed)+';\n    function category(condition){if(condition==null || condition<0 || condition>=CATEGORIES.length()){return UNKNOWN;}var c=CATEGORIES.substring(condition,condition+1);return c.equals("A") ? HAIL : c.toNumber();}\n\n'+weather_source[finish:]
        folder.joinpath('WeatherIcons.mc').write_text(weather_source)
    source+='return [null,null,null,null,null,0,"--:--","--:--"];}\n'
    source+='    function trend(kind,now,minutes){'+('return TrendData.fetch(kind,now,minutes);' if api>=(2,1) else 'return {:values=>[],:range=>[null,null]};')+'}\n'
    source+='    function clock(moment){if(moment==null){return "--:--";}var d=Gregorian.info(moment,Time.FORMAT_SHORT);return d.hour.format("%02d")+":"+d.min.format("%02d");}\n}\n'
    folder.joinpath('LegacyExtras.mc').write_text(source)
    source='import Toybox.WatchUi;\nmodule LegacyPower {const HAS_SETTINGS='+str(native_menu).lower()+';function prepare(){'+('' if native_menu else 'FacePrefs.prepare();')+'}function views(view){return [view'+(',new LegacyPowerDelegate(view)' if api>=(2,3) else '')+'];}function settings(){'
    source+=('var menu=new FaceSettingsMenu(0);return [menu,new FaceSettingsDelegate(menu,0)];' if native_menu else 'return null;')+'}}\n'
    if api>=(2,3):source+='class LegacyPowerDelegate extends WatchUi.WatchFaceDelegate {var _view;function initialize(view){WatchFaceDelegate.initialize();_view=view;}function onPowerBudgetExceeded(info){_view.budgetExceeded();}}\n'
    folder.joinpath('LegacyPower.mc').write_text(source)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='*');parser.add_argument('--sources-only',action='store_true');args=parser.parse_args()
    plain=ROOT/'generated/modern-no-paging';plain.mkdir(parents=True,exist_ok=True)
    for path in (ROOT/'source').glob('*.mc'):plain.joinpath(path.name).write_text(path.read_text().replace('(:extendedCode)',''))
    rows=[]
    for path in sorted(DEVICES.glob('*/compiler.json')):
        try:c=json.loads(path.read_text());s=json.loads((path.parent/'simulator.json').read_text())
        except (ValueError,FileNotFoundError):continue
        types={a['type']:a['memoryLimit'] for a in c['appTypes']}
        if 'watchFace' not in types:continue
        if args.only and c['deviceId'] not in args.only:continue
        # Regional hardware may expose an older API than the device group.
        api=min(tuple(map(int,part['connectIQVersion'].split('.'))) for part in c['partNumbers'])
        api=min(tuple(map(int,part['connectIQVersion'].split('.'))) for part in c['partNumbers'])
        modern=api>=(3,3) and (types['watchFace']>65536 or c.get('codePageSize',0)>0)
        # Colour AMOLED/LCD watches use the full renderer only; the low-memory
        # legacy face stays MIP-only.
        if c.get('displayType')!='mip' and not modern:continue
        g=geometry(c,s,modern);icon=c.get('launcherIcon',dict(width=40,height=40));key=c['deviceFamily']+'-'+str(round(g['scale']*1000000))+f'-c{round(g["circle_scale"]*1000000)}-t{round(g["time_scale"]*1000000)}-icon{icon["width"]}x{icon["height"]}'
        paging=c.get('codePageSize',0)>0
        renderer='modern' if api>=(3,3) and (types['watchFace']>65536 or paging) else 'legacy'
        mode='完整' if api>=(3,3) else '轻量兼容'
        if api<(2,3):key+='-noclip'
        if renderer=='legacy':key+='-legacy'+('-ui' if api>=(3,0) and (paging or types['watchFace']>65536) else '-phone')
        if types['watchFace']<65536:key+='-compact-text'
        if c.get('displayType')=='amoled':key+='-amoled'
        rows.append(dict(id=c['deviceId'],name=c['displayName'],api='.'.join(map(str,api)),memory=types['watchFace'],family=c['deviceFamily'],geometry=g,icon=icon,asset_key=key,paging=paging,mode=mode,renderer=renderer,on_watch_settings=api>=(3,0) and (paging or types['watchFace']>65536),color=c.get('bitsPerPixel',1)>1,amoled=c.get('displayType')=='amoled'))
    seen=set()
    for row in rows:
        g=row['geometry'];folder=ROOT/'generated/profiles'/row['id']
        if folder.exists():shutil.rmtree(folder)
        folder.mkdir(parents=True,exist_ok=True)
        api=tuple(map(int,row['api'].split('.')))
        profile=f'// Generated from Garmin {row["family"]}.\nimport Toybox.WatchUi;\nmodule DeviceProfile {{const SCALE={g["scale"]};const X={g["x"]};const Y={g["y"]};const CIRCLE_SCALE={g["circle_scale"]};const CIRCLE_X={g["circle_x"]};const CIRCLE_Y={g["circle_y"]};const ANALOG={str(g["analog"]).lower()};const CLIP={str(api>=(2,3)).lower()};const BODY={str(api>=(3,3)).lower()};const WEATHER={str(api>=(3,2)).lower()};'
        profile+=('const SECONDS_X=146;const SECONDS_Y=63;const SECONDS_LEFT=116;const SECONDS_WIDTH=58;const SECONDS_HEIGHT=14;' if g['analog'] else 'const SECONDS_X=153;const SECONDS_Y=90;const SECONDS_LEFT=140;const SECONDS_WIDTH=28;const SECONDS_HEIGHT=21;')
        profile+=''.join(f'const {k.upper()}={g[k]};' for k in ('weather_shift','upper_shift','footer_left_width','footer_right_x','footer_right_width','lower_right_width'))
        if g['analog']:
            profile+='var _holding=false;function hands(view,awake){var mode=FacePrefs.get("analogHandMode");var want=mode==2 || (mode==1 && awake);if(want==_holding){return;}view.setClockHandPosition({:clockState=>want ? WatchUi.ANALOG_CLOCK_STATE_HOLDING : WatchUi.ANALOG_CLOCK_STATE_SYSTEM_TIME,:hour=>270,:minute=>90});_holding=want;}function releaseHands(view){if(_holding){view.setClockHandPosition({:clockState=>WatchUi.ANALOG_CLOCK_STATE_SYSTEM_TIME});_holding=false;}}'
        else:profile+='function hands(view,awake){}function releaseHands(view){}'
        profile+=f'const COLOR={str(row["color"]).lower()};const AMOLED={str(row["amoled"]).lower()};'
        folder.joinpath('DeviceProfile.mc').write_text(profile+'}\n')
        if row['asset_key'] not in seen and not args.sources_only:
            resource=scaled_assets(row['asset_key'],g,row['icon'],api<(2,3),row['memory']<65536,row['amoled'])
            if not row['on_watch_settings']:
                shutil.rmtree(resource/'config')
                shutil.rmtree(resource.parent/'resources-eng/config')
            if row['renderer']=='legacy':
                allowed={'Chart'}|{f'DataF{f}S{s}' for f in range(3) for s in [8,12,14,16]}|{f'TimeF{f}S{s}' for f in range(3) for s in [54,58,64]}|{f'LiveHeartF{f}S{s}' for f in range(3) for s in [18,22]}
                for res in [resource,resource.parent/'resources-eng']:
                    # English shares the Chinese folder's superset fonts and has no fonts.xml of its own.
                    fonts=res/'fonts/fonts.xml'
                    if not fonts.exists():continue
                    tree=ET.parse(fonts)
                    for item in list(tree.getroot()):
                        if item.get('id') not in allowed:tree.getroot().remove(item)
                    tree.write(fonts,encoding='utf-8')
                shutil.rmtree(resource/'native')
            seen.add(row['asset_key'])
        if row['renderer']=='legacy':legacy_extras(folder,api,g['analog'],row['on_watch_settings'],row['memory'],g)
    legacy_core()
    for preview in [False,True]:
        manifest=ROOT/('preview/manifest.xml' if preview else 'manifest.xml')
        tree=ET.parse(manifest);app=tree.getroot().find('iq:application',NS);app.set('minApiLevel','1.2.0')
        products=app.find('iq:products',NS);products.clear()
        for row in rows:ET.SubElement(products,'{'+NS['iq']+'}product',id=row['id'])
        ET.indent(tree,space='    ');tree.write(manifest,encoding='utf-8',xml_declaration=True)
        jungle=['project.manifest = '+str(manifest.relative_to(ROOT)),f'base.sourcePath = source;{"preview" if preview else "live"};profiles/base','base.resourcePath = resources;resources-eng'+(';preview/resources' if preview else ''),'base.lang.zhs = resources']
        jungle.append('base.lang.eng = resources-eng')
        for row in rows:
            mode=('source' if row['paging'] else 'generated/modern-no-paging') if row['renderer']=='modern' else 'generated/legacy-core'
            jungle.append(f'{row["id"]}.sourcePath = {mode};{"preview" if preview else "live"};generated/profiles/{row["id"]}')
            if row['renderer']=='legacy' and row['on_watch_settings']:jungle.append(f'{row["id"]}.excludeAnnotations = classicPrefs')
            jungle.append(f'{row["id"]}.resourcePath = generated/assets/{row["asset_key"]}/resources;generated/assets/{row["asset_key"]}/resources-eng'+(';preview/resources' if preview else ''))
            jungle.append(f'{row["id"]}.lang.zhs = generated/assets/{row["asset_key"]}/resources')
            jungle.append(f'{row["id"]}.lang.eng = generated/assets/{row["asset_key"]}/resources-eng')
        ROOT.joinpath('preview.jungle' if preview else 'monkey.jungle').write_text('\n'.join(jungle)+'\n')
    ROOT.joinpath('config/mip-devices.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(f'Generated {len(rows)} MIP watch targets, {len(seen)} native asset profiles.')

if __name__=='__main__':main()
