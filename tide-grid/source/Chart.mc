import Toybox.ActivityMonitor;
import Toybox.Lang;
import Toybox.Time;
import Toybox.Time.Gregorian;

class Chart {
    const TITLES = ["", "TIDE 12H", "STEPS 7D", "HEART 2H", "DISTANCE 7D", "CALORIES 7D"];
    var samples as Array<Numeric or Null> = [];
    var minimum;
    var maximum;
    private var mode = -1;
    private var updated = -1;

    function invalidate() { updated = -1; }

    function refresh(now, source, tide) {
        if (source == 0) { return; }
        var age = now - updated;
        var interval = source == 3 || source == 1 ? 600 : 180;
        if (source == mode && updated >= 0 && age >= 0 && age < interval) { return; }
        mode = source;
        updated = now;
        var count = source == 1 ? 25 : source == 3 ? 12 : 7;
        if (samples.size() != count) { samples = new[count] as Array<Numeric or Null>; }
        for (var i = 0; i < count; i++) { samples[i] = null; }
        if (source == 1) {
            tide.fill(now, samples);
        } else if (source == 3) {
            fillHeart(now);
        } else {
            fillDaily(now, source);
        }
        measure(source);
    }

    function measure(source) {
        minimum = null;
        maximum = null;
        for (var i = 0; i < samples.size(); i++) {
            var v = samples[i];
            if (v == null) { continue; }
            if (minimum == null || v < minimum) { minimum = v; }
            if (maximum == null || v > maximum) { maximum = v; }
        }
        if (minimum != null && source != 1 && source != 3) { minimum = 0; }
    }

    function fillHeart(now) {
        if (!(ActivityMonitor has :getHeartRateHistory)) { return; }
        var earliest = now - 7200;
        var it = ActivityMonitor.getHeartRateHistory(new Time.Duration(7200), true);
        var sums = new[12];
        var counts = new[12];
        // Bound both runtime and allocation on the smallest watches.
        for (var i = 0; i < 240; i++) {
            var entry = it.next();
            if (entry == null) { break; }
            if (entry.when == null || entry.heartRate == null || entry.heartRate <= 0 || entry.heartRate > 300) { continue; }
            var time = entry.when.value();
            if (time > now || time < earliest) { continue; }
            var bucket = ((time - earliest) / 600).toNumber();
            if (bucket > 11) { bucket = 11; }
            sums[bucket] = (sums[bucket] == null ? 0 : sums[bucket]) + entry.heartRate;
            counts[bucket] = (counts[bucket] == null ? 0 : counts[bucket]) + 1;
        }
        for (var i = 0; i < 12; i++) {
            if (counts[i] != null) { samples[i] = sums[i] / counts[i]; }
        }
    }

    function civilDay(epoch) {
        var parts = Gregorian.info(new Time.Moment(epoch), Time.FORMAT_SHORT);
        return Gregorian.moment({:year => parts.year, :month => parts.month, :day => parts.day}).value();
    }

    function fillDaily(now, source) {
        var today = civilDay(now);
        var history = ActivityMonitor.getHistory();
        if (history != null) {
            for (var i = 0; i < history.size(); i++) {
                var row = history[i];
                if (row == null || row.startOfDay == null) { continue; }
                var offset = (today - civilDay(row.startOfDay.value())) / 86400;
                if (offset >= 1 && offset <= 6) { samples[6-offset] = dailyValue(row, source); }
            }
        }
        var current = ActivityMonitor.getInfo();
        if (current != null) { samples[6] = dailyValue(current, source); }
    }

    function dailyValue(row, source) {
        if (source == 2) { return row.steps; }
        if (source == 4) { return row.distance; }
        return row.calories;
    }

    (:demo)
    function fixture(source) {
        var variants = [
            [28, 46, 66, 87, 102, 113, 120, 122, 120, 114, 105, 93, 79, 65, 51, 38, 27, 21, 19, 22, 29, 42, 54, 62, 73],
            [4333, 7850, 6733, 9810, 6040, 10444, 8426],
            [67, 64, 68, 73, 96, 110, 102, 95, 84, 78, 80, 74],
            [254000, 515000, 623000, 702000, 457000, 860000, 631000],
            [1520, 1863, 1720, 2011, 1945, 2445, 1872]
        ];
        samples = variants[source-1];
        measure(source);
    }
}
