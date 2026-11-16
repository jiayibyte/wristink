import Toybox.Test;
import Toybox.Weather;
(:test)
function celestialMatchesPinnedReference(logger) {
 Sky.ready=false;Sky.refresh(1781988600,720,39.9d,116.4d,null,null);
 Test.assert((Sky.sunAltitude-(-0.00357600220167d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(-0.76228856661259d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.21281171877212d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.38422977679068d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1782014400,720,39.9d,116.4d,null,null);
 Test.assert((Sky.sunAltitude-(1.27725418615620d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(0.10877596661176d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.22314390316244d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.41602890734230d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1782042000,720,39.9d,116.4d,null,null);
 Test.assert((Sky.sunAltitude-(0.00403318807040d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(0.77471825728673d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.23410500441224d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.45014736899817d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1793642400,720,39.9d,116.4d,null,null);
 Test.assert((Sky.sunAltitude-(-0.93267594253207d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(0.36274102325980d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.77995669579030d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.40644298064402d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1773986400,720,0d,0d,null,null);
 Test.assert((Sky.sunAltitude-(-0.03498791617226d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(-0.24038345646053d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.04259137281441d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.01779711663277d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1793703600,720,-33.8688d,151.2093d,null,null);
 Test.assert((Sky.sunAltitude-(-0.49191516049743d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(-0.99467485889874d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.80589127862898d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.32799921089802d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1793710800,720,40.7128d,-74.006d,null,null);
 Test.assert((Sky.sunAltitude-(0.25377714101943d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(1.02732216343517d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.80892032264898d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.31909564958104d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1782000000,720,78.22d,15.65d,null,null);
 Test.assert((Sky.sunAltitude-(0.21013658075688d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(-0.00742685479682d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.21738721903927d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.39825942757453d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1797854400,720,78.22d,15.65d,null,null);
 Test.assert((Sky.sunAltitude-(-0.21095927151376d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(0.29246159231190d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.40385335319408d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.91150478068398d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1793026800,720,39.9d,116.4d,null,null);
 Test.assert((Sky.sunAltitude-(-1.04071367956088d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(1.11539188744512d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.51968664653894d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.99617977078033d)).abs()<0.0003);
 Sky.ready=false;Sky.refresh(1794207600,720,39.9d,116.4d,null,null);
 Test.assert((Sky.sunAltitude-(0.33755973263490d)).abs()<0.0003);
 Test.assert((Sky.moonAltitude-(0.26362320200329d)).abs()<0.0003);
 Test.assert((Sky.moonPhase-(0.98550001883586d)).abs()<0.0003);
 Test.assert((Sky.illumination-(0.00207364401369d)).abs()<0.0003);
 return true;
}

(:test)
function risingSettingAndPolarVisibility(logger) {
 Sky.ready=false;Sky.refresh(1781991000,290,39.9d,116.4d,null,null);var early=Sky.sunProgress;
 Sky.refresh(1782014400,720,39.9d,116.4d,null,null);var noon=Sky.sunProgress;
 Sky.refresh(1782042000,1180,39.9d,116.4d,null,null);Test.assert(early<noon);Test.assert(noon<Sky.sunProgress);
 Sky.refresh(1782000000,0,78.22d,15.65d,null,null);Test.assert(Sky.sunVisible);
 Sky.refresh(1797854400,720,78.22d,15.65d,null,null);Test.assert(!Sky.sunVisible);
 return true;
}
(:test)
function fallbackMoonCrossesMidnightAndDoesNotClaimLocation(logger) {
 Sky.ready=false;Sky.refresh(1793026800,1380,null,null,null,null);Test.assert(Sky.approximate);
 Test.assert(Sky.moonPhase>0.45 && Sky.moonPhase<0.55);Test.assert(Sky.moonVisible);Test.assert(!Sky.sunVisible);
 Sky.refresh(1793026800,720,null,null,null,null);Test.assert(!Sky.moonVisible);Test.assert(Sky.sunVisible);
 Test.assert(Sky.interval(10,1380,360)!=null);Test.assert(Sky.interval(720,1380,360)==null);
 Test.assert(Sky.interval(0,0,0)==null);return true;
}
(:test)
function clearWeatherHasNoCloudsAndOtherWeatherChangesMountains(logger) {
 Test.assertEqual(WeatherStyle.category(Weather.CONDITION_CLEAR),WeatherStyle.CLEAR);
 Test.assertEqual(WeatherStyle.cover(WeatherStyle.CLEAR,100),0);
 Test.assertEqual(WeatherStyle.cover(WeatherStyle.UNKNOWN,100),0);
 Test.assertEqual(WeatherStyle.category(Weather.CONDITION_HEAVY_SNOW),WeatherStyle.SNOW);
 Test.assertEqual(WeatherStyle.category(Weather.CONDITION_THUNDERSTORMS),WeatherStyle.STORM);
 Test.assertEqual(WeatherStyle.category(9999),WeatherStyle.UNKNOWN);
 return true;
}

(:test)
function moonDisplaySeparatesDayNightFromTrueAstronomy(logger) {
 // Beijing reference: both bodies are above the horizon at local noon.
 Sky.ready=false;Sky.refresh(1782014400,720,39.9d,116.4d,null,null);
 Test.assert(Sky.sunVisible && Sky.moonVisible);
 Test.assert(!Sky.showMoon(0));Test.assert(Sky.showMoon(1));
 Sky.refresh(1793026800,1380,39.9d,116.4d,null,null);
 Test.assert(!Sky.sunVisible && Sky.moonVisible);
 Test.assert(Sky.showMoon(0));Test.assert(Sky.showMoon(1));
 Sky.refresh(1781988600,290,39.9d,116.4d,null,null);
 Test.assert(!Sky.moonVisible);Test.assert(!Sky.showMoon(0));Test.assert(!Sky.showMoon(1));
 Sky.refresh(1794207600,720,39.9d,116.4d,null,null);
 Test.assert(Sky.illumination<0.005);Test.assert(!Sky.showMoon(1));
 Sky.ready=false;return true;
}
