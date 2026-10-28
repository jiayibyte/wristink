import Toybox.Graphics;
import Toybox.Weather;

module WeatherIcons {
    const UNKNOWN = 0;
    const CLEAR = 1;
    const PARTLY = 2;
    const CLOUDY = 3;
    const RAIN = 4;
    const SNOW = 5;
    const THUNDER = 6;
    const MIX = 7;
    const FOG = 8;
    const WIND = 9;
    const HAIL = 10;
    var current = UNKNOWN;

    // Map Garmin's cached weather condition, including shower/snow variants.
    function category(condition) {
        switch (condition) {
            case Weather.CONDITION_CLEAR: case Weather.CONDITION_FAIR: return CLEAR;
            case Weather.CONDITION_PARTLY_CLOUDY: case Weather.CONDITION_PARTLY_CLEAR:
            case Weather.CONDITION_MOSTLY_CLEAR: case Weather.CONDITION_THIN_CLOUDS: return PARTLY;
            case Weather.CONDITION_MOSTLY_CLOUDY: case Weather.CONDITION_CLOUDY: return CLOUDY;
            case Weather.CONDITION_RAIN: case Weather.CONDITION_LIGHT_RAIN: case Weather.CONDITION_HEAVY_RAIN:
            case Weather.CONDITION_SCATTERED_SHOWERS: case Weather.CONDITION_LIGHT_SHOWERS: case Weather.CONDITION_SHOWERS:
            case Weather.CONDITION_HEAVY_SHOWERS: case Weather.CONDITION_CHANCE_OF_SHOWERS:
            case Weather.CONDITION_CLOUDY_CHANCE_OF_RAIN: case Weather.CONDITION_DRIZZLE:
            case Weather.CONDITION_UNKNOWN_PRECIPITATION: return RAIN;
            case Weather.CONDITION_SNOW: case Weather.CONDITION_LIGHT_SNOW: case Weather.CONDITION_HEAVY_SNOW:
            case Weather.CONDITION_CHANCE_OF_SNOW: case Weather.CONDITION_CLOUDY_CHANCE_OF_SNOW:
            case Weather.CONDITION_FLURRIES: return SNOW;
            case Weather.CONDITION_THUNDERSTORMS: case Weather.CONDITION_SCATTERED_THUNDERSTORMS:
            case Weather.CONDITION_CHANCE_OF_THUNDERSTORMS: return THUNDER;
            case Weather.CONDITION_WINTRY_MIX: case Weather.CONDITION_LIGHT_RAIN_SNOW: case Weather.CONDITION_HEAVY_RAIN_SNOW:
            case Weather.CONDITION_RAIN_SNOW: case Weather.CONDITION_CHANCE_OF_RAIN_SNOW:
            case Weather.CONDITION_CLOUDY_CHANCE_OF_RAIN_SNOW: case Weather.CONDITION_FREEZING_RAIN:
            case Weather.CONDITION_SLEET: case Weather.CONDITION_ICE_SNOW: return MIX;
            case Weather.CONDITION_FOG: case Weather.CONDITION_HAZY: case Weather.CONDITION_HAZE:
            case Weather.CONDITION_MIST: case Weather.CONDITION_DUST: case Weather.CONDITION_SMOKE:
            case Weather.CONDITION_SAND: case Weather.CONDITION_VOLCANIC_ASH: return FOG;
            case Weather.CONDITION_WINDY: case Weather.CONDITION_TORNADO: case Weather.CONDITION_SQUALL:
            case Weather.CONDITION_SANDSTORM: case Weather.CONDITION_HURRICANE: case Weather.CONDITION_TROPICAL_STORM: return WIND;
            case Weather.CONDITION_HAIL: case Weather.CONDITION_ICE: return HAIL;
        }
        // Missing or unknown conditions must not imply that the sky is sunny.
        return UNKNOWN;
    }

    function draw(dc, x, y, ink, paper) {
        dc.setColor(ink, paper);
        var rows = WeatherGlyphs.pixels(current);
        for (var row = 0; row < 15; row++) {
            for (var col = 0; col < 15; col++) {
                if ((rows[row] & (1 << col)) != 0) { dc.drawPoint(x + col, y + row); }
            }
        }
    }
}
