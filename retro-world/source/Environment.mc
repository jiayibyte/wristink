import Toybox.Lang;
import Toybox.Position;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Weather;

module Environment {
    const POLL_SECONDS=300;
    const WEATHER_MAX_AGE=10800;
    const FIX_MAX_AGE=7200;
    var temperature=null;var condition=null;var latitude=null;var longitude=null;
    var source=0;var sunrise="--:--";var sunset="--:--";var revision=0;
    var _readAt=-1;var _sunDay=-1;var _sunLat=null;var _sunLon=null;var _location as Position.Location? = null;
    var reads=0;var sunCalculations=0;
    function fresh(when,stamp,limit) {
        if(when==null) {return false;}var age=stamp-when.value();return age>=0 && age<=limit;
    }
    function validCoordinates(coords as Array?) {
        return coords!=null && coords.size()>=2 && coords[0]!=null && coords[1]!=null && coords[0]>=-90 && coords[0]<=90 && coords[1]>=-180 && coords[1]<=180;
    }
    function fixUsable(fix,stamp) {
        return fix!=null && fix.position!=null && fix.accuracy!=null && fix.accuracy>0 && fix.accuracy<=4 && fresh(fix.when,stamp,FIX_MAX_AGE) && validCoordinates(fix.position.toDegrees());
    }
    function weatherFresh(weather,stamp) {return weather!=null && fresh(weather.observationTime,stamp,WEATHER_MAX_AGE);}
    function chooseLocation(fix,weather,stamp) as Dictionary? {
        if(fixUsable(fix,stamp)) {return {:position=>fix.position,:source=>1};}
        if(weatherFresh(weather,stamp) && weather.observationLocationPosition!=null && validCoordinates(weather.observationLocationPosition.toDegrees())) {
            return {:position=>weather.observationLocationPosition,:source=>2};
        }
        return null;
    }
    function due(last,stamp,wake) {return last<0 || stamp<last || stamp-last>=POLL_SECONDS || (wake && stamp-last>=60);}
    function timeText(moment) {
        if(moment==null) {return "--:--";}var d=Gregorian.info(moment,Time.FORMAT_SHORT);
        return d.hour.format("%02d")+":"+d.min.format("%02d");
    }
    function refresh(now,wake) {
        var stamp=now.value();
        if(due(_readAt,stamp,wake)) {
            _readAt=stamp;reads++;revision++;
            if(PreviewMode.ENABLED) {
                temperature=24;condition=Weather.CONDITION_RAIN;latitude=39.90;longitude=116.40;source=2;
                sunrise="06:04";sunset="17:18";return;
            }
            var weather=Weather.getCurrentConditions();
            var goodWeather=weatherFresh(weather,stamp);
            temperature=goodWeather ? weather.temperature : null;condition=goodWeather ? weather.condition : null;
            // Read the last known fix. Never request or enable GPS location events.
            var fix=Position.getInfo();var chosen=chooseLocation(fix,weather,stamp);
            _location=chosen==null ? null : chosen[:position];source=chosen==null ? 0 : chosen[:source];
            if(_location==null) {latitude=null;longitude=null;}
            else {var coords=_location.toDegrees() as Array<Double>;latitude=coords[0];longitude=coords[1];}
        }
        if(PreviewMode.ENABLED) {return;}
        if(_location==null) {sunrise="--:--";sunset="--:--";_sunDay=-1;return;}
        var d=Gregorian.info(now,Time.FORMAT_SHORT);var day=d.year*10000+d.month*100+d.day;
        // Round only the cache key (~10 km), never the coordinates used in the calculation.
        var latKey=(latitude*10).toNumber();var lonKey=(longitude*10).toNumber();
        if(day!=_sunDay || latKey!=_sunLat || lonKey!=_sunLon) {
            sunrise=timeText(Weather.getSunrise(_location,now));sunset=timeText(Weather.getSunset(_location,now));
            _sunDay=day;_sunLat=latKey;_sunLon=lonKey;sunCalculations++;
        }
    }
    function category(value) {
        if(value==null) {return 0;}
        switch(value) {
            case Weather.CONDITION_CLEAR:case Weather.CONDITION_PARTLY_CLEAR:case Weather.CONDITION_MOSTLY_CLEAR:return 1;
            case Weather.CONDITION_PARTLY_CLOUDY:case Weather.CONDITION_MOSTLY_CLOUDY:case Weather.CONDITION_CLOUDY:return 2;
            case Weather.CONDITION_RAIN:case Weather.CONDITION_LIGHT_RAIN:case Weather.CONDITION_HEAVY_RAIN:
            case Weather.CONDITION_SCATTERED_SHOWERS:case Weather.CONDITION_LIGHT_SHOWERS:case Weather.CONDITION_SHOWERS:
            case Weather.CONDITION_HEAVY_SHOWERS:case Weather.CONDITION_CHANCE_OF_SHOWERS:case Weather.CONDITION_DRIZZLE:return 3;
            case Weather.CONDITION_SNOW:case Weather.CONDITION_LIGHT_SNOW:case Weather.CONDITION_HEAVY_SNOW:
            case Weather.CONDITION_WINTRY_MIX:case Weather.CONDITION_LIGHT_RAIN_SNOW:case Weather.CONDITION_HEAVY_RAIN_SNOW:
            case Weather.CONDITION_RAIN_SNOW:case Weather.CONDITION_ICE:case Weather.CONDITION_HAIL:return 4;
            case Weather.CONDITION_THUNDERSTORMS:case Weather.CONDITION_SCATTERED_THUNDERSTORMS:case Weather.CONDITION_CHANCE_OF_THUNDERSTORMS:return 5;
            case Weather.CONDITION_FOG:case Weather.CONDITION_HAZY:case Weather.CONDITION_HAZE:
            case Weather.CONDITION_MIST:case Weather.CONDITION_SMOKE:case Weather.CONDITION_DUST:case Weather.CONDITION_SAND:return 6;
            case Weather.CONDITION_WINDY:case Weather.CONDITION_TORNADO:case Weather.CONDITION_SQUALL:case Weather.CONDITION_SANDSTORM:return 7;
        }
        return 0;
    }
    function weatherText() {
        var labels=["WX","SUN","CLD","RAIN","SNOW","TSTM","FOG","WIND"];
        return labels[category(condition)]+" "+(temperature==null ? "--" : temperature.format("%.0f"))+"C";
    }
}
