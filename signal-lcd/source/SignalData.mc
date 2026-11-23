import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Lang;
import Toybox.System;
import Toybox.Time;
import Toybox.Weather;

module Field {
    const OFF = 0;
    const HEART = 1;
    const BATTERY = 2;
    const STEPS = 3;
    const CALORIES = 4;
    const DISTANCE = 5;
    const TEMP = 6;
    const NOTIFY = 7;
    const ALT = 8;
    const FLOORS = 9;
    const SECONDS = 10;
    const LABELS = ["", "BPM", "BAT", "STEPS", "KCAL", "KM", "TEMP", "MSG", "ALT", "FLOORS", "SEC"];
    const SYMBOLS = ["", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"];
}

module GaugeMode {
    const STEPS = 0;
    const BATTERY = 1;
    const OFF = 2;
    const DAY = 3;
    const FLOORS = 4;
    const INTENSITY = 5;
}

module FaceStatus {
    const OFF = 0;
    const MUTE = 1;
    const CONNECTED = 2;
    const ALARM = 3;
    const DND = 4;
    const NOTIFICATIONS = 5;
    const LOW_BATTERY = 6;
    const VIBRATION_OFF = 7;
    const DISCONNECTED = 8;
    const CHARGING = 9;
    const LABELS = ["", "MUTE", "LINK", "ALARM", "DND", "MSG", "LOW BAT", "VIB OFF", "NO LINK", "CHARGE"];
    const SYMBOLS = ["", "n", "m", "l", "o", "h", "p", "q", "r", "s"];

    function visible(mode, settings, data) {
        if (mode == OFF) { return false; }
        if (Profile.DEMO) { return true; }
        switch (mode) {
            case MUTE: return settings.tonesOn == false;
            case CONNECTED: return settings.phoneConnected == true;
            case ALARM: return settings.alarmCount > 0;
            case DND: return (settings has :doNotDisturb) && settings.doNotDisturb == true;
            case NOTIFICATIONS: return settings.notificationCount > 0;
            case LOW_BATTERY:
                var battery = data.percent(GaugeMode.BATTERY);
                return battery != null && battery >= 0 && battery <= 20;
            case VIBRATION_OFF: return settings.vibrateOn == false;
            case DISCONNECTED: return settings.phoneConnected == false;
            case CHARGING: return data.charging();
        }
        return false;
    }
}

class SignalData {
    var _values = new [11];
    var _minute = -1;
    var _weatherAt = -1;
    var _celsius;
    var _goal;
    var _floorGoal;
    var _intensityPercent;
    var _batteryDays;
    var _charging = false;
    var _distanceLabel = "KM";
    var _altitudeLabel = "M";

    function initialize() {}

    function reset() {
        _minute = -1;
        _weatherAt = -1;
        _celsius = null;
    }

