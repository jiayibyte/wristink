import Toybox.Test;
import Toybox.Weather;
import Toybox.Time.Gregorian;
import Toybox.Graphics;
import Toybox.WatchUi;

(:test)
function weatherIconsKeepDistinctConditionsAndNightVariants(logger) {
    var samples=[Weather.CONDITION_CLEAR,Weather.CONDITION_CLOUDY,Weather.CONDITION_FOG,Weather.CONDITION_HAIL,Weather.CONDITION_PARTLY_CLOUDY,Weather.CONDITION_RAIN,Weather.CONDITION_SNOW,Weather.CONDITION_THUNDERSTORMS,Weather.CONDITION_UNKNOWN,Weather.CONDITION_WINDY,Weather.CONDITION_WINTRY_MIX];
    var expected=[0,2,3,4,5,7,8,9,10,11,12];
    for(var i=0;i<samples.size();i++) {Test.assertEqual(WeatherIcons.select(samples[i],false),expected[i]);}
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_CLEAR,true),1);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_PARTLY_CLOUDY,true),6);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_FAIR,true),1);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_THIN_CLOUDS,true),6);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_CLOUDY,true),2);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_FREEZING_RAIN,false),12);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_CLOUDY_CHANCE_OF_RAIN_SNOW,false),12);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_FLURRIES,false),8);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_CLOUDY_CHANCE_OF_RAIN,false),7);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_HURRICANE,false),11);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_VOLCANIC_ASH,false),3);
    Test.assertEqual(WeatherIcons.select(Weather.CONDITION_UNKNOWN_PRECIPITATION,false),10);
    Test.assertEqual(WeatherIcons.select(null,false),10);Test.assertEqual(WeatherIcons.select(-999,true),10);
    return true;
}

(:test)
function weatherDayNightUsesExactSunBoundariesAndPolarFallback(logger) {
    Test.assert(WeatherIcons.nightAt(363,364,1038));Test.assert(!WeatherIcons.nightAt(364,364,1038));
    Test.assert(!WeatherIcons.nightAt(1037,364,1038));Test.assert(WeatherIcons.nightAt(1038,364,1038));
    Test.assert(!WeatherIcons.nightAt(60,1200,420));Test.assert(WeatherIcons.nightAt(800,1200,420));
    Test.assert(WeatherIcons.nightAt(359,null,null));Test.assert(!WeatherIcons.nightAt(360,null,null));
    Test.assert(WeatherIcons.nightAt(1080,null,null));
    var lat=Environment.latitude;var lon=Environment.longitude;var rise=Environment.sunrise;var set=Environment.sunset;
    Environment.latitude=90.0;Environment.longitude=0.0;Environment.sunrise="--:--";Environment.sunset="--:--";
    var summer=WeatherIcons.isNight(Gregorian.moment({:year=>2026,:month=>6,:day=>21,:hour=>12}));
    var winter=WeatherIcons.isNight(Gregorian.moment({:year=>2026,:month=>12,:day=>21,:hour=>12}));
    Environment.latitude=lat;Environment.longitude=lon;Environment.sunrise=rise;Environment.sunset=set;
    Test.assert(!summer);Test.assert(winter);return true;
}

(:test)
function allOfficialWeatherCellsFitAndRenderInNativeSlot(logger) {
    var bitmap=WatchUi.loadResource(Rez.Drawables.WeatherSmall);
    Test.assertEqual(bitmap.getWidth(),13*DeviceDrawing.size(9,DeviceProfile.SCALE));Test.assertEqual(bitmap.getHeight(),DeviceDrawing.size(9,DeviceProfile.SCALE));
    var buffer=DeviceDrawing.buffer(9,9,DeviceProfile.SCALE);var dc=DeviceDrawing.resolve(buffer).getDc();
    var cell=DeviceDrawing.size(9,DeviceProfile.SCALE);
    for(var kind=0;kind<WeatherIcons.COUNT;kind++) {
        dc.setClip(0,0,cell,cell);dc.drawBitmap(-kind*cell,0,bitmap);dc.clearClip();
    }
    return true;
}
