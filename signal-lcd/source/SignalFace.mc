import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class SignalApp extends Application.AppBase {
    var _face;

    function initialize() { AppBase.initialize(); }

    function getInitialView() {
        _face = new SignalFace();
        return [_face];
    }

    function onSettingsChanged() {
        if (_face != null) { _face.settingsChanged(); }
    }
}

class SignalFace extends WatchUi.WatchFace {
    const WEEK = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
    var _data;
    var _timeFont;
    var _label;
    var _dateFont;
    var _secondsFont;
    var _value;
    var _symbol;
    var _windowValue;
    var _aodFont;
    var _theme;
    var _type;
    var _format;
    var _date;
    var _gauge;
    var _batteryDays;
    var _showSeconds;
    var _windowSeconds;
    var _slots;
    var _statuses;
    var _powerStatus;
    var _colors;
    var _awake = true;
    var _paintedMinute = -1;
    var _paintedSecond = -1;
    var _paintedAod = false;
    var _clockTick;
    var _clockTickOverCorner;
    var _windowTick;
    var _windowDigitsX;
    var _windowDashesX;
    var _windowSymbolY;
    var _reported = false;

    function initialize() {
        WatchFace.initialize();
        _data = new SignalData();
        settingsChanged();
    }

    function setting(key, last, fallback) {
        var value = null;
        try { value = Application.Properties.getValue(key); } catch (e) {}
        return choice(value, last, fallback);
    }

    // Garmin Connect / the store may return a choice as Long, Float or a
    // numeric String. Rejecting those silently restored the default.
    function choice(value, last, fallback) {
        if (value instanceof Long || value instanceof Float || value instanceof Double || value instanceof String) {
            value = value.toNumber();
        }
        return value instanceof Number && value >= 0 && value <= last ? value : fallback;
    }

    function settingsChanged() {
        _theme = setting("Theme", Profile.THEME_MAX, 1);
        _type = setting("Typeface", 2, 0);
        _format = setting("TimeFormat", 2, 0);
        _date = setting("DateStyle", 3, 0);
        _gauge = setting("Gauge", GaugeMode.INTENSITY, GaugeMode.STEPS);
        _batteryDays = setting("BatteryDisplay", 1, 0) == 1;
        _showSeconds = setting("ClockSeconds", 1, 0) == 1;
        var hasWindow = Profile.XR >= 0;
        _slots = [
            hasWindow ? setting("Window", Field.SECONDS, Profile.WINDOW_DEFAULT) : Field.OFF,
            setting("TopLeft", Field.FLOORS, Field.STEPS),
            setting("TopRight", Field.FLOORS, Field.BATTERY),
            hasWindow ? Field.OFF : setting("BottomLeft", Field.FLOORS, Field.CALORIES),
            hasWindow ? Field.OFF : setting("BottomMiddle", Field.FLOORS, Field.TEMP),
            hasWindow ? Field.OFF : setting("BottomRight", Field.FLOORS, Field.NOTIFY),
            hasWindow ? setting("TopThird", Field.FLOORS, Field.TEMP) : Field.OFF,
            hasWindow ? setting("TopFourth", Field.FLOORS, Field.FLOORS) : Field.OFF
        ];
        _windowSeconds = _slots[0] == Field.SECONDS;
        _statuses = [
            setting("StatusText", FaceStatus.CHARGING, FaceStatus.MUTE),
            setting("StatusLeft", FaceStatus.CHARGING, FaceStatus.CONNECTED),
            setting("StatusRight", FaceStatus.CHARGING, FaceStatus.ALARM)
        ];
        _powerStatus = _statuses.indexOf(FaceStatus.LOW_BATTERY) >= 0 ||
            _statuses.indexOf(FaceStatus.CHARGING) >= 0;
        _colors = palette();
        _timeFont = null;
        if (!_showSeconds) { _secondsFont = null; }
        _clockTick = null;
        _windowTick = null;
        _paintedMinute = -1;
        _data.reset();
        WatchUi.requestUpdate();
    }