    function refresh(when, slots, gauge, settings, needsPowerStatus, preferBatteryDays) {
        var stamp = when.value();
        var minute = stamp / 60;
        if (_minute == minute) { return; }
        _minute = minute;

        if (Profile.DEMO) {
            _values = [null, 78, 82, 8640, 1628, 6.4, 19, 2, 1380, 12, null];
            if (Profile.EXTREME) {
                _values = [null, 199, 100, 129000, 40828, 128.5, -26, 103, -1400, 106, null];
            }
            _goal = 10000;
            _floorGoal = 16;
            _intensityPercent = progressRatio(94,150);
            _batteryDays = preferBatteryDays ? 18.4 : null;
            return;
        }

        var steps = gauge == GaugeMode.STEPS || slots.indexOf(Field.STEPS) >= 0;
        var distance = slots.indexOf(Field.DISTANCE) >= 0;
        var calories = slots.indexOf(Field.CALORIES) >= 0;
        var floors = gauge == GaugeMode.FLOORS || slots.indexOf(Field.FLOORS) >= 0;
        var intensity = gauge == GaugeMode.INTENSITY;
        var heart = slots.indexOf(Field.HEART) >= 0;
        var altitude = slots.indexOf(Field.ALT) >= 0;
        if (steps || distance || calories || floors || intensity) {
            var daily = ActivityMonitor.getInfo();
            _floorGoal = null;
            _intensityPercent = null;
            if (daily != null) {
                _values[Field.STEPS] = daily.steps;
                _values[Field.CALORIES] = daily.calories;
                // Watches without a barometer (Forerunner 55, Venu Sq...) have no
                // floorsClimbed member at all. Reading it there is a fatal error.
                _values[Field.FLOORS] = (daily has :floorsClimbed) ? daily.floorsClimbed : null;
                var miles = settings.distanceUnits == System.UNIT_STATUTE;
                _distanceLabel = miles ? "MI" : "KM";
                _values[Field.DISTANCE] = daily.distance == null ? null :
                    daily.distance / (miles ? 160934.4 : 100000.0);
                _goal = daily.stepGoal;
                if (gauge == GaugeMode.FLOORS && (daily has :floorsClimbedGoal)) {
                    _floorGoal = daily.floorsClimbedGoal;
                }
                if (intensity && (daily has :activeMinutesWeek) && (daily has :activeMinutesWeekGoal)) {
                    var activeWeek = daily.activeMinutesWeek;
                    if (activeWeek != null) {
                        _intensityPercent = progressRatio(activeWeek.total,daily.activeMinutesWeekGoal);
                    }
                }
            } else {
                _values[Field.STEPS] = null;
                _values[Field.CALORIES] = null;
                _values[Field.FLOORS] = null;
                _values[Field.DISTANCE] = null;
                _goal = null;
            }
        }
        if (gauge == GaugeMode.BATTERY || slots.indexOf(Field.BATTERY) >= 0 || needsPowerStatus) {
            var power = System.getSystemStats();
            _values[Field.BATTERY] = power.battery;
            _charging = needsPowerStatus && (power has :charging) && power.charging == true;
            _batteryDays = preferBatteryDays && (power has :batteryInDays) ? power.batteryInDays : null;
        }
        if (slots.indexOf(Field.NOTIFY) >= 0) {
            _values[Field.NOTIFY] = settings.notificationCount;
        }
        if (heart || altitude) {
            var active = Activity.getActivityInfo();
            if (heart) {
                var bpm = active == null ? null : active.currentHeartRate;
                if (!validBpm(bpm) && (ActivityMonitor has :getHeartRateHistory)) {
                    var sample = ActivityMonitor.getHeartRateHistory(1, true).next();
                    bpm = sample != null && sample.when != null && fresh(sample.when, stamp, 180) ?
                        sample.heartRate : null;
                }
                _values[Field.HEART] = validBpm(bpm) ? bpm : null;
            }
            if (altitude) {
                var meters = active == null || !(active has :altitude) ? null : active.altitude;
                var feet = settings.elevationUnits == System.UNIT_STATUTE;
                _altitudeLabel = feet ? "FT" : "M";
                _values[Field.ALT] = meters == null ? null : meters * (feet ? 3.28084 : 1.0);
            }
        }
        if (slots.indexOf(Field.TEMP) >= 0) {
            if (_weatherAt < 0 || stamp < _weatherAt || stamp - _weatherAt >= 900) {
                _weatherAt = stamp;
                _celsius = null;
                if ((Toybox has :Weather) && (Weather has :getCurrentConditions)) {
                    var conditions = Weather.getCurrentConditions();
                    if (conditions != null && conditions.observationTime != null &&
                        fresh(conditions.observationTime, stamp, 10800)) {
                        _celsius = conditions.temperature;
                    }
                }
            }
            _values[Field.TEMP] = _celsius;
        }
    }

    function fresh(when, stamp, maxAge) {
        var age = stamp - when.value();
        return age >= 0 && age <= maxAge;
    }

    function validBpm(v) {
        return v != null && v >= 25 && v <= 250 && v != ActivityMonitor.INVALID_HR_SAMPLE;
    }

    function percent(gauge) {
        switch (gauge) {
            case GaugeMode.BATTERY: return _values[Field.BATTERY];
            case GaugeMode.FLOORS: return progressRatio(_values[Field.FLOORS],_floorGoal);
            case GaugeMode.INTENSITY: return _intensityPercent;
        }
        return progressRatio(_values[Field.STEPS],_goal);
    }

    function progressRatio(value, goal) {
        return value == null || value < 0 || goal == null || goal <= 0 ? null : value * 100.0 / goal;
    }

    function charging() { return _charging; }

    function label(field) {
        if (field == Field.DISTANCE) { return _distanceLabel; }
        if (field == Field.ALT) { return _altitudeLabel; }
        return Field.LABELS[field];
    }

    function text(field, settings, second, compact) {
        if (field == Field.SECONDS) { return second < 0 ? "--" : second.format("%02d"); }
        var v = _values[field];
        if (v == null) { return "--"; }
        if (field == Field.BATTERY) {
            if (_batteryDays != null && _batteryDays >= 0) {
                return _batteryDays.format(_batteryDays < 1 ? "%.1f" : "%.0f")+"d";
            }
            return v.format("%.0f")+"%";
        }
        if (field == Field.TEMP) {
            var f = settings.temperatureUnits == System.UNIT_STATUTE && !Profile.DEMO;
            // 19°C, or 19° where the unit letter does not fit.
            var degrees = (f ? v * 1.8 + 32 : v).format("%.0f") + "°";
            return compact ? degrees : degrees + (f ? "F" : "C");
        }
        if (field == Field.DISTANCE) {
            return v < 100 && !compact ? v.format("%.1f") : v.format("%.0f");
        }
        var n = v.toNumber();
        if (n.abs() >= (compact ? 1000 : 10000)) {
            // Full: 12.9K or 129K. Compact keeps one decimal below ten: 8.6K.
            var k = n / 1000.0;
            return k.abs() < (compact ? 10 : 100) ? k.format("%.1f") + "K" : k.format("%.0f") + "K";
        }
        return n.format("%d");
    }
}
