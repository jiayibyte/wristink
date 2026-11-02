"""Generate phone settings in English and Chinese from one stable schema."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    ("Hidden", "隐藏"), ("Heart rate", "心率"), ("Battery days", "预计续航天数"),
    ("Steps", "步数"), ("Calories", "热量"), ("Altitude (m)", "海拔（米）"),
    ("Distance (km)", "距离（公里）"), ("Weather temperature (C)", "天气温度（摄氏）"),
    ("Sunrise", "日出"), ("Sunset", "日落"), ("Battery percent", "电量百分比"),
    ("Step goal", "步数目标"), ("Floors climbed", "已爬楼层"),
    ("Intensity minutes (weighted)", "强度活动分钟（加权）"), ("Notifications", "通知数"),
]
SLOTS = [("Top", "顶部"), ("Below top", "顶部下方"), ("Upper white row", "白底上行"),
         ("Lower white row", "白底下行"), ("Above time", "时间上方"),
         ("Below time", "时间下方"), ("Weather window", "天气窗"),
         ("Bottom left (value only)", "底部左侧（仅数值）"), ("Bottom right (value only)", "底部右侧（仅数值）")]

def generate():
    props = ET.Element("properties"); settings = ET.Element("settings")
    strings = [ET.Element("strings"), ET.Element("strings")]
    def string(key, labels):
        for tree, label in zip(strings, labels): ET.SubElement(tree, "string", id=key).text=label
    ET.SubElement(strings[1],"string",id="AppName").text="寰游时刻"
    def setting(key, labels, default, options=None):
        ET.SubElement(props, "property", id=key, type="boolean" if isinstance(default,bool) else "number").text=str(default).lower()
        string(key+"Title",labels)
        item=ET.SubElement(settings,"setting",propertyKey="@Properties."+key,title="@Strings."+key+"Title")
        config=ET.SubElement(item,"settingConfig",type="boolean" if options is None else "list")
        if options:
            for value, label in options:
                sid=key+"Option"+str(value).replace("-","N");string(sid,label)
                ET.SubElement(config,"listEntry",value=str(value)).text="@Strings."+sid
    setting("TimeFormat",("Time format","时间格式"),0,[(0,("Follow watch","跟随手表")),(1,("12 hour","12 小时制")),(2,("24 hour","24 小时制"))])
    setting("LeadingZero",("Leading zero in 12-hour time","12 小时制显示小时前导零"),False)
    setting("RefreshMode",("Seconds refresh (continuous on supported MIP)","秒刷新（支持的 MIP 可持续）"),1,[(0,("Gesture only","仅抬腕")),(1,("Continuous partial updates","持续局部刷新"))])
    for key,en,zh in [("ShowSeconds","Digital seconds","数字秒数"),("ShowNeedle","Second hand","秒针"),("ShowDate","Date and weekday","日期与星期"),("ShowMap","World map","世界地图"),("ShowMarker","Map location marker","地图定位点")]:
        setting(key,(en,zh),True)
    setting("MapSkin",("Map style","地图样式"),-1,[(-1,("Automatic / weather","自动／天气"))]+[(i,(f"Style {i+1:02d}",f"样式 {i+1:02d}")) for i in range(16)])
    for i,labels in enumerate(SLOTS): setting(f"Field{i+1}",labels,i+1,list(enumerate(FIELDS)))
    setting("ManualLocation",("Use manual location for map / sun times","地图／日出日落使用手动位置"),False)
    for key,labels,limit in [("Latitude",("Latitude (-90 to 90)","纬度（-90 至 90）"),90),("Longitude",("Longitude (-180 to 180)","经度（-180 至 180）"),180)]:
        ET.SubElement(props,"property",id=key,type="float").text="0.0"
        string(key+"Title",labels)
        item=ET.SubElement(settings,"setting",propertyKey="@Properties."+key,title="@Strings."+key+"Title")
        ET.SubElement(item,"settingConfig",type="numeric",min=str(-limit),max=str(limit))
    for name,tree in [("properties.xml",props),("settings.xml",settings)]:
        folder=ROOT/"resources/settings";folder.mkdir(parents=True,exist_ok=True);ET.indent(tree);ET.ElementTree(tree).write(folder/name,encoding="utf-8",xml_declaration=True)
    for path,tree in zip([ROOT/"resources/strings/settings.xml",ROOT/"resources-zhs/strings/settings.xml"],strings):
        path.parent.mkdir(parents=True,exist_ok=True);ET.indent(tree);ET.ElementTree(tree).write(path,encoding="utf-8",xml_declaration=True)

if __name__ == "__main__": generate()
