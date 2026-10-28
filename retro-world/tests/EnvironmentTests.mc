import Toybox.Test;
import Toybox.Time;
import Toybox.Weather;

class CoordinateFixture {
    var coords;
    function initialize(lat,lon) {coords=[lat,lon];}
    function toDegrees() {return coords;}
}
class FixFixture {
    var position;var accuracy;var when;
    function initialize(stamp,lat,lon,quality) {when=new Time.Moment(stamp);position=new CoordinateFixture(lat,lon);accuracy=quality;}
}
class WeatherFixture {
    var observationTime;var observationLocationPosition;
    function initialize(stamp,lat,lon) {observationTime=new Time.Moment(stamp);observationLocationPosition=new CoordinateFixture(lat,lon);}
}

(:test)
function locationUsesRecentFixThenWeatherAndNeverInventsZeroCoordinates(logger) {
    var now=20000;var fix=new FixFixture(19900,39.9,116.4,4);var wx=new WeatherFixture(19000,35.7,139.7);
    var result=Environment.chooseLocation(fix,wx,now);Test.assertEqual(result[:source],1);
    result=Environment.chooseLocation(new FixFixture(10000,39.9,116.4,4),wx,now);Test.assertEqual(result[:source],2);
    result=Environment.chooseLocation(new FixFixture(19900,39.9,116.4,0),wx,now);Test.assertEqual(result[:source],2);
    Test.assert(Environment.chooseLocation(null,new WeatherFixture(1000,35.7,139.7),now)==null);
    Test.assert(Environment.chooseLocation(new FixFixture(21000,39.9,116.4,4),null,now)==null);
    Test.assert(Environment.chooseLocation(new FixFixture(19900,91,0,4),null,now)==null);
    Test.assert(Environment.chooseLocation(null,null,now)==null);
    Test.assert(Environment.chooseLocation(new FixFixture(19900,0,0,4),null,now)!=null);
    return true;
}

(:test)
function worldCrossMatchesEquirectangularProjectionAndBounds(logger) {
    var p=SolarMap.project(39.9,116.4);Test.assertEqual(p[0],72);Test.assertEqual(p[1],8);
    p=SolarMap.project(0,0);Test.assertEqual(p[0],44);Test.assertEqual(p[1],14);
    p=SolarMap.project(90,-180);Test.assertEqual(p[0],0);Test.assertEqual(p[1],0);
    p=SolarMap.project(-90,180);Test.assertEqual(p[0],88);Test.assertEqual(p[1],28);
    Test.assert(SolarMap.project(91,0)==null);Test.assert(SolarMap.project(0,181)==null);
    Test.assert(!Environment.validCoordinates(null));Test.assert(!Environment.validCoordinates([null,116.4]));
    return true;
}

(:test)
function localWeatherThemesAndMissingDataAreDistinct(logger) {
    Test.assertEqual(Environment.category(Weather.CONDITION_CLEAR),1);
    Test.assertEqual(Environment.category(Weather.CONDITION_CLOUDY),2);
    Test.assertEqual(Environment.category(Weather.CONDITION_HEAVY_RAIN),3);
    Test.assertEqual(Environment.category(Weather.CONDITION_SNOW),4);
    Test.assertEqual(Environment.category(Weather.CONDITION_THUNDERSTORMS),5);
    Test.assertEqual(Environment.category(Weather.CONDITION_FOG),6);
    Test.assertEqual(Environment.category(Weather.CONDITION_WINDY),7);
    Test.assertEqual(Environment.category(null),0);
    Test.assertEqual(Environment.category(-999),0);
    Test.assertEqual(Environment.timeText(null),"--:--");
    return true;
}

(:test)
function environmentPollIsLowFrequencyAndRejectsFutureSamples(logger) {
    Test.assert(Environment.due(-1,1000,false));Test.assert(!Environment.due(1000,1299,false));
    Test.assert(Environment.due(1000,1300,false));Test.assert(!Environment.due(1000,1059,true));
    Test.assert(Environment.due(1000,1060,true));Test.assert(Environment.due(2000,1000,false));
    Test.assert(!Environment.fresh(new Time.Moment(1001),1000,100));
    Test.assert(Environment.fresh(new Time.Moment(900),1000,100));
    Test.assert(!Environment.fresh(new Time.Moment(899),1000,100));
    return true;
}
