import Toybox.Weather;
module WeatherStyle {
    const UNKNOWN=0;const CLEAR=1;const PARTLY=2;const CLOUDY=3;const RAIN=4;const SNOW=5;const STORM=6;const FOG=7;
    function category(c) {
        if(c==null) {return UNKNOWN;}
        switch(c) {
            case Weather.CONDITION_CLEAR:return CLEAR;
            case Weather.CONDITION_PARTLY_CLEAR:case Weather.CONDITION_MOSTLY_CLEAR:case Weather.CONDITION_PARTLY_CLOUDY:return PARTLY;
            case Weather.CONDITION_MOSTLY_CLOUDY:case Weather.CONDITION_CLOUDY:return CLOUDY;
            case Weather.CONDITION_THUNDERSTORMS:case Weather.CONDITION_SCATTERED_THUNDERSTORMS:case Weather.CONDITION_CHANCE_OF_THUNDERSTORMS:return STORM;
            case Weather.CONDITION_RAIN:case Weather.CONDITION_LIGHT_RAIN:case Weather.CONDITION_HEAVY_RAIN:case Weather.CONDITION_SCATTERED_SHOWERS:
            case Weather.CONDITION_LIGHT_SHOWERS:case Weather.CONDITION_SHOWERS:case Weather.CONDITION_HEAVY_SHOWERS:case Weather.CONDITION_CHANCE_OF_SHOWERS:case Weather.CONDITION_DRIZZLE:return RAIN;
            case Weather.CONDITION_SNOW:case Weather.CONDITION_LIGHT_SNOW:case Weather.CONDITION_HEAVY_SNOW:case Weather.CONDITION_WINTRY_MIX:
            case Weather.CONDITION_LIGHT_RAIN_SNOW:case Weather.CONDITION_HEAVY_RAIN_SNOW:case Weather.CONDITION_RAIN_SNOW:case Weather.CONDITION_ICE:case Weather.CONDITION_HAIL:return SNOW;
            case Weather.CONDITION_FOG:case Weather.CONDITION_HAZY:case Weather.CONDITION_HAZE:case Weather.CONDITION_MIST:case Weather.CONDITION_SMOKE:case Weather.CONDITION_DUST:case Weather.CONDITION_SAND:return FOG;
        }
        return UNKNOWN;
    }
    function cover(kind,value) {
        if(kind==CLEAR || kind==UNKNOWN) {return 0;}
        if(kind==CLOUDY || kind==RAIN || kind==SNOW || kind==STORM || kind==FOG) {return value==null ? 90 : Sky.clamp(value,70,100);}
        return value==null ? 35 : Sky.clamp(value,10,65);
    }
    function theme(kind,clouds) {
        if(kind==RAIN || kind==STORM) {return 2;}if(kind==SNOW) {return 3;}if(kind==FOG) {return 4;}
        return kind==CLOUDY || clouds>=65 ? 1 : 0;
    }
}
