import Toybox.Lang;
import Toybox.WatchUi;
module SlotCatalog {
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
