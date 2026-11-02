import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class RetroWorldApp extends Application.AppBase {
    function initialize() { AppBase.initialize(); }
    function getInitialView() {var view=new RetroWorldView();return [view,new RetroWorldDelegate(view)];}
    function onSettingsChanged() {
        FaceSettings.load();SolarMap._slot=-1;Environment._readAt=-1;Environment._sunDay=-1;
        var views=WatchUi.getCurrentView();
        var view=views[0];if(view instanceof RetroWorldView) {view.settingsChanged();}
        WatchUi.requestUpdate();
    }
}

class RetroWorldDelegate extends WatchUi.WatchFaceDelegate {
    var _view;
    function initialize(view) {WatchFaceDelegate.initialize();_view=view;}
    function onPowerBudgetExceeded(powerInfo) {_view._partialBlocked=true;}
}

class RetroWorldView extends WatchUi.WatchFace {
    var _aod;var _dial;var _large;var _date;var _weekdays;var _circle;var _letters;var _weather;
    var _tiny;var _medium;var _weatherFont;var _environmentWake=true;
    var _minute=-1;var _logged=false;var _sleeping=false;
    var _hour=0;var _min=0;var _reportedMinute=-1;var _visibleSecond=-1;
    var _circleBuffer;var _secSprites as Array<WatchUi.BitmapResource> = [];var _xs as Array<Number> = [];var _ys as Array<Number> = [];
    var _oldSecond=-1;var _lastSecond=-1;var _partialBlocked=false;
    function initialize() {
        WatchFace.initialize();
        FaceSettings.load();
        _dial=WatchUi.loadResource(Rez.Drawables.Dial);
        if(DeviceProfile.COLOR) {_aod=WatchUi.loadResource(Rez.Drawables.Aod);}
        _large=WatchUi.loadResource(Rez.Drawables.Large);
        _date=WatchUi.loadResource(Rez.Drawables.Date);
        _letters=WatchUi.loadResource(Rez.Drawables.Letters);
        _weekdays=WatchUi.loadResource(Rez.Drawables.Weekdays);
        _circle=WatchUi.loadResource(Rez.Drawables.Circle);
        _weather=WatchUi.loadResource(Rez.Drawables.WeatherSmall);
        _tiny=WatchUi.loadResource(Rez.Fonts.Tiny);_medium=WatchUi.loadResource(Rez.Fonts.Medium);
        _weatherFont=WatchUi.loadResource(Rez.Fonts.WeatherSmall);
        // The native default accepts the resource's transparent palette slots on MIP.
        _circleBuffer=DeviceDrawing.buffer(39,39,DeviceProfile.CIRCLE_SCALE);
        var sprites=[Rez.Drawables.Sec0,Rez.Drawables.Sec1,Rez.Drawables.Sec2,Rez.Drawables.Sec3,Rez.Drawables.Sec4,Rez.Drawables.Sec5,Rez.Drawables.Sec6,Rez.Drawables.Sec7,Rez.Drawables.Sec8,Rez.Drawables.Sec9];
        for(var i=0;i<sprites.size();i++) {_secSprites.add(WatchUi.loadResource(sprites[i]));}
        for(var s=0;s<60;s++) {
            var a=(s*6-90)*Math.PI/180;
            _xs.add(144+(Math.cos(a)*18).toNumber());_ys.add(31+(Math.sin(a)*18).toNumber());
        }
        SolarMap.initialize();
    }
    function onShow() {_minute=-1;_environmentWake=true;}
    function settingsChanged() {_minute=-1;_environmentWake=true;_partialBlocked=false;}
    function onExitSleep() {
        _sleeping=false;_minute=-1;_environmentWake=true;
        if(PreviewMode.DIAGNOSTIC) {Performance.log("RETRO_SECONDS_WAKE");}WatchUi.requestUpdate();
    }
    function onEnterSleep() {
        _sleeping=true;
        if(DeviceProfile.COLOR) {_minute=-1;WatchUi.requestUpdate();}
        // The OS owns gesture duration. Supported MIP targets continue via
        // onPartialUpdate; AMOLED retains its independent minute-based AOD.
        if(PreviewMode.DIAGNOSTIC) {Performance.log("RETRO_SECONDS_SLEEP held="+_visibleSecond);}
    }
    function number(dc,atlas,n,x,y,w,h) {
        DeviceDrawing.sprite(dc,atlas,n,x,y,w,h,atlas==_weekdays ? 7 : 10);
    }
    function pair(dc,atlas,n,x,y,w,h) {
        number(dc,atlas,(n/10).toNumber(),x,y,w,h);
        number(dc,atlas,n%10,x+w+1,y,w,h);
    }
    function letters(dc,word as String,x,y,spacing) {
        var chars=word.toCharArray();
        for(var i=0;i<chars.size();i++) {
            var k=chars[i].toNumber()-65;DeviceDrawing.sprite(dc,_letters,k,x+i*spacing,y,6,10,26);
        }
    }
    function buildCircle() {
        var dc=DeviceDrawing.cache(DeviceDrawing.resolve(_circleBuffer).getDc(),true);dc.drawBitmap(-12,-12,_circle);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
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
    function secondDigit(dc,n,x) {DeviceDrawing.sprite(dc,_secSprites[n],0,x,122,13,24,1);}
    function needleClip(dc,s) {
        var px=_xs[s];var py=_ys[s];
        var x=px<144 ? px-1 : 143;var y=py<31 ? py-1 : 30;
        var w=(px-144).abs()+3;var h=(py-31).abs()+3;
        dc.setClip(x,y,w,h);
    }
    function paintCircle(dc,s) {
        dc=DeviceDrawing.circle(dc);
        var circleBuffer=DeviceDrawing.resolve(_circleBuffer);
        if(DeviceProfile.COLOR && (circleBuffer has :isCached) && !circleBuffer.isCached()) {buildCircle();}
        // Cached hour/minute dial; erase only the OLD needle's small bounding box.
        if(_oldSecond<0) {dc.setClip(125,12,39,39);dc.drawBitmap(125,12,circleBuffer);}
        else {
            if(_oldSecond==s) {return;}
            needleClip(dc,_oldSecond);dc.drawBitmap(125,12,circleBuffer);
        }
        // Minute redraws restore the held needle while asleep; only awake ticks change it.
        if(FaceSettings.showNeedle) {
            needleClip(dc,s);dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.setPenWidth(1);
            dc.drawLine(144,31,_xs[s],_ys[s]);
        }
        _oldSecond=s;
        dc.clearClip();
    }
    function metric(dc,x,y,width,value,font,light) {
        dc.setClip(x,y,width,font==_medium ? 12 : 8);
        dc.setColor(light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK,light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK);
        dc.fillRectangle(x,y,width,font==_medium ? 12 : 8);
        dc.setColor(light ? Graphics.COLOR_BLACK : Graphics.COLOR_WHITE,light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK);
        dc.drawText(x+width/2,y,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.clearClip();
    }
    function header(dc) {field(dc,0,26,6,83,_medium,false,false);}
    function field(dc,index,x,y,width,font,light,compact) {
        var kind=FaceSettings.slots[index];var value=DataFields.text(kind,compact);
        if(dc.getTextWidthInPixels(value,font)>width) {font=_tiny;}
        if(dc.getTextWidthInPixels(value,font)>width) {value=DataFields.value(kind);}
        // Narrow weather/sun windows use a compact numeric representation.
        if(dc.getTextWidthInPixels(value,font)>width) {value="--";}
        metric(dc,x,y,width,value,font,light);
    }
    function statusRow(dc,left,y,value) {
        // Both rows share a fixed ink origin, even when the data gains digits.
        // Use the complete 9px aperture. This native bitmap font's visible ink
        // sits one pixel below the SDK vertical-center anchor, so compensate it.
        dc.setClip(18,y-2,84,9);dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
        dc.drawText(left,y+1,_tiny,value,Graphics.TEXT_JUSTIFY_LEFT|Graphics.TEXT_JUSTIFY_VCENTER);dc.clearClip();
    }
    function weatherPanel(dc) {
        if(FaceSettings.slots[6]!=7) {field(dc,6,129,77,36,_tiny,true,false);return;}
        var kind=WeatherIcons.current(Time.now());
        DeviceDrawing.sprite(dc,_weather,kind,129,76,9,9,13);
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
        if(DeviceProfile.COLOR || !FaceSettings.continuous || _partialBlocked || _minute<0 || !_sleeping) {return;}
        // Wait for the top-of-minute full frame before using its cached hands.
        if(_minute!=(stamp/60).toNumber()) {return;}
        _visibleSecond=sec;tick(DeviceDrawing.target(dc),stamp,sec);
    }
    function onPartialUpdate(dc) {partialAt(dc,Time.now().value(),System.getClockTime().sec);}
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
        if(DeviceProfile.COLOR && _sleeping) {
            if(stamp!=_minute) {
                var is24=FaceSettings.is24(System.getDeviceSettings().is24Hour);
                AlwaysOn.draw(dc,_aod,is24 ? clock.hour : (clock.hour%12==0 ? 12 : clock.hour%12),clock.min,stamp);_minute=stamp;
            }
            return;
        }
        dc=DeviceDrawing.target(dc);
        var hr=PreviewMode.ENABLED ? 22 : clock.hour;
        var mn=PreviewMode.ENABLED ? 8 : clock.min;
        if(!_sleeping || _visibleSecond<0 || (FaceSettings.continuous && !_partialBlocked)) {_visibleSecond=clock.sec;}
        var sec=_visibleSecond;
        _hour=hr;_min=mn;
        if(_minute==stamp) {
            if(_sleeping) {return;}
            tick(dc,now.value(),sec);return;
        }
        var date=Gregorian.info(now,Time.FORMAT_SHORT);
        var settings=System.getDeviceSettings();
        LiveData.refresh(now.value(),settings);
        Environment.refresh(now,_environmentWake);_environmentWake=false;
        var is24=FaceSettings.is24(PreviewMode.ENABLED ? false : settings.is24Hour);
        var shown=FaceSettings.shownHour(hr,is24);
        dc.clearClip();dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.clear();dc.setPenWidth(1);
        DeviceDrawing.raw(dc).drawBitmap(0,0,_dial);
        // Keep the original digit shapes. A 10px gutter to the left of the
        // hour pair holds stacked AM/PM; 12h single digits omit the leading 0.
        if(is24 || FaceSettings.leadingZero || shown>=10) {number(dc,_large,(shown/10).toNumber(),26,111,22,35);}
        number(dc,_large,shown%10,49,111,22,35);pair(dc,_large,mn,79,111,22,35);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
        dc.fillRectangle(72,122,3,3);dc.fillRectangle(72,133,3,3);
        if(!is24) {letters(dc,hr>=12 ? "P" : "A",17,114,6);letters(dc,"M",17,127,6);}
        var day=PreviewMode.ENABLED ? 30 : date.day;
        var month=PreviewMode.ENABLED ? 6 : date.month;
        var weekday=PreviewMode.ENABLED ? 0 : date.day_of_week-1;
        if(FaceSettings.showDate) {
        number(dc,_weekdays,weekday,84,96,32,10);
        if(month>=10) {number(dc,_date,1,123,94,8,13);}
        number(dc,_date,month%10,132,94,8,13);pair(dc,_date,day,144,94,8,13);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.drawLine(140,100,142,100);
        }
        metrics(dc);
        if(FaceSettings.showMap) {SolarMap.paint(dc,now);}
        else {dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.fillRectangle(17,56,89,29);}
        buildCircle();paintCircle(dc,sec);seconds(dc,sec);_minute=stamp;
        if(PreviewMode.DIAGNOSTIC && !_logged) {
            Performance.log("RETRO_FRAME_OK version=2.1.0 demo="+PreviewMode.ENABLED+" free="+System.getSystemStats().freeMemory+" hour="+hr+" minute="+mn+" month="+month+" day="+day+" weekday="+weekday+" mode24="+is24+" data="+(PreviewMode.ENABLED ? "fixture" : "garmin")+" configurable_seconds=true map_skin="+SolarMap.skin+" weather_kind="+Environment.category(Environment.condition)+" location_source="+Environment.source+" sunrise="+Environment.sunrise+" sunset="+Environment.sunset);
            _logged=true;
        }
        if(PreviewMode.DIAGNOSTIC && _reportedMinute!=stamp) {
            if(_reportedMinute>=0) {Performance.log("RETRO_MINUTE_OK asleep="+_sleeping+" held_second="+_visibleSecond+" env_reads="+Environment.reads+" map_builds="+SolarMap.builds+" sun_calls="+Environment.sunCalculations);}
            _reportedMinute=stamp;
        }
    }
}
