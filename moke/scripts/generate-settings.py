"""Single catalog for native menus, phone settings, defaults and configuration checks."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
METRICS=['隐藏','电量百分比','步数','距离','爬升楼层','热量','心率','气温','日落时间','日出时间','湿度','通知数量','步数目标百分比','风速','月相亮度百分比','心率范围','体感温度','剩余续航天数','海拔','身体电量','今日强度分钟','本周强度分钟','今日强度完成百分比','本周强度完成百分比','久坐等级','恢复时间','压力','呼吸频率','气压']
PROGRESS=['隐藏','身体电量','电量百分比','步数目标','今日强度（周目标除以7）','本周强度目标','久坐等级','爬升楼层目标']
STYLES=['图标和数值','仅数值','百分比','数值与目标','进度线和数值','分格和数值','趋势图']
FONT=['跟随全局','简洁黑体','加粗黑体','紧凑黑体']
SIZE=['跟随全局','小','标准','大']
CARDS=['隐藏']+[r['label'] for r in json.loads((ROOT/'config/card-artwork.json').read_text())]
groups=[]; rows=[]
def group(key,label):
    groups.append([key,label]);return len(groups)-1
def add(g,key,label,default,options=None,limits=None):
    kind=1 if isinstance(default,bool) else (2 if limits else 0)
    rows.append(dict(group=g,key=key,label=label,type=kind,default=default,options=options or [],min=(limits or [0,0])[0],max=(limits or [0,len(options or [])-1])[1]))
g=group('general','全局外观')
for k,l,d in [('darkTheme','黑色背景',True),('showIcons','显示数据图标',True),('showUnits','显示单位',True),('linkFooterFonts','底部两项字号联动',True)]:add(g,k,l,d)
add(g,'dataFont','全局数据字体',0,['简洁黑体','加粗黑体','紧凑黑体'])
add(g,'dataSize','全局数据字号',1,['小','标准','大'])
add(g,'temperatureUnit','温度单位',0,['摄氏度','华氏度'])
add(g,'distanceUnit','距离单位',0,['公里','英里'])
add(g,'altitudeUnit','高度单位',0,['米','英尺'])
add(g,'powerProfile','刷新策略',0,['省电（曲线5分钟／天气30分钟）','标准（曲线1分钟／天气5分钟）'])
add(g,'analogHandMode','机械指针避让（仅Crossover）',0,['保持系统走时（省电）','抬腕时水平避让','表盘显示期间水平避让'])
g=group('time','时间与秒数')
for k,l,d in [('showTime','显示大时间',True),('showSeconds','显示秒数',True),('leadingZero','小时补零',True)]:add(g,k,l,d)
add(g,'timeFormat','时间制式',0,['24小时','12小时（上午下午）'])
add(g,'timeSeparator','时间分隔符',0,['冒号','圆点','空格'])
add(g,'secondsMode','秒数刷新策略',0,['随卡片自动切换','仅抬腕显示','持续显示（耗电较高）','关闭（最省电）'])
for prefix,label in [('time','大时间'),('seconds','秒数')]:
    add(g,prefix+'Font',label+'字体',0,['当前数字','简洁黑体','窄体数字'])
    add(g,prefix+'Size',label+'字号',1,['小','标准','大'])
g=group('date','日期与状态')
add(g,'showDate','显示日期',True)
add(g,'dateFormat','日期格式',0,['10/19 一','10月19日','2026/10/19','10-19 周一','一 10/19','10/19','2026-10-19','10月19日 周一'])
add(g,'dateFont','日期字体',0,FONT);add(g,'dateSize','日期字号',0,SIZE)
add(g,'showMoveBar','显示活动指示区',True)
add(g,'moveSource','活动指示区数据',6,PROGRESS)
add(g,'moveStyle','活动指示区样式',0,['小人和分格','细进度线','百分比'])
add(g,'moveFont','活动百分比字体',0,FONT)
add(g,'showWind','显示风向箭头',True);add(g,'showMoon','显示月相',True)
g=group('circle','右上圆窗')
add(g,'showCircle','显示整个圆窗',True)
add(g,'heartRefresh','中心心率刷新',0,['每5秒读取当前心率','仅抬腕时每5秒','每分钟（省电）'])
add(g,'heartSource','心率数据来源',0,['系统当前心率','最新系统采样（≤3分钟，非实时）'])
add(g,'circle','中心数据',6,METRICS)
add(g,'circleStyle','中心显示方式',0,STYLES[:4])
add(g,'circleGoal','中心自定目标（0自动）',0,limits=[0,1000000])
add(g,'circleFont','中心字体',0,['当前数字','简洁黑体','窄体数字'])
add(g,'circleSize','中心字号',1,['小','标准','大'])
add(g,'showCircleIcon','显示中心图标',True)
add(g,'circleBackground','圆窗背景',1,['黑色','白色','跟随整体背景'])
add(g,'cellsSource','八格数据来源',0,PROGRESS)
add(g,'cellsStyle','八格显示方式',0,['纹理扇形','实心扇形','连续内环'])
add(g,'ringSource','外圈数据来源',0,PROGRESS)
add(g,'ringStyle','外圈线条样式',1,['细线','标准线','粗线','八段进度'])
add(g,'ringStart','外圈起点',0,['顶部','右侧','底部','左侧'])
g=group('cards','右侧卡片与数据')
add(g,'showStatus','显示卡片区',True)
add(g,'showBeijingCard','显示上方卡片',True);add(g,'showAlipayCard','显示下方卡片',True)
add(g,'topCardImage','上方卡片图案',1,CARDS);add(g,'bottomCardImage','下方卡片图案',2,CARDS)
add(g,'sideData','替换卡片的数据（隐藏则卡片）',0,METRICS)
add(g,'sideFont','右侧数据字体',0,FONT);add(g,'sideSize','右侧数据字号',1,SIZE)
for key,label,default in [('topOne','顶部第一行',7),('topTwo','第二行左侧',17),('topThree','第二行右侧',0),('bottomLeft','下方左侧',2),('bottomRight','下方右侧',15),('footerLeft','底部左侧',5),('footerRight','底部右侧',18)]:
    g=group(key,label)
    add(g,key,'数据（隐藏可关闭本区）',default,METRICS)
    add(g,key+'Style','显示方式',6 if key=='bottomRight' else 0,STYLES if key=='bottomRight' else STYLES[:6])
    add(g,key+'Font','字体',0,FONT);add(g,key+'Size','字号',0,SIZE)
    add(g,key+'Goal','自定目标（0自动）',0,limits=[0,1000000])
g=group('chart','趋势图')
add(g,'showHeartGraph','启用下方右侧趋势图',True)
add(g,'chartStyle','趋势图样式',0,['折线','面积','竖线'])
add(g,'chartMinutes','趋势时间跨度',1,['15分钟','30分钟','60分钟'])
add(g,'showChartLabels','显示最高最低值',True)
add(g,'chartLabelFont','刻度字体',0,['像素小字','简洁黑体','加粗黑体','紧凑黑体'])

def main():
    (ROOT/'config').mkdir(exist_ok=True)
    schema=dict(groups=groups,metrics=METRICS,progress=PROGRESS,settings=rows)
    (ROOT/'config/settings-catalog.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n')
    def js(x):return json.dumps(x,ensure_ascii=False)
    strings=ET.Element('strings');ET.SubElement(strings,'string',id='AppName').text='墨刻'
    ET.SubElement(strings,'string',id='LocaleEnglish').text='false'
    menu={'MenuOn':'开启','MenuOff':'关闭','MenuAuto':'自动／跟随系统','MenuNext':'下一页','MenuPrevious':'上一页','MenuResetGroup':'恢复本区默认','MenuSelected':'已选择','MenuTitle':'个性化表盘','MenuResetAll':'恢复全部默认'}
    for key,value in menu.items():ET.SubElement(strings,'string',id=key).text=value
    folder=ROOT/'resources/config';folder.mkdir(exist_ok=True)
    resource=ET.Element('jsonDataResources')
    folder.joinpath('groups.json').write_text(js([x[1] for x in groups]))
    ET.SubElement(resource,'jsonData',id='ConfigGroups',filename='groups.json')
    refs=[]
    tables=[]
    for row in rows:
        if row['options'] not in tables:tables.append(row['options'])
    option_refs=[]
    for i,table in enumerate(tables):
        filename='options-'+str(i)+'.json';folder.joinpath(filename).write_text(js(table))
        ET.SubElement(resource,'jsonData',id='ConfigOptions'+str(i),filename=filename);option_refs.append('Rez.JsonData.ConfigOptions'+str(i))
        if len(table)>12:
            width=max(map(len,table));packed=''.join(label.ljust(width) for label in table)
            packed_name='labels-'+str(i)+'.json';folder.joinpath(packed_name).write_text(js(packed))
            ET.SubElement(resource,'jsonData',id='ConfigLabels'+str(i),filename=packed_name)
    page_counts=[]
    for i in range(len(groups)):
        packed=[[r['key'],r['label'],r['type'],r['default'],tables.index(r['options'])] for r in rows if r['group']==i]
        folder.joinpath('group-'+str(i)+'.json').write_text(js(packed))
        page_counts.append((len(packed)+5)//6)
        for page in range(page_counts[-1]):
            filename=f'group-{i}-page-{page}.json';folder.joinpath(filename).write_text(js(packed[page*6:page*6+6]))
            ET.SubElement(resource,'jsonData',id=f'ConfigGroup{i}Page{page}',filename=filename)
            refs.append((i,page,f'Rez.JsonData.ConfigGroup{i}Page{page}'))
    rt=ET.ElementTree(resource);ET.indent(rt,space='  ');rt.write(folder/'resources.xml',encoding='utf-8')
    mc='// Menu metadata is loaded one group at a time.\nimport Toybox.Lang;\nimport Toybox.WatchUi;\nmodule SettingsCatalog {\n'
    mc+='    const COUNT = '+str(len(groups))+';\n'
    mc+='    function rowId(group,page) as ResourceId {switch(group*16+page){\n'
    for group,page,ref in refs:mc+='        case '+str(group*16+page)+':return '+ref+';\n'
    mc+='    }return Rez.JsonData.ConfigGroup0Page0;}\n'
    mc+='    function pages(group){switch(group){\n'
    for i,count in enumerate(page_counts):
        if count!=1:mc+='        case '+str(i)+':return '+str(count)+';\n'
    mc+='    }return 1;}\n'
    mc+='    const OPTIONS = ['+','.join(option_refs)+'];\n'
    # Packed strings avoid allocating an entire choice array for each menu caption.
    mc+='    function label(index,value) as String {switch(index){\n'
    for i,table in enumerate(tables):
        if len(table)<=12:continue
        width=max(map(len,table))
        mc+='        case '+str(i)+':return packedLabel(Rez.JsonData.ConfigLabels'+str(i)+','+str(len(table))+',value);\n'
    mc+='    }var labels=choices(index);return labels[value] as String;}\n'
    mc+='    function packedLabel(id as ResourceId,count,value) as String {var text=WatchUi.loadResource(id) as String;var width=(text.length()/count).toNumber();return text.substring(value*width,(value+1)*width); }\n'
    mc+='''    function groups() as Array<String> { return WatchUi.loadResource(Rez.JsonData.ConfigGroups) as Array<String>; }
    function rows(group,page) as Array { return WatchUi.loadResource(rowId(group,page)) as Array; }
    function choices(index) as Array { return WatchUi.loadResource(OPTIONS[index]) as Array; }
}
'''
    mc=mc.replace('    function ', '    (:extendedCode)\n    function ')
    (ROOT/'source/SettingsCatalog.mc').write_text(mc)
    defaults='// Small validated defaults: no full settings map is loaded while rendering.\nmodule PrefsDefaults {\n'
    defaults+='    function value(key) { switch(key) {\n'
    for row in rows:
        if row['type']!=1 and row['default']!=0:defaults+='        case '+js(row['key'])+':return '+js(row['default'])+';\n'
    defaults+='    } return 0; }\n'
    defaults+='''    function max(key) {
        var suffix=key.length()>=4 ? key.substring(key.length()-4,key.length()) : "";
        if(suffix.equals("Goal")){return 1000000;}
        if(suffix.equals("Font") || suffix.equals("Size")){
            return key.equals("dataFont") || key.equals("dataSize") || key.equals("timeFont") || key.equals("timeSize") || key.equals("circleFont") || key.equals("circleSize") || key.equals("secondsFont") || key.equals("secondsSize") ? 2 : 3;
        }
        if(key.length()>=5 && key.substring(key.length()-5,key.length()).equals("Style")){return key.equals("cellsStyle") || key.equals("chartStyle") || key.equals("moveStyle") ? 2 : (key.equals("circleStyle") || key.equals("ringStyle") ? 3 : (key.equals("bottomRightStyle") ? 6 : 5));}
        switch(key){
            case "cellsSource":case "ringSource":case "moveSource":case "dateFormat":return 7;
            case "ringStart":return 3;
            case "timeSeparator":case "circleBackground":case "chartMinutes":case "heartRefresh":case "analogHandMode":return 2;
            case "secondsMode":return 3;
            case "topCardImage":case "bottomCardImage":return 20;
            case "timeFormat":case "temperatureUnit":case "distanceUnit":case "altitudeUnit":case "powerProfile":case "heartSource":return 1;
        }
        return 28;
    }
}
'''
    (ROOT/'source/PrefsDefaults.mc').write_text(defaults)
    properties=ET.Element('properties');settings=ET.Element('settings');option_ids={}
    for row in rows:
        k=row['key'];typ=row['type']
        ET.SubElement(properties,'property',id=k,type='boolean' if typ==1 else 'number').text=str(row['default']).lower()
        title=groups[row['group']][1]+' · '+row['label']
        ET.SubElement(strings,'string',id='Setting_'+k,scope='settings').text=title
        el=ET.SubElement(settings,'setting',propertyKey='@Properties.'+k,title='@Strings.Setting_'+k)
        cfg=ET.SubElement(el,'settingConfig',type=['list','boolean','numeric'][typ])
        if typ==2:cfg.set('min',str(row['min']));cfg.set('max',str(row['max']))
        for i,text in enumerate(row['options']):
            ident=option_ids.setdefault(text,'Option_'+str(len(option_ids)))
            if strings.find("string[@id='"+ident+"']") is None:ET.SubElement(strings,'string',id=ident,scope='settings').text=text
            ET.SubElement(cfg,'listEntry',value=str(i)).text='@Strings.'+ident
    for path,el in [('resources/settings/properties.xml',properties),('resources/settings/settings.xml',settings),('resources/strings/strings.xml',strings)]:
        tree=ET.ElementTree(el);ET.indent(tree,space='  ');tree.write(ROOT/path,encoding='utf-8',xml_declaration=True)
    import subprocess
    subprocess.run(['python3',str(ROOT/'scripts/generate-english.py')],check=True)
    print(f'Generated {len(rows)} shared settings in {len(groups)} groups; {len(METRICS)-1} data choices.')
if __name__=='__main__':main()
