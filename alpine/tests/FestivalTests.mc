import Toybox.Test;
import Toybox.Application;
import Toybox.WatchUi;
(:test)
function festivalsUseLunarDatesAndWindowEdges(logger) {
 // HKO 2026 and 2027 calendar facts, independent public reference dates.
 Test.assertEqual(Festival.choose(2026,2,15,0),0);
 Test.assertEqual(Festival.choose(2026,2,16,0),1);
 Test.assertEqual(Festival.choose(2026,2,17,0),1);
 Test.assertEqual(Festival.choose(2026,2,23,0),1);
 Test.assertEqual(Festival.choose(2026,2,24,0),0);
 Test.assertEqual(Festival.choose(2027,2,5,0),1);
 Test.assertEqual(Festival.choose(2027,2,12,0),1);
 Test.assertEqual(Festival.choose(2027,2,13,0),0);
 Test.assertEqual(Festival.choose(2026,9,24,0),0);
 Test.assertEqual(Festival.choose(2026,9,25,0),4);
 Test.assertEqual(Festival.choose(2026,9,26,0),0);
 Test.assertEqual(Festival.choose(2027,9,15,0),4);
 Test.assertEqual(Festival.choose(2025,10,6,0),4);
 Test.assertEqual(Festival.choose(2040,9,20,0),4);
 Test.assertEqual(Festival.choose(2041,2,1,0),0);
 Test.assertEqual(Festival.dayOfYear(2024,3,1),61);
 Test.assertEqual(Festival.dayOfYear(2025,3,1),60);
 return true;
}
(:test)
function festivalsRespectOffAndManualWithoutChangingWeather(logger) {
 Test.assertEqual(Festival.choose(2026,12,23,0),0);
 Test.assertEqual(Festival.choose(2026,12,24,0),2);
 Test.assertEqual(Festival.choose(2026,12,26,0),2);
 Test.assertEqual(Festival.choose(2026,12,27,0),0);
 Test.assertEqual(Festival.choose(2026,10,31,0),3);
 Test.assertEqual(Festival.choose(2026,11,1,0),0);
 Test.assertEqual(Festival.choose(2026,2,17,1),0);
 for(var i=2;i<=5;i++) {Test.assertEqual(Festival.choose(2026,6,21,i),i-1);}
 var old=Settings.festival;Settings.load();old=Settings.festival;
 var oldLeft=Settings.left;var oldMiddle=Settings.middle;
 var weather=Data.weather;Data.weather=WeatherStyle.RAIN;
 Test.assert(Settings.setFestival(5));Settings.load();Test.assertEqual(Settings.festival,5);
 Test.assertEqual(Data.weather,WeatherStyle.RAIN);Test.assertEqual(Settings.left,oldLeft);Test.assertEqual(Settings.middle,oldMiddle);
 Test.assert(!Settings.setFestival(6));Test.assert(!Settings.setFestival(-1));Test.assertEqual(Settings.festival,5);
 Settings.setFestival(old);Data.weather=weather;return true;
}
(:test)
function festivalAssetsCoverWeatherAndLighting(logger) {
 // Exercise every resource mapping without keeping a second landscape in memory.
 for(var holiday=0;holiday<=4;holiday++) {
  for(var key=1;key<=20;key++) {
   var bitmap=WatchUi.loadResource(LandscapeArt.id(holiday*20+key));
   Test.assertEqual(bitmap.getWidth(),Device.W);Test.assertEqual(bitmap.getHeight(),Device.H);
   bitmap=null;
  }
 }
 return true;
}
