import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Math;
import Toybox.SensorHistory;
import Toybox.System;
import Toybox.Time;

module LiveData {
    var heart=null;var batteryDays=null;var steps=null;var calories=null;
    var altitude=null;var distance=null;
    var heartAt=-1;
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
        heartAt=stamp;
        if(PreviewMode.ENABLED) {heart=76;return true;}
        var live=Activity.getActivityInfo().currentHeartRate;
        heart=heartValid(live) ? live : recentHeart(ActivityMonitor.getHeartRateHistory(1,true).next(),stamp);
        return true;
    }
    function refresh(stamp,settings) {
        refreshHeart(stamp);
        if(PreviewMode.ENABLED) {
            batteryDays=24.3;steps=8608;calories=1688;altitude=128;distance=642000;return;
        }
        var daily=ActivityMonitor.getInfo();var info=Activity.getActivityInfo();
        batteryDays=remainingDays(System.getSystemStats());
        steps=nonnegative(daily.steps);calories=nonnegative(daily.calories);distance=nonnegative(daily.distance);
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
