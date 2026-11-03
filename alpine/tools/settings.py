"""Single source for persisted IDs, Connect IQ settings and on-watch menus."""
from pathlib import Path
from xml.sax.saxutils import escape
R=Path(__file__).resolve().parents[1]
metrics=['Steps','Heart rate','Calories','Altitude','Battery days','Distance','Weather / temperature','Stress','Notifications','Sunrise','Sunset','Hidden']
cnmetrics=['步数','心率','总热量','海拔','剩余天数','距离','天气 / 温度','压力','通知数','日出','日落','隐藏']
slots=[('CircleData',6,'Circle / weather slot','圆窗 / 天气位'),('HeaderTop',11,'Top data','顶部数据'),('HeaderLeft',11,'Mountain left data','山景左侧数据'),('HeaderRight',11,'Mountain right (colour)','山景右侧（彩屏）'),('Left',0,'Bottom left','底部左侧'),('Middle',1,'Bottom middle','底部中间'),('Right',2,'Bottom right','底部右侧')]
fields=[('TimeFormat',0,'Time format','时间格式',['System','12 hour','24 hour'],['跟随系统','12 小时','24 小时']),('Scene',0,'Landscape','山景',['Automatic','Dawn','Day','Dusk','Night','Rain','Warm accent','Lightning','Rainbow','Fireworks','Snow','Overcast','Fog'],['自动','黎明','白昼','黄昏','夜晚','雨景','暖色强调','闪电','彩虹','烟花','雪天','阴天','雾天']),('Smart',True,'Smart scenes','智能场景',None,None),('Seconds',True,'Seconds when awake','抬腕显示秒数',None,None),('LowBattery',20,'Low battery threshold (%)','低电量阈值（%）',None,None),('StressLimit',75,'Stress threshold','压力阈值',None,None)]
props=['<property id="Circle" type="number">0</property>'];settings=[]
en=['<string id="AppName">WristInk Alpine</string>','<string id="DataSlots">Fields</string><string id="CircleSlot">Circle</string><string id="WeatherSlot">Time left</string><string id="WeatherShort">Weather</string>'];zh=['<string id="AppName">山境 Alpine</string>','<string id="DataSlots">数据位</string><string id="CircleSlot">圆窗</string><string id="WeatherSlot">时间左侧</string><string id="WeatherShort">天气/温度</string>']
for i,(a,b) in enumerate(zip(metrics,cnmetrics)):
 en.append(f'<string id="Metric{i}">{escape(a)}</string>');zh.append(f'<string id="Metric{i}">{escape(b)}</string>')
for key,default,title,cn in slots:
 props.append(f'<property id="{key}" type="number">{default}</property>');en.append(f'<string id="{key}">{escape(title)}</string>');zh.append(f'<string id="{key}">{escape(cn)}</string>')
 config='<settingConfig type="list">'+''.join(f'<listEntry value="{i}">@Strings.Metric{i}</listEntry>' for i in range(len(metrics)))+'</settingConfig>'
 settings.append(f'<setting propertyKey="@Properties.{key}" title="@Strings.{key}">{config}</setting>')
for key,default,title,cn,opts,cnopts in fields:
 typ='boolean' if isinstance(default,bool) else 'number';props.append(f'<property id="{key}" type="{typ}">{str(default).lower()}</property>');en.append(f'<string id="{key}">{escape(title)}</string>');zh.append(f'<string id="{key}">{escape(cn)}</string>')
 if opts:
  config='<settingConfig type="list">'
  for i,(a,b) in enumerate(zip(opts,cnopts)):
   sid=f'{key}{i}';en.append(f'<string id="{sid}">{escape(a)}</string>');zh.append(f'<string id="{sid}">{escape(b)}</string>');config+=f'<listEntry value="{i}">@Strings.{sid}</listEntry>'
  config+='</settingConfig>'
 elif typ=='boolean':config='<settingConfig type="boolean"/>'
 else:config=f'<settingConfig type="numeric" min="{5 if key=="LowBattery" else 25}" max="{50 if key=="LowBattery" else 100}"/>'
 settings.append(f'<setting propertyKey="@Properties.{key}" title="@Strings.{key}">{config}</setting>')
(R/'resources/settings').mkdir(exist_ok=True)
(R/'resources/settings/properties.xml').write_text('<properties>'+''.join(props)+'</properties>\n')
(R/'resources/settings/settings.xml').write_text('<settings>'+''.join(settings)+'</settings>\n')
for path,items in [('resources',en),('resources-zhs',zh)]: (R/path/'strings/strings.xml').write_text('<strings>'+''.join(items)+'</strings>\n')
# Native menu strings and stable IDs generated from the same definition.
keys=','.join('"'+x[0]+'"' for x in slots);names=','.join('Rez.Strings.'+x[0] for x in slots)
(R/'source/SlotCatalog.mc').write_text('''import Toybox.Lang;
import Toybox.WatchUi;
module SlotCatalog {
 var keys as Array<String> = ['''+keys+'''];
 var titles as Array<ResourceId> = ['''+names+'''];
 var metrics as Array<ResourceId> = ['''+','.join('Rez.Strings.WeatherShort' if i==6 else 'Rez.Strings.Metric'+str(i) for i in range(len(metrics)))+'''];
 function isSlot(key) {for(var i=0;i<keys.size();i++) {if(keys[i].equals(key)) {return true;}}return false;}
 function name(value as Number) as String {return WatchUi.loadResource(metrics[value]) as String;}
}
''')
