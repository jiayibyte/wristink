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
    function text(dc,x,y,font,value,c) {color(dc,c);dc.drawText(p(x),p(y),font,value,Graphics.TEXT_JUSTIFY_CENTER);}
    function fitted(dc,x,y,font,value,width,c) {
        // Long values use the smaller native font; never clip a partial number.
        var f=dc.getTextWidthInPixels(value,font)>p(width) ? _small : font;
        if(dc.getTextWidthInPixels(value,f)>p(width)) {value="--";}
        text(dc,x,y,f,value,c);
    }
    function accent(scene) {
        if(Device.MONO) {return Graphics.COLOR_WHITE;}
        if(scene==1) {return 0xCCCCFF;}if(scene==3 || scene==6) {return 0xFFAA55;}
        if(scene==4 || scene==9) {return 0x9999FF;}if(scene==5) {return 0x99BBBB;}return 0x66DDDD;
    }
    function skyColor(scene,k) {
        if(Device.MONO) {return Graphics.COLOR_WHITE;}
        var top=0x226699;var bottom=0x99DDDD;
        switch(scene) {
            case 1:top=0x666699;bottom=0xFFCCCC;break;
            case 3:top=0x884466;bottom=0xFFAA55;break;
            case 4:case 9:top=0x111133;bottom=0x336699;break;
            case 5:top=0x334455;bottom=0x99AAAA;break;
            case 6:top=0x223333;bottom=0xCC7744;break;
            case 7:top=0x112233;bottom=0x228899;break;
        }
        var r=((top>>16)&255)*(1-k)+((bottom>>16)&255)*k;
        var g=((top>>8)&255)*(1-k)+((bottom>>8)&255)*k;
        var b=(top&255)*(1-k)+(bottom&255)*k;
        if(!Device.AMOLED) {r=Math.round(r/85)*85;g=Math.round(g/85)*85;b=Math.round(b/85)*85;}
        return (r.toNumber()<<16)|(g.toNumber()<<8)|b.toNumber();
    }
    function landscape(dc,minutes,stamp) {
        var cx=Device.MONO ? 78 : 130;var cy=Device.MONO ? 87 : 135;var radius=Device.MONO ? 76 : 121;
        var top=Device.MONO ? 8 : 13;
        // Scanline circle produces a real circular horizon and a bounded gradient.
        for(var y=top;y<cy;y+=2) {
            var dy=cy-y;var half=Math.sqrt(max(0,radius*radius-dy*dy));
            rect(dc,cx-half,y,2*half,2,skyColor(_scene,(y-top).toFloat()/(cy-top)));
        }
        color(dc,_accent);dc.setPenWidth(max(1,p(2)));dc.drawArc(p(cx),p(cy),p(radius+3),Graphics.ARC_CLOCKWISE,174,6);dc.setPenWidth(1);
        // Sun follows the visual daytime interval. If solar events are unavailable,
        // the clock interval is deliberately only an illustration.
        var dayStart=Data.rise==null ? 360 : Data.rise;var dayEnd=Data.set==null ? 1080 : Data.set;
        var fraction=dayEnd>dayStart ? (minutes-dayStart).toFloat()/(dayEnd-dayStart) : 0.5;
        fraction=max(0.08,min(0.92,fraction));
        var sunX=cx-radius*.68*Math.cos(fraction*Math.PI);var sunY=cy-15-radius*.64*Math.sin(fraction*Math.PI);
        if(Device.MONO) {sunX=30+30*fraction;sunY=33-4*Math.sin(fraction*Math.PI);}
        if(_scene==4 || _scene==9) {
            for(var i=0;i<22;i++) {var sx=cx-radius+12+(i*37)%(radius*2-24);var sy=top+13+(i*19)%(cy-top-22);var dx=sx-cx;var ddy=sy-cy;
                if(dx*dx+ddy*ddy<(radius-8)*(radius-8)) {rect(dc,sx,sy,1,1,Device.MONO ? 0 : 0xCCCCFF);}}
            var mx=Device.MONO ? 42 : cx+radius*.49;var my=Device.MONO ? 32 : cy-radius*.64;disk(dc,mx,my,Device.MONO ? 5 : 7,Device.MONO ? 0 : 0xFFFFCC);
            var age=Scene.moon(stamp);
            if(age<12 || age>17) {disk(dc,mx+(age<14.765 ? -3 : 3),my-1,Device.MONO ? 4 : 6,skyColor(_scene,0.35));}
        } else {disk(dc,sunX,sunY,Device.MONO ? 4 : 6,Device.MONO ? 0 : 0xFFFFDD);}
        if(_scene==5) {
            for(var r=0;r<22;r++) {var rx=cx-radius+14+(r*29)%(radius*2-28);var ry=top+18+(r*17)%(cy-top-24);line(dc,rx,ry,rx-3,ry+6,Device.MONO ? 0 : 0xCCDDEE);}
        }
        if(_scene==8) {
            var rainbow=[0xFF7777,0xFFBB55,0xFFFF99,0x66CC99,0x66AAFF];
            for(var a=0;a<5;a++) {color(dc,Device.MONO ? (a%2==0 ? 0 : 0xFFFFFF) : rainbow[a]);dc.setPenWidth(max(1,p(2)));dc.drawArc(p(cx),p(cy+3),p(radius-10-a*3),Graphics.ARC_CLOCKWISE,166,14);}
            dc.setPenWidth(1);
        }
        if(_scene==9) {firework(dc,cx-radius*.5,cy-radius*.62,Device.MONO ? 0 : 0xFFCC88);firework(dc,cx+radius*.29,cy-radius*.70,Device.MONO ? 0 : 0x99DDFF);}
        if(_scene==7) {poly(dc,[[cx+radius*.42,top+15],[cx+radius*.2,top+43],[cx+radius*.34,top+42],[cx+radius*.16,top+65],[cx+radius*.52,top+34],[cx+radius*.36,top+35]],Device.MONO ? 0 : 0xEEFFFF);}
        // Snow ridge: original polygon artwork, laid out separately for each family.
        var mx=Device.MONO ? 75 : 129;var base=Device.MONO ? 89 : 136;var peak=Device.MONO ? 35 : 60;var mw=Device.MONO ? 57 : 81;
        poly(dc,[[mx-mw-18,base],[mx-mw*.47,peak+18],[mx-mw*.18,peak+34],[mx+mw*.48,peak+13],[mx+mw+15,base]],0x000000);
        poly(dc,[[mx-mw,base],[mx,peak],[mx+mw,base]],0x000000);
        poly(dc,[[mx-mw*.72,base-14],[mx,peak+5],[mx-3,peak+24],[mx+9,peak+19],[mx+mw*.34,peak+43],[mx+7,peak+34],[mx-4,peak+47],[mx-2,peak+29],[mx-20,peak+51],[mx-13,peak+30]],0xFFFFFF);
        poly(dc,[[mx+mw*.26,peak+32],[mx+mw*.48,peak+18],[mx+mw*.66,peak+37],[mx+mw*.51,peak+31],[mx+mw*.53,peak+39]],0xFFFFFF);
        poly(dc,[[mx-mw*.65,peak+35],[mx-mw*.47,peak+23],[mx-mw*.35,peak+35],[mx-mw*.46,peak+31],[mx-mw*.58,peak+43]],0xFFFFFF);
        if(_scene==6) {poly(dc,[[mx,peak+4],[mx+4,peak+25],[mx-3,peak+33],[mx+4,peak+51],[mx-8,peak+38],[mx-2,peak+25]],Device.MONO ? 0xFFFFFF : 0xFF8833);for(var v=0;v<7;v++) {disk(dc,mx+(v*7)%17-8,peak-6-v*3,1,Device.MONO ? 0 : 0xFFCC66);}}
        // Pine silhouettes along the horizon; a lit hut indicates unread messages.
        for(var t=0;t<13;t++) {var tx=(Device.MONO ? 8 : 16)+t*(Device.MONO ? 12 : 19);var th=4+(t*7)%7;
            poly(dc,[[tx-3,base],[tx,base-th],[tx+3,base]],0);}
        var hx=Device.MONO ? 133 : 221;var hy=base-7;
        rect(dc,hx-6,hy,12,7,0);poly(dc,[[hx-9,hy],[hx,hy-6],[hx+9,hy]],0);
        if(Data.notifications!=null && Data.notifications>0) {rect(dc,hx-3,hy+1,3,3,Device.MONO ? 0xFFFFFF : 0xFFDD66);}
        if(Device.MONO) {
            rect(dc,16,5,95,17,0);text(dc,62,7,_small,"ALT "+Data.numeric(Data.elevation())+(Data.imperialAlt ? "FT" : "M"),0xFFFFFF);
            rect(dc,8,73,57,12,0);text(dc,36,75,_small,"BAT "+Data.daysText(),0xFFFFFF);
        } else {
            // Header values follow the arc without relying on recent vector-font APIs.
            text(dc,130,23,_small,"ALT "+Data.numeric(Data.elevation())+(Data.imperialAlt ? "FT" : "M"),0xFFFFFF);
            text(dc,47,76,_small,"HR "+Data.numeric(Data.heart),0xFFFFFF);
            text(dc,213,76,_small,"BAT "+Data.daysText(),0xFFFFFF);
        }
    }
    function firework(dc,x,y,c) {for(var i=0;i<12;i++) {var a=i*Math.PI/6;line(dc,x+4*Math.cos(a),y+4*Math.sin(a),x+11*Math.cos(a),y+11*Math.sin(a),c);}}
    function circle(dc) {
        if(!Device.MONO) {return;}
        // A circular clearance follows the physical aperture; no rectangular sky remnants.
        dc.setColor(0,0);dc.fillCircle(Device.CX,Device.CY,Device.CR+p(15));
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
            rect(dc,xs[i]-width/2,y,width,Device.MONO ? 28 : 38,0);
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
        rect(dc,x-10,y,20,Device.MONO ? 12 : 17,0);
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