    function palette() {
        if (Profile.MONO) {
            return _theme == 5 ? [0xffffff,0xffffff,0,0,0,0] : [0,0,0xffffff,0xffffff,0xffffff,0xffffff];
        }
        return Profile.COLORS[_theme];
    }

    function onShow() { _paintedMinute = -1; }
    function onHide() {
        _paintedMinute = -1;
        _clockTick = null;
        _windowTick = null;
        _timeFont = null;
        _label = null;
        _dateFont = null;
        _secondsFont = null;
        _value = null;
        _symbol = null;
        _windowValue = null;
        _aodFont = null;
    }

    function onEnterSleep() {
        _awake = false;
        if (Profile.AMOLED || _showSeconds || _windowSeconds) { WatchUi.requestUpdate(); }
    }

    function onExitSleep() {
        _awake = true;
        if (Profile.AMOLED || _showSeconds || _windowSeconds) { WatchUi.requestUpdate(); }
    }

    function loadDisplayFonts() {
        if (_timeFont == null) {
            var id = _type == 1 ? Rez.Fonts.Contour : (_type == 2 ? Rez.Fonts.Matrix : Rez.Fonts.Segment);
            _timeFont = WatchUi.loadResource(id);
        }
        if (_label == null) {
            _label = WatchUi.loadResource(Rez.Fonts.Label);
            _dateFont = WatchUi.loadResource(Rez.Fonts.Date);
            _value = WatchUi.loadResource(Rez.Fonts.Value);
            _symbol = WatchUi.loadResource(Rez.Fonts.Symbol);
            if (Profile.XR >= 0) { _windowValue = WatchUi.loadResource(Profile.windowValueId()); }
        }
        if (_showSeconds && _secondsFont == null) { _secondsFont = WatchUi.loadResource(Rez.Fonts.Seconds); }
    }

    // The same LCD coordinate space fits beneath the independent round window.
    function x(r) { return Profile.LCD_X + p(r); }
    function y(r) { return Profile.LCD_Y + p(r); }
    function p(r) { return Math.round(r * Profile.LCD_SIZE).toNumber(); }

    function larger(a,b) { return a > b ? a : b; }
    function smaller(a,b) { return a < b ? a : b; }

    function color(dc, fg) { dc.setColor(fg, Graphics.COLOR_TRANSPARENT); }

    function box(dc, x0, y0, w, h, c) {
        color(dc,c);
        dc.fillRectangle(x0,y0,w,h);
    }

    function text(dc, cx, top, font, value, fg) {
        color(dc,fg);
        // Our BMFont cells end in a guard space. Remove it from the centering
        // width, so all fields share the same alignment of their visible ink.
        var trailing = Profile.LABEL_GAP;
        if (font == _dateFont) { trailing = Profile.DATE_GAP; }
        else if (font == _secondsFont) { trailing = Profile.SECONDS_GAP; }
        else if (font == _value) { trailing = Profile.VALUE_GAP; }
        else if (font == _symbol) { trailing = Profile.SYMBOL_GAP; }
        else if (font == _windowValue) { trailing = Profile.WINDOW_VALUE_GAP; }
        else if (font == _timeFont) { trailing = Profile.TIME_GAP; }
        else if (Profile.AMOLED && font == _aodFont) { trailing = Profile.AOD_GAP; }
        var width = dc.getTextWidthInPixels(value,font) - trailing;
        dc.drawText(cx-width/2,top,font,value,Graphics.TEXT_JUSTIFY_LEFT);
    }

    function fit(dc, value, fallback, maxWidth, font, gap) {
        if (dc.getTextWidthInPixels(value,font)-gap <= maxWidth) { return value; }
        return dc.getTextWidthInPixels(fallback,font)-gap <= maxWidth ? fallback : "--";
    }

