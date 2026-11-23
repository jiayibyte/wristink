import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class RetroWorldApp extends Application.AppBase {
    var _view;
    function initialize() { AppBase.initialize(); }
    function getInitialView() {_view=new RetroWorldView();return [_view,new RetroWorldDelegate(_view)];}
    function onSettingsChanged() {
        FaceSettings.load();SolarMap._slot=-1;Environment._readAt=-1;Environment._sunDay=-1;
        // WatchUi.getCurrentView() needs API 3.4. On Instinct 2/2S, Descent G1,
        // Forerunner 245/745/945 and Venu (API 3.2-3.3) it was a Symbol Not
        // Found crash, so changes from the phone never reached the dial.
        if(_view!=null) {_view.settingsChanged();}
        WatchUi.requestUpdate();
    }
}

class RetroWorldDelegate extends WatchUi.WatchFaceDelegate {
    var _view;
    function initialize(view) {WatchFaceDelegate.initialize();_view=view;}
    function onPowerBudgetExceeded(powerInfo) {_view.partialBudgetExceeded();}
}

class RetroWorldView extends WatchUi.WatchFace {
    var _aod;var _dial;var _large;var _date;var _weekdays;var _circle;var _letters;var _weather;
    var _tiny;var _medium;var _weatherFont;var _environmentWake=true;
    var _minute=-1;var _dataMinute=-1;var _logged=false;var _sleeping=false;
    var _hour=0;var _min=0;var _reportedMinute=-1;var _visibleSecond=-1;
    var _circleBuffer;var _secFont;var _icons;var _xs as Array<Number> = [];var _ys as Array<Number> = [];
    var _oldSecond=-1;var _lastSecond=-1;var _partialBlocked=false;
    var _partialHeartAllowed=true;var _budgetStrikes=0;
    // API 3 monochrome watches (Instinct 2/2S, Descent G1) keep bitmaps and fonts
    // in the 64 KB app heap. Resident, they left under 3 KB and the first frame
    // ran out of memory. There the dial and the frame-only fonts are loaded per
    // full frame, one after the other.
    var _lean=false;
    var _secondWidth=13;var _secondHeight=24;var _secondY=122;var _secondTensX=132;var _secondOnesX=146;
    function initialize() {
        WatchFace.initialize();
        FaceSettings.load();Theme.load(FaceSettings.theme);
        // Colour screens draw vector panels in the theme; monochrome keeps the approved bitmap.
        _lean=!DeviceProfile.COLOR && !(Graphics has :createBufferedBitmap);
        if(DeviceProfile.COLOR) {_icons=WatchUi.loadResource(Rez.Fonts.Icons);} else if(!_lean) {_dial=WatchUi.loadResource(Rez.Drawables.Dial);}
        if(DeviceProfile.AMOLED) {_aod=WatchUi.loadResource(Rez.Drawables.Aod);}
        // Two-tone sprites are fonts, drawn in the theme's ink. The partial
        // update needs the circle, seconds and data-field fonts at all times.
        _circle=WatchUi.loadResource(Rez.Fonts.Face);
        _secFont=WatchUi.loadResource(Rez.Fonts.SegSec);
        _tiny=WatchUi.loadResource(Rez.Fonts.Tiny);_medium=WatchUi.loadResource(Rez.Fonts.Medium);
        if(!_lean) {loadFrameFonts();}
        // The native default accepts the resource's transparent palette slots on MIP.
        _circleBuffer=DeviceDrawing.buffer(39,39,DeviceProfile.CIRCLE_SCALE);
        // The seconds glyphs are generated at the native device size. Do not
        // transform their coordinates every second.
        _secondWidth=DeviceDrawing.size(13,DeviceProfile.SCALE);_secondHeight=DeviceDrawing.size(24,DeviceProfile.SCALE);
        _secondY=Math.round(DeviceProfile.Y+122*DeviceProfile.SCALE).toNumber();
        _secondTensX=Math.round(DeviceProfile.X+132*DeviceProfile.SCALE).toNumber();
        _secondOnesX=Math.round(DeviceProfile.X+146*DeviceProfile.SCALE).toNumber();
        for(var s=0;s<60;s++) {
            var a=(s*6-90)*Math.PI/180;
            _xs.add(144+(Math.cos(a)*18).toNumber());_ys.add(31+(Math.sin(a)*18).toNumber());
        }
        SolarMap.initialize();
    }
    function loadFrameFonts() {
        if(_large!=null) {return;}
        _large=WatchUi.loadResource(Rez.Fonts.Seg);
        _date=WatchUi.loadResource(Rez.Fonts.SegDate);
        _letters=WatchUi.loadResource(Rez.Fonts.Caps);
        _weekdays=WatchUi.loadResource(Rez.Fonts.Days);
        _weather=WatchUi.loadResource(Rez.Fonts.WxIcon);
        _weatherFont=WatchUi.loadResource(Rez.Fonts.WeatherSmall);
    }
    function releaseFrameFonts() {_large=null;_date=null;_letters=null;_weekdays=null;_weather=null;_weatherFont=null;}
    function onShow() {_minute=-1;_dataMinute=-1;_environmentWake=true;_partialBlocked=false;}
    function settingsChanged() {
        _dataMinute=-1;_minute=-1;_environmentWake=true;_partialBlocked=false;_partialHeartAllowed=true;_budgetStrikes=0;
        if(FaceSettings.theme!=Theme.index) {
            // Cached buffers hold the old theme's palette: recreate them.
            Theme.load(FaceSettings.theme);_circleBuffer=null;
            _circleBuffer=DeviceDrawing.buffer(39,39,DeviceProfile.CIRCLE_SCALE);SolarMap.initialize();
        }
    }
    function partialBudgetExceeded() {
        // Degrade instead of stopping. The first overrun drops the optional
        // heart redraw and the second hand, keeping only the seconds digits,
        // the cheapest work in the callback. Only a second overrun waits for
        // the next wake. (Previously one overrun froze the seconds until wake.)
        _budgetStrikes++;
        _partialBlocked=_budgetStrikes>=2;
        // The OS can stop partial callbacks after a violation. Wait for user
        // wake, then continue seconds without optional heart-rate reads/draws.
        _partialHeartAllowed=false;
        // The OS rejects the over-budget frame, so its drawing caches no longer
        // describe the display. Restore both digits and the complete dial next.
        _minute=-1;_lastSecond=-1;_oldSecond=-1;
    }
    function onExitSleep() {
        _sleeping=false;_minute=-1;_environmentWake=true;_partialBlocked=false;
        if(PreviewMode.DIAGNOSTIC) {Performance.log("RETRO_SECONDS_WAKE");}WatchUi.requestUpdate();
    }
    function onEnterSleep() {
        _sleeping=true;
        if(DeviceProfile.AMOLED || !FaceSettings.continuous) {_minute=-1;WatchUi.requestUpdate();}
        // The OS owns gesture duration. Supported MIP targets continue via
        // onPartialUpdate; AMOLED retains its independent minute-based AOD.
        if(PreviewMode.DIAGNOSTIC) {Performance.log("RETRO_SECONDS_SLEEP held="+_visibleSecond);}
    }
    function number(dc,font,n,x,y,w,h) {
        dc.setColor(Theme.ink,Graphics.COLOR_TRANSPARENT);dc.drawText(x,y,font,n.toString(),Graphics.TEXT_JUSTIFY_LEFT);
    }
    function pair(dc,atlas,n,x,y,w,h) {
        number(dc,atlas,(n/10).toNumber(),x,y,w,h);
        number(dc,atlas,n%10,x+w+1,y,w,h);
    }
    function letters(dc,word as String,x,y,spacing) {
        var chars=word.toCharArray();
        for(var i=0;i<chars.size();i++) {
            dc.setColor(Theme.ink,Graphics.COLOR_TRANSPARENT);dc.drawText(x+i*spacing,y,_letters,chars[i].toString(),Graphics.TEXT_JUSTIFY_LEFT);
        }
    }
    function buildCircle() {
        var dc=DeviceDrawing.cache(DeviceDrawing.resolve(_circleBuffer).getDc(),true);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.clear();
        dc.setColor(Theme.paper,Graphics.COLOR_TRANSPARENT);dc.drawText(-12,-12,_circle,"D",Graphics.TEXT_JUSTIFY_LEFT);
        dc.setColor(Theme.ink,Graphics.COLOR_TRANSPARENT);dc.drawText(-12,-12,_circle,"M",Graphics.TEXT_JUSTIFY_LEFT);
        dc.setColor(Theme.ink,Graphics.COLOR_WHITE);
        dc.setPenWidth(3);hand(dc,(_hour%12)*30+_min*0.5,11,19,19);
        dc.setPenWidth(2);hand(dc,_min*6,16,19,19);
        dc.setPenWidth(1);dc.fillCircle(19,19,2);_oldSecond=-1;_lastSecond=-1;
    }
    function hand(dc,degrees,radius,x,y) {
        var a=(degrees-90)*Math.PI/180;
        dc.drawLine(x,y,x+(Math.cos(a)*radius).toNumber(),y+(Math.sin(a)*radius).toNumber());
    }
    function seconds(dc,s) {
        if(!FaceSettings.showSeconds) {return;}
        if(s==_lastSecond) {return;}
        var tens=(s/10).toNumber();
        if(_lastSecond<0 || tens!=(_lastSecond/10).toNumber()) {secondDigit(dc,tens,132);}
        secondDigit(dc,s%10,146);_lastSecond=s;
    }
    function secondDigit(dc,n,x) {
        dc=DeviceDrawing.raw(dc);x=x==132 ? _secondTensX : _secondOnesX;
        dc.setClip(x,_secondY,_secondWidth,_secondHeight);
        dc.setColor(Theme.paper,Theme.paper);dc.fillRectangle(x,_secondY,_secondWidth,_secondHeight);
        dc.setColor(Theme.ink,Graphics.COLOR_TRANSPARENT);dc.drawText(x,_secondY,_secFont,n.toString(),Graphics.TEXT_JUSTIFY_LEFT);dc.clearClip();
    }
    function needleClip(dc,s) {
        var px=_xs[s];var py=_ys[s];
        var x=px<144 ? px-1 : 143;var y=py<31 ? py-1 : 30;
        var w=(px-144).abs()+3;var h=(py-31).abs()+3;
        dc.setClip(x,y,w,h);
    }
    function paintCircle(dc,s) {
        dc=DeviceDrawing.circle(dc);
        var circleBuffer=DeviceDrawing.resolve(_circleBuffer);
        if((circleBuffer has :isCached) && !circleBuffer.isCached()) {buildCircle();}
        // After a budget overrun the standby second hand is dropped: show the
        // hour/minute dial without a frozen needle.
        if(_sleeping && _budgetStrikes>0) {dc.setClip(125,12,39,39);dc.drawBitmap(125,12,circleBuffer);dc.clearClip();_oldSecond=-1;return;}
        // Cached hour/minute dial; erase only the OLD needle's small bounding box.
        if(_oldSecond<0) {dc.setClip(125,12,39,39);dc.drawBitmap(125,12,circleBuffer);}
        else {
            if(_oldSecond==s) {return;}
            needleClip(dc,_oldSecond);dc.drawBitmap(125,12,circleBuffer);
        }
        // Minute redraws restore the held needle while asleep; only awake ticks change it.
        if(FaceSettings.showNeedle) {
            needleClip(dc,s);dc.setColor(Theme.hand,Graphics.COLOR_WHITE);dc.setPenWidth(1);
            dc.drawLine(144,31,_xs[s],_ys[s]);
        }
        _oldSecond=s;
        dc.clearClip();
    }
    // Text on the black background takes the colour of its data kind on colour screens.
    function tone(kind) {
        if(!DeviceProfile.COLOR) {return Graphics.COLOR_WHITE;}
        if(Theme.index==4) {return kind==1 ? DeviceProfile.RED : Theme.label;}
        switch(kind) {
            case 1:return DeviceProfile.RED;
            case 2:case 10:return DeviceProfile.GREEN;
            case 5:case 12:return DeviceProfile.TEAL;
            case 6:case 3:case 11:case 13:return DeviceProfile.SKY;
            case 4:case 7:case 8:case 9:return DeviceProfile.AMBER;
        }
        return Theme.label;
    }
    function metric(dc,x,y,width,value,font,light) {metricTone(dc,x,y,width,value,font,light,Graphics.COLOR_WHITE);}
    function metricTone(dc,x,y,width,value,font,light,ink) {
        dc.setClip(x,y,width,font==_medium ? 12 : 8);
        dc.setColor(light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK,light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK);
        dc.fillRectangle(x,y,width,font==_medium ? 12 : 8);
        dc.setColor(light ? Theme.ink : ink,light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK);
        dc.drawText(x+width/2,y,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.clearClip();
    }
    function header(dc) {field(dc,0,26,6,83,_medium,false,false);}
    function field(dc,index,x,y,width,font,light,compact) {
        var kind=FaceSettings.slots[index];var value=DataFields.text(kind,compact);
        if(dc.getTextWidthInPixels(value,font)>width) {font=_tiny;}
        if(dc.getTextWidthInPixels(value,font)>width) {value=DataFields.value(kind);}
        // Narrow weather/sun windows use a compact numeric representation.
        if(dc.getTextWidthInPixels(value,font)>width) {value="--";}
        metricTone(dc,x,y,width,value,font,light,tone(kind));
    }
    function statusRow(dc,left,y,value) {
        // Both rows share a fixed ink origin, even when the data gains digits.
        // Use the complete 9px aperture. This native bitmap font's visible ink
        // sits one pixel below the SDK vertical-center anchor, so compensate it.
        dc.setClip(18,y-2,84,9);dc.setColor(Theme.ink,Graphics.COLOR_WHITE);
        dc.drawText(left,y+1,_tiny,value,Graphics.TEXT_JUSTIFY_LEFT|Graphics.TEXT_JUSTIFY_VCENTER);dc.clearClip();
    }
    function icon(dc,kind,x,y) {
        dc.setColor(Theme.ink,Graphics.COLOR_TRANSPARENT);dc.drawText(x,y,_weather,"abcdefghijklm".substring(kind,kind+1),Graphics.TEXT_JUSTIFY_LEFT);
    }
    // Rounded panel inset by `inset` logical pixels; shared outlines are drawn in layers.
    function slab(dc,x0,y0,x1,y1,r,inset,c) {
        var w=x1-x0+1-2*inset;var h=y1-y0+1-2*inset;if(w<=0 || h<=0) {return;}
        dc.setColor(c,c);dc.fillRoundedRectangle(x0+inset,y0+inset,w,h,r>inset ? r-inset : 1);
    }
    // Colour screens: panels as vectors in the theme. The time display and the
    // date tab are one shape: all frame layers first, then the gap, then paper,
    // so the junction has a single continuous outline.
    function panels(dc) {
        var f=Theme.frame;var p=Theme.paper;var k=Graphics.COLOR_BLACK;
        slab(dc,16,31,109,49,4,0,p);
        slab(dc,13,52,109,88,4,0,f);slab(dc,13,52,109,88,4,1,k);slab(dc,13,52,109,88,4,2,p);
        if(DeviceProfile.SUBSCREEN) {slab(dc,123,74,165,86,3,0,p);} else {slab(dc,116,67,170,87,4,0,p);}
        slab(dc,10,106,165,150,5,0,f);slab(dc,79,90,165,110,4,0,f);
        slab(dc,10,106,165,150,5,1,k);slab(dc,79,90,165,110,4,1,k);
        slab(dc,10,106,165,150,5,3,p);slab(dc,79,90,165,110,4,3,p);
        dc.setColor(Theme.ink,p);dc.fillRectangle(18,40,90,1);dc.fillRectangle(119,94,1,14);
        dc.setColor(DeviceProfile.AMBER,Graphics.COLOR_TRANSPARENT);dc.fillRectangle(16,151,144,1);
        dc.drawText(82,163,_icons,"S",Graphics.TEXT_JUSTIFY_LEFT);
        var c=DeviceDrawing.circle(dc);
        c.setColor(p,Graphics.COLOR_TRANSPARENT);c.drawText(113,0,_circle,"D",Graphics.TEXT_JUSTIFY_LEFT);
        c.setColor(Theme.ink,Graphics.COLOR_TRANSPARENT);c.drawText(113,0,_circle,"M",Graphics.TEXT_JUSTIFY_LEFT);
    }
    function weatherPanel(dc) {
        if(!DeviceProfile.SUBSCREEN) {
            // Full screens have room under the dial: 15px icon, medium numerals.
            if(FaceSettings.slots[6]!=7) {field(dc,6,119,72,49,_medium,true,false);return;}
            icon(dc,WeatherIcons.current(Time.now()),120,70);
            var text=(Environment.temperature==null ? "--" : Environment.temperature.format("%.0f"))+"C";
            var big=dc.getTextWidthInPixels(text,_medium)<=32;
            metric(dc,136,big ? 72 : 74,32,text,big ? _medium : _tiny,true);
            return;
        }
        if(FaceSettings.slots[6]!=7) {field(dc,6,129,77,36,_tiny,true,false);return;}
        var kind=WeatherIcons.current(Time.now());
        icon(dc,kind,129,76);
        var value=(Environment.temperature==null ? "--" : Environment.temperature.format("%.0f"))+"C";
        var f=dc.getTextWidthInPixels(value,_weatherFont)<=25 ? _weatherFont : _tiny;
        metric(dc,140,77,25,value,f,true);
    }
    function metrics(dc) {
        header(dc);
        field(dc,1,18,21,91,_tiny,false,false);
        field(dc,2,18,32,84,_tiny,true,false);
        field(dc,3,18,42,84,_tiny,true,false);
        weatherPanel(dc);
        field(dc,4,14,98,62,_tiny,false,false);
        field(dc,5,38,154,100,_tiny,false,false);
        field(dc,7,49,164,31,_tiny,false,true);
        field(dc,8,99,164,31,_tiny,false,true);
        if(FaceSettings.slots[7]!=8 || FaceSettings.slots[8]!=9) {
            dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.fillRectangle(82,163,13,8);
        }
    }
    function heartFields(dc) {
        if(FaceSettings.slots[0]==1) {header(dc);}
        if(FaceSettings.slots[1]==1) {field(dc,1,18,21,91,_tiny,false,false);}
        if(FaceSettings.slots[2]==1) {field(dc,2,18,32,84,_tiny,true,false);}
        if(FaceSettings.slots[3]==1) {field(dc,3,18,42,84,_tiny,true,false);}
        if(FaceSettings.slots[4]==1) {field(dc,4,14,98,62,_tiny,false,false);}
        if(FaceSettings.slots[5]==1) {field(dc,5,38,154,100,_tiny,false,false);}
        if(FaceSettings.slots[6]==1) {field(dc,6,129,77,36,_tiny,true,false);}
        if(FaceSettings.slots[7]==1) {field(dc,7,49,164,31,_tiny,false,true);}
        if(FaceSettings.slots[8]==1) {field(dc,8,99,164,31,_tiny,false,true);}
    }
    function tick(dc,stamp,sec) {
        if(FaceSettings.hasHeart() && LiveData.refreshTickHeart(stamp)) {heartFields(dc);}
        seconds(dc,sec);if(FaceSettings.showNeedle) {paintCircle(dc,sec);}
    }
    function partialAt(dc,stamp,sec) {
        if(DeviceProfile.AMOLED || !FaceSettings.continuous || _partialBlocked || _minute<0 || !_sleeping) {return;}
        // Only the second hand depends on the minute frame (its cached hands).
        // The digits keep running even if that frame arrives late; previously a
        // late frame froze the seconds for the whole minute.
        var needle=FaceSettings.showNeedle && _budgetStrikes==0 && _minute==(stamp/60).toNumber();
        // A purged dial must be rebuilt by a full callback, never inside the
        // restricted partial-update budget: skip only the needle meanwhile.
        if(needle && _circleBuffer!=null) {
            var cached=DeviceDrawing.resolve(_circleBuffer);
            if((cached has :isCached) && !cached.isCached()) {needle=false;}
        }
        _visibleSecond=sec;
        dc=DeviceDrawing.target(dc);
        // Reserve the tight MIP budget for the two seconds displays. Current HR
        // remains live while awake; at rest sample at most once every 5 seconds,
        // using the current cached sample only (never history in this callback).
        if(_partialHeartAllowed && (LiveData.heartAt<0 || stamp<LiveData.heartAt || stamp-LiveData.heartAt>=5) && FaceSettings.hasHeart() && LiveData.refreshTickHeart(stamp)) {heartFields(dc);}
        seconds(dc,sec);if(needle) {paintCircle(dc,sec);}
    }
    function onPartialUpdate(dc) {
        // A single timestamp supplies both the minute cache key and seconds.
        // Avoid a second clock object/API call in the budgeted path, and avoid
        // mixing values from opposite sides of a second/minute rollover.
        var stamp=Time.now().value();partialAt(dc,stamp,stamp%60);
    }
    function onUpdate(dc) {
        if(self has :diagnosticUpdate) {diagnosticUpdate(dc);return;}
        updateAt(dc,Time.now(),System.getClockTime());
    }
    (:diagnostic)
    function diagnosticUpdate(dc) {
        if(!Benchmark.done) {Benchmark.run(self,dc);return;}
        updateAt(dc,Time.now(),System.getClockTime());
        if(!Benchmark.ready) {Benchmark.ready=true;System.println("PERF_READY");System.exit();}
    }
    function updateAt(dc,now,clock) {
        var stamp=(now.value()/60).toNumber();
        if(DeviceProfile.AMOLED && _sleeping) {
            var is24=FaceSettings.is24(System.getDeviceSettings().is24Hour);
            AlwaysOn.draw(dc,_aod,is24 ? clock.hour : (clock.hour%12==0 ? 12 : clock.hour%12),clock.min,stamp);_minute=stamp;
            return;
        }
        dc=DeviceDrawing.target(dc);
        var hr=PreviewMode.ENABLED ? 22 : clock.hour;
        var mn=PreviewMode.ENABLED ? 8 : clock.min;
        if(!_sleeping || _visibleSecond<0 || FaceSettings.continuous) {_visibleSecond=clock.sec;}
        var sec=_visibleSecond;
        _hour=hr;_min=mn;
        // onUpdate supplies a full frame: LCD/AMOLED back buffers and the
        // Instinct sub-screen need not retain the previous callback's pixels.
        // Only onPartialUpdate may rely on the existing frame. Keep expensive
        // data reads minute-cached independently of drawing.
        var date=Gregorian.info(now,Time.FORMAT_SHORT);
        var settings=System.getDeviceSettings();
        if(_dataMinute!=stamp) {
            LiveData.refresh(now.value(),settings);
            Environment.refresh(now,_environmentWake);_environmentWake=false;
            _dataMinute=stamp;
        } else if(!_sleeping && FaceSettings.hasHeart()) {LiveData.refreshTickHeart(now.value());}
        var is24=FaceSettings.is24(PreviewMode.ENABLED ? false : settings.is24Hour);
        var shown=FaceSettings.shownHour(hr,is24);
        dc.clearClip();dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.clear();dc.setPenWidth(1);
        if(DeviceProfile.COLOR) {panels(dc);}
        else {
            var dial=_lean ? WatchUi.loadResource(Rez.Drawables.Dial) : _dial;
            DeviceDrawing.raw(dc).drawBitmap(0,0,dial);dial=null;
        }
        if(_lean) {loadFrameFonts();}
        // Keep the original digit shapes. A 10px gutter to the left of the
        // hour pair holds stacked AM/PM; 12h single digits omit the leading 0.
        if(is24 || FaceSettings.leadingZero || shown>=10) {number(dc,_large,(shown/10).toNumber(),26,111,22,35);}
        number(dc,_large,shown%10,49,111,22,35);pair(dc,_large,mn,79,111,22,35);
        dc.setColor(Theme.ink,Graphics.COLOR_WHITE);
        dc.fillRectangle(72,122,3,3);dc.fillRectangle(72,133,3,3);
        if(!is24) {letters(dc,hr>=12 ? "P" : "A",17,114,6);letters(dc,"M",17,127,6);}
        var day=PreviewMode.ENABLED ? 30 : date.day;
        var month=PreviewMode.ENABLED ? 6 : date.month;
        var weekday=PreviewMode.ENABLED ? 0 : date.day_of_week-1;
        if(FaceSettings.showDate) {
        number(dc,_weekdays,weekday,84,96,32,10);
        if(month>=10) {number(dc,_date,1,123,94,8,13);}
        number(dc,_date,month%10,132,94,8,13);pair(dc,_date,day,144,94,8,13);
        dc.setColor(Theme.ink,Graphics.COLOR_WHITE);dc.drawLine(140,100,142,100);
        }
        metrics(dc);
        if(FaceSettings.showMap) {SolarMap.paint(dc,now);}
        else {dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.fillRectangle(17,56,89,29);}
        buildCircle();paintCircle(dc,sec);
        if(!_sleeping || FaceSettings.continuous) {seconds(dc,sec);}
        if(_lean) {releaseFrameFonts();}
        _minute=stamp;
        if(PreviewMode.DIAGNOSTIC && !_logged) {
            Performance.log("RETRO_FRAME_OK version=2.2.0 demo="+PreviewMode.ENABLED+" free="+System.getSystemStats().freeMemory+" hour="+hr+" minute="+mn+" month="+month+" day="+day+" weekday="+weekday+" mode24="+is24+" data="+(PreviewMode.ENABLED ? "fixture" : "garmin")+" configurable_seconds=true map_skin="+SolarMap.skin+" weather_kind="+Environment.category(Environment.condition)+" location_source="+Environment.source+" sunrise="+Environment.sunrise+" sunset="+Environment.sunset);
            _logged=true;
        }
        if(PreviewMode.DIAGNOSTIC && _reportedMinute!=stamp) {
            if(_reportedMinute>=0) {Performance.log("RETRO_MINUTE_OK asleep="+_sleeping+" held_second="+_visibleSecond+" env_reads="+Environment.reads+" map_builds="+SolarMap.builds+" sun_calls="+Environment.sunCalculations);}
            _reportedMinute=stamp;
        }
    }
}
