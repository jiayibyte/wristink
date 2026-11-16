import Toybox.Lang;
import Toybox.WatchUi;
module SlotCatalog {
 var choiceKeys as Array<String> = ["Scene","WeatherLink","SkyDecor","TimeFormat","SkyDisplay","PanelStyle","Festival"];
 var choiceTitles as Array<ResourceId> = [Rez.Strings.Scene,Rez.Strings.WeatherLink,Rez.Strings.SkyDecor,Rez.Strings.TimeFormat,Rez.Strings.SkyDisplay,Rez.Strings.PanelStyle,Rez.Strings.Festival];
 var scenes as Array<ResourceId> = [Rez.Strings.Scene0,Rez.Strings.Scene1,Rez.Strings.Scene2,Rez.Strings.Scene3,Rez.Strings.Scene4,Rez.Strings.Scene5,Rez.Strings.Scene6,Rez.Strings.Scene7,Rez.Strings.Scene8,Rez.Strings.Scene9,Rez.Strings.Scene10,Rez.Strings.Scene11,Rez.Strings.Scene12,Rez.Strings.Scene13,Rez.Strings.Scene14,Rez.Strings.Scene15,Rez.Strings.Scene16,Rez.Strings.Scene17];
 var weatherLinks as Array<ResourceId> = [Rez.Strings.WeatherLink0,Rez.Strings.WeatherLink1];
 var skyDecorations as Array<ResourceId> = [Rez.Strings.SkyDecor0,Rez.Strings.SkyDecor1,Rez.Strings.SkyDecor2,Rez.Strings.SkyDecor3];
 var timeFormats as Array<ResourceId> = [Rez.Strings.TimeFormat0,Rez.Strings.TimeFormat1,Rez.Strings.TimeFormat2];
 var skyDisplays as Array<ResourceId> = [Rez.Strings.SkyDisplay0,Rez.Strings.SkyDisplay1];
 function isChoice(key) {for(var i=0;i<choiceKeys.size();i++) {if(choiceKeys[i].equals(key)) {return true;}}return false;}
 function choices(key as String) as Array<ResourceId> {
  switch(key) {case "Scene":return scenes;case "WeatherLink":return weatherLinks;case "SkyDecor":return skyDecorations;case "TimeFormat":return timeFormats;case "SkyDisplay":return skyDisplays;case "PanelStyle":return panelStyles;}
  return festivals;
 }
 function choiceName(key as String,value as Number) as String {return WatchUi.loadResource(choices(key)[value]) as String;}
 var festivals as Array<ResourceId> = [Rez.Strings.Festival0,Rez.Strings.Festival1,Rez.Strings.Festival2,Rez.Strings.Festival3,Rez.Strings.Festival4,Rez.Strings.Festival5];
 function festivalName(value as Number) as String {return WatchUi.loadResource(festivals[value]) as String;}
 var panelStyles as Array<ResourceId> = [Rez.Strings.PanelStyle0,Rez.Strings.PanelStyle1,Rez.Strings.PanelStyle2,Rez.Strings.PanelStyle3];
 function panelName(value as Number) as String {return WatchUi.loadResource(panelStyles[value]) as String;}
 var keys as Array<String> = ["CircleData","HeaderTop","HeaderLeft","HeaderRight","Left","Middle","Right"];
 var titles as Array<ResourceId> = [Rez.Strings.CircleData,Rez.Strings.HeaderTop,Rez.Strings.HeaderLeft,Rez.Strings.HeaderRight,Rez.Strings.Left,Rez.Strings.Middle,Rez.Strings.Right];
 var metrics as Array<ResourceId> = [Rez.Strings.Metric0,Rez.Strings.Metric1,Rez.Strings.Metric2,Rez.Strings.Metric3,Rez.Strings.Metric4,Rez.Strings.Metric5,Rez.Strings.WeatherShort,Rez.Strings.Metric7,Rez.Strings.Metric8,Rez.Strings.Metric9,Rez.Strings.Metric10,Rez.Strings.Metric11];
 function isSlot(key) {for(var i=0;i<keys.size();i++) {if(keys[i].equals(key)) {return true;}}return false;}
 function name(value as Number) as String {return WatchUi.loadResource(metrics[value]) as String;}
}