    function progress(dc, hour, minute) {
        if (_gauge == GaugeMode.OFF) { return; }
        var raw = _gauge == GaugeMode.DAY ? (hour*60+minute)*100.0/1440.0 : _data.percent(_gauge);
        var bars = 17;
        var full = raw == null ? 0 : Math.floor(smaller(100,larger(0,raw))*bars/100.0).toNumber();
        var top = y(.234);
        var span = p(.420);
        var pitch = span/bars;
        var gap = larger(1,p(.008));
        var width = pitch-gap;
        // Center the fixed pixel grid without distributing the remainder across cells.
        var start = x(.273)+(span-(bars*pitch-gap))/2;
        var height = p(.031);
        var ink = _colors[2];
        var labelY = top+(height-Profile.LABEL_H)/2;
        text(dc,x(.224),labelY,_label,"0",ink);
        text(dc,x(.779),labelY,_label,"100",ink);
        color(dc,ink);
        for (var i=0; i<bars; i++) {
            var left = start+i*pitch;
            if (i < full) {
                dc.fillRectangle(left,top,width,height);
            } else {
                dc.fillRectangle(left,top,width,1);
                dc.fillRectangle(left,top+height-1,width,1);
                // Two-pixel cells need an open middle so they read as empty.
                if (width > 2) {
                    dc.fillRectangle(left,top+1,1,height-2);
                    dc.fillRectangle(left+width-1,top+1,1,height-2);
                }
            }
        }
    }

    function calendar(dc, info, status) {
        if (status != null) { text(dc,x(.628),y(.309),_label,status,_colors[2]); }
        if (_date == 3) { return; }
        var week = WEEK[info.day_of_week-1];
        if (_date != 2) { text(dc,x(.250),y(.366),_dateFont,week,_colors[2]); }
        text(dc,x(_date == 2 ? .5 : .644),y(.366),_dateFont,dateText(info),_colors[2]);
    }

    function dateText(info) {
        var day = info.day.format("%02d");
        var month = info.month.format("%d");
        if (_date == 2) { return day+"-"+month; }
        var digits = month+"-"+day;
        // Like the LCD it imitates, a one-digit month leaves its tens cell blank.
        // The Date atlas gives the space a digit's advance, so October to
        // December occupy the same cells instead of pushing into the frame.
        if (_date == 0) { digits = "'"+(info.year%100).format("%02d")+(info.month < 10 ? "- " : "-")+digits; }
        return digits;
    }

    function upperRight(dc, settings, seconds) {
        var field = _slots[0];
        if (Profile.XR < 0 || field == Field.OFF) { return; }
        var cx = Profile.CX;
        var cy = Profile.CY;
        var r = Profile.XR;
        var ink = _colors[2];
        var symbol = _theme == 0 ? _colors[2] : _colors[4];
        if (Profile.MONO) {
            ink = 0;
            symbol = ink;
            color(dc,0xffffff);
            dc.fillCircle(cx,cy,r);
            if (_theme == 5) {
                color(dc,ink);
                dc.drawCircle(cx,cy,r);
            }
        } else {
            color(dc,_colors[5]);
            dc.fillCircle(cx,cy,r);
            color(dc,_colors[1]);
            dc.fillCircle(cx,cy,r-larger(1,p(.005)));
        }
        if (_windowSeconds) {
            text(dc,cx,_windowSymbolY,_symbol,Field.SYMBOLS[field],symbol);
            paintWindowTick(dc,seconds < 0 ? "--" : seconds.format("%02d"),seconds < 0);
            return;
        }
        var unit = field == Field.DISTANCE || field == Field.ALT ? _data.label(field) : "";
        var raw = _data.text(field,settings,seconds,false);
        var compact = _data.text(field,settings,seconds,true);
        if (raw != "--") { raw += unit; }
        if (compact != "--") { compact += unit; }
        var limit = r*7/5;
        var big = dc.getTextWidthInPixels(raw,_windowValue)-Profile.WINDOW_VALUE_GAP <= limit;
        var font = big ? _windowValue : _value;
        var height = big ? Profile.WINDOW_VALUE_H : Profile.VALUE_H;
        var gap = big ? Profile.WINDOW_VALUE_GAP : Profile.VALUE_GAP;
        var value = fit(dc,raw,compact,limit,font,gap);
        var separation = windowSeparation();
        var iconY = cy-(height+Profile.SYMBOL_H+separation)/2;
        text(dc,cx,iconY,_symbol,Field.SYMBOLS[field],symbol);
        text(dc,cx,iconY+Profile.SYMBOL_H+separation,font,value,ink);
    }

