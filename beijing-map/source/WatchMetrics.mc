import Toybox.ActivityMonitor;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Sensor;
import Toybox.System;

// Live values only. Missing sensor data stays null and is displayed as --.
class WatchMetrics {
    var steps=null;var dailyMetres=null;var battery=null;var heartRate=null;
    var sensorAt=null;var lastRefresh=null;var sensorsStarted=false;
    (:extendedCode)
    function initialize() {}
    (:extendedCode)
    function start() {
        if(sensorsStarted){return;}
        try{Sensor.setEnabledSensors([Sensor.SENSOR_HEARTRATE]);sensorsStarted=true;Sensor.enableSensorEvents(method(:onSensor));}catch(e){stop();}
    }
    (:extendedCode)
    function stop() {
        if(!sensorsStarted){return;}
        try{Sensor.enableSensorEvents(null);}catch(e){}
        try{Sensor.setEnabledSensors([]);}catch(e){}
        sensorsStarted=false;
    }
    (:extendedCode)
    function onSensor(info as Sensor.Info) as Void {
        heartRate=info.heartRate!=null && info.heartRate>0?info.heartRate:null;
        sensorAt=System.getTimer();
    }
    (:extendedCode)
    function refresh() {
        var now=System.getTimer();
        if(lastRefresh!=null && now-lastRefresh<1000){return;}
        lastRefresh=now;battery=System.getSystemStats().battery;
        var info=ActivityMonitor.getInfo();steps=info.steps;
        dailyMetres=info.distance==null?null:info.distance/100.0; // Garmin daily distance is centimetres.
        if(sensorAt==null || now-sensorAt>10000){heartRate=null;}
    }
    (:extendedCode)
    function batteryText(){return battery==null?"--":battery.format("%.0f")+"%";}
    (:extendedCode)
    function heartText(){return heartRate==null?"--":heartRate.toString();}
    (:extendedCode)
    function stepsText(){return steps==null?"--":steps.toString();}
    (:extendedCode)
    function dailyText(){return dailyMetres==null?"--":(dailyMetres/1000.0).format("%.2f");}
}

module DashboardDraw {
    // Seven-segment digits fit a full HH:MM:SS in the 62px physical window.
    const DIGITS=[63,6,91,79,102,109,125,7,127,111];
    (:extendedCode)
    function duration(seconds) {
        var value=seconds.toNumber();
        return (value/3600).toNumber().format("%02d")+":"+((value/60).toNumber()%60).format("%02d")+":"+(value%60).format("%02d");
    }
    (:extendedCode)
    function tinyTimer(dc,seconds) {
        var text=duration(seconds);var chars=text.toCharArray();var width=chars.size()*6-1;var x=144-width/2;
        for(var i=0;i<chars.size();i++){
            var c=chars[i].toNumber();var at=x+i*6;
            if(c==58){dc.fillRectangle(at+2,27,1,1);dc.fillRectangle(at+2,31,1,1);continue;}
            var mask=DIGITS[c-48];
            if((mask&1)!=0){dc.drawLine(at,24,at+4,24);}
            if((mask&2)!=0){dc.drawLine(at+4,24,at+4,28);}
            if((mask&4)!=0){dc.drawLine(at+4,28,at+4,32);}
            if((mask&8)!=0){dc.drawLine(at,32,at+4,32);}
            if((mask&16)!=0){dc.drawLine(at,28,at,32);}
            if((mask&32)!=0){dc.drawLine(at,24,at,28);}
            if((mask&64)!=0){dc.drawLine(at,28,at+4,28);}
        }
    }
    (:extendedCode)
    function tabs(dc,page) {
        dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillRectangle(77,167,23,9);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
        dc.drawCircle(83,171,2);dc.drawCircle(94,171,2);dc.fillCircle(page==0?83:94,171,2);
    }
}
