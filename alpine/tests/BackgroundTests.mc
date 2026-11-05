import Toybox.Test;
import Toybox.WatchUi;
import Toybox.Math;
(:test)
function pinnedSkinsWinOverHealthAndCalendar(logger) {
 Settings.load();var old=Settings.scene;var link=Settings.weatherLink;var holiday=Settings.festival;
 var battery=Data.battery;var stress=Data.stress;var weather=Data.weather;var rain=Data.rainy;
 Data.battery=1;Data.stress=99;Data.weather=WeatherStyle.RAIN;Data.rainy=true;Sky.phase=2;
 for(var i=1;i<=17;i++) {Settings.scene=i;Test.assertEqual(Scene.choose(720),i);}
 Settings.scene=13;Test.assertEqual(Scene.holiday(2026,12,25),0);
 Test.assert(Scene.artKey(13)>=101 && Scene.artKey(13)<=120);
 Test.assertEqual(Scene.resourceKey(13,2),Scene.artKey(13));
 for(var i=14;i<=17;i++) {Settings.scene=i;Test.assertEqual(Scene.holiday(2026,6,21),i-13);}
 Settings.scene=0;Settings.festival=0;Test.assertEqual(Scene.holiday(2026,12,25),2);
 Settings.scene=2;Test.assertEqual(Scene.holiday(2026,12,25),0);
 Settings.scene=old;Settings.weatherLink=link;Settings.festival=holiday;
 Data.battery=battery;Data.stress=stress;Data.weather=weather;Data.rainy=rain;return true;
}
(:test)
function weatherLinkChangesEffectsWithoutChangingPinnedSkin(logger) {
 var link=Settings.weatherLink;var scene=Settings.scene;var weather=Data.weather;var cover=Data.cloudCover;
 Settings.scene=13;Settings.weatherLink=0;Data.weather=WeatherStyle.RAIN;Data.cloudCover=92;
 Test.assertEqual(Scene.choose(720),13);Test.assertEqual(Scene.effectiveWeather(13),WeatherStyle.RAIN);Test.assertEqual(Scene.clouds(13),92);
 var rain=Scene.artKey(13);Data.weather=WeatherStyle.SNOW;Test.assert(Scene.artKey(13)!=rain);
 Test.assertEqual(Scene.choose(720),13);
 Settings.weatherLink=1;Test.assertEqual(Scene.effectiveWeather(13),WeatherStyle.CLEAR);Test.assertEqual(Scene.clouds(13),0);
 Test.assertEqual(Scene.effectiveWeather(5),WeatherStyle.RAIN);Test.assertEqual(Scene.effectiveWeather(10),WeatherStyle.SNOW);
 Test.assertEqual(Scene.effectiveWeather(11),WeatherStyle.CLOUDY);Test.assertEqual(Scene.effectiveWeather(12),WeatherStyle.FOG);
 Settings.scene=7;Test.assertEqual(Scene.effectiveWeather(7),WeatherStyle.STORM);
 Settings.scene=scene;Settings.weatherLink=link;Data.weather=weather;Data.cloudCover=cover;return true;
}
(:test)
function backgroundsAndOrnamentsPersistIndependently(logger) {
 Settings.load();var scene=Settings.scene;var link=Settings.weatherLink;var decor=Settings.skyDecor;
 var left=Settings.left;var format=Settings.timeFormat;
 for(var i=0;i<=17;i++) {Test.assert(Settings.setChoice("Scene",i));Settings.load();Test.assertEqual(Settings.scene,i);}
 Test.assert(Settings.setChoice("WeatherLink",1));Test.assert(Settings.setChoice("SkyDecor",3));Settings.load();
 Test.assertEqual(Settings.scene,17);Test.assertEqual(Settings.skyDecor,3);Test.assertEqual(Settings.weatherLink,1);
 Test.assert(!Settings.setChoice("Scene",18));Test.assert(!Settings.setChoice("WeatherLink",2));Test.assert(!Settings.setChoice("SkyDecor",4));
 Test.assert(!Settings.setChoice("SkyDecor",null));Test.assertEqual(Settings.skyDecor,3);
 Test.assertEqual(Settings.left,left);Test.assertEqual(Settings.timeFormat,format);
 Settings.setChoice("Scene",scene);Settings.setChoice("WeatherLink",link);Settings.setChoice("SkyDecor",decor);return true;
}
(:test)
function auroraAssetsCoverEveryLightingAndWeather(logger) {
 for(var key=101;key<=120;key++) {
  var bitmap=WatchUi.loadResource(LandscapeArt.id(key));
  Test.assertEqual(bitmap.getWidth(),Device.W);Test.assertEqual(bitmap.getHeight(),Device.H);bitmap=null;
 }
 return true;
}
class OrnamentProbe {
 var calls=0;var valid=true;var left=0;var top=0;var width=0;var height=0;
 function setClip(x,y,w,h) {left=x;top=y;width=w;height=h;}
 function clearClip() {}
 function drawBitmap(x,y,bitmap) {
  calls++;
  for(var i=left;i<left+width;i++) {
   valid=valid && i>=0 && i<Device.W && top>=0 && top+height<=Device.SKYLINE[i]-Device.SKYSHIFT;
   if(Device.MONO) {
    var dx=i-Device.CX;var dy=top+height/2-Device.CY;var r=Device.CR+Math.round(3*Device.S).toNumber();
    valid=valid && dx*dx+dy*dy>r*r;
    if(Settings.top!=11) {valid=valid && top>=Math.round(20*Device.S).toNumber();}
   }
  }
 }
}
(:test)
function ornamentsDefaultOffAndStayAboveRidgesAndCircle(logger) {
 Settings.load();Test.assertEqual(Settings.skyDecor,0);var top=Settings.top;Settings.top=11;
 var off=new OrnamentProbe();SkyOrnaments.draw(off,0,1782014400);Test.assertEqual(off.calls,0);
 var birds=new OrnamentProbe();SkyOrnaments.draw(birds,1,1782014400);Test.assertEqual(birds.calls,2);Test.assert(birds.valid);
 var plane=new OrnamentProbe();SkyOrnaments.draw(plane,2,1782014400);Test.assertEqual(plane.calls,1);Test.assert(plane.valid);
 var both=new OrnamentProbe();SkyOrnaments.draw(both,3,1782014400);Test.assertEqual(both.calls,3);Test.assert(both.valid);
 Settings.top=1;var header=new OrnamentProbe();SkyOrnaments.draw(header,3,1782014400);Test.assert(header.valid);Settings.top=top;return true;
}

class CloudClipProbe {
 var valid=true;var calls=0;
 function setColor(a,b) {}
 function setClip(x,y,w,h) {
  calls++;
  for(var i=x;i<x+w;i++) {if(i>=0 && i<Device.W) {valid=valid && y>=0 && y+h<=Device.SKYLINE[i]-Device.SKYSHIFT;}}
 }
 function fillCircle(x,y,r) {}
 function clearClip() {}
}
(:test)
function monochromeCloudsStayAboveRidgesWithoutExtraBitmap(logger) {
 if(!Device.MONO) {return true;}
 var view=new AlpineView();var top=Settings.top;var probe=new CloudClipProbe();
 for(var header=0;header<2;header++) {
  Settings.top=header==0 ? 11 : 1;
  for(var d=-3;d<=3;d++) {
   view.cloud(probe,10+d,35,29,0xFFFFFF);view.cloud(probe,77-d,24,30,0xFFFFFF);view.cloud(probe,43,36,37,0xFFFFFF);
  }
 }
 Test.assert(probe.calls>0 && probe.valid);Settings.top=top;view.releaseFaceResources();return true;
}