    function windowSeparation() { return larger(2,p(.019)); }

    function dataSlot(dc, field, settings, seconds, anchor, top, capacity) {
        if (field == Field.OFF) { return; }
        var aligned = Profile.XR >= 0;
        var icon = Field.SYMBOLS[field];
        var iconWidth = dc.getTextWidthInPixels(icon,_symbol)-Profile.SYMBOL_GAP;
        var gap = aligned ? Profile.ICON_GAP : larger(1,p(.014));
        var unit = field == Field.DISTANCE || field == Field.ALT ? _data.label(field) : null;
        var unitWidth = unit == null ? 0 : dc.getTextWidthInPixels(unit,_label)-Profile.LABEL_GAP;
        var unitSpace = unit == null ? 0 : gap+unitWidth;
        var raw = _data.text(field,settings,seconds,false);
        var compact = _data.text(field,settings,seconds,true);
        // A constant icon column keeps every value in a column on one x.
        var iconSpace = aligned ? Profile.ICON_W : iconWidth;
        var available = capacity-iconSpace-gap-unitSpace;
        var value = fit(dc,raw,compact,available,_value,Profile.VALUE_GAP);
        var valueWidth = dc.getTextWidthInPixels(value,_value)-Profile.VALUE_GAP;
        var left = aligned ? anchor : anchor-(iconSpace+gap+valueWidth+unitSpace)/2;
        var valueLeft = left+iconSpace+gap;
        text(dc,left+iconSpace/2,top+(Profile.VALUE_H-Profile.SYMBOL_H)/2,_symbol,icon,_colors[4]);
        text(dc,valueLeft+valueWidth/2,top,_value,value,_colors[3]);
        if (unit != null) {
            text(dc,valueLeft+valueWidth+gap+unitWidth/2,top+Profile.VALUE_H-Profile.LABEL_H,_label,unit,_colors[3]);
        }
    }

    function outsideData(dc, settings, seconds) {
        if (Profile.XR >= 0) {
            // Two rows by two columns beside the aperture; see window_grid().
            // The left column may run to 2px before the right column's icons.
            var left = Profile.COL2-Profile.COL1-2;
            dataSlot(dc,_slots[1],settings,seconds,Profile.COL1,Profile.ROW1,left);
            dataSlot(dc,_slots[2],settings,seconds,Profile.COL2,Profile.ROW1,Profile.ROW1_END-Profile.COL2+1);
            dataSlot(dc,_slots[6],settings,seconds,Profile.COL1,Profile.ROW2,left);
            dataSlot(dc,_slots[7],settings,seconds,Profile.COL2,Profile.ROW2,Profile.ROW2_END-Profile.COL2+1);
            return;
        }
        dataSlot(dc,_slots[1],settings,seconds,x(.367),y(.122),p(.237));
        dataSlot(dc,_slots[2],settings,seconds,x(.633),y(.122),p(.237));
        for (var i=0; i<3; i++) {
            dataSlot(dc,_slots[i+3],settings,seconds,x(.284+i*.216),y(.791),p(.206));
        }
    }

    function lcdShell(dc) {
        var left = x(.078);
        var top = y(.203);
        var w = x(.922)-left;
        var h = y(.732)-top;
        var edge = larger(1,p(.006));
        color(dc,_colors[5]);
        dc.fillRoundedRectangle(left,top,w,h,p(.063));
        color(dc,_colors[1]);
        dc.fillRoundedRectangle(left+edge,top+edge,w-2*edge,h-2*edge,p(.058));
    }

    function panel(dc) {
        lcdShell(dc);
        var rule = larger(1,p(.003));
        box(dc,x(.107),y(.292),p(.786),rule,_colors[5]);
        box(dc,x(.104),y(.469),p(.792),rule,_colors[5]);
    }

