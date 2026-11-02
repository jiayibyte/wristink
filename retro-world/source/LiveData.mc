import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Math;
import Toybox.SensorHistory;
import Toybox.System;
import Toybox.Time;

module LiveData {
    var heart=null;var batteryDays=null;var steps=null;var calories=null;
    var altitude=null;var distance=null;
    var heartAt=-1;var heartValidAt=-1;
    var battery=null;var stepGoal=null;var floors=null;var activeMinutes=null;var notifications=null;
    function heartValid(v) {return v!=null && v>0 && v<=300 && v!=ActivityMonitor.INVALID_HR_SAMPLE;}
    function recentHeart(sample,stamp) {
        if(sample==null || sample.when==null || !heartValid(sample.heartRate)) {return null;}
        var age=stamp-sample.when.value();return age>=0 && age<=180 ? sample.heartRate : null;
    }
    function nonnegative(v) {return v!=null && v>=0 ? v : null;}
    function numeric(v) {return v==null ? "--" : v.format("%.0f");}
    function distanceText(cm) {return cm==null || cm<0 ? "--" : (cm/100000.0).format("%.2f");}
    function remainingDays(stats) {
        if(stats==null || !(stats has :batteryInDays)) {return null;}
        return nonnegative(stats.batteryInDays);
    }
    function daysText(days) {return days==null || days<0 ? "--" : days.format("%.1f");}
    function refreshHeart(stamp) {
        if(heartAt>=0 && stamp>=heartAt && stamp-heartAt<5) {return false;}
        heartAt=stamp;var previous=heart;
        if(PreviewMode.ENABLED) {heart=76;return previous!=heart;}
        var info=Activity.getActivityInfo();var live=info==null ? null : info.currentHeartRate;
        if(heartValid(live)) {heart=live;heartValidAt=stamp;}
        else {
            var sample=ActivityMonitor.getHeartRateHistory(1,true).next();
            heart=recentHeart(sample,stamp);heartValidAt=heart==null ? -1 : sample.when.value();
        }
        return previous!=heart;
    }
    function refreshTickHeart(stamp) {
        if(heartAt==stamp) {return false;}
        heartAt=stamp;var previous=heart;
        if(PreviewMode.ENABLED) {heart=76;return previous!=heart;}
        var info=Activity.getActivityInfo();var live=info==null ? null : info.currentHeartRate;
        if(heartValid(live)) {heart=live;heartValidAt=stamp;}
        else if(heartValidAt<0 || stamp<heartValidAt || stamp-heartValidAt>180) {heart=null;}
        return previous!=heart;
    }
    function refresh(stamp,settings) {
        refreshHeart(stamp);
        if(PreviewMode.ENABLED) {
            batteryDays=24.3;steps=8608;calories=1688;altitude=128;distance=642000;
            battery=86;stepGoal=10000;floors=8;activeMinutes=32;notifications=2;return;
        }
        var daily=ActivityMonitor.getInfo();var info=Activity.getActivityInfo();
        var stats=System.getSystemStats();batteryDays=remainingDays(stats);battery=nonnegative(stats.battery);
        steps=nonnegative(daily.steps);calories=nonnegative(daily.calories);distance=nonnegative(daily.distance);
        stepGoal=nonnegative(daily.stepGoal);
        floors=(daily has :floorsClimbed) ? nonnegative(daily.floorsClimbed) : null;
        activeMinutes=null;
        if((daily has :activeMinutesDay) && daily.activeMinutesDay!=null) {
            var active=daily.activeMinutesDay;
            if(active.moderate!=null && active.vigorous!=null) {activeMinutes=active.moderate+2*active.vigorous;}
        }
        notifications=(settings has :notificationCount) ? nonnegative(settings.notificationCount) : null;
        // Negative elevations are valid; a null value is never replaced with zero.
        altitude=info.altitude;
        if(altitude==null && (SensorHistory has :getElevationHistory)) {
            var elevation=SensorHistory.getElevationHistory({:period=>1,:order=>SensorHistory.ORDER_NEWEST_FIRST}).next();
            if(elevation!=null && elevation.when!=null && elevation.data!=null) {
                var age=stamp-elevation.when.value();if(age>=0 && age<=900) {altitude=elevation.data;}
            }
        }
    }
}
