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
    function getInitialView() {return [new RetroWorldView()];}
}

class RetroWorldView extends WatchUi.WatchFace {
    var _dial;var _large;var _date;var _weekdays;var _circle;var _letters;var _weather;
    var _tiny;var _medium;var _weatherFont;var _environmentWake=true;
    var _minute=-1;var _logged=false;var _sleeping=false;
    var _hour=0;var _min=0;var _reportedMinute=-1;var _visibleSecond=-1;
    var _circleBuffer;var _secSprites as Array<WatchUi.BitmapResource> = [];var _xs as Array<Number> = [];var _ys as Array<Number> = [];
    var _oldSecond=-1;var _lastSecond=-1;
    function initialize() {
        WatchFace.initialize();
        _dial=WatchUi.loadResource(Rez.Drawables.Dial);
        _large=WatchUi.loadResource(Rez.Drawables.Large);
        _date=WatchUi.loadResource(Rez.Drawables.Date);
        _letters=WatchUi.loadResource(Rez.Drawables.Letters);
        _weekdays=WatchUi.loadResource(Rez.Drawables.Weekdays);
        _circle=WatchUi.loadResource(Rez.Drawables.Circle);
        _weather=WatchUi.loadResource(Rez.Drawables.WeatherSmall);
        _tiny=WatchUi.loadResource(Rez.Fonts.Tiny);_medium=WatchUi.loadResource(Rez.Fonts.Medium);
        _weatherFont=WatchUi.loadResource(Rez.Fonts.WeatherSmall);
        // The native default accepts the resource's transparent palette slots on MIP.
        _circleBuffer=Graphics.createBufferedBitmap({:width=>39,:height=>39}).get();
        var sprites=[Rez.Drawables.Sec0,Rez.Drawables.Sec1,Rez.Drawables.Sec2,Rez.Drawables.Sec3,Rez.Drawables.Sec4,Rez.Drawables.Sec5,Rez.Drawables.Sec6,Rez.Drawables.Sec7,Rez.Drawables.Sec8,Rez.Drawables.Sec9];
        for(var i=0;i<sprites.size();i++) {_secSprites.add(WatchUi.loadResource(sprites[i]));}
        for(var s=0;s<60;s++) {
            var a=(s*6-90)*Math.PI/180;
            _xs.add(144+(Math.cos(a)*18).toNumber());_ys.add(31+(Math.sin(a)*18).toNumber());
        }
        SolarMap.initialize();
    }
    function onShow() {_minute=-1;_environmentWake=true;}
    function onExitSleep() {
        _sleeping=false;_minute=-1;_environmentWake=true;
        System.println("RETRO_SECONDS_WAKE");WatchUi.requestUpdate();
    }
    function onEnterSleep() {
        _sleeping=true;
        // Hold the last visible second; do not repaint or sample seconds at rest.
        System.println("RETRO_SECONDS_SLEEP held="+_visibleSecond);
    }
    function number(dc,atlas,n,x,y,w,h) {
        dc.setClip(x,y,w,h);dc.drawBitmap(x-n*w,y,atlas);dc.clearClip();
    }
    function pair(dc,atlas,n,x,y,w,h) {
        number(dc,atlas,(n/10).toNumber(),x,y,w,h);
        number(dc,atlas,n%10,x+w+1,y,w,h);
    }
    function letters(dc,word as String,x,y,spacing) {
        var chars=word.toCharArray();
        for(var i=0;i<chars.size();i++) {
            var k=chars[i].toNumber()-65;dc.setClip(x+i*spacing,y,5,10);
            dc.drawBitmap(x+i*spacing-k*6,y,_letters);dc.clearClip();
        }
    }
    function buildCircle() {
        var dc=_circleBuffer.getDc();dc.drawBitmap(-12,-12,_circle);
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
        if(s==_lastSecond) {return;}
        var tens=(s/10).toNumber();
        if(_lastSecond<0 || tens!=(_lastSecond/10).toNumber()) {secondDigit(dc,tens,132);}
        secondDigit(dc,s%10,146);_lastSecond=s;
    }
    function secondDigit(dc,n,x) {dc.setClip(x,122,13,24);dc.drawBitmap(x,122,_secSprites[n]);dc.clearClip();}
    function needleClip(dc,s) {
        var px=_xs[s];var py=_ys[s];
        var x=px<144 ? px-1 : 143;var y=py<31 ? py-1 : 30;
        var w=(px-144).abs()+3;var h=(py-31).abs()+3;
        dc.setClip(x,y,w,h);
    }
    function paintCircle(dc,s) {
        // Cached hour/minute dial; erase only the OLD needle's small bounding box.
        if(_oldSecond<0) {dc.setClip(125,12,39,39);dc.drawBitmap(125,12,_circleBuffer);}
        else {
            if(_oldSecond==s) {return;}
            needleClip(dc,_oldSecond);dc.drawBitmap(125,12,_circleBuffer);
        }
        // Minute redraws restore the held needle while asleep; only awake ticks change it.
        needleClip(dc,s);dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.setPenWidth(1);
        dc.drawLine(144,31,_xs[s],_ys[s]);_oldSecond=s;
        dc.clearClip();
    }
    function metric(dc,x,y,width,value,font,light) {
        dc.setClip(x,y,width,font==_medium ? 12 : 8);
        dc.setColor(light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK,light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK);
        dc.fillRectangle(x,y,width,font==_medium ? 12 : 8);
        dc.setColor(light ? Graphics.COLOR_BLACK : Graphics.COLOR_WHITE,light ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK);
        dc.drawText(x+width/2,y,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.clearClip();
    }
    function header(dc) {metric(dc,26,6,83,"HR "+LiveData.numeric(LiveData.heart),_medium,false);}
    function statusRow(dc,centerX,y,value) {
        // These labels contain 3px-wide letters/digits and exactly one 1px space.
        // Center the visible ink (omit the final advance), not the font's padded cell.
        // Hardware's circular bezel clips the two row apertures differently.
        var inkWidth=value.length()*4-3;
        var left=centerX-((inkWidth-1)/2).toNumber();
        // Use the complete 9px aperture. This native bitmap font's visible ink
        // sits one pixel below the SDK vertical-center anchor, so compensate it.
        dc.setClip(18,y-2,84,9);dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
        dc.drawText(left,y+1,_tiny,value,Graphics.TEXT_JUSTIFY_LEFT|Graphics.TEXT_JUSTIFY_VCENTER);dc.clearClip();
    }
    function weatherPanel(dc) {
        var kind=Environment.category(Environment.condition);
        dc.setClip(129,76,9,9);dc.drawBitmap(129-kind*9,76,_weather);dc.clearClip();
        var value=(Environment.temperature==null ? "--" : Environment.temperature.format("%.0f"))+"C";
        var f=dc.getTextWidthInPixels(value,_weatherFont)<=25 ? _weatherFont : _tiny;
        metric(dc,140,77,25,value,f,true);
    }
    function metrics(dc) {
        header(dc);
        metric(dc,18,21,91,"BAT "+LiveData.daysText(LiveData.batteryDays)+"D",_tiny,false);
        statusRow(dc,58,33,"STEP "+LiveData.numeric(LiveData.steps));
        statusRow(dc,59,43,"KCAL "+LiveData.numeric(LiveData.calories));
        weatherPanel(dc);
        metric(dc,14,98,62,"ALT "+LiveData.numeric(LiveData.altitude)+"M",_tiny,false);
        metric(dc,38,154,100,"DIST "+LiveData.distanceText(LiveData.distance)+"KM",_tiny,false);
        metric(dc,57,164,31,Environment.sunrise,_tiny,false);
        metric(dc,110,164,31,Environment.sunset,_tiny,false);
    }
    function onUpdate(dc) {
        var now=Time.now();var clock=System.getClockTime();
        var stamp=(now.value()/60).toNumber();
        var hr=PreviewMode.ENABLED ? 22 : clock.hour;
        var mn=PreviewMode.ENABLED ? 8 : clock.min;
        if(!_sleeping || _visibleSecond<0) {_visibleSecond=clock.sec;}
        var sec=_visibleSecond;
        _hour=hr;_min=mn;
        if(_minute==stamp) {
            if(_sleeping) {return;}
            if(LiveData.refreshHeart(now.value())) {header(dc);}
            seconds(dc,sec);paintCircle(dc,sec);return;
        }
        var date=Gregorian.info(now,Time.FORMAT_SHORT);
        var settings=System.getDeviceSettings();
        LiveData.refresh(now.value(),settings);
        Environment.refresh(now,_environmentWake);_environmentWake=false;
        var is24=PreviewMode.ENABLED ? false : settings.is24Hour;
        var shown=is24 ? hr : (hr%12==0 ? 12 : hr%12);
        dc.clearClip();dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_BLACK);dc.clear();
        dc.drawBitmap(0,0,_dial);
        pair(dc,_large,shown,24,111,22,35);pair(dc,_large,mn,79,111,22,35);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
        dc.fillRectangle(72,122,3,3);dc.fillRectangle(72,133,3,3);
        if(!is24) {letters(dc,hr>=12 ? "PM" : "AM",15,113,5);}
        var day=PreviewMode.ENABLED ? 30 : date.day;
        var month=PreviewMode.ENABLED ? 6 : date.month;
        var weekday=PreviewMode.ENABLED ? 0 : date.day_of_week-1;
        number(dc,_weekdays,weekday,84,96,32,10);
        if(month>=10) {number(dc,_date,1,123,94,8,13);}
        number(dc,_date,month%10,132,94,8,13);pair(dc,_date,day,144,94,8,13);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.drawLine(140,100,142,100);
        metrics(dc);SolarMap.paint(dc,now);buildCircle();paintCircle(dc,sec);seconds(dc,sec);_minute=stamp;
        if(!_logged) {
            System.println("RETRO_FRAME_OK version=1.2.11 demo="+PreviewMode.ENABLED+" free="+System.getSystemStats().freeMemory+" hour="+hr+" minute="+mn+" month="+month+" day="+day+" weekday="+weekday+" mode24="+is24+" data="+(PreviewMode.ENABLED ? "fixture" : "garmin")+" wake_only_seconds=true map_skin="+SolarMap.skin+" weather_kind="+Environment.category(Environment.condition)+" location_source="+Environment.source+" sunrise="+Environment.sunrise+" sunset="+Environment.sunset);
            _logged=true;
        }
        if(_reportedMinute!=stamp) {
            if(_reportedMinute>=0) {System.println("RETRO_MINUTE_OK asleep="+_sleeping+" held_second="+_visibleSecond+" env_reads="+Environment.reads+" map_builds="+SolarMap.builds+" sun_calls="+Environment.sunCalculations);}
            _reportedMinute=stamp;
        }
    }
    // Intentionally no onPartialUpdate override: no app-level one-Hz work at rest.
}