    function clock(dc, time, pm, second, leftStatus, rightStatus) {
        text(dc,x(.438),y(.531),_timeFont,time,_colors[2]);
        if (pm) { text(dc,x(.151),y(.539),_label,"P",_colors[2]); }
        var rightWidth = rightStatus == null ? 0 :
            dc.getTextWidthInPixels(rightStatus,_symbol)-Profile.SYMBOL_GAP;
        var rightX = smaller(x(.866),x(.922)-larger(1,p(.006))-(rightWidth-rightWidth/2)-1);
        if (leftStatus != null) {
            var leftX = x(.789);
            if (rightStatus != null) {
                var leftWidth = dc.getTextWidthInPixels(leftStatus,_symbol)-Profile.SYMBOL_GAP;
                leftX = smaller(leftX,rightX-rightWidth/2-(leftWidth-leftWidth/2)-1);
            }
            text(dc,leftX,y(.525),_symbol,leftStatus,_colors[2]);
        }
        if (rightStatus != null) { text(dc,rightX,y(.519),_symbol,rightStatus,_colors[2]); }
        if (_showSeconds && second >= 0) { paintClockTick(dc,second.format("%02d")); }
    }

    function prepareSecondRegions(dc) {
        // Decimal digits in both atlases share a fixed advance.
        if (_showSeconds && _clockTick == null) {
            var width = dc.getTextWidthInPixels("00",_secondsFont)-Profile.SECONDS_GAP;
            _clockTick = [x(.815)-width/2,y(.591),width,Profile.SECONDS_H];
            var edge = larger(1,p(.006));
            var radius = p(.058);
            var dx = larger(0,_clockTick[0]+width-(x(.922)-edge-radius));
            var dy = larger(0,_clockTick[1]+Profile.SECONDS_H-(y(.732)-edge-radius));
            _clockTickOverCorner = dx*dx+dy*dy > radius*radius;
        }
        if (_windowSeconds && _windowTick == null) {
            var digits = dc.getTextWidthInPixels("00",_windowValue)-Profile.WINDOW_VALUE_GAP;
            var dashes = dc.getTextWidthInPixels("--",_windowValue)-Profile.WINDOW_VALUE_GAP;
            var width = larger(digits,dashes);
            var gap = windowSeparation();
            _windowSymbolY = Profile.CY-(Profile.WINDOW_VALUE_H+Profile.SYMBOL_H+gap)/2;
            _windowTick = [Profile.CX-width/2,_windowSymbolY+Profile.SYMBOL_H+gap,
                width,Profile.WINDOW_VALUE_H];
            _windowDigitsX = Profile.CX-digits/2;
            _windowDashesX = Profile.CX-dashes/2;
        }
    }

    function paintClockTick(dc, value) {
        color(dc,_colors[2]);
        dc.drawText(_clockTick[0],_clockTick[1],_secondsFont,value,Graphics.TEXT_JUSTIFY_LEFT);
    }

    function paintWindowTick(dc, value, blank) {
        color(dc,Profile.MONO ? 0 : _colors[2]);
        dc.drawText(blank ? _windowDashesX : _windowDigitsX,_windowTick[1],
            _windowValue,value,Graphics.TEXT_JUSTIFY_LEFT);
    }

    function repaintSecondRegions(dc, second) {
        if (Profile.AMOLED && (dc has :setAntiAlias)) { dc.setAntiAlias(true); }
        var blank = second < 0;
        var value = blank ? "--" : second.format("%02d");
        if (_showSeconds) {
            if (_clockTickOverCorner) {
                // Restore the curve inside the seconds rectangle, including on the 2S.
                dc.setClip(_clockTick[0],_clockTick[1],_clockTick[2],_clockTick[3]);
                box(dc,_clockTick[0],_clockTick[1],_clockTick[2],_clockTick[3],_colors[0]);
                lcdShell(dc);
                dc.clearClip();
            } else {
                box(dc,_clockTick[0],_clockTick[1],_clockTick[2],_clockTick[3],_colors[1]);
            }
            if (!blank) { paintClockTick(dc,value); }
        }
        if (_windowSeconds) {
            box(dc,_windowTick[0],_windowTick[1],_windowTick[2],_windowTick[3],
                Profile.MONO ? 0xffffff : _colors[1]);
            paintWindowTick(dc,value,blank);
        }
    }

