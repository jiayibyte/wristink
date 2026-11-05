import Toybox.Test;
import Toybox.System;
import Toybox.Time;
import Toybox.WatchUi;
import Toybox.Application;

// Exercise actual update/lifecycle methods, recording writes instead of drawing pixels.
class SecondsDrawingProbe extends RetroWorldView {
    var digitWrites=0;var needleWrites=0;var writtenSecond=-1;
    function initialize() {WatchFace.initialize();}
    function seconds(dc,s) {digitWrites++;writtenSecond=s;}
    function paintCircle(dc,s) {needleWrites++;}
    function header(dc) {}
    function heartFields(dc) {}
}

(:test)
function sleepStopsBothSecondWritesAndWakeResumesThem(logger) {
    FaceSettings.continuous=false;
    var view=new SecondsDrawingProbe();var now=Time.now().value();
    view._minute=(now/60).toNumber();LiveData.heartAt=now;
    view.onUpdate(null);
    Test.assertEqual(view.digitWrites,1);Test.assertEqual(view.needleWrites,1);
    var held=view._visibleSecond;
    view.onEnterSleep();view._minute=(Time.now().value()/60).toNumber();
    view.onUpdate(null);view.onUpdate(null);
    Test.assertEqual(view.digitWrites,1);Test.assertEqual(view.needleWrites,1);
    Test.assertEqual(view._visibleSecond,held);
    view.onExitSleep();Test.assert(!view._sleeping);Test.assertEqual(view._minute,-1);
    // Simulate completion of the requested full-frame refresh, then test awake ticks.
    view._minute=(Time.now().value()/60).toNumber();LiveData.heartAt=Time.now().value();
    view.onUpdate(null);
    Test.assertEqual(view.digitWrites,2);Test.assertEqual(view.needleWrites,2);
    Test.assert(view.writtenSecond>=0 && view.writtenSecond<=59);
    FaceSettings.continuous=true;return true;
}

(:test)
function continuousMipTicksUseCachedFrameAndStopOnBudgetExceeded(logger) {
    if(DeviceProfile.COLOR) {return true;}
    var view=new SecondsDrawingProbe();var stamp=Time.now().value();
    FaceSettings.continuous=true;view._minute=(stamp/60).toNumber();view._sleeping=true;
    LiveData.heartAt=stamp;
    var builds=SolarMap.builds;var reads=Environment.reads;
    view.partialAt(null,stamp,17);
    Test.assertEqual(view.writtenSecond,17);Test.assertEqual(view.needleWrites,1);
    Test.assertEqual(SolarMap.builds,builds);Test.assertEqual(Environment.reads,reads);
    var delegate=new RetroWorldDelegate(view);delegate.onPowerBudgetExceeded(new WatchUi.WatchFacePowerInfo());
    Test.assert(view._partialBlocked);Test.assert(!view._partialHeartAllowed);
    Test.assertEqual(view._minute,-1);Test.assertEqual(view._lastSecond,-1);Test.assertEqual(view._oldSecond,-1);
    view.partialAt(null,stamp,18);Test.assertEqual(view.digitWrites,1);
    view.settingsChanged();Test.assert(!view._partialBlocked);
    view.partialAt(null,stamp,19);Test.assertEqual(view.digitWrites,1);
    return true;
}

// Exercise the native seconds sprite path without repeated bitmap metadata reads.
class SecondsSpriteDc {
    var clips=0;var writes=0;var x=-1;var y=-1;var width=-1;var height=-1;
    function clearClip() {}
    function setClip(xx,yy,w,h) {x=xx;y=yy;width=w;height=h;clips++;}
    function drawBitmap(xx,yy,bitmap) {Test.assertEqual(xx,x);Test.assertEqual(yy,y);writes++;}
}

(:test)
function cachedSecondSpriteCoordinatesMatchNativeResources(logger) {
    var view=new RetroWorldView();var dc=new SecondsSpriteDc();
    var previous=new SecondsSpriteDc();
    DeviceDrawing.sprite(DeviceDrawing.target(previous),view._secSprites[9],0,132,122,13,24,1);
    view.secondDigit(dc,9,132);
    Test.assertEqual(dc.x,previous.x);Test.assertEqual(dc.y,previous.y);
    Test.assertEqual(dc.width,previous.width);Test.assertEqual(dc.height,previous.height);
    var wrapped=new NativeFaceDc(DeviceProfile.SCALE,DeviceProfile.X,DeviceProfile.Y);wrapped.bind(dc);
    view.secondDigit(wrapped,0,146);Test.assertEqual(dc.x,view._secondOnesX);
    Test.assertEqual(dc.clips,2);Test.assertEqual(dc.writes,2);
    return true;
}

