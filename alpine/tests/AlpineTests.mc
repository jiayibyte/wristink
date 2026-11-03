import Toybox.Test;
import Toybox.Graphics;
import Toybox.Time;
import Toybox.WatchUi;
(:test)
function timeFormatBoundaries(logger) {
 Test.assertEqual(Settings.shownHour(0,false),12);Test.assertEqual(Settings.shownHour(12,false),12);
 Test.assertEqual(Settings.shownHour(23,false),11);Test.assertEqual(Settings.shownHour(0,true),0);
 Settings.timeFormat=0;Test.assert(Settings.is24(true));Test.assert(!Settings.is24(false));
 Settings.timeFormat=1;Test.assert(!Settings.is24(true));Settings.timeFormat=2;Test.assert(Settings.is24(false));Settings.timeFormat=0;return true;
}
(:test)
function freshnessRejectsMissingStaleFuture(logger) {
 var now=Time.now().value();Test.assert(!Data.fresh(null,now,180));
 Test.assert(Data.fresh(new Time.Moment(now-180),now,180));Test.assert(!Data.fresh(new Time.Moment(now-181),now,180));
 Test.assert(!Data.fresh(new Time.Moment(now+1),now,180));return true;
}
(:test)
function heartRejectsSentinels(logger) {Test.assert(!Data.validHeart(null));Test.assert(!Data.validHeart(0));Test.assert(!Data.validHeart(301));Test.assert(Data.validHeart(80));return true;}
(:test)
function sunriseTransitionsAndMissingLocation(logger) {
 Test.assertEqual(Scene.phase(329,null,null),4);Test.assertEqual(Scene.phase(330,null,null),1);
 Test.assertEqual(Scene.phase(405,null,null),2);Test.assertEqual(Scene.phase(1035,null,null),3);Test.assertEqual(Scene.phase(1110,null,null),4);
 Test.assertEqual(Scene.phase(400,420,1080),1);Test.assertEqual(Scene.phase(800,1200,400),2);return true;
}
(:test)
function scenesRespectPriorityAndExplicitChoice(logger) {
 Settings.scene=0;Settings.smart=true;Data.rise=null;Data.set=null;
 Data.battery=10;Data.stress=90;Data.rainy=true;Data.steps=11000;Data.stepGoal=10000;
 Test.assertEqual(Scene.choose(800),7);Data.battery=80;Test.assertEqual(Scene.choose(800),6);
 Data.stress=0;Test.assertEqual(Scene.choose(800),5);Data.rainy=false;
 Test.assertEqual(Scene.choose(800),8);Test.assertEqual(Scene.choose(30),9);
 Settings.smart=false;Test.assertEqual(Scene.choose(800),2);Settings.scene=3;Test.assertEqual(Scene.choose(800),3);
 Settings.scene=0;Settings.smart=true;Data.steps=null;Data.battery=null;Data.stress=null;return true;
}
(:test)
function zerosNegativeAltitudeAndUnits(logger) {
 Data.altitude=-59;Data.imperialAlt=false;Test.assertEqual(Data.value(3),"-59");
 Data.imperialAlt=true;Test.assertEqual(Data.label(3),"FT");Test.assertEqual(Data.value(3),"-194");
 Data.steps=0;Data.calories=0;Data.battery=0;Data.batteryDays=0.0;Test.assertEqual(Data.value(0),"0");Test.assertEqual(Data.value(2),"0");Test.assertEqual(Data.value(4),"0.0D");
 Data.distance=0;Data.imperialDist=false;Test.assertEqual(Data.value(5),"0.0");Data.imperialDist=true;Test.assertEqual(Data.label(5),"MI");
 Data.temp=0;Data.fahrenheit=true;Test.assertEqual(Data.temperature(),"32");Data.fahrenheit=false;Test.assertEqual(Data.temperature(),"0");
 Data.imperialAlt=false;Data.imperialDist=false;return true;
}
(:test)
function absentValuesNeverBecomeFixtures(logger) {
 Data.heart=null;Data.steps=null;Data.calories=null;Data.altitude=null;Data.distance=null;Data.battery=null;Data.batteryDays=null;Data.temp=null;
 for(var i=0;i<6;i++) {Test.assertEqual(Data.value(i),i==4 ? "--D" : "--");}
 Test.assertEqual(Data.temperature(),"--");Data.steps=10;Data.stepGoal=0;Test.assert(!Data.goal());return true;
}
class SleepProbe extends AlpineView {
 var writes=0;
 function initialize() {AlpineView.initialize();}
 function seconds(dc,sec) {writes++;}
 function circle(dc) {}
 function metrics(dc) {}
}
(:test)
function sleepStopsSecondPaintingAndWakeInvalidates(logger) {
 if(Device.AMOLED) {return true;}
 var b;var ref;
 if(Graphics has :createBufferedBitmap) {ref=Graphics.createBufferedBitmap({:width=>1,:height=>1});b=ref.get();}
 else {b=new Graphics.BufferedBitmap({:width=>1,:height=>1});}
 var dc=b.getDc();
 var v=new SleepProbe();Data.heartAt=Time.now().value();v._minute=(Time.now().value()/60).toNumber();
 v.onUpdate(dc);Test.assertEqual(v.writes,1);
 v.onEnterSleep();v._minute=(Time.now().value()/60).toNumber();v._second=-1;v.onUpdate(dc);Test.assertEqual(v.writes,1);
 v.onExitSleep();Test.assert(!v._sleep);Test.assertEqual(v._minute,-1);return true;
}
(:test)
function defaultInstinctCircleIsHeart(logger) {Settings.load();Test.assertEqual(Settings.circle,0);return true;}
(:test)
function moonCycleIsBounded(logger) {Test.assert(Scene.moon(0)>=0);Test.assert(Scene.moon(0)<29.53059);Test.assert(Scene.moon(Time.now().value())<29.53059);return true;}

