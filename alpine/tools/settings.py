from pathlib import Path
from xml.sax.saxutils import escape
R=Path(__file__).resolve().parents[1]
fields=[('TimeFormat',0,'Time format','时间格式',['System','12 hour','24 hour'],['跟随系统','12 小时','24 小时']),('Scene',0,'Landscape','山景',['Automatic','Dawn','Day','Dusk','Night','Rain','Volcano','Lightning','Rainbow','Fireworks'],['自动','黎明','白昼','黄昏','夜晚','雨景','火山','闪电','彩虹','烟花']),('Circle',0,'Instinct circle','本能圆窗',['Heart rate','Battery days','Stress'],['心率','剩余天数','压力']),('Smart',True,'Smart scenes','智能场景',None,None),('Seconds',True,'Seconds when awake','抬腕显示秒数',None,None),('LowBattery',20,'Low battery threshold (%)','低电量阈值（%）',None,None),('StressLimit',75,'Stress threshold','压力阈值',None,None)]
for key,title,cn,default in [('Left','Left data','左侧数据',0),('Middle','Middle data','中间数据',1),('Right','Right data','右侧数据',2)]:fields.append((key,default,title,cn,['Steps','Heart rate','Calories','Altitude','Battery days','Distance'],['步数','心率','总热量','海拔','剩余天数','距离']))
props=[];settings=[];en=['<string id="AppName">WristInk Alpine</string>'];zh=['<string id="AppName">山境 Alpine</string>']
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
