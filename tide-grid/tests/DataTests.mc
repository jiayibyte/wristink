import Toybox.ActivityMonitor;
import Toybox.Application;
import Toybox.Lang;
import Toybox.Test;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.System;
import Toybox.Weather;

(:test)
function selectsTheNearestPortAnywhere(logger) {
    var tides = new TideData();
    Test.assertEqual(tides.nearest(24.45, 118.08)[0], "XIAMEN");
    Test.assertEqual(tides.nearest(37.807, -122.466)[0], "SAN FRANCISCO");
    // Inland: the closest port however far (Beijing -> Dalian, about 460 km).
    Test.assertEqual(tides.nearest(39.9042, 116.4074)[0], "DALIAN");
    Test.assertEqual(tides.nearest(38.6270, -90.1994)[0], "NEW YORK");
    Test.assertEqual(tides.nearest(51.5072, -0.1276)[0], "PORTSMOUTH");
    Test.assert(tides.nearest(0, 0) == null);
    Application.Properties.setValue("TidePlace", 5);
    tides.reset(true);
    Test.assertEqual(tides.name(), "XIAMEN");
    Application.Properties.setValue("TidePlace", 23);
    tides.reset(true);
    Test.assertEqual(tides.name(), "SAN FRANCISCO");
    Application.Properties.setValue("TidePlace", 0);
    tides.reset(true);
    Test.assert(tides.name() == null);
    return true;
}

(:test)
function localTideForecastMatchesReferenceModel(logger) {
    var now = 1794970800; // 2026-11-18 03:00 UTC
    var tides = new TideData();
    var samples = new[25] as Array<Numeric or Null>;
    Application.Properties.setValue("TidePlace", 5);
    tides.reset(true);
    tides.update(now);
    tides.fill(now, samples);
    // Independent uptide reconstruction from the same published constituents.
    Test.assert((samples[0]-48.948).abs() < 2.50);
    Test.assert((samples[6]+111.046).abs() < 2.50);
    Test.assert((samples[24]-132.951).abs() < 2.50);
    Test.assert(tides.next(now, 1, false) != null);
    Test.assert(tides.height(now, 0) != null);
    Application.Properties.setValue("TidePlace", 23);
    tides.reset(true);
    tides.update(now);
    tides.fill(now, samples);
    Test.assert((samples[0]-26.507).abs() < 2.50);
    Test.assert((samples[12]+54.363).abs() < 2.50);
    Application.Properties.setValue("TidePlace", 0);
    return true;
}

(:test)
function heartRateRejectsInvalidSamples(logger) {
    // ActivityMonitor marks gaps in the history with 255.
    Test.assert(!Readings.validHeartRate(ActivityMonitor.INVALID_HR_SAMPLE));
    Test.assert(!Readings.validHeartRate(null));
    Test.assert(!Readings.validHeartRate(0));
    Test.assert(Readings.validHeartRate(74));
    Test.assert(Readings.validHeartRate(199));
    return true;
}

(:test)
function packedCatalogRecordsParse(logger) {
    var xiamen = TideCatalog.port(4);
    Test.assertEqual(xiamen[0], "XIAMEN");
    Test.assert((xiamen[1]-24.45).abs() < .001);
    Test.assert((xiamen[2]-118.067).abs() < .001);
    Test.assertEqual(xiamen[3].length(), TideCatalog.TERMS.size()*3);
    var legacy = 0;
    for (var i = 0; i < TideCatalog.PORTS.size(); i++) {
        var port = TideCatalog.port(i);
        Test.assert(port[0].length() > 0 && port[3].length() == TideCatalog.TERMS.size()*3);
        if (port[4].length() > 0) { legacy++; }
    }
    // Four retired NOAA station ids still migrate to their stations.
    Test.assertEqual(legacy, 4);
    return true;
}

(:test)
function paletteCarriesOnlyThisScreenFamily(logger) {
    var rows = Panel.MONO || Panel.LOW_COLOR ? 2 : 12;
    Test.assertEqual(Panel.PALETTE.length(), rows*7*6);
    for (var i = 0; i < rows*7; i++) {
        Test.assert(Panel.PALETTE.substring(i*6, i*6+6).toNumberWithBase(16) != null);
    }
    return true;
}

(:test)
function phoneSettingsAcceptLooseTypes(logger) {
    // Values from Garmin Connect may not keep the declared Number / Boolean type.
    Test.assertEqual(Preferences.choice(2, 0, 6), 2);
    Test.assertEqual(Preferences.choice(2l, 0, 6), 2);
    Test.assertEqual(Preferences.choice(2.0, 0, 6), 2);
    Test.assertEqual(Preferences.choice("2", 0, 6), 2);
    Test.assertEqual(Preferences.choice("x", 0, 6), 0);
    Test.assertEqual(Preferences.choice(6, 0, 6), 0);
    Test.assertEqual(Preferences.toFlag(false, true), false);
    Test.assertEqual(Preferences.toFlag("false", true), false);
    Test.assertEqual(Preferences.toFlag(0, true), false);
    Test.assertEqual(Preferences.toFlag(null, true), true);
    Test.assertEqual(Preferences.read("NoSuchKey", 4, 6), 4);
    return true;
}