class BatteryDaysFixture {var batteryInDays=null;function initialize(v) {batteryInDays=v;}}
class LegacyBatteryFixture {var battery=76;}
(:test)
function batteryEstimateUsesOnlySystemDays(logger) {
 Test.assert(Data.remainingDays(null)==null);
 Test.assert(Data.remainingDays(new LegacyBatteryFixture())==null);
 Test.assert(Data.remainingDays(new BatteryDaysFixture(null))==null);
 Test.assert(Data.remainingDays(new BatteryDaysFixture(-1))==null);
 Data.batteryDays=Data.remainingDays(new BatteryDaysFixture(18.4));Test.assertEqual(Data.daysText(),"18D");
 Data.batteryDays=Data.remainingDays(new BatteryDaysFixture(2.5));Test.assertEqual(Data.daysText(),"2.5D");
 Data.batteryDays=Data.remainingDays(new BatteryDaysFixture(0.0));Test.assertEqual(Data.daysText(),"0.0D");
 Data.batteryDays=null;Data.battery=100;Test.assertEqual(Data.value(4),"--D");return true;
}

(:test)
function everestBackgroundCachesAndAllScenesRender(logger) {
 var ref=null;var bitmap;
 if(Graphics has :createBufferedBitmap) {ref=Graphics.createBufferedBitmap({:width=>1,:height=>1});bitmap=ref.get();}
 else {bitmap=new Graphics.BufferedBitmap({:width=>1,:height=>1});}
 var dc=bitmap.getDc();var view=new AlpineView();var stamp=Time.now().value();
 Data.heart=80;Data.altitude=1280;Data.batteryDays=18.4;Data.notifications=0;
 view._scene=2;view.landscape(dc,840,stamp);
 var first=view._background;view.landscape(dc,841,stamp);
 Test.assert(view._background==first);Test.assertEqual(view._artScene,2);first=null;
 for(var scene=1;scene<=9;scene++) {
  view._scene=scene;view.landscape(dc,840,stamp);
  Test.assertEqual(view._artScene,scene);Test.assert(view._background!=null);
  view.restore(dc,12,12,20,10);
 }
 return true;
}
