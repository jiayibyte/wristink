import Toybox.Test;
import Toybox.Time;
import Toybox.Graphics;
class PowerTickProbe extends AlpineView {
 var secondWrites=0;var metricWrites=0;var circleWrites=0;var aodWrites=0;var last24=false;
 function initialize() {AlpineView.initialize();}
 function seconds(dc,sec) {secondWrites++;}
 function metrics(dc,heartOnly) {metricWrites++;}
 function circle(dc) {circleWrites++;}
 function aod(dc,h,m,is24) {aodWrites++;last24=is24;}
}
(:test)
function disabledSecondsAndSleepingTicksDoNoPainting(logger) {
 Settings.load();var seconds=Settings.seconds;
 var ref=null;var bitmap;
 if(Graphics has :createBufferedBitmap) {ref=Graphics.createBufferedBitmap({:width=>1,:height=>1});bitmap=ref.get();}
 else {bitmap=new Graphics.BufferedBitmap({:width=>1,:height=>1});}
 var dc=bitmap.getDc();
 var v=new PowerTickProbe();Settings.seconds=false;var now=Time.now().value();Data.heartAt=now;
 v._minute=(now/60).toNumber();v._second=-1;
 for(var i=0;i<20;i++) {v.onUpdate(dc);}
 Test.assertEqual(v.secondWrites,0);Test.assertEqual(v.metricWrites,0);Test.assertEqual(v.circleWrites,0);
 v._sleep=true;Settings.seconds=true;v.onUpdate(dc);Test.assertEqual(v.secondWrites,0);
 v.releaseFaceResources();Settings.seconds=seconds;return true;
}
(:test)
function aodReleasesLandscapeAndUsesOnlyMinuteClock(logger) {
 if(!Device.AMOLED) {return true;}
 Settings.load();var format=Settings.timeFormat;
 var ref=null;var bitmap;
 if(Graphics has :createBufferedBitmap) {ref=Graphics.createBufferedBitmap({:width=>1,:height=>1});bitmap=ref.get();}
 else {bitmap=new Graphics.BufferedBitmap({:width=>1,:height=>1});}
 var dc=bitmap.getDc();
 var v=new PowerTickProbe();Settings.timeFormat=1;v.onEnterSleep();
 var minute=Data.minute;var environment=Data.environmentAt;var heart=Data.heartAt;
 v.onUpdate(dc);Test.assertEqual(v.aodWrites,1);Test.assert(!v.last24);
 Test.assert(v._time==null);Test.assert(v._metric==null);Test.assert(v._circle==null);
 Test.assert(v._background==null);Test.assert(v._aod!=null);
 v.onUpdate(dc);Test.assertEqual(v.aodWrites,1);
 Test.assertEqual(Data.minute,minute);Test.assertEqual(Data.environmentAt,environment);Test.assertEqual(Data.heartAt,heart);
 v.onExitSleep();Test.assertEqual(v._minute,-1);v.loadFonts();Test.assert(v._time!=null && v._aod==null);
 v.releaseFaceResources();Settings.timeFormat=format;return true;
}
class MetricPatchProbe extends AlpineView {
 var restores=0;var labels=0;var painted="";var widest=0;var edges=0;var area=0;
 function initialize() {AlpineView.initialize();}
 function restore(dc,x,y,w,h) {restores++;area+=w*h;if(w>widest) {widest=w;}}
 function text(dc,x,y,font,value,c) {labels++;painted+=value+"|";}
 function rect(dc,x,y,w,h,c) {edges++;}
 function line(dc,x,y,xx,yy,c) {edges++;}
 function poly(dc,points,c) {edges++;}
}
(:test)
function heartPatchTouchesOnlyConfiguredValueBoxes(logger) {
 Settings.load();var l=Settings.left;var m=Settings.middle;var r=Settings.right;
 var steps=Data.steps;var heart=Data.heart;var calories=Data.calories;
 Settings.left=0;Settings.middle=1;Settings.right=2;Data.steps=8620;Data.heart=80;Data.calories=1688;
 var ref=null;var bitmap;
 if(Graphics has :createBufferedBitmap) {ref=Graphics.createBufferedBitmap({:width=>1,:height=>1});bitmap=ref.get();}
 else {bitmap=new Graphics.BufferedBitmap({:width=>1,:height=>1});}
 var dc=bitmap.getDc();var v=new MetricPatchProbe();v.metrics(dc,true);
 Test.assertEqual(v.restores,1);Test.assertEqual(v.labels,1);Test.assertEqual(v.painted,"80|");Test.assert(v.widest<50);Test.assertEqual(v.edges,0);Test.assertEqual(v.area,Device.MONO ? 35*12 : 43*21);
 var all=new MetricPatchProbe();Settings.left=1;Settings.middle=1;Settings.right=1;all.metrics(dc,true);
 Test.assertEqual(all.restores,3);Test.assertEqual(all.labels,3);Test.assertEqual(all.edges,0);
 v.releaseFaceResources();all.releaseFaceResources();Settings.left=l;Settings.middle=m;Settings.right=r;Data.steps=steps;Data.heart=heart;Data.calories=calories;
 return true;
}
