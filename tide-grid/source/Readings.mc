import Toybox;
import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Complications;
import Toybox.Lang;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Weather;

class Readings {
    var values as Array<String or Null> = new String[Preferences.COUNT];
    var weatherIcon = "f";
    var moonAge = 0.0;
    private var weatherAt = -1;
    private var sunKey = -1;
    private var sunAt = -1;
    private var sunZone;
    private var sunPosition;
    private var rise;
    private var set;
    private var lastTemp;
    private var location;

    function invalidate() {
        weatherAt = -1;
        sunKey = -1;
        sunAt = -1;
        sunPosition = null;
        rise = null;
        set = null;
        location = null;
    }

    function update(now, day, enabled as Array<Boolean>, format12, tide, settings) {
        var wantDaily = enabled[3] || enabled[6] || enabled[7] || enabled[9];
        var daily = wantDaily ? ActivityMonitor.getInfo() : null;
        var info = enabled[4] || enabled[8] ? Activity.getActivityInfo() : null;
        if (enabled[1]) {
            values[1] = day.day.format("%02d") + " " + Preferences.MONTHS[day.month-1];
        }
        if (enabled[15]) { values[15] = Preferences.DAYS[day.day_of_week-1]; }
        if (enabled[19]) { values[19] = Preferences.DAYS[day.day_of_week-1] + " " + day.day.format("%02d"); }
        if (enabled[2]) { values[2] = number(System.getSystemStats().battery, "%"); }
        if (enabled[3]) { values[3] = daily == null ? null : compact(daily.steps); }
        if (enabled[4]) {
            var hr = info == null ? null : info.currentHeartRate;
            if ((hr == null || hr <= 0 || hr > 300) && (ActivityMonitor has :getHeartRateHistory)) {
                var last = ActivityMonitor.getHeartRateHistory(1, true).next();
                if (last != null && last.when != null && now >= last.when.value() && now-last.when.value() < 180) {
                    hr = last.heartRate;
                }
            }
            values[4] = hr != null && hr > 0 && hr <= 300 ? hr.format("%d") : null;
        }
        if (enabled[6]) {
            var cm = daily == null ? null : daily.distance;
            var miles = settings.distanceUnits == System.UNIT_STATUTE;
            values[6] = cm == null ? null : (cm/(miles ? 160934.4 : 100000.0)).format("%.1f") + (miles ? "MI" : "KM");
        }
        if (enabled[7]) { values[7] = daily == null ? null : compact(daily.calories); }
        if (enabled[8]) {
            var altitude = info != null && (info has :altitude) ? info.altitude : null;
            var feet = settings.elevationUnits == System.UNIT_STATUTE;
            values[8] = altitude == null ? null : (altitude * (feet ? 3.28084 : 1)).toNumber().format("%d") + (feet ? "FT" : "M");
        }
        if (enabled[9]) {
            values[9] = daily != null && (daily has :floorsClimbed) ? compact(daily.floorsClimbed) : null;
        }
        if (enabled[10]) {
            values[10] = (settings has :notificationCount) ? compact(settings.notificationCount) : null;
        }
        if (enabled[11]) { values[11] = tide.next(now, 1, format12); }
        if (enabled[12]) { values[12] = tide.next(now, 0, format12); }
        if (enabled[16]) { values[16] = tide.height(now, 1); }
        if (enabled[17]) { values[17] = tide.height(now, 0); }
        if (enabled[18] || enabled[20]) {
            // Mean synodic cycle, anchored to the NASA 2000-01-06 18:14 UTC new moon.
            var cycle = (now - 947182440) / 2551442.8;
            moonAge = (cycle - Toybox.Math.floor(cycle)) * 29.530588;
            var spring = Toybox.Math.cos(moonAge / 29.530588 * 2 * Toybox.Math.PI).abs();
            values[18] = moonAge.format("%.1f");
            values[20] = spring > .83 ? "L" : spring < .39 ? "S" : "M";
        }
        var wantSunrise = enabled[Preferences.SUNRISE];
        var wantSunset = enabled[Preferences.SUNSET];
        var port = wantSunrise || wantSunset ? tide.position() : null;
        if (enabled[Preferences.TEMP] || (port == null && (wantSunrise || wantSunset))) {
            refreshWeather(now);
        }
        if (enabled[Preferences.TEMP]) {
            var imperial = settings.temperatureUnits == System.UNIT_STATUTE;
            var temp = lastTemp == null ? null : imperial ? lastTemp * 1.8 + 32 : lastTemp;
            values[Preferences.TEMP] = temp == null ? null : temp.format("%.0f") + (imperial ? "°F" : "°C");
        }
        if (wantSunrise || wantSunset) {
            refreshSun(now, day, port, wantSunrise, wantSunset);
            if (wantSunrise) { values[Preferences.SUNRISE] = sunText(rise, format12); }
            if (wantSunset) { values[Preferences.SUNSET] = sunText(set, format12); }
        }
    }

