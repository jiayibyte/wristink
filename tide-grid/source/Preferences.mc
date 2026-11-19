import Toybox.Application;
import Toybox.Lang;
import Toybox.System;

module Preferences {
    const OFF = 0;
    const DATE = 1;
    const BAT = 2;
    const STEPS = 3;
    const HEART = 4;
    const TEMP = 5;
    const DISTANCE = 6;
    const CALORIES = 7;
    const ELEVATION = 8;
    const FLOORS = 9;
    const NOTIFICATIONS = 10;
    const HIGH = 11;
    const LOW = 12;
    const SUNRISE = 13;
    const SUNSET = 14;
    const WEEKDAY = 15;

    const HIGH_LEVEL = 16;
    const LOW_LEVEL = 17;
    const MOON_AGE = 18;
    const DAY_DATE = 19;
    const CYCLE = 20;
    const COUNT = 21;
    const AUTO_HEADING = 21;
    const LOCAL_CAPTION = 22;
    const AWAKE_SECONDS = 23;

    const HEADING_SLOT = 10;
    const CAPTION_SLOT = 11;
    const SECONDS_SLOT = 12;

    const ICONS = ["", "", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
                   "p", "", "", "", "", ""];
    const SLOTS = ["HeaderLeft", "HeaderRight", "CircleTop", "CircleBottom",
                   "ChartLeft", "ChartRight", "TimeAux", "FooterLeft", "FooterCenter", "FooterRight",
                   "Heading", "ClockCaption", "SecondsSlot"];
    const DEFAULTS = [SUNRISE, SUNSET, HIGH, HIGH_LEVEL, MOON_AGE, CYCLE, DAY_DATE, STEPS, HEART, BAT,
                      AUTO_HEADING, LOCAL_CAPTION, AWAKE_SECONDS];
    const DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
    const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

    function slot(index) {
        var fallback = DEFAULTS[index];
        var value = read(SLOTS[index], fallback, AWAKE_SECONDS+1);
        return value < COUNT || value == fallback ? value : fallback;
    }

    function read(key, fallback, count) {
        var value = Application.Properties.getValue(key);
        return value instanceof Number && value >= 0 && value < count ? value : fallback;
    }
}
