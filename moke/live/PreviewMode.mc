// Only the normal build includes this module. No simulated values are compiled into it.
import Toybox.Lang;
module PreviewMode {
    const ENABLED = false;
    const INTENSITY_WEEK_GOAL = 0;
    function currentHeartRate(stamp) { return null; }
    function bodyBattery() { return null; }
    function intensityProgress() { return null; }
    function moveBarLevel() { return null; }
    function weatherCondition() { return null; }
    function metric(kind) { return "--"; }
    function number(kind) { return null; }
    function trend(kind) as Array<Number or Null> { return []; }
    function history() as Array<Number or Null> { return []; }
}