(:test)
function partialSecondsDoNotPollHeartEverySecond(logger) {
    if(DeviceProfile.COLOR) {return true;}
    var view=new SecondsDrawingProbe();var stamp=Time.now().value();stamp-=stamp%60;
    FaceSettings.continuous=true;view._minute=(stamp/60).toNumber();view._sleeping=true;
    LiveData.heartAt=stamp;
    for(var i=1;i<5;i++) {view.partialAt(null,stamp+i,i);}
    Test.assertEqual(view.digitWrites,4);Test.assertEqual(view.needleWrites,4);
    Test.assertEqual(LiveData.heartAt,stamp);
    view.partialAt(null,stamp+5,5);Test.assertEqual(LiveData.heartAt,stamp+5);
    view.partialAt(null,stamp+6,6);Test.assertEqual(LiveData.heartAt,stamp+5);
    view._partialHeartAllowed=false;
    view.partialAt(null,stamp+10,10);Test.assertEqual(LiveData.heartAt,stamp+5);
    Test.assertEqual(view.digitWrites,7);Test.assertEqual(view.needleWrites,7);
    view.partialAt(null,stamp+60,0);Test.assertEqual(view.digitWrites,7);
    return true;
}

(:test)
function budgetFallbackWaitsForWakeAndRestoresSeconds(logger) {
    var view=new SecondsDrawingProbe();
    var delegate=new RetroWorldDelegate(view);
    delegate.onPowerBudgetExceeded(new WatchUi.WatchFacePowerInfo());
    Test.assert(view._partialBlocked);Test.assert(!view._partialHeartAllowed);
    // User wake recovers seconds without settings edits or repeatedly retrying
    // the rejected drawing work from inside a restricted partial callback.
    view.onExitSleep();Test.assert(!view._partialBlocked);
    delegate.onPowerBudgetExceeded(new WatchUi.WatchFacePowerInfo());
    Test.assert(view._partialBlocked);Test.assert(!view._partialHeartAllowed);
    view.onExitSleep();Test.assert(!view._partialBlocked);Test.assertEqual(view._minute,-1);
    view.settingsChanged();Test.assert(view._partialHeartAllowed);
    return true;
}

(:test)
function settingsControlTimeFieldsAndValidatePersistedValues(logger) {
    FaceSettings.timeFormat=1;Test.assert(!FaceSettings.is24(true));
    Test.assertEqual(FaceSettings.shownHour(0,false),12);Test.assertEqual(FaceSettings.shownHour(13,false),1);
    FaceSettings.timeFormat=2;Test.assert(FaceSettings.is24(false));
    Test.assertEqual(FaceSettings.shownHour(0,true),0);Test.assertEqual(FaceSettings.shownHour(23,true),23);
    FaceSettings.timeFormat=0;Test.assert(FaceSettings.is24(true));Test.assert(!FaceSettings.is24(false));
    Test.assertEqual(FaceSettings.bounded(null,3,0,14),3);
    Test.assertEqual(FaceSettings.bounded(99,3,0,14),3);
    Test.assertEqual(FaceSettings.bounded("1",3,0,14),3);
    Test.assertEqual(FaceSettings.bounded(0,3,0,14),0);
    Test.assertEqual(DataFields.text(0,false),"");
    var old=LiveData.altitude;LiveData.altitude=-42;Test.assertEqual(DataFields.value(5),"-42M");LiveData.altitude=old;
    return true;
}

(:test)
function phonePropertiesLoadAndInvalidateTheExistingView(logger) {
    var keys=["TimeFormat","Field1","RefreshMode","MapSkin","LeadingZero"];
    var values=[2,10,0,15,true];var old=[];
    for(var i=0;i<keys.size();i++) {old.add(Application.Properties.getValue(keys[i]));Application.Properties.setValue(keys[i],values[i]);}
    FaceSettings.load();
    Test.assert(FaceSettings.is24(false));Test.assertEqual(FaceSettings.slots[0],10);
    Test.assert(!FaceSettings.continuous);Test.assertEqual(FaceSettings.mapSkin,15);Test.assert(FaceSettings.leadingZero);
    var view=new SecondsDrawingProbe();view._minute=123;view._partialBlocked=true;view.settingsChanged();
    Test.assertEqual(view._minute,-1);Test.assert(!view._partialBlocked);Test.assert(view._environmentWake);
    for(var j=0;j<keys.size();j++) {Application.Properties.setValue(keys[j],old[j]);}
    FaceSettings.load();return true;
}
