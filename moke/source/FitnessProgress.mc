import Toybox.SensorHistory;
import Toybox.Math;

module FitnessProgress {
    function latestBodyBattery() {
        if(!(SensorHistory has :getBodyBatteryHistory)){return null;}
        var sample = SensorHistory.getBodyBatteryHistory({:period => 1, :order => SensorHistory.ORDER_NEWEST_FIRST}).next();
        if (sample == null || sample.data == null || sample.data < 0 || sample.data > 100) { return null; }
        return sample.data;
    }
    function segmentCount(value) {
        if (value == null || value <= 0) { return 0; }
        if (value >= 100) { return 8; }
        return Math.ceil(value * 8 / 100.0).toNumber();
    }
    function dailyRatio(info) {
        if (info == null || info.activeMinutesDay == null || info.activeMinutesWeekGoal == null || info.activeMinutesWeekGoal <= 0) { return null; }
        // Garmin's total already includes double credit for vigorous minutes.
        // The system exposes only a weekly goal; the requested daily target is week / 7.
        return completion(info.activeMinutesDay.total, info.activeMinutesWeekGoal / 7.0);
    }
    function completion(minutes, goal) {
        if (minutes == null || goal == null || goal <= 0) { return null; }
        var ratio = minutes.toFloat() / goal;
        return ratio < 0 ? 0.0 : (ratio > 1 ? 1.0 : ratio);
    }
}
