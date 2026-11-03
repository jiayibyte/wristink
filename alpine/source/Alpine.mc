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
    function getSettingsView() {Settings.load();return [new SlotMenu(),new SlotMenuDelegate(view)];}
    function onSettingsChanged() {if(Mode.DEMO) {Mode.refresh();}if(view!=null) {view.settingsChanged();}}
}

class AlpineView extends WatchUi.WatchFace {
    var _time;var _small;var _label;var _metric;var _circle;var _aod;
    var _background=null;var _front=null;var _artScene=-1;
    var _sleep=false;var _minute=-1;var _scene=2;var _second=-1;var _accent=0x66CCCC;var _logged=false;
    function initialize() {
        WatchFace.initialize();Settings.load();
        if(Device.MONO) {_front=WatchUi.loadResource(Rez.Drawables.SkyFront);}
        _time=WatchUi.loadResource(Rez.Fonts.Time);_small=WatchUi.loadResource(Rez.Fonts.Small);
        _label=WatchUi.loadResource(Rez.Fonts.Label);_metric=WatchUi.loadResource(Rez.Fonts.Metric);_circle=WatchUi.loadResource(Rez.Fonts.Circle);_aod=WatchUi.loadResource(Rez.Fonts.Aod);
    }
    function settingsChanged() {Settings.load();_minute=-1;Data.minute=-1;Data.heartAt=-1;Data.environmentAt=-1;WatchUi.requestUpdate();}
    function onShow() {_minute=-1;}
    function onEnterSleep() {_sleep=true;_minute=-1;WatchUi.requestUpdate();}
    function onExitSleep() {_sleep=false;_minute=-1;Data.heartAt=-1;WatchUi.requestUpdate();}
    function max(a,b) {return a>b ? a : b;}
    function min(a,b) {return a<b ? a : b;}
    function p(v) {return Math.round(v*Device.S).toNumber();}
    function color(dc,c) {dc.setColor(c,Graphics.COLOR_TRANSPARENT);}
    function line(dc,x1,y1,x2,y2,c) {color(dc,c);dc.drawLine(p(x1),p(y1),p(x2),p(y2));}
    function rect(dc,x,y,w,h,c) {color(dc,c);dc.fillRectangle(p(x),p(y),p(x+w)-p(x),p(y+h)-p(y));}
    function disk(dc,x,y,r,c) {color(dc,c);dc.fillCircle(p(x),p(y),p(r));}
    function poly(dc,points as Array<Array<Numeric>>,c) {
        var vertices=[];for(var i=0;i<points.size();i++) {vertices.add([p(points[i][0]),p(points[i][1])]);}
        color(dc,c);dc.fillPolygon(vertices);
    }
    function text(dc,x,y,font,value,c) {
        var xx=p(x);var yy=p(y);
        if(c==0xFFFFFF && _background!=null) {
            color(dc,0);dc.drawText(xx-1,yy,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.drawText(xx+1,yy,font,value,Graphics.TEXT_JUSTIFY_CENTER);
            dc.drawText(xx,yy-1,font,value,Graphics.TEXT_JUSTIFY_CENTER);dc.drawText(xx,yy+1,font,value,Graphics.TEXT_JUSTIFY_CENTER);
        }
        color(dc,c);dc.drawText(xx,yy,font,value,Graphics.TEXT_JUSTIFY_CENTER);
    }
    function restore(dc,x,y,w,h) {
        dc.setClip(p(x),p(y),p(x+w)-p(x),p(y+h)-p(y));
        if(_background!=null) {dc.drawBitmap(0,0,_background);}else {dc.setColor(0,0);dc.clear();}
        dc.clearClip();
    }
    function accent(scene) {
        if(Device.MONO) {return Graphics.COLOR_WHITE;}
        if(scene==1) {return 0xCCCCFF;}if(scene==3 || scene==6 || scene==7) {return 0xFFAA55;}
        if(scene==4 || scene==9) {return 0x9999FF;}if(scene==5) {return 0x99BBBB;}return 0x66DDDD;
    }
    function skyPixel(x,y) {return x>=0 && y>=0 && x<Device.W && y<Device.H && y<Device.SKYLINE[x];}
    function cloud(dc,x,y,width,c) {
        // Native filled primitives avoid per-pixel VM loops in a watch-face callback.
        var w=p(width);var xx=p(x);var yy=p(y);var r=(w*.20).toNumber();
        dc.setClip(xx,yy-r,w,r*2+1);color(dc,c);
        dc.fillCircle(xx+r,yy+r,r);
        dc.fillCircle(xx+(w*.47).toNumber(),yy+(w*.15).toNumber(),(w*.25).toNumber());
        dc.fillCircle(xx+(w*.76).toNumber(),yy+r,r);
        dc.clearClip();
    }
    function body(dc,progress,isMoon,stamp) {
        var x=(Device.MONO ? 10 : 12)+(Device.MONO ? 98 : 236)*progress;
        var leftEdge=Device.SKYLINE[p(Device.MONO ? 10 : 12)]/Device.S;var rightEdge=Device.SKYLINE[p(Device.MONO ? 108 : 248)]/Device.S;
        var baseline=leftEdge+(rightEdge-leftEdge)*progress;var y=baseline-(baseline-(Device.MONO ? 24 : 48))*Math.sin(progress*Math.PI);
        var radius=p(isMoon ? (Device.MONO ? 4 : 7) : (Device.MONO ? 3 : 6));var cx=p(x);var cy=p(y);
        var angle=Sky.moonPhase*2*Math.PI;var flip=Data.latitude!=null && Data.latitude<0 ? -1 : 1;
        color(dc,Device.MONO ? 0xFFFFFF : (isMoon ? 0xF6E9C7 : 0xFFF2CC));
        for(var yy=-radius;yy<=radius;yy++) {for(var xx=-radius;xx<=radius;xx++) {
            var rr=(xx*xx+yy*yy).toFloat()/(radius*radius);
            if(rr<=1 && skyPixel(cx+xx,cy+yy) && (!isMoon || flip*xx.toFloat()/radius*Math.sin(angle)-Math.sqrt(1-rr)*Math.cos(angle)>0)) {dc.drawPoint(cx+xx,cy+yy);}
        }}
    }
    function landscape(dc,minutes,stamp) {
        Sky.refresh(stamp,minutes,Data.latitude,Data.longitude,Data.rise,Data.set);
        var key=Scene.artKey(_scene);
        if(_artScene!=key || _background==null) {
            var ids=[Rez.Drawables.Sky1,Rez.Drawables.Sky2,Rez.Drawables.Sky3,Rez.Drawables.Sky4,Rez.Drawables.Sky5,Rez.Drawables.Sky6,Rez.Drawables.Sky7,Rez.Drawables.Sky8,Rez.Drawables.Sky9,Rez.Drawables.Sky10,Rez.Drawables.Sky11,Rez.Drawables.Sky12,Rez.Drawables.Sky13,Rez.Drawables.Sky14,Rez.Drawables.Sky15,Rez.Drawables.Sky16,Rez.Drawables.Sky17,Rez.Drawables.Sky18,Rez.Drawables.Sky19,Rez.Drawables.Sky20] as Array<ResourceId>;
            _background=null;_background=WatchUi.loadResource(ids[key-1]);_artScene=key;
        }
        dc.drawBitmap(0,0,_background);
        var weather=Scene.effectiveWeather(_scene);var cover=Scene.clouds(_scene);
        if(Sky.phase==4 && cover<70) {
            var count=(Device.MONO ? 15 : 42)*(100-cover)/100;
            for(var i=0;i<count;i++) {
                var sx=p(8+(i*47)%(Device.MONO ? 100 : 244));var sy=p(8+(i*17)%(Device.MONO ? 28 : 45));
                if(skyPixel(sx,sy)) {color(dc,Device.MONO ? 0xFFFFFF : 0xAACCDD);dc.drawPoint(sx,sy);}
            }
        }
        // Each body has its own horizon visibility; a daytime Moon is allowed.
        if(cover<85) {
            if(Sky.sunVisible) {body(dc,Sky.sunProgress,false,stamp);}
            if(Sky.moonVisible && Sky.illumination>0.005) {body(dc,Sky.moonProgress,true,stamp);}
        }
        // Clouds are entirely dynamic: a clear or unknown weather state paints none.
        if(cover>0) {
            var c=Device.MONO ? 0xFFFFFF : (Sky.phase==4 ? 0x476375 : (cover>=70 ? 0x91AAB3 : 0xCDDDE0));
            var drift=((stamp/300).toNumber()%7)-3;
            cloud(dc,(Device.MONO ? 10 : 20)+drift,Device.MONO ? 35 : 45,Device.MONO ? 29 : 51,c);
            if(cover>=30) {cloud(dc,(Device.MONO ? 77 : 176)-drift,Device.MONO ? 24 : 44,Device.MONO ? 30 : 60,c);}
            if(cover>=70) {cloud(dc,Device.MONO ? 43 : 98,Device.MONO ? 36 : 45,Device.MONO ? 37 : 65,c);}
        }
        if(Device.MONO && cover>0 && _front!=null) {dc.drawBitmap(0,0,_front);}
        if(weather==WeatherStyle.RAIN || weather==WeatherStyle.STORM || weather==WeatherStyle.SNOW) {
            for(var r=0;r<18;r++) {
                var rx=p(8+(r*29)%(Device.MONO ? 104 : 244));var ry=p(26+(r*13)%(Device.MONO ? 31 : 60));
                var c=Device.MONO ? 0xFFFFFF : (weather==WeatherStyle.SNOW ? 0xEEF4F0 : 0xA2BAC6);
                if(weather==WeatherStyle.SNOW) {for(var k=-1;k<=1;k++) {if(skyPixel(rx+k,ry)) {color(dc,c);dc.drawPoint(rx+k,ry);}}if(skyPixel(rx,ry-1)) {color(dc,c);dc.drawPoint(rx,ry-1);}if(skyPixel(rx,ry+1)) {dc.drawPoint(rx,ry+1);}}
                else {for(var j=0;j<p(4);j++) {if(skyPixel(rx-j/2,ry+j)) {color(dc,c);dc.drawPoint(rx-j/2,ry+j);}}}
            }
        }
        if(weather==WeatherStyle.STORM) {poly(dc,Device.MONO ? [[30,20],[22,36],[28,34],[23,46],[38,29],[30,30]] : [[218,26],[200,51],[213,48],[201,69],[227,41],[215,43]],Device.MONO ? 0xFFFFFF : 0xDAF4F5);}
        if(_scene==8) {
            var colors=[0xEE9966,0xDDCC88,0x88BBAA];
            for(var a=0;a<3;a++) {color(dc,Device.MONO ? 0xFFFFFF : colors[a]);dc.drawArc(p(Device.MONO ? 67 : 130),p(Device.MONO ? 87 : 145),p((Device.MONO ? 70 : 123)-a*3),Graphics.ARC_CLOCKWISE,160,20);}
        }
        if(_scene==9) {firework(dc,Device.MONO ? 33 : 63,Device.MONO ? 40 : 44,Device.MONO ? 0xFFFFFF : 0xEECC99);if(!Device.MONO) {firework(dc,182,50,0x99CCDD);}}
        headers(dc);
        // A tiny lit tent represents unread notifications in the foreground valley.
        if(Data.notifications!=null && Data.notifications>0) {
            var tx=Device.MONO ? 150 : 220;var ty=Device.MONO ? 84 : 132;
            poly(dc,[[tx-4,ty],[tx,ty-4],[tx+4,ty]],Device.MONO ? 0xFFFFFF : 0xDBAE62);
        }
    }
    function firework(dc,x,y,c) {for(var i=0;i<12;i++) {var a=i*Math.PI/6;line(dc,x+4*Math.cos(a),y+4*Math.sin(a),x+11*Math.cos(a),y+11*Math.sin(a),c);}}
    function slotHeader(dc,x,y,width,kind) {
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
    function metrics(dc) {
        var keys=[Settings.left,Settings.middle,Settings.right];
        var xs=Device.MONO ? [46,88,130] : [79,130,181];
        var y=Device.MONO ? 139 : 204;var width=Device.MONO ? 39 : 47;
        var values=[Data.value(keys[0]),Data.value(keys[1]),Data.value(keys[2])];
        // Fit as one row: an exceptional long value never makes only its neighbours larger.
        var font=_metric;
        for(var j=0;j<3;j++) {if(dc.getTextWidthInPixels(values[j],font)>p(width-2)) {font=_label;}}
        for(var i=0;i<3;i++) {
            restore(dc,xs[i]-width/2,y,width,Device.MONO ? 28 : 38);
            if(keys[i]==11) {continue;}
            rect(dc,xs[i]-width/2,y,width,Device.MONO ? 11 : 15,_accent);
            text(dc,xs[i],y+(Device.MONO ? 1 : (Device.AMOLED ? 2 : -1)),_label,Data.label(keys[i]),0);
            var value=dc.getTextWidthInPixels(values[i],font)>p(width-2) ? "--" : values[i];
            text(dc,xs[i],Device.MONO ? 152 : 222,font,value,0xFFFFFF);
        }
        if(!Device.MONO) {
            line(dc,101,253,159,253,0x333333);
            if(Data.steps!=null && Data.stepGoal!=null && Data.stepGoal>0) {line(dc,101,253,101+58*min(1,Data.steps.toFloat()/Data.stepGoal),253,_accent);}
        }
    }
    function seconds(dc,sec) {
        var x=Device.MONO ? 158 : 232;var y=Device.MONO ? 118 : 168;
        restore(dc,x-10,y,20,Device.MONO ? 12 : 17);
        if(Settings.seconds && !_sleep) {text(dc,x,y,_small,sec.format("%02d"),0xFFFFFF);}
    }
    function timeText(hour,minute,is24) {return Settings.shownHour(hour,is24).format("%02d")+":"+minute.format("%02d");}
    function aod(dc,h,m,is24) {
        dc.setColor(0,0);dc.clear();dc.setPenWidth(1);
        // Four disjoint minute bands ensure every lit pixel rests in the next minute.
        var rows=[64,105,146,187];var y=rows[m%4];text(dc,130,y,_aod,timeText(h,m,is24),0x777777);
    }
    function onUpdate(dc) {
        var now=Mode.DEMO ? new Time.Moment(Mode.STAMP) : Time.now();var clock=System.getClockTime();var sys=System.getDeviceSettings();
        var h=Mode.DEMO ? (Mode.MINUTES/60).toNumber() : clock.hour;var m=Mode.DEMO ? Mode.MINUTES%60 : clock.min;var sec=Mode.DEMO ? 16 : clock.sec;
        var is24=Settings.is24(sys.is24Hour);var minute=(now.value()/60).toNumber();
        if(Device.AMOLED && _sleep) {if(_minute!=minute) {aod(dc,h,m,is24);_minute=minute;}return;}
        if(_minute==minute) {
            if(_sleep) {return;}
            var heartChanged=Data.refreshHeart(now.value());
            if(heartChanged && Settings.headersUse(1)) {_minute=-1;}
            else {
                if(heartChanged) {if(Settings.circle==1) {circle(dc);}metrics(dc);}
                if(sec!=_second) {seconds(dc,sec);_second=sec;}return;
            }
        }
        Data.refresh(now,sys);Sky.refresh(now.value(),h*60+m,Data.latitude,Data.longitude,Data.rise,Data.set);_scene=Scene.choose(h*60+m);_accent=accent(_scene);
        dc.clearClip();dc.setPenWidth(1);dc.setColor(0,0);dc.clear();landscape(dc,h*60+m,now.value());
        var x=Device.MONO ? 82 : 130;var y=Device.MONO ? 88 : 136;
        text(dc,x,y,_time,timeText(h,m,is24),0xFFFFFF);
        if(!Device.MONO) {text(dc,232,150,_small,is24 ? "24H" : (h>=12 ? "PM" : "AM"),0xFFFFFF);}
        var d=Gregorian.info(now,Time.FORMAT_SHORT);var weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"];
        var date=Mode.DEMO ? Mode.DATE : weekdays[d.day_of_week-1]+"  "+d.month.format("%02d")+"/"+d.day.format("%02d");
        text(dc,Device.MONO ? 88 : 130,Device.MONO ? 126 : 187,_small,date,0xFFFFFF);
        if(Device.MONO && !is24) {text(dc,158,99,_small,h>=12 ? "PM" : "AM",0xFFFFFF);}
        metrics(dc);circle(dc);seconds(dc,sec);_minute=minute;_second=sec;
        if(!_logged) {System.println("ALPINE_READY demo="+Mode.DEMO+" free="+System.getSystemStats().freeMemory+" width="+Device.W+" height="+Device.H);_logged=true;}
    }
}
