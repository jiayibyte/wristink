import Toybox.Weather;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Math;

// Atlas order follows the official Garmin support images; independent of map skins.
module WeatherIcons {
    const COUNT=13;
    function select(value,night) {
        if(value==null) {return 10;}
        switch(value) {
            case Weather.CONDITION_CLEAR:case Weather.CONDITION_FAIR:case Weather.CONDITION_MOSTLY_CLEAR:return night ? 1 : 0;
            case Weather.CONDITION_PARTLY_CLEAR:case Weather.CONDITION_PARTLY_CLOUDY:case Weather.CONDITION_THIN_CLOUDS:return night ? 6 : 5;
            case Weather.CONDITION_CLOUDY:case Weather.CONDITION_MOSTLY_CLOUDY:return 2;
            case Weather.CONDITION_FOG:case Weather.CONDITION_HAZE:case Weather.CONDITION_HAZY:case Weather.CONDITION_MIST:
            case Weather.CONDITION_SMOKE:case Weather.CONDITION_DUST:case Weather.CONDITION_SAND:case Weather.CONDITION_VOLCANIC_ASH:return 3;
            case Weather.CONDITION_HAIL:return 4;
            case Weather.CONDITION_RAIN:case Weather.CONDITION_LIGHT_RAIN:case Weather.CONDITION_HEAVY_RAIN:
            case Weather.CONDITION_SHOWERS:case Weather.CONDITION_LIGHT_SHOWERS:case Weather.CONDITION_HEAVY_SHOWERS:
            case Weather.CONDITION_SCATTERED_SHOWERS:case Weather.CONDITION_CHANCE_OF_SHOWERS:
            case Weather.CONDITION_CLOUDY_CHANCE_OF_RAIN:case Weather.CONDITION_DRIZZLE:return 7;
            case Weather.CONDITION_SNOW:case Weather.CONDITION_LIGHT_SNOW:case Weather.CONDITION_HEAVY_SNOW:
            case Weather.CONDITION_FLURRIES:case Weather.CONDITION_CHANCE_OF_SNOW:case Weather.CONDITION_CLOUDY_CHANCE_OF_SNOW:return 8;
            case Weather.CONDITION_THUNDERSTORMS:case Weather.CONDITION_SCATTERED_THUNDERSTORMS:case Weather.CONDITION_CHANCE_OF_THUNDERSTORMS:return 9;
            case Weather.CONDITION_WINDY:case Weather.CONDITION_TORNADO:case Weather.CONDITION_SQUALL:
            case Weather.CONDITION_SANDSTORM:case Weather.CONDITION_HURRICANE:case Weather.CONDITION_TROPICAL_STORM:return 11;
            case Weather.CONDITION_WINTRY_MIX:case Weather.CONDITION_RAIN_SNOW:case Weather.CONDITION_LIGHT_RAIN_SNOW:
            case Weather.CONDITION_HEAVY_RAIN_SNOW:case Weather.CONDITION_CHANCE_OF_RAIN_SNOW:case Weather.CONDITION_CLOUDY_CHANCE_OF_RAIN_SNOW:
            case Weather.CONDITION_SLEET:case Weather.CONDITION_ICE:case Weather.CONDITION_ICE_SNOW:case Weather.CONDITION_FREEZING_RAIN:return 12;
        }
        return 10;
    }
    function nightAt(minute,rise,set) {
        if(rise==null || set==null || rise==set) {return minute<360 || minute>=1080;}
        return !(rise<set ? minute>=rise && minute<set : minute>=rise || minute<set);
    }
    function isNight(now) {
        var local=Gregorian.info(now,Time.FORMAT_SHORT);
        var rise=MapStyle.minutes(Environment.sunrise);var set=MapStyle.minutes(Environment.sunset);
        if((rise==null || set==null || rise==set) && Environment.latitude!=null && Environment.longitude!=null) {
            var u=Gregorian.utcInfo(now,Time.FORMAT_SHORT);
            var day=SolarMap.dayOfYear(u.year,u.month,u.day);
            var dec=23.44*Math.sin((day-80)*2*Math.PI/365.2422)*Math.PI/180;
            var lat=Environment.latitude*Math.PI/180;
            var sunLon=SolarMap.subsolarLongitude(u.hour*3600+u.min*60+u.sec);
            return Math.sin(lat)*Math.sin(dec)+Math.cos(lat)*Math.cos(dec)*Math.cos((Environment.longitude-sunLon)*Math.PI/180)<0;
        }
        return nightAt(local.hour*60+local.min,rise,set);
    }
    function current(now) {
        // Solar math only matters for the two icon families with night variants.
        var day=select(Environment.condition,false);
        return day==0 || day==5 ? select(Environment.condition,isNight(now)) : day;
    }
}
