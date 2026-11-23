import Toybox.Graphics;
import Toybox.System;
import Toybox.Test;
import Toybox.Time;
import Toybox.Time.Gregorian;

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
function dateKeepsItsCellsInTwoDigitMonths(logger) {
    var face = new SignalFace();
    face._date = 0;
    var november = Gregorian.info(Gregorian.moment({:year=>2026,:month=>11,:day=>19,:hour=>12}),Time.FORMAT_SHORT);
    var june = Gregorian.info(Gregorian.moment({:year=>2030,:month=>6,:day=>30,:hour=>12}),Time.FORMAT_SHORT);
    Test.assertEqual(face.dateText(november),"'26-11-19");
    Test.assertEqual(face.dateText(june),"'30- 6-30");
    face._date = 2;
    Test.assertEqual(face.dateText(november),"19-11");
    return true;
}

(:test)
function liveDataSurvivesMissingSensors(logger) {
    // Every field and gauge on the running device, including watches without
    // a barometer, floors, intensity minutes or weather.
    var data = new SignalData();
    var settings = System.getDeviceSettings();
    var slots = [Field.HEART, Field.BATTERY, Field.STEPS, Field.CALORIES, Field.DISTANCE,
                 Field.TEMP, Field.NOTIFY, Field.ALT, Field.FLOORS];
    for (var gauge = 0; gauge <= GaugeMode.INTENSITY; gauge++) {
        data.reset();
        data.refresh(Time.now(),slots,gauge,settings,true,gauge % 2 == 0);
        data.percent(gauge);
        for (var i = 0; i < slots.size(); i++) {
            Test.assert(data.text(slots[i],settings,-1,false) != null);
            Test.assert(data.text(slots[i],settings,-1,true) != null);
        }
    }
    return true;
}

(:test)
function valuesShortenOnlyWhenNeeded(logger) {
    var data = new SignalData();
    var settings = System.getDeviceSettings();
    data._values[Field.TEMP] = 19;
    data._values[Field.STEPS] = 8640;
    data._values[Field.CALORIES] = 12900;
    var metric = settings.temperatureUnits != System.UNIT_STATUTE;
    Test.assertEqual(data.text(Field.TEMP,settings,-1,false),metric ? "19°C" : "66°F");
    Test.assertEqual(data.text(Field.TEMP,settings,-1,true),metric ? "19°" : "66°");
    Test.assertEqual(data.text(Field.STEPS,settings,-1,false),"8640");
    Test.assertEqual(data.text(Field.STEPS,settings,-1,true),"8.6K");
    Test.assertEqual(data.text(Field.CALORIES,settings,-1,false),"12.9K");
    Test.assertEqual(data.text(Field.CALORIES,settings,-1,true),"13K");
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
