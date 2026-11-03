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
    function getInitialView() {view=new AlpineView();return [view];}
    function onSettingsChanged() {if(view!=null) {view.settingsChanged();}}
}

class AlpineView extends WatchUi.WatchFace {
    var _time;var _small;var _label;var _metric;var _circle;var _aod;
    var _background=null;var _artScene=-1;
    var _sleep=false;var _minute=-1;var _scene=2;var _second=-1;var _accent=0x66CCCC;var _logged=false;
    function initialize() {
        WatchFace.initialize();Settings.load();
        _time=WatchUi.loadResource(Rez.Fonts.Time);_small=WatchUi.loadResource(Rez.Fonts.Small);
        _label=WatchUi.loadResource(Rez.Fonts.Label);_metric=WatchUi.loadResource(Rez.Fonts.Metric);_circle=WatchUi.loadResource(Rez.Fonts.Circle);_aod=WatchUi.loadResource(Rez.Fonts.Aod);
    }
    function settingsChanged() {Settings.load();_minute=-1;Data.minute=-1;Data.environmentAt=-1;WatchUi.requestUpdate();}
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
        if(scene==1) {return 0xCCCCFF;}if(scene==3 || scene==6) {return 0xFFAA55;}
        if(scene==4 || scene==9) {return 0x9999FF;}if(scene==5) {return 0x99BBBB;}return 0x66DDDD;
    }
    function landscape(dc,minutes,stamp) {
        if(_artScene!=_scene || _background==null) {
            var ids=[Rez.Drawables.Everest1,Rez.Drawables.Everest2,Rez.Drawables.Everest3,Rez.Drawables.Everest4,Rez.Drawables.Everest5,Rez.Drawables.Everest6,Rez.Drawables.Everest7,Rez.Drawables.Everest8,Rez.Drawables.Everest9];
            _background=null;_background=WatchUi.loadResource(ids[_scene-1]);_artScene=_scene;
        }
        dc.drawBitmap(0,0,_background);
        var dayStart=Data.rise==null ? 360 : Data.rise;var dayEnd=Data.set==null ? 1080 : Data.set;
        var fraction=dayEnd>dayStart ? (minutes-dayStart).toFloat()/(dayEnd-dayStart) : 0.5;
        fraction=max(0.08,min(0.92,fraction));
        if(_scene==4 || _scene==9) {
            for(var i=0;i<(Device.MONO ? 15 : 42);i++) {
                var sx=8+(i*47)%(Device.MONO ? 100 : 244);var sy=8+(i*17)%(Device.MONO ? 28 : 45);
                rect(dc,sx,sy,1,1,Device.MONO ? 0xFFFFFF : 0xAACCDD);
                if(!Device.MONO && i%11==0) {line(dc,sx-1,sy,sx+1,sy,0xCCDDEE);line(dc,sx,sy-1,sx,sy+1,0xCCDDEE);}
            }
            moon(dc,Device.MONO ? 38 : 215,Device.MONO ? 33 : 42,Device.MONO ? 4 : 7,stamp);
        } else {
            var sx=Device.MONO ? 30+30*fraction : 185+45*fraction;
            var sy=Device.MONO ? 33-4*Math.sin(fraction*Math.PI) : 49;
            disk(dc,sx,sy,Device.MONO ? 3 : 6,Device.MONO ? 0xFFFFFF : 0xFFF2CC);
        }
        if(_scene==5) {
            for(var r=0;r<18;r++) {var rx=8+(r*29)%(Device.MONO ? 104 : 244);var ry=20+(r*13)%(Device.MONO ? 23 : 50);line(dc,rx,ry,rx-2,ry+4,Device.MONO ? 0xFFFFFF : 0xA2BAC6);}
        }
        if(_scene==7) {poly(dc,Device.MONO ? [[30,20],[22,36],[28,34],[23,46],[38,29],[30,30]] : [[218,26],[200,51],[213,48],[201,69],[227,41],[215,43]],Device.MONO ? 0xFFFFFF : 0xDAF4F5);}
        if(_scene==8) {
            var colors=[0xEE9966,0xDDCC88,0x88BBAA];
            for(var a=0;a<3;a++) {color(dc,Device.MONO ? 0xFFFFFF : colors[a]);dc.drawArc(p(Device.MONO ? 67 : 130),p(Device.MONO ? 87 : 145),p((Device.MONO ? 70 : 123)-a*3),Graphics.ARC_CLOCKWISE,160,20);}
        }
        if(_scene==9) {firework(dc,Device.MONO ? 33 : 63,Device.MONO ? 40 : 44,Device.MONO ? 0xFFFFFF : 0xEECC99);if(!Device.MONO) {firework(dc,182,50,0x99CCDD);}}
        if(Device.MONO) {
            text(dc,62,7,_small,"ALT "+Data.numeric(Data.elevation())+(Data.imperialAlt ? "FT" : "M"),0xFFFFFF);
            text(dc,36,75,_small,"BAT "+Data.daysText(),0xFFFFFF);
        } else {
            text(dc,130,23,_small,"ALT "+Data.numeric(Data.elevation())+(Data.imperialAlt ? "FT" : "M"),0xFFFFFF);
            text(dc,47,76,_small,"HR "+Data.numeric(Data.heart),0xFFFFFF);
            text(dc,213,76,_small,"BAT "+Data.daysText(),0xFFFFFF);
        }
        // A tiny lit tent represents unread notifications in the foreground valley.
        if(Data.notifications!=null && Data.notifications>0) {
            var tx=Device.MONO ? 150 : 220;var ty=Device.MONO ? 84 : 132;
            poly(dc,[[tx-4,ty],[tx,ty-4],[tx+4,ty]],Device.MONO ? 0xFFFFFF : 0xDBAE62);
        }
    }
    function moon(dc,x,y,r,stamp) {
        var radius=p(r);var cx=p(x);var cy=p(y);var angle=Scene.moon(stamp)/29.53059*2*Math.PI;
        color(dc,Device.MONO ? 0xFFFFFF : 0xF6E9C7);
        for(var yy=-radius;yy<=radius;yy++) {for(var xx=-radius;xx<=radius;xx++) {
            var rr=(xx*xx+yy*yy).toFloat()/(radius*radius);
            if(rr<=1 && xx.toFloat()/radius*Math.sin(angle)-Math.sqrt(1-rr)*Math.cos(angle)>0) {dc.drawPoint(cx+xx,cy+yy);}
        }}
    }
    function firework(dc,x,y,c) {for(var i=0;i<12;i++) {var a=i*Math.PI/6;line(dc,x+4*Math.cos(a),y+4*Math.sin(a),x+11*Math.cos(a),y+11*Math.sin(a),c);}}
    function circle(dc) {
        if(!Device.MONO) {return;}
        // Keep only a narrow bezel; scenery continues underneath the hardware window.
        dc.setColor(0,0);dc.fillCircle(Device.CX,Device.CY,Device.CR+p(3));
        color(dc,0xFFFFFF);dc.fillCircle(Device.CX,Device.CY,Device.CR);
        var label=Settings.circle==0 ? "BPM" : (Settings.circle==1 ? "DAYS" : "STR");
        var value=Settings.circle==0 ? Data.heart : (Settings.circle==1 ? Data.battery : Data.stress);
        color(dc,0);dc.drawText(Device.CX,Device.CY-p(19),_small,label,Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(Device.CX,Device.CY-p(6),Settings.circle==1 ? _metric : _circle,Settings.circle==1 ? Data.daysText() : Data.numeric(value),Graphics.TEXT_JUSTIFY_CENTER);
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
        var now=Time.now();var clock=System.getClockTime();var sys=System.getDeviceSettings();
        var h=Mode.DEMO ? 14 : clock.hour;var m=Mode.DEMO ? 23 : clock.min;var sec=Mode.DEMO ? 16 : clock.sec;
        var is24=Settings.is24(sys.is24Hour);var minute=(now.value()/60).toNumber();
        if(Device.AMOLED && _sleep) {if(_minute!=minute) {aod(dc,h,m,is24);_minute=minute;}return;}
        if(_minute==minute) {
            if(!_sleep) {if(Data.refreshHeart(now.value())) {circle(dc);metrics(dc);}if(sec!=_second) {seconds(dc,sec);_second=sec;}}
            return;
        }
        Data.refresh(now,sys);_scene=Scene.choose(h*60+m);_accent=accent(_scene);
        dc.clearClip();dc.setPenWidth(1);dc.setColor(0,0);dc.clear();landscape(dc,h*60+m,now.value());
        var x=Device.MONO ? 82 : 130;var y=Device.MONO ? 88 : 136;
        text(dc,x,y,_time,timeText(h,m,is24),0xFFFFFF);
        if(!Device.MONO) {text(dc,25,150,_small,Data.temperature()+(Data.fahrenheit ? "F" : "C"),0xFFFFFF);text(dc,232,150,_small,is24 ? "24H" : (h>=12 ? "PM" : "AM"),0xFFFFFF);}
        var d=Gregorian.info(now,Time.FORMAT_SHORT);var weekdays=["SUN","MON","TUE","WED","THU","FRI","SAT"];
        var date=Mode.DEMO ? "SUN  08/09" : weekdays[d.day_of_week-1]+"  "+d.month.format("%02d")+"/"+d.day.format("%02d");
        text(dc,Device.MONO ? 88 : 130,Device.MONO ? 126 : 187,_small,date,0xFFFFFF);
        if(Device.MONO && !is24) {text(dc,158,99,_small,h>=12 ? "PM" : "AM",0xFFFFFF);}
        metrics(dc);circle(dc);seconds(dc,sec);_minute=minute;_second=sec;
        if(!_logged) {System.println("ALPINE_READY demo="+Mode.DEMO+" free="+System.getSystemStats().freeMemory+" width="+Device.W+" height="+Device.H);_logged=true;}
    }
}