    function refreshWeather(now) {
        if (weatherAt < 0 || now < weatherAt || now - weatherAt >= 900) {
            weatherAt = now;
            var conditions = Weather.getCurrentConditions();
            var recent = conditions != null && (conditions.observationTime == null ||
                         (now >= conditions.observationTime.value() && now - conditions.observationTime.value() <= 21600));
            lastTemp = recent ? conditions.temperature : null;
            weatherIcon = recent ? weatherGlyph(conditions.condition) : "f";
            location = recent && (conditions has :observationLocationPosition) ?
                       conditions.observationLocationPosition : null;
        }
    }

    function refreshSun(now, day, port, wantRise, wantSet) {
        var target = port == null ? location : port;
        var key = dateKey(day);
        var clock = System.getClockTime();
        var zone = clock.timeZoneOffset + clock.dst;
        var missing = (wantRise && rise == null) || (wantSet && set == null);
        if (key == sunKey && target == sunPosition && zone == sunZone && now >= sunAt &&
            (!missing || now-sunAt < 900)) {
            return;
        }
        sunKey = key;
        sunZone = zone;
        sunPosition = target;
        sunAt = now;
        rise = wantRise ? sunFor(now, key, target, port != null, true) : null;
        set = wantSet ? sunFor(now, key, target, port != null, false) : null;
    }

    function sunFor(now, key, target, isPort, sunrise) {
        var event = target == null ? null : solarEvent(target, now, sunrise);
        if (event != null) {
            var fields = Gregorian.info(event, Time.FORMAT_SHORT);
            var eventDay = dateKey(fields);
            if (eventDay != key) {
                // A remote port's sunrise or sunset can fall on the adjacent
                // date in the watch's time zone. Ask for the neighboring day.
                event = solarEvent(target, now + (eventDay < key ? 86400 : -86400), sunrise);
                if (event != null) {
                    fields = Gregorian.info(event, Time.FORMAT_SHORT);
                    eventDay = dateKey(fields);
                }
            }
            if (event != null && eventDay == key) { return fields.hour*3600 + fields.min*60; }
        }
        return isPort ? null : deviceSun(sunrise);
    }

    function solarEvent(target, when, sunrise) {
        var date = new Time.Moment(when);
        if (sunrise && (Weather has :getSunrise)) { return Weather.getSunrise(target, date); }
        if (!sunrise && (Weather has :getSunset)) { return Weather.getSunset(target, date); }
        return null;
    }

    function deviceSun(sunrise) {
        if (!(Toybox has :Complications) || !(Complications has :getComplication)) { return null; }
        try {
            var kind = sunrise ? Complications.COMPLICATION_TYPE_SUNRISE : Complications.COMPLICATION_TYPE_SUNSET;
            var data = Complications.getComplication(new Complications.Id(kind));
            var value = data == null ? null : data.value;
            return value instanceof Number && value >= 0 && value < 86400 ? value : null;
        } catch (e instanceof Complications.ComplicationNotFoundException) {
            return null;
        }
    }

    function dateKey(fields) {
        return fields.year*416 + fields.month*32 + fields.day;
    }

    function weatherGlyph(condition) {
        if (condition == null) { return "f"; }
        if (condition == 0 || condition == 23) { return "Ā"; }
        if (condition == 1 || condition == 22) { return "ą"; }
        if (condition == 2 || condition == 20) { return "Ă"; }
        if (condition == 4 || condition == 16 || condition == 17) { return "Ĉ"; }
        if (condition == 5) { return "ċ"; }
        if (condition == 6 || condition == 12) { return "ĉ"; }
        if (condition == 8 || condition == 9) { return "ă"; }
        if (condition == 10) { return "Ą"; }
        if (condition == 7 || condition == 18 || condition == 19 || condition == 21) { return "Č"; }
        return "ć";
    }

    function sunText(seconds, format12) {
        if (seconds == null) { return null; }
        var hour = seconds/3600;
        var h = format12 ? (hour + 11) % 12 + 1 : hour;
        var suffix = format12 && hour >= 12 ? "P" : "";
        return h.format("%d") + ":" + ((seconds%3600)/60).format("%02d") + suffix;
    }

    function number(value, suffix) {
        return value == null ? null : value.format("%.0f") + suffix;
    }

    function compact(value) {
        if (value == null || value < 0) { return null; }
        if (value < 10000) { return value.format("%.0f"); }
        return (value / 1000.0).format("%.1f") + "K";
    }
}