    function onUpdate(dc) {
        drawFrame(dc,Time.now());
    }

    function drawFrame(dc, now) {
        var stamp = now.value();
        var minute = stamp/60;
        var awake = _awake || (Profile.DEMO && !Profile.AOD_PREVIEW);
        var aod = Profile.AMOLED && (!awake || Profile.AOD_PREVIEW);
        var second = awake && !aod && (_showSeconds || _windowSeconds) ?
            (Profile.DEMO ? 50 : stamp%60) : -1;
        if (_paintedMinute == minute && _paintedAod == aod) {
            if (_paintedSecond != second) {
                repaintSecondRegions(dc,second);
                _paintedSecond = second;
            }
            return;
        }
        var settings = System.getDeviceSettings();
        var info = Gregorian.info(now,Time.FORMAT_SHORT);
        var hr = Profile.DEMO ? Profile.HOUR : info.hour;
        var min = Profile.DEMO ? Profile.MINUTE : info.min;
        var is24 = _format == 2 || (_format == 0 && settings.is24Hour);
        var hour = is24 ? hr : (hr+11)%12+1;
        var time = hour.format(is24 ? "%02d" : "%d") + ":" + min.format("%02d");
        _paintedMinute = minute;
        _paintedAod = aod;
        _paintedSecond = second;
        // Smooth the LCD frame's curves where the panel can blend; MIP keeps
        // crisp whole pixels.
        if (Profile.AMOLED && (dc has :setAntiAlias)) { dc.setAntiAlias(true); }
        dc.setColor(0,aod ? 0 : _colors[0]);
        dc.clear();
        if (aod) {
            drawAlwaysOn(dc,time,Profile.AOD_PREVIEW ? Profile.AOD_PHASE : minute%4);
            report(dc);
            return;
        }

        loadDisplayFonts();
        prepareSecondRegions(dc);
        _data.refresh(now,_slots,_gauge,settings,_powerStatus,_batteryDays);
        panel(dc);
        var label = FaceStatus.visible(_statuses[0],settings,_data) ? FaceStatus.LABELS[_statuses[0]] : null;
        var leftStatus = FaceStatus.visible(_statuses[1],settings,_data) ? FaceStatus.SYMBOLS[_statuses[1]] : null;
        var rightStatus = FaceStatus.visible(_statuses[2],settings,_data) ? FaceStatus.SYMBOLS[_statuses[2]] : null;
        progress(dc,hr,min);
        calendar(dc,Profile.DEMO ? Gregorian.info(Profile.DEMO_DATE,Time.FORMAT_SHORT) : info,label);
        clock(dc,time,!is24 && hr >= 12,second,leftStatus,rightStatus);
        upperRight(dc,settings,second);
        outsideData(dc,settings,second);
        report(dc);
    }

    function drawAlwaysOn(dc,time,phase) {
        if (_aodFont == null) { _aodFont = WatchUi.loadResource(Profile.aodFontId()); }
        // Each successive minute uses a disjoint row. Small single-color text
        // is the only lit content in the system-managed always-on state.
        var stride = Profile.AOD_H+2;
        var center = Profile.SIZE/2;
        text(dc,Profile.X+center,Profile.Y+center-stride*2+phase*stride,_aodFont,time,0x7C8582);
    }

    function report(dc) {
        if (Profile.DEMO && !_reported) {
            _reported = true;
            System.println("SIGNAL_FRAME " + dc.getWidth() + "x" + dc.getHeight() +
                " free=" + System.getSystemStats().freeMemory + " type=" + _type);
        }
    }
}
