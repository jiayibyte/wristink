import Toybox.Application;
import Toybox.Graphics;
import Toybox.Math;
import Toybox.Lang;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class AlpineApp extends Application.AppBase {
    var view;
    function initialize() {AppBase.initialize();}
    function getInitialView() {if(Mode.DEMO) {Mode.refresh();}view=new AlpineView();return [view];}
    function getSettingsView() {if(view!=null) {view.prepareSettings();}Settings.load();var menu=new SlotMenu();return [menu,new SlotMenuDelegate(view,menu)];}
    function onSettingsChanged() {if(Mode.DEMO) {Mode.refresh();}if(view!=null) {view.settingsChanged();}}
}

class AlpineView extends WatchUi.WatchFace {
    var _time;var _small;var _label;var _metric;var _circle;var _aod;
    var _background=null;var _artScene=-1;var _holiday=0;
    var _sleep=false;var _minute=-1;var _scene=2;var _second=-1;var _accent=0x66CCCC;var _logged=false;
    var _settingsOpen=false;
    function initialize() {
        WatchFace.initialize();Settings.load();loadFonts();
    }
    function loadFonts() {
        _aod=null;_time=WatchUi.loadResource(Rez.Fonts.Time);_label=WatchUi.loadResource(Rez.Fonts.Label);
        // 2S uses the same 7px master for labels and dates: share the font handle.
        _small=Device.MONO && Device.S<1 ? _label : WatchUi.loadResource(Rez.Fonts.Small);
        _metric=WatchUi.loadResource(Rez.Fonts.Metric);_circle=WatchUi.loadResource(Rez.Fonts.Circle);
        // Monochrome devices never enter the AMOLED AOD rendering path.
    }
    function settingsChanged() {Settings.load();_minute=-1;Data.minute=-1;Data.heartAt=-1;Data.environmentAt=-1;WatchUi.requestUpdate();}
    function onShow() {_settingsOpen=false;_minute=-1;}
    function releaseFonts() {_time=null;_small=null;_label=null;_metric=null;_circle=null;_aod=null;}
    function prepareSettings() {_settingsOpen=true;_minute=-1;releaseFonts();}
    function releaseFaceResources() {
        _background=null;_artScene=-1;_minute=-1;
        releaseFonts();
    }
    function onHide() {if(_settingsOpen) {releaseFonts();}else {releaseFaceResources();}}
    function onEnterSleep() {_sleep=true;_minute=-1;if(Device.AMOLED) {releaseFaceResources();}WatchUi.requestUpdate();}
    function onExitSleep() {_sleep=false;_minute=-1;Data.heartAt=-1;WatchUi.requestUpdate();}
    function max(a as Numeric,b as Numeric) as Numeric {return a>b ? a : b;}
    function min(a as Numeric,b as Numeric) as Numeric {return a<b ? a : b;}
    function p(v as Numeric) as Number {return Math.round(v*Device.S).toNumber();}
    function color(dc,c as Number) {dc.setColor(c,Graphics.COLOR_TRANSPARENT);}
    function line(dc,x1 as Numeric,y1 as Numeric,x2 as Numeric,y2 as Numeric,c as Number) {color(dc,c);dc.drawLine(p(x1),p(y1),p(x2),p(y2));}
    function rect(dc,x as Numeric,y as Numeric,w as Numeric,h as Numeric,c as Number) {color(dc,c);dc.fillRectangle(p(x),p(y),p(x+w)-p(x),p(y+h)-p(y));}
    function disk(dc,x as Numeric,y as Numeric,r as Numeric,c as Number) {color(dc,c);dc.fillCircle(p(x),p(y),p(r));}
    function poly(dc,points as Array<Array<Numeric>>,c) {
        color(dc,c);dc.fillPolygon(points);
    }
    function text(dc,x as Numeric,y as Numeric,font,value as String,c as Number) {
        var xx=p(x);var yy=p(y);
        if(!Device.MONO && c==0xFFFFFF && _background!=null && font==_time) {
            color(dc,0);dc.drawText(xx-1,yy,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.drawText(xx+1,yy,font,value,Graphics.TEXT_JUSTIFY_CENTER);
            dc.drawText(xx,yy-1,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.drawText(xx,yy+1,font,value,Graphics.TEXT_JUSTIFY_CENTER);
        }
        color(dc,c);dc.drawText(xx,yy,font,value,Graphics.TEXT_JUSTIFY_CENTER);
    }
    function restore(dc,x as Numeric,y as Numeric,w as Numeric,h as Numeric) {
        dc.setClip(p(x),p(y),p(x+w)-p(x),p(y+h)-p(y));
        if(_background!=null) {dc.drawBitmap(0,0,_background);}else {dc.setColor(0,0);dc.clear();}
        dc.clearClip();
    }
    function accent(scene) {
        if(Device.MONO) {return Graphics.COLOR_WHITE;}
        if(scene==1) {return 0xCCCCFF;}if(scene==3 || scene==6 || scene==7) {return 0xFFAA55;}
        if(scene==4 || scene==9) {return 0x9999FF;}if(scene==5) {return 0x99BBBB;}return 0x66DDDD;
    }
    function skyPixel(x,y) {return x>=0 && y>=0 && x<Device.W && y<Device.H && y<Device.SKYLINE[x]-Device.SKYSHIFT;}
    function cloud(dc,x as Numeric,y as Numeric,width as Numeric,c as Number) {
        // Native filled primitives avoid per-pixel VM loops in a watch-face callback.
        var w=p(width);var xx=p(x);var yy=p(y);var r=(w*.20).toNumber();
        var top=yy-r;var bottom=yy+r+1;
        if(Device.MONO) {
            // Keep clouds above the highest ridge in their span. This avoids a
            // second full-width foreground bitmap in the tiny watch-face heap.
            var edge=Device.H;
            for(var i=xx;i<xx+w;i++) {if(i>=0 && i<Device.W) {var e=Device.SKYLINE[i]-Device.SKYSHIFT;if(e<edge) {edge=e;}}}
            if(bottom>edge) {yy-=bottom-edge;top=yy-r;bottom=edge;}
            if(Settings.top!=11 && top<p(20)) {top=p(20);}
        }
        if(bottom<=top) {return;}
        dc.setClip(xx,top,w,bottom-top);color(dc,c);
        dc.fillCircle(xx+r,yy+r,r);
        dc.fillCircle(xx+(w*.47).toNumber(),yy+(w*.15).toNumber(),(w*.25).toNumber());
        dc.fillCircle(xx+(w*.76).toNumber(),yy+r,r);
        dc.clearClip();
    }
    function body(dc,progress,isMoon,stamp) {
        var x=(Device.MONO ? 10 : 12)+(Device.MONO ? 98 : 236)*progress;
        var leftEdge=(Device.SKYLINE[p(Device.MONO ? 10 : 12)]-Device.SKYSHIFT)/Device.S;var rightEdge=(Device.SKYLINE[p(Device.MONO ? 108 : 248)]-Device.SKYSHIFT)/Device.S;
        var baseline=leftEdge+(rightEdge-leftEdge)*progress;var y=baseline-(baseline-(Device.MONO ? 24 : 48))*Math.sin(progress*Math.PI);
        var radius=p(isMoon ? (Device.MONO ? 4 : 7) : (Device.MONO ? 3 : 6));var cx=p(x);var cy=p(y);
        var angle=Sky.moonPhase*2*Math.PI;var flip=Data.latitude!=null && Data.latitude<0 ? -1 : 1;
        var sine=isMoon ? Math.sin(angle) : 0;var cosine=isMoon ? Math.cos(angle) : 0;
        color(dc,Device.MONO ? 0xFFFFFF : (isMoon ? 0xF6E9C7 : 0xFFF2CC));
        for(var yy=-radius;yy<=radius;yy++) {var run=null;for(var xx=-radius;xx<=radius+1;xx++) {
            var rr=(xx*xx+yy*yy).toFloat()/(radius*radius);
            var lit=xx<=radius && rr<=1 && skyPixel(cx+xx,cy+yy) && (!isMoon || flip*xx.toFloat()/radius*sine-Math.sqrt(1-rr)*cosine>0);
            if(lit && run==null) {run=xx;}
            if(!lit && run!=null) {dc.drawLine(cx+run,cy+yy,cx+xx-1,cy+yy);run=null;}
        }}
    }
    function prepareBackground() {
        var key=1;
        if(_artScene!=key || _background==null) {
            _background=null;_background=WatchUi.loadResource(LandscapeArt.id(key));_artScene=key;
        }
    }
    function landscape(dc,minutes,stamp) {prepareBackground();dc.drawBitmap(0,0,_background);}
    function firework(dc,x as Numeric,y as Numeric,c as Number) {for(var i=0;i<12;i++) {var a=i*Math.PI/6;line(dc,x+4*Math.cos(a),y+4*Math.sin(a),x+11*Math.cos(a),y+11*Math.sin(a),c);}}
    function slotHeader(dc,x as Numeric,y as Numeric,width as Numeric,kind as Number) {
        if(kind==11) {return;}
        var value=Data.header(kind);var font=_small;
        if(dc.getTextWidthInPixels(value,font)>p(width)) {font=_label;}
        if(dc.getTextWidthInPixels(value,font)>p(width)) {value=Data.label(kind)+" --";}
        text(dc,x,y,font,value,0xFFFFFF);
    }
    function headers(dc) {
        if(Device.MONO) {
            slotHeader(dc,62,7,94,Settings.top);slotHeader(dc,36,75,60,Settings.upperLeft);
        } else {
            slotHeader(dc,130,23,140,Settings.top);slotHeader(dc,47,76,64,Settings.upperLeft);slotHeader(dc,213,76,64,Settings.upperRight);
        }
    }
    function circle(dc) {
        if(!Device.MONO) {timeLeft(dc);return;}
        // The physical circle remains independently aligned to the SDK aperture.
        dc.setColor(0,0);dc.fillCircle(Device.CX,Device.CY,Device.CR+p(3));
        if(Settings.circle==11) {return;}
        color(dc,0xFFFFFF);dc.fillCircle(Device.CX,Device.CY,Device.CR);
        if(Settings.circle==6) {WeatherGlyph.draw(dc,Device.CX,Device.CY-p(16),0,0xFFFFFF);}
        else {color(dc,0);dc.drawText(Device.CX,Device.CY-p(19),_small,Data.label(Settings.circle),Graphics.TEXT_JUSTIFY_CENTER);}
        var value=Data.value(Settings.circle);var width=Device.CR*2-p(10);var font=_circle;
        if(dc.getTextWidthInPixels(value,font)>width) {font=_metric;}
        if(dc.getTextWidthInPixels(value,font)>width) {font=_label;}
        if(dc.getTextWidthInPixels(value,font)>width) {value="--";}
        color(dc,0);dc.drawText(Device.CX,Device.CY-p(6),font,value,Graphics.TEXT_JUSTIFY_CENTER);
    }
    function timeLeft(dc) {
        restore(dc,5,141,37,43);if(Settings.circle==11) {return;}
        if(Settings.circle==6) {WeatherGlyph.draw(dc,p(24),p(149),0xFFFFFF,0);}
        else {text(dc,24,145,_label,Data.label(Settings.circle),0xFFFFFF);}
        var value=Data.value(Settings.circle);var font=dc.getTextWidthInPixels(value,_small)<=p(34) ? _small : _label;
        if(dc.getTextWidthInPixels(value,font)>p(34)) {value="--";}
        text(dc,24,165,font,value,0xFFFFFF);
    }
    function metrics(dc,heartOnly) {
        var keys=[Settings.left,Settings.middle,Settings.right];
        var start=Device.MONO ? 46 : 79;var gap=Device.MONO ? 42 : 51;
        var y=Device.MONO ? 139 : 204;var width=Device.MONO ? 39 : 47;
        var values=[Data.value(keys[0]),Data.value(keys[1]),Data.value(keys[2])];
        // Fit as one row: an exceptional long value never makes only its neighbours larger.
        var font=_metric;
        for(var j=0;j<3;j++) {if(dc.getTextWidthInPixels(values[j],font)>p(width-2)) {font=_label;}}
        // Clear the complete strip before repainting, including wings and borders.
        // This also handles heart-rate-only redraws without stale ornaments.
        if(!heartOnly) {
            restore(dc,0,y,Device.MONO ? 176 : 260,Device.MONO ? 29 : 40);
            PanelDecor.draw(self,dc,Settings.panelStyle,[keys[0]!=11,keys[1]!=11,keys[2]!=11],_accent);
        }
        for(var i=0;i<3;i++) {
            if(keys[i]==11 || (heartOnly && keys[i]!=1)) {continue;}
            var x=start+gap*i;
            if(heartOnly) {restore(dc,x-width/2+2,Device.MONO ? 152 : 222,width-4,Device.MONO ? 12 : 21);}
            else {text(dc,x,y+(Device.MONO ? 2 : (Device.AMOLED ? 2 : 1)),_label,Data.label(keys[i]),Settings.panelStyle==2 ? _accent : 0);}
            var value=dc.getTextWidthInPixels(values[i],font)>p(width-2) ? "--" : values[i];
            text(dc,x,Device.MONO ? 152 : 222,font,value,0xFFFFFF);
        }
        if(!Device.MONO && !heartOnly) {
            line(dc,101,253,159,253,0x333333);
            if(Data.steps!=null && Data.stepGoal!=null && Data.stepGoal>0) {line(dc,101,253,101+58*min(1,Data.steps.toFloat()/Data.stepGoal),253,_accent);}
        }
    }
    function dateDecor(dc,date) {
        if(Settings.panelStyle==0) {return;}
        var center=Device.MONO ? 88 : 130;var y=Device.MONO ? 130 : 194;
        // Reserve the real font advance, including longer weekdays / locales.
        var half=dc.getTextWidthInPixels(date,_small)/Device.S/2;
        // Mono seconds restore x=148..168: keep raised ornaments outside that box.
        var edge=Device.MONO ? 30 : 48;
        for(var side=0;side<2;side++) {
            var dir=side==0 ? -1 : 1;
            var inner=center+dir*(half+5);var outer=side==0 ? edge : center*2-edge;
            if(center-edge<=half+9) {continue;}
            line(dc,inner,y,outer,y,_accent);
            if(Settings.panelStyle==1) {line(dc,inner,y+1,inner+dir*5,y+1,_accent);}
            else if(Settings.panelStyle==2) {line(dc,outer,y,outer-dir*3,y-3,_accent);}
            else {
                var x=outer-dir*2;
                poly(dc,[[p(x),p(y-2)],[p(x+2),p(y)],[p(x),p(y+2)],[p(x-2),p(y)]],_accent);
            }
        }
    }
    function seconds(dc,sec) {
        if(!Settings.seconds || _sleep) {return;}
        var x=Device.MONO ? 158 : 232;var y=Device.MONO ? 118 : 168;
        restore(dc,x-10,y,20,Device.MONO ? 12 : 17);
        text(dc,x,y,_small,sec.format("%02d"),0xFFFFFF);
    }
    function timeText(hour,minute,is24) {return Settings.shownHour(hour,is24).format("%02d")+":"+minute.format("%02d");}
    function aod(dc,h,m,is24) {
        dc.setColor(0,0);dc.clear();dc.setPenWidth(1);
        // Four disjoint minute bands ensure every lit pixel rests in the next minute.
        var rows=[64,105,146,187];var y=rows[m%4];text(dc,130,y,_aod,timeText(h,m,is24),0x777777);
    }
    function onUpdate(dc) {
        var now=Mode.DEMO ? new Time.Moment(Mode.STAMP) : Time.now();var minute=(now.value()/60).toNumber();
        if(_minute==minute) {
            if(_sleep) {return;}
            var heartChanged=Data.refreshHeart(now.value());
            if(heartChanged && Settings.headersUse(1)) {_minute=-1;}
            else {
                if(heartChanged) {if(Settings.circle==1) {circle(dc);}if(Settings.left==1 || Settings.middle==1 || Settings.right==1) {metrics(dc,true);}}
                if(Settings.seconds) {var tick=Mode.DEMO ? 16 : System.getClockTime().sec;if(tick!=_second) {seconds(dc,tick);_second=tick;}}return;
            }
        }
        // Device settings and the full clock are minute/lifecycle work, never a
        // compulsory read on a disabled-seconds or sleeping callback.
        var clock=System.getClockTime();var sys=System.getDeviceSettings();
        var h=Mode.DEMO ? (Mode.MINUTES/60).toNumber() : clock.hour;var m=Mode.DEMO ? Mode.MINUTES%60 : clock.min;var sec=Mode.DEMO ? 16 : clock.sec;
        var is24=Settings.is24(sys.is24Hour);
        if(Device.AMOLED && _sleep) {if(_aod==null) {_aod=WatchUi.loadResource(Rez.Fonts.Aod);}aod(dc,h,m,is24);_minute=minute;return;}
        Data.refresh(now,sys);_scene=2;
        var d=Gregorian.info(now,Time.FORMAT_SHORT);
        _holiday=0;_accent=accent(2);
        // Reuse the background while menus are shown. If a skin changed, obtain
        // its largest allocation before rebuilding the smaller font objects.
        prepareBackground();if(_time==null) {loadFonts();}
        dc.clearClip();dc.setPenWidth(1);dc.setColor(0,0);dc.clear();landscape(dc,h*60+m,now.value());
        var x=Device.MONO ? 82 : 130;var y=Device.MONO ? 84 : 136;
        text(dc,x,y,_time,timeText(h,m,is24),0xFFFFFF);
        if(!Device.MONO) {text(dc,232,150,_small,is24 ? "24H" : (h>=12 ? "PM" : "AM"),0xFFFFFF);}
        var weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"];
        var date=Mode.DEMO ? Mode.DATE : weekdays[d.day_of_week-1]+"  "+d.month.format("%02d")+"/"+d.day.format("%02d");
        text(dc,Device.MONO ? 88 : 130,Device.MONO ? 126 : 187,_small,date,0xFFFFFF);
        dateDecor(dc,date);
        if(Device.MONO && !is24) {text(dc,158,99,_small,h>=12 ? "PM" : "AM",0xFFFFFF);}
        metrics(dc,false);circle(dc);seconds(dc,sec);_minute=minute;_second=sec;
        if(Mode.DEMO && !_logged) {System.println("ALPINE_READY demo=true free="+System.getSystemStats().freeMemory+" width="+Device.W+" height="+Device.H);_logged=true;}
    }
}
