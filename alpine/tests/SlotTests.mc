import Toybox.Test;
import Toybox.Application;
(:test)
function dataSlotMappingsAndWeatherUnits(logger) {
 Data.weather=WeatherStyle.SNOW;Data.temp=-6;Data.fahrenheit=false;
 Test.assertEqual(Data.label(6),"SNOW");Test.assertEqual(Data.value(6),"-6C");
 Data.fahrenheit=true;Test.assertEqual(Data.value(6),"21F");
 Data.temp=0;Data.fahrenheit=false;Test.assertEqual(Data.value(6),"0C");
 Data.temp=null;Data.weather=0;Test.assertEqual(Data.value(6),"--");
 Data.stress=0;Data.notifications=0;Test.assertEqual(Data.value(7),"0");Test.assertEqual(Data.value(8),"0");
 Data.rise=0;Data.set=23*60+59;Test.assertEqual(Data.value(9),"00:00");Test.assertEqual(Data.value(10),"23:59");
 Data.rise=null;Test.assertEqual(Data.value(9),"--:--");
 Test.assertEqual(Data.label(11),"");Test.assertEqual(Data.value(11),"");Test.assertEqual(Data.header(11),"");
 return true;
}
(:test)
function slotChoicesPersistAndDoNotOverwriteOtherSlots(logger) {
 Settings.load();var circle=Settings.circle;var mid=Settings.middle;var top=Settings.top;
 var ok=Settings.setSlot("CircleData",8) && Settings.setSlot("Middle",4) && Settings.setSlot("HeaderTop",5);
 Settings.load();ok=ok && Settings.circle==8 && Settings.middle==4 && Settings.top==5;
 ok=ok && !Settings.setSlot("CircleData",12) && !Settings.setSlot("Unknown",1);
 ok=ok && Settings.circle==8;
 Settings.setSlot("CircleData",circle);Settings.setSlot("Middle",mid);Settings.setSlot("HeaderTop",top);
 Test.assert(ok);return true;
}
(:test)
function legacyCircleAndDefaultsHaveStableMeaning(logger) {
 Test.assertEqual(Settings.legacyCircle(0),6);Test.assertEqual(Settings.legacyCircle(1),4);Test.assertEqual(Settings.legacyCircle(2),7);
 var old=Application.Properties.getValue("Circle");var value=Application.Properties.getValue("CircleData");
 Application.Storage.setValue("DataSlotsVersion",1);Application.Properties.setValue("Circle",1);Application.Properties.setValue("CircleData",6);
 Settings.load();var ok=Settings.circle==4;
 Settings.setSlot("CircleData",6);Settings.load();ok=ok && Settings.circle==6;
 Application.Properties.setValue("Circle",old);Settings.setSlot("CircleData",value);
 Test.assert(ok);return true;
}
