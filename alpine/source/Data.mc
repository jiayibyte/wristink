import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.SensorHistory;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Position;
import Toybox.Weather;
module Data {
    var heart=null;var steps=null;var calories=null;var altitude=null;var distance=null;var battery=null;var stress=null;
    var batteryDays=null;
    var latitude=null;var longitude=null;var weather=0;var cloudCover=0;
    var stepGoal=null;var notifications=0;var temp=null;var rainy=false;var rise=null;var set=null;
    var heartAt=-1;var environmentAt=-1;var minute=-1;var imperialAlt=false;var imperialDist=false;var fahrenheit=false;
    function fresh(when,now,age) {return when!=null && now>=when.value() && now-when.value()<=age;}
    function validHeart(v) {return v!=null && v>0 && v<=300 && v!=ActivityMonitor.INVALID_HR_SAMPLE;}
    function numeric(v) {return v==null ? "--" : v.format("%.0f");}
    function remainingDays(stats) {
        if(stats==null || !(stats has :batteryInDays)) {return null;}
        var days=stats.batteryInDays;
        return days!=null && days>=0 ? days : null;
    }
    function daysText() {
        if(batteryDays==null || batteryDays<0) {return "--D";}
        return (batteryDays>=10 ? batteryDays.toNumber().format("%d") : batteryDays.format("%.1f"))+"D";
    }
    function recent(sample,now,age) {return sample!=null && sample.data!=null && fresh(sample.when,now,age) ? sample.data : null;}
    function refreshHeart(now) {
        if(heartAt>=0 && now>=heartAt && now-heartAt<5) {return false;}
        heartAt=now;var before=heart;
        if(Mode.DEMO) {heart=80;return before!=heart;}
        var info=Activity.getActivityInfo();heart=info==null ? null : info.currentHeartRate;
        if(!validHeart(heart)) {
            var sample=ActivityMonitor.getHeartRateHistory(1,true).next();
            heart=sample!=null && fresh(sample.when,now,180) && validHeart(sample.heartRate) ? sample.heartRate : null;
        }
        return before!=heart;
    }
    function refresh(now,settings) {
        refreshHeart(now.value());var m=(now.value()/60).toNumber();if(minute==m) {return;}minute=m;
        imperialAlt=settings.elevationUnits==System.UNIT_STATUTE;imperialDist=settings.distanceUnits==System.UNIT_STATUTE;fahrenheit=settings.temperatureUnits==System.UNIT_STATUTE;
        if(Mode.DEMO) {steps=8620;stepGoal=10000;calories=1688;altitude=1280;battery=76;batteryDays=18.4;distance=642000;notifications=2;temp=Mode.WEATHER==5 ? -6 : (Mode.WEATHER==4 ? 16 : 24);stress=32;weather=Mode.WEATHER;cloudCover=WeatherStyle.cover(weather,null);rainy=weather==4 || weather==6;latitude=Mode.LAT;longitude=Mode.LON;rise=null;set=null;return;}
        var d=ActivityMonitor.getInfo();var a=Activity.getActivityInfo();
        steps=d==null ? null : d.steps;stepGoal=d==null ? null : d.stepGoal;calories=d==null ? null : d.calories;distance=d==null ? null : d.distance;
        var stats=System.getSystemStats();battery=stats.battery;batteryDays=remainingDays(stats);notifications=settings.notificationCount;
        altitude=a==null ? null : a.altitude;
        if(altitude==null && (SensorHistory has :getElevationHistory)) {altitude=recent(SensorHistory.getElevationHistory({:period=>1,:order=>SensorHistory.ORDER_NEWEST_FIRST}).next(),now.value(),900);}
        stress=null;
        if(SensorHistory has :getStressHistory) {stress=recent(SensorHistory.getStressHistory({:period=>1,:order=>SensorHistory.ORDER_NEWEST_FIRST}).next(),now.value(),300);if(stress!=null && (stress<0 || stress>100)) {stress=null;}}
        environment(now);
    }
    function weatherRain(c) {
        return c==Weather.CONDITION_RAIN || c==Weather.CONDITION_LIGHT_RAIN || c==Weather.CONDITION_HEAVY_RAIN || c==Weather.CONDITION_SHOWERS || c==Weather.CONDITION_SCATTERED_SHOWERS || c==Weather.CONDITION_THUNDERSTORMS || c==Weather.CONDITION_DRIZZLE;
    }
    function environment(now) {
        var stamp=now.value();if(environmentAt>=0 && stamp>=environmentAt && stamp-environmentAt<300) {return;}environmentAt=stamp;
        var w=Weather.getCurrentConditions();var good=w!=null && fresh(w.observationTime,stamp,10800);
        temp=good ? w.temperature : null;weather=good ? WeatherStyle.category(w.condition) : WeatherStyle.UNKNOWN;
        var cover=good && (w has :cloudCover) ? w.cloudCover : null;cloudCover=WeatherStyle.cover(weather,cover);
        rainy=weather==WeatherStyle.RAIN || weather==WeatherStyle.STORM;rise=null;set=null;latitude=null;longitude=null;
        var loc=null;var p=Position.getInfo();
        if(p!=null && p.position!=null && p.accuracy!=null && p.accuracy>0 && p.accuracy<=4 && fresh(p.when,stamp,7200)) {loc=p.position;}
        else if(good && (w has :observationLocationPosition)) {loc=w.observationLocationPosition;}
        if(loc!=null) {var coords=loc.toDegrees();if(coords!=null && coords.size()>=2 && Sky.validLocation(coords[0],coords[1])) {latitude=coords[0];longitude=coords[1];}else {loc=null;}}
        if(loc!=null && (Weather has :getSunrise) && (Weather has :getSunset)) {
            var r=Weather.getSunrise(loc,now);var s=Weather.getSunset(loc,now);
            if(r!=null) {var ri=Gregorian.info(r,Time.FORMAT_SHORT);rise=ri.hour*60+ri.min;}
            if(s!=null) {var si=Gregorian.info(s,Time.FORMAT_SHORT);set=si.hour*60+si.min;}
        }
    }
    function elevation() {return altitude==null ? null : altitude*(imperialAlt ? 3.28084 : 1.0);}
    function temperature() {return temp==null ? "--" : numeric(fahrenheit ? temp*1.8+32 : temp);}
    function label(kind) {return ["STEP","BPM","KCAL",imperialAlt ? "FT" : "M","BAT",imperialDist ? "MI" : "KM"][kind];}
    function value(kind) {
        switch(kind) {
            case 0:return steps!=null && steps>=100000 ? (steps/1000.0).format("%.0f")+"K" : numeric(steps);
            case 1:return numeric(heart);case 2:return numeric(calories);case 3:return numeric(elevation());case 4:return daysText();
            case 5:return distance==null ? "--" : (distance/(imperialDist ? 160934.4 : 100000.0)).format("%.1f");
        }
        return "--";
    }
    function goal() {return steps!=null && stepGoal!=null && stepGoal>0 && steps>=stepGoal;}
}
