import Toybox.Test;
import Toybox.System;
import Toybox.Time;
import Toybox.WatchUi;

// Exercise actual update/lifecycle methods, recording writes instead of drawing pixels.
class SecondsDrawingProbe extends RetroWorldView {
    var digitWrites=0;var needleWrites=0;var writtenSecond=-1;
    function initialize() {WatchFace.initialize();}
    function seconds(dc,s) {digitWrites++;writtenSecond=s;}
    function paintCircle(dc,s) {needleWrites++;}
    function header(dc) {}
}

(:test)
function sleepStopsBothSecondWritesAndWakeResumesThem(logger) {
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
    return true;
}
