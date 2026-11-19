import Toybox.Application;
import Toybox.Graphics;
import Toybox.Math;
import Toybox.Lang;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class TideGridFace extends WatchUi.WatchFace {
    // background, dial, border, main ink, quiet ink, accent, secondary accent
    const AMOLED_THEMES = [
        [0x071518, 0x10272B, 0x28464B, 0xEDF6E8, 0x9CB9B6, 0x61E8C9, 0xF5BB71],
        [0x190C10, 0x2F1A1C, 0x5F3433, 0xFFF1DD, 0xD0A99D, 0xFF8A69, 0xF1CC83],
        [0x0B1421, 0x152640, 0x325071, 0xEFF5FF, 0xA1BCD7, 0x93C7FF, 0xCFB3F4],
        [0x101710, 0x1D2A1B, 0x394D32, 0xF4F2DB, 0xAFC0A0, 0xBCE881, 0xF0CA8B],
        [0x080B0C, 0x191E22, 0x47515A, 0xF3F5F6, 0xBDC7CE, 0xE4E9EC, 0xA8B4BE],
        [0xF4EBD6, 0xE6DBC2, 0xB9AB8F, 0x172522, 0x425954, 0x00685E, 0x923B20],
        [0x000000, 0x1B1103, 0x78591D, 0xFFEBC1, 0xD0AB62, 0xFFB942, 0xFFED97],
        [0x10091E, 0x241639, 0x603780, 0xF5ECFF, 0xC4AADF, 0xB8A4FF, 0xFF84D4],
        [0x08090C, 0x221015, 0x842A3A, 0xFFF2F3, 0xD4A0AA, 0xFF6077, 0xFFBF79],
        [0x020900, 0x112010, 0x437133, 0xE7FFCC, 0xA9CC92, 0xC4FF4D, 0x63E4AB],
        [0xF7E7E8, 0xF1D7DA, 0x9E6B79, 0x321723, 0x683E4E, 0x9B2D57, 0x514678],
        [0xEAF5F8, 0xCEDFEE, 0x7792A6, 0x122837, 0x3C5767, 0x136A83, 0x593B8F]
    ];
    const MIP_THEMES = [
        [0x000000, 0x005555, 0x00AAAA, 0xFFFFFF, 0xAAAAAA, 0x55FFFF, 0xFFAA00],
        [0x000000, 0x550000, 0xAA5500, 0xFFFFAA, 0xAAAAAA, 0xFFAA55, 0xFFFF00],
        [0x000000, 0x000055, 0x0055AA, 0xFFFFFF, 0xAAAAAA, 0x55FFFF, 0xAAAAFF],
        [0x000000, 0x005500, 0x55AA00, 0xFFFFAA, 0xAAAAAA, 0xAAFF55, 0xFFAA55],
        [0x000000, 0x000000, 0x555555, 0xFFFFFF, 0xAAAAAA, 0xFFFFFF, 0xAAAAAA],
        [0xFFFFAA, 0xFFAAAA, 0xAA5555, 0x000000, 0x555555, 0x005555, 0xAA0000],
        [0x000000, 0x555500, 0xAA5500, 0xFFFFAA, 0xFFAA55, 0xFFAA00, 0xFFFF55],
        [0x000000, 0x550055, 0xAA55AA, 0xFFFFFF, 0xFFAAFF, 0xAAAAFF, 0xFF55FF],
        [0x000000, 0x550000, 0xAA0000, 0xFFFFFF, 0xFFAAAA, 0xFF5555, 0xFFAA55],
        [0x000000, 0x005500, 0x55AA00, 0xFFFFAA, 0xAAFFAA, 0xAAFF00, 0x55FFAA],
        [0xFFAAFF, 0xFFAAAA, 0xAA55AA, 0x550000, 0x550055, 0xAA0055, 0x5500AA],
        [0xAAFFFF, 0xAAAAFF, 0x5555AA, 0x000055, 0x005555, 0x0055AA, 0x5500AA]
    ];
    const MONO_DARK = [0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF];
    const MONO_LIGHT = [0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000];

    private var slots as Array<Number> = new Number[13];
    private var enabled as Array<Boolean> = new Boolean[Preferences.COUNT];
    private var chart as Chart;
    private var tides;
    private var readings as Readings;
    private var palette as Array<Number> = MONO_DARK;
    private var style = -1;
    private var chartMode;
    private var clockFormat;
    private var instrument;
    private var timeFont;
    private var secondsFont;
    private var awakeSeconds;
    private var lastSecond = -1;
    private var sleeping = false;
    private var renderedMinute = -1;
    private var drawEnabled = false;

    function initialize() {
        WatchFace.initialize();
        chart = new Chart();
        tides = new TideData();
        readings = new Readings();
        reloadSettings();
    }

    function onShow() as Void {
        drawEnabled = false;
    }

    function onLayout(dc as Dc) as Void {
        instrument = WatchUi.loadResource(Rez.Fonts.Instrument);
        drawEnabled = false;
    }

    function onEnterSleep() as Void {
        sleeping = true;
        drawEnabled = false;
    }

    function onExitSleep() as Void {
        sleeping = false;
        drawEnabled = false;
    }

    function reloadSettings() {
        var theme = Preferences.read("Theme", Panel.MONO || Panel.LOW_COLOR ? 4 : 0, AMOLED_THEMES.size());
        if (Panel.MONO || Panel.LOW_COLOR) {
            palette = theme == 5 ? MONO_LIGHT : MONO_DARK;
        } else {
            palette = Panel.AMOLED ? AMOLED_THEMES[theme] : MIP_THEMES[theme];
        }
        var chosen = Preferences.read("TimeFont", 1, 3);
        if (style != chosen) {
            style = chosen;
            timeFont = null;
        }
        chartMode = Preferences.read("Chart", 1, 6);
        clockFormat = Preferences.read("ClockFormat", 0, 3);
        for (var i = 0; i < enabled.size(); i++) { enabled[i] = false; }
        for (var i = 0; i < slots.size(); i++) {
            var metric = Preferences.slot(i);
            slots[i] = metric;
            if (metric < Preferences.COUNT) { enabled[metric] = true; }
        }
        awakeSeconds = slots[Preferences.SECONDS_SLOT] == Preferences.AWAKE_SECONDS &&
                       Application.Properties.getValue("WristSeconds") != false;
        tides.reset(chartMode == 1 || enabled[Preferences.HIGH] || enabled[Preferences.LOW] ||
                    enabled[Preferences.HIGH_LEVEL] || enabled[Preferences.LOW_LEVEL]);
        readings.invalidate();
        chart.invalidate();
        drawEnabled = false;
    }

    function onUpdate(dc as Dc) as Void {
        var moment = Time.now();
        var now = moment.value();
        var minute = now / 60;
        if (drawEnabled && renderedMinute == minute) {
            if (awakeSeconds && !sleeping && !Fixture.ENABLED && lastSecond != now) {
                drawSeconds(dc, now % 60);
                lastSecond = now;
            }
            return;
        }
        renderedMinute = minute;
        lastSecond = now;
        drawEnabled = true;
        var config = System.getDeviceSettings();
        var use12 = clockFormat == 1 || (clockFormat == 0 && !config.is24Hour);
        var day = Gregorian.info(moment, Time.FORMAT_SHORT);
        var hour = day.hour;
        var mins = day.min;
        if (Fixture.ENABLED) {
            hour = 22;
            mins = 58;
            use12 = true;
        }
        var digits = (use12 ? (hour + 11) % 12 + 1 : hour).format(use12 ? "%d" : "%02d") + ":" + mins.format("%02d");
        if (sleeping && Panel.AMOLED) {
            drawAod(dc, digits, minute);
            return;
        }
        if (timeFont == null) {
            var resource = style == 0 ? Rez.Fonts.Harbor : style == 1 ? Rez.Fonts.Dock : Rez.Fonts.Beacon;
            timeFont = WatchUi.loadResource(resource);
        }
        if (Fixture.ENABLED) {
            fillFixture();
        } else {
            if (tides.update(now)) { chart.invalidate(); }
            readings.update(now, day, enabled, use12, tides, config);
            chart.refresh(now, chartMode, tides);
        }
        drawFull(dc, digits, use12 && hour >= 12, awakeSeconds && !sleeping ? (Fixture.ENABLED ? 50 : now % 60) : null);
    }

    (:demo)
    function fillFixture() {
        readings.values = [null, "30 AUG", "86%", "8426", "74", "21°C", "6.3KM", "1872",
                           "126M", "12", "2", "3:03", "8:54P", "6:18", "6:26P", "SUN",
                           "196CM", "22CM", "1.0", "SUN 30", "L"];
        readings.moonAge = 1.0;
        readings.weatherIcon = "ą";
        if (chartMode != 0) { chart.fixture(chartMode); }
    }

    (:liveOnly)
    function fillFixture() {
    }

    function drawAod(dc, digits, minute) {
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();
        var dx = (minute % 3 - 1) * (Panel.W / 24);
        var dy = ((minute / 3) % 3 - 1) * (Panel.H / 18);
        dc.setColor(0x636D69, Graphics.COLOR_TRANSPARENT);
        var font = Graphics.FONT_MEDIUM;
        if (dc.getTextWidthInPixels(digits, font) * dc.getFontHeight(font) > Panel.W * Panel.H * .075) {
            font = Graphics.FONT_SMALL;
        }
        dc.drawText(Panel.W/2 + dx, Panel.H/2 + dy, font, digits,
                    Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    function clockTop() { return px(Panel.H, .677); }
    function sideX() { return px(Panel.W, .785); }

    function drawFull(dc, digits, pm, seconds) {
        dc.setColor(palette[0], palette[0]);
        dc.clear();
        var w = Panel.W;
        var h = Panel.H;
        var small = Panel.SMALL;
        var hardwareWindow = Panel.SUB && !Panel.ROUND;
        drawHeader(dc, hardwareWindow);

        var graphBottom = px(h, .600);
        var graphTop = px(h, hardwareWindow ? .397 : .369);
        if (Panel.SUB && graphTop < Panel.CY+Panel.R+8) { graphTop = Panel.CY+Panel.R+8; }
        if (chartMode != 0) {
            var graphWidth = px(w, .552);
            drawChart(dc, (w-graphWidth)/2, graphTop, graphWidth, graphBottom-3);
        }
        drawChartSides(dc, graphTop, graphBottom);
        var rail = px(w, .409);
        line(dc, w/2-rail, graphBottom, w/2+rail, palette[4]);
        var y = clockTop();
        var left = px(w, .157);
        var caption = slots[Preferences.CAPTION_SLOT];
        var captionX = px(w, .343);
        if (caption == Preferences.LOCAL_CAPTION) {
            label(dc, captionX, graphBottom+3, "HOME", instrument, palette[4], Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            pair(dc, caption, captionX, graphBottom+3, px(w, .360), palette[4]);
        }
        if (pm) {
            label(dc, left-3, y+(Panel.CLOCK_H-small)*2/3,
                  "P", instrument, palette[3], Graphics.TEXT_JUSTIFY_RIGHT);
        }
        label(dc, left, y, digits, timeFont, palette[3], Graphics.TEXT_JUSTIFY_LEFT);
        pair(dc, slots[6], sideX(), y, px(w, .180), palette[4]);
        var secondSlot = slots[Preferences.SECONDS_SLOT];
        if (seconds != null) {
            drawSeconds(dc, seconds);
        } else if (secondSlot != Preferences.AWAKE_SECONDS) {
            var secondRow = y + small + 2 + px(Panel.CLOCK_H, .18);
            pair(dc, secondSlot, sideX(), secondRow, px(w, .180), palette[3]);
        }

        var bottom = px(h, .884);
        var span = px(w, Panel.ROUND ? .169 : .204);
        var maxWidth = px(w, Panel.ROUND ? .165 : .195);
        for (var i = 0; i < 3; i++) {
            pair(dc, slots[7+i], w/2+(i-1)*span, bottom, maxWidth, i == 1 ? palette[3] : palette[5]);
        }
    }

    function drawHeader(dc, hardwareWindow) {
        var w = Panel.W;
        var h = Panel.H;
        var small = Panel.SMALL;
        var left = px(w, hardwareWindow ? .343 : .313);
        var y = px(h, hardwareWindow ? .105 : .137);
        var headingMode = slots[Preferences.HEADING_SLOT];
        var titleX = hardwareWindow ? left : w/2;
        var cap = px(w, hardwareWindow ? .445 : .648);
        if (headingMode == Preferences.AUTO_HEADING) {
            var heading = headingText(hardwareWindow);
            while (heading.length() > 1 && dc.getTextWidthInPixels(heading, instrument) > cap) {
                heading = heading.substring(0, heading.length()-1);
            }
            label(dc, titleX, y, heading, instrument, palette[4], Graphics.TEXT_JUSTIFY_CENTER);
        } else {
            pair(dc, headingMode, titleX, y, cap, palette[4]);
        }
        var firstY = px(h, hardwareWindow ? .198 : .225);
        var secondY = firstY + small + px(h, .014);
        pair(dc, slots[0], left, firstY, px(w, .330), palette[3]);
        pair(dc, slots[1], left, secondY, px(w, .330), palette[3]);
        if (Panel.SUB) {
            drawWindow(dc, Panel.CX, Panel.CY, Panel.R);
        } else {
            var right = px(w, .734);
            pair(dc, slots[2], right, firstY, px(w, .238), palette[5]);
            pair(dc, slots[3], right, secondY, px(w, .238), palette[4]);
        }
    }

    function headingText(hardwareWindow) {
        if (chartMode != 1) {
            return chartMode == 0 ? "LOCAL" : chart.TITLES[chartMode];
        }
        if (Fixture.ENABLED) {
            return hardwareWindow ? "ELIZABETH_2" : "PORT ELIZABETH_2";
        }
        var port = tides.name();
        return port != null ? port : "TIDE";
    }

    function drawWindow(dc, x, y, r) {
        var hasTop = slots[2] != 0;
        var hasBottom = slots[3] != 0;
        if (!hasTop && !hasBottom) { return; }
        var small = Panel.SMALL;
        dc.setColor(palette[1], Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(x, y, r);
        dc.setColor(palette[2], Graphics.COLOR_TRANSPARENT);
        dc.drawCircle(x, y, r);
        if (hasTop && hasBottom) {
            pair(dc, slots[2], x, y-small-1, r*8/5, palette[5]);
            pair(dc, slots[3], x, y+2, r*8/5, palette[6]);
        } else {
            pair(dc, hasTop ? slots[2] : slots[3], x, y-small/2, r*8/5, palette[5]);
        }
    }

    function drawChartSides(dc, top, bottom) {
        var x = px(Panel.W, .132);
        var y = top + px(bottom-top, .38);
        var r = px(Panel.W, .047);
        if (slots[4] == Preferences.MOON_AGE) {
            dc.setColor(palette[4], Graphics.COLOR_TRANSPARENT);
            dc.fillCircle(x, y, r);
            dc.setColor(palette[0], Graphics.COLOR_TRANSPARENT);
            var age = readings.moonAge;
            var shade = (age < 14.765 ? age : 29.53-age)/14.765;
            var offset = px(2*r+1, shade);
            if (age < 14.765) { offset = -offset; }
            dc.setClip(x-r, y-r, r*2+1, r*2+1);
            dc.fillCircle(x+offset, y, r);
            dc.clearClip();
            dc.setColor(palette[4], Graphics.COLOR_TRANSPARENT);
            dc.drawCircle(x, y, r);
            pair(dc, slots[4], x, y+r+2, px(Panel.W, .193), palette[4]);
        } else {
            pair(dc, slots[4], x, y, px(Panel.W, .193), palette[4]);
        }
        x = px(Panel.W, .844);
        if (slots[5] == Preferences.CYCLE) {
            var centerY = y+r;
            var size = r+1;
            dc.setColor(palette[4], Graphics.COLOR_TRANSPARENT);
            dc.drawArc(x, centerY, size, Graphics.ARC_CLOCKWISE, 178, 351);
            dc.drawLine(x, centerY, x+size-1, centerY-size/2);
            pair(dc, slots[5], x+size/2, y-Panel.SMALL/2, px(Panel.W, .11), palette[4]);
        } else {
            pair(dc, slots[5], x, y, px(Panel.W, .183), palette[4]);
        }
    }

    function drawChart(dc, left, top, width, axis) {
        if (chart.maximum == null || axis-top < 3) {
            var status = chartMode == 1 ? tides.status() : "NO HISTORY";
            label(dc, left+width/2, top+Panel.SMALL, status, instrument, palette[4], Graphics.TEXT_JUSTIFY_CENTER);
            return;
        }
        var count = chart.samples.size();
        var range = chart.maximum-chart.minimum;
        var gap = px(Panel.W, chartMode == 1 ? .004 : .009);
        if (gap < 1) { gap = 1; }
        for (var i = 0; i < count; i++) {
            var value = chart.samples[i];
            if (value == null) { continue; }
            var offset = width * i / count;
            var barWidth = width * (i+1) / count - offset - gap;
            var normalized = range == 0 ? (value == 0 ? 0.0 : .56) : (value-chart.minimum).toFloat()/range;
            var bar = 1 + px(axis-top-1, normalized);
            var current = i == (chartMode == 1 ? 6 : count-1);
            dc.setColor(current ? palette[6] : palette[5], Graphics.COLOR_TRANSPARENT);
            var x = left + offset;
            if (chartMode == 1 && Panel.MONO && !current) {
                for (var y = axis-1; y >= axis-bar; y -= 2) {
                    dc.drawLine(x, y, x+barWidth-1, y);
                }
            } else {
                dc.fillRectangle(x, axis-bar, barWidth, bar);
            }
        }
    }

    function drawSeconds(dc, seconds) {
        if (secondsFont == null) { secondsFont = WatchUi.loadResource(Rez.Fonts.Seconds); }
        var x = sideX();
        var y = clockTop() + Panel.SMALL + 2;
        var text = seconds.format("%02d");
        var width = dc.getTextWidthInPixels("00", secondsFont);
        var height = dc.getFontHeight(secondsFont);
        dc.setColor(palette[0], Graphics.COLOR_TRANSPARENT);
        dc.fillRectangle(x-width/2-1, y, width+2, height);
        label(dc, x, y, text, secondsFont, palette[3], Graphics.TEXT_JUSTIFY_CENTER);
    }

    function pair(dc, metric, x, y, maxWidth, ink) {
        if (metric == 0) { return; }
        var value = readings.values[metric];
        if (value == null) { value = "--"; }
        var icon = metric == 5 ? readings.weatherIcon : Preferences.ICONS[metric];
        var width = dc.getTextWidthInPixels(value, instrument);
        if (width > maxWidth && (metric == Preferences.DATE || metric == Preferences.DAY_DATE)) {
            var space = value.find(" ");
            if (space != null) { value = value.substring(0,space) + value.substring(space+1,value.length()); }
            width = dc.getTextWidthInPixels(value, instrument);
        }
        if (width > maxWidth && metric == Preferences.DISTANCE) {
            var point = value.find(".");
            if (point != null) {
                var unit = value.substring(value.length()-2,value.length());
                value = value.substring(0,value.length()-2).toFloat().format("%.0f") + unit;
                width = dc.getTextWidthInPixels(value, instrument);
            }
        }
        if (icon.length() == 0) {
            label(dc, x, y, width > maxWidth ? "--" : value, instrument, ink, Graphics.TEXT_JUSTIFY_CENTER);
            return;
        }
        var iconWidth = dc.getTextWidthInPixels(icon, instrument);
        var gap = Panel.SUB ? 2 : px(Panel.W, .009);
        if (width > maxWidth) {
            value = "--";
            width = dc.getTextWidthInPixels(value, instrument);
        }
        if (width + iconWidth + gap > maxWidth) {
            label(dc, x, y, value, instrument, ink, Graphics.TEXT_JUSTIFY_CENTER);
            return;
        }
        var left = x-(width+iconWidth+gap)/2;
        label(dc, left, y, icon, instrument, palette[4], Graphics.TEXT_JUSTIFY_LEFT);
        label(dc, left+iconWidth+gap, y, value, instrument, ink, Graphics.TEXT_JUSTIFY_LEFT);
    }

    function label(dc, x, y, value, font, ink, align) {
        dc.setColor(ink, Graphics.COLOR_TRANSPARENT);
        dc.drawText(x, y, font, value, align);
    }

    function line(dc, left, y, right, color) {
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(left, y, right, y);
    }

    function px(size, fraction) {
        return (size * fraction + .5).toNumber();
    }
}
