import Toybox.Graphics;
import Toybox.Test;
import Toybox.Time;

class RecordedDisplay {
    var _bitmap;
    var _measure;
    var clears;
    var shapes;
    var widths;
    var rectangles;
    var strings;
    var clips;
    var _clipped;

    function initialize() {
        if (Graphics has :createBufferedBitmap) {
            _bitmap = Graphics.createBufferedBitmap({:width=>1,:height=>1});
            _measure = _bitmap.get().getDc();
        } else {
            _bitmap = new Graphics.BufferedBitmap({:width=>1,:height=>1});
            _measure = _bitmap.getDc();
        }
        reset();
    }

    function reset() {
        clears = 0;
        shapes = 0;
        widths = 0;
        rectangles = [];
        strings = [];
        clips = [];
        _clipped = false;
    }

    function setColor(fg,bg) {}
    function clear() { clears++; }
    function fillRoundedRectangle(x,y,w,h,r) { if (!_clipped) { shapes++; } }
    function fillCircle(x,y,r) { shapes++; }
    function drawCircle(x,y,r) { shapes++; }
    function fillRectangle(x,y,w,h) { rectangles.add([x,y,w,h]); }
    function setClip(x,y,w,h) { clips.add([x,y,w,h]); _clipped = true; }
    function clearClip() { _clipped = false; }

    function getTextWidthInPixels(value,font) {
        widths++;
        return _measure.getTextWidthInPixels(value,font);
    }

    function drawText(x,y,font,value,justification) {
        strings.add([x,y,value]);
    }
}

class RecordedSignalData extends SignalData {
    var reads = 0;

    function initialize() { SignalData.initialize(); }

    function refresh(when,slots,gauge,settings,needsPowerStatus,preferBatteryDays) {
        reads++;
    }
}

function verifyRegion(actual,expected) {
    for (var i=0; i<4; i++) { Test.assertEqual(actual[i],expected[i]); }
}

function verifyNoBodyWrites(dc) {
    Test.assertEqual(dc.clears,0);
    Test.assertEqual(dc.shapes,0);
    Test.assertEqual(dc.widths,0);
}

function verifyMIPClock(small,window) {
    if (Profile.AMOLED || (window && Profile.XR < 0)) { return true; }
    var display = new RecordedDisplay();
    var face = new SignalFace();
    var data = new RecordedSignalData();
    face._data = data;
    face._showSeconds = small;
    face._windowSeconds = window;
    if (Profile.XR >= 0) { face._slots[0] = window ? Field.SECONDS : Field.HEART; }
    var base = 1760000040;
    face.drawFrame(display,new Time.Moment(base+20));
    Test.assertEqual(data.reads,1);
    Test.assertEqual(display.clears,1);

    display.reset();
    face.drawFrame(display,new Time.Moment(base+21));
    verifyNoBodyWrites(display);
    Test.assertEqual(data.reads,1);
    var count = (small ? 1 : 0)+(window ? 1 : 0);
    Test.assertEqual(display.rectangles.size(),count);
    Test.assertEqual(display.strings.size(),count);
    if (small) { verifyRegion(display.rectangles[0],face._clockTick); }
    if (window) { verifyRegion(display.rectangles[count-1],face._windowTick); }
    if (small && face._clockTickOverCorner) {
        Test.assertEqual(display.clips.size(),1);
        verifyRegion(display.clips[0],face._clockTick);
    } else {
        Test.assertEqual(display.clips.size(),0);
    }
    for (var i=0; i<count; i++) { Test.assertEqual(display.strings[i][2],"21"); }

    display.reset();
    face.drawFrame(display,new Time.Moment(base+21));
    verifyNoBodyWrites(display);
    Test.assertEqual(display.rectangles.size(),0);
    Test.assertEqual(display.strings.size(),0);

    face.onEnterSleep();
    face.drawFrame(display,new Time.Moment(base+22));
    verifyNoBodyWrites(display);
    Test.assertEqual(display.rectangles.size(),count);
    Test.assertEqual(display.strings.size(),window ? 1 : 0);
    if (window) { Test.assertEqual(display.strings[0][2],"--"); }
    Test.assertEqual(data.reads,1);

    display.reset();
    face.drawFrame(display,new Time.Moment(base+23));
    verifyNoBodyWrites(display);
    Test.assertEqual(display.rectangles.size(),0);
    Test.assertEqual(display.strings.size(),0);

    face.onExitSleep();
    face.drawFrame(display,new Time.Moment(base+24));
    verifyNoBodyWrites(display);
    Test.assertEqual(display.rectangles.size(),count);
    Test.assertEqual(display.strings.size(),count);
    Test.assertEqual(data.reads,1);

    display.reset();
    face.drawFrame(display,new Time.Moment(base+60));
    Test.assertEqual(display.clears,1);
    Test.assertEqual(data.reads,2);
    face.onHide();
    face.onShow();
    display.reset();
    face.drawFrame(display,new Time.Moment(base+60));
    Test.assertEqual(display.clears,1);
    return true;
}

(:test)
function newInstallDefaultsToNoSmallSeconds(logger) {
    Test.assertEqual(new SignalFace()._showSeconds,false);
    return true;
}

(:test)
function mipOffDoesNoWorkBetweenMinutes(logger) { return verifyMIPClock(false,false); }

(:test)
function mipClockSecondsOnlyTouchesClock(logger) { return verifyMIPClock(true,false); }

(:test)
function mipWindowSecondsOnlyTouchesWindow(logger) { return verifyMIPClock(false,true); }

(:test)
function mipBothTickRegionsStayIndependent(logger) { return verifyMIPClock(true,true); }

(:test)
function amoledRestoresAodAndLiveFrame(logger) {
    if (!Profile.AMOLED) { return true; }
    var display = new RecordedDisplay();
    var face = new SignalFace();
    var data = new RecordedSignalData();
    face._data = data;
    face._showSeconds = true;
    var base = 1760000040;
    face.drawFrame(display,new Time.Moment(base+10));
    Test.assertEqual(data.reads,1);

    display.reset();
    face.drawFrame(display,new Time.Moment(base+11));
    verifyNoBodyWrites(display);
    Test.assertEqual(display.rectangles.size(),1);
    verifyRegion(display.rectangles[0],face._clockTick);
    Test.assertEqual(display.strings[0][2],"11");

    display.reset();
    face.onEnterSleep();
    face.drawFrame(display,new Time.Moment(base+12));
    Test.assertEqual(display.clears,1);
    Test.assertEqual(display.shapes,0);
    Test.assertEqual(display.rectangles.size(),0);
    Test.assertEqual(display.strings.size(),1);
    Test.assertEqual(data.reads,1);

    display.reset();
    face.drawFrame(display,new Time.Moment(base+13));
    verifyNoBodyWrites(display);
    Test.assertEqual(display.strings.size(),0);
    Test.assertEqual(data.reads,1);
    face.drawFrame(display,new Time.Moment(base+60));
    Test.assertEqual(display.clears,1);
    Test.assertEqual(display.strings.size(),1);
    Test.assertEqual(data.reads,1);

    display.reset();
    face.onExitSleep();
    face.drawFrame(display,new Time.Moment(base+61));
    Test.assertEqual(display.clears,1);
    Test.assertEqual(data.reads,2);
    return true;
}