(:test)
function phoneSettingsChangeReachesTheFace(logger) {
    var app = Application.getApp() as TideGridApp;
    var face = new TideGridFace();
    app.face = face;
    Application.Properties.setValue("Chart", 3);
    Application.Properties.setValue("ClockFormat", 2);
    Application.Properties.setValue("WristSeconds", false);
    app.onSettingsChanged();
    Test.assertEqual(face.chartMode, 3);
    Test.assertEqual(face.clockFormat, 2);
    Test.assertEqual(face.awakeSeconds, false);
    Application.Properties.setValue("Chart", 1);
    Application.Properties.setValue("ClockFormat", 0);
    Application.Properties.setValue("WristSeconds", true);
    app.onSettingsChanged();
    Test.assertEqual(face.chartMode, 1);
    Test.assertEqual(face.awakeSeconds, true);
    app.face = null;
    return true;
}

(:test)
function chartRangesKeepZeroAndMissingDataDistinct(logger) {
    var chart = new Chart();
    chart.samples = [null, -4, 0, 6] as Array<Numeric or Null>;
    chart.measure(1);
    Test.assertEqual(chart.minimum, -4);
    Test.assertEqual(chart.maximum, 6);
    chart.samples = [null, 0, 342, null] as Array<Numeric or Null>;
    chart.measure(2);
    Test.assertEqual(chart.minimum, 0);
    Test.assertEqual(chart.maximum, 342);
    chart.samples = [null, null] as Array<Numeric or Null>;
    chart.measure(3);
    Test.assert(chart.minimum == null && chart.maximum == null);
    return true;
}

(:test)
function nativeFrameDrawsTheFullDialAndSleepFrame(logger) {
    if (!(Toybox.Graphics has :createBufferedBitmap)) { return true; }
    var reference = Toybox.Graphics.createBufferedBitmap({
        :width => Panel.W, :height => Panel.H
    });
    var buffer = reference.get();
    var face = new TideGridFace();
    var dc = buffer.getDc();
    Application.Properties.setValue("Chart", 1);
    Application.Properties.setValue("TimeFont", 1);
    face.reloadSettings();
    face.onLayout(dc);
    face.onUpdate(dc);
    face.onEnterSleep();
    face.onUpdate(dc);
    face.onExitSleep();
    face.onUpdate(dc);
    Test.assertEqual(dc.getWidth(), Panel.W);
    Test.assertEqual(dc.getHeight(), Panel.H);

    Application.Properties.setValue("Heading", Preferences.DATE);
    Application.Properties.setValue("ClockCaption", Preferences.OFF);
    Application.Properties.setValue("SecondsSlot", Preferences.BAT);
    Application.Properties.setValue("Chart", 0);
    Application.Properties.setValue("Theme", Panel.MONO || Panel.LOW_COLOR ? 5 : 11);
    Test.assertEqual(Preferences.slot(Preferences.HEADING_SLOT), Preferences.DATE);
    Test.assertEqual(Preferences.slot(Preferences.CAPTION_SLOT), Preferences.OFF);
    Test.assertEqual(Preferences.slot(Preferences.SECONDS_SLOT), Preferences.BAT);
    face.reloadSettings();
    face.onUpdate(dc);

    Application.Properties.setValue("SecondsSlot", Preferences.LOCAL_CAPTION);
    Test.assertEqual(Preferences.slot(Preferences.SECONDS_SLOT), Preferences.AWAKE_SECONDS);
    Application.Properties.setValue("Heading", Preferences.AUTO_HEADING);
    Application.Properties.setValue("ClockCaption", Preferences.LOCAL_CAPTION);
    Application.Properties.setValue("SecondsSlot", Preferences.AWAKE_SECONDS);
    Application.Properties.setValue("Chart", 1);
    Application.Properties.setValue("Theme", Panel.MONO || Panel.LOW_COLOR ? 4 : 0);
    return true;
}


(:test)
function sunriseAndSunsetFollowSelectedPort(logger) {
    if (!(Weather has :getSunrise) || !(Weather has :getSunset)) { return true; }
    var now = 1795054104; // 2026-11-19 02:08:24 UTC
    var day = Gregorian.info(new Time.Moment(now), Time.FORMAT_SHORT);
    var enabled = new Boolean[Preferences.COUNT];
    for (var i=0; i<enabled.size(); i++) { enabled[i] = false; }
    enabled[Preferences.SUNRISE] = true;
    enabled[Preferences.SUNSET] = true;
    var tides = new TideData();
    var readings = new Readings();
    var settings = System.getDeviceSettings();

    Application.Properties.setValue("TidePlace", 5);
    tides.reset(true);
    readings.update(now, day, enabled, false, tides, settings);
    var riseXiamen = readings.values[Preferences.SUNRISE];
    var setXiamen = readings.values[Preferences.SUNSET];
    Test.assert(riseXiamen != null && setXiamen != null);

    // Same Readings object and watch date. A station change must refresh the
    // solar cache even before the next minute or weather refresh.
    Application.Properties.setValue("TidePlace", 23);
    tides.reset(true);
    readings.update(now, day, enabled, false, tides, settings);
    var riseSanFrancisco = readings.values[Preferences.SUNRISE];
    var setSanFrancisco = readings.values[Preferences.SUNSET];
    Test.assert(riseSanFrancisco != null && setSanFrancisco != null);
    Test.assert(!riseSanFrancisco.equals(riseXiamen));
    Test.assert(!setSanFrancisco.equals(setXiamen));
    logger.debug("XIAMEN " + riseXiamen + " / " + setXiamen);
    logger.debug("SAN FRANCISCO " + riseSanFrancisco + " / " + setSanFrancisco);
    Application.Properties.setValue("TidePlace", 0);
    return true;
}
