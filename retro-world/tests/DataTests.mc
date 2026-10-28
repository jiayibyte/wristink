import Toybox.Test;
import Toybox.Time;

class BatteryDaysFixture {
    var battery=86;var batteryInDays;
    function initialize(days) {batteryInDays=days;}
}
class PercentOnlyFixture {
    var battery=86;
    function initialize() {}
}

(:test)
function batteryDaysUseGarminEstimateWithoutConvertingPercent(logger) {
    Test.assertEqual(LiveData.remainingDays(new BatteryDaysFixture(24.3)),24.3);
    Test.assertEqual(LiveData.remainingDays(new BatteryDaysFixture(0)),0);
    Test.assert(LiveData.remainingDays(new BatteryDaysFixture(-1))==null);
    Test.assert(LiveData.remainingDays(new BatteryDaysFixture(null))==null);
    Test.assert(LiveData.remainingDays(new PercentOnlyFixture())==null);
    Test.assert(LiveData.remainingDays(null)==null);
    Test.assertEqual(LiveData.daysText(24.3),"24.3");
    Test.assertEqual(LiveData.daysText(0),"0.0");
    Test.assertEqual(LiveData.daysText(null),"--");
    Test.assertEqual(LiveData.daysText(-1),"--");
    return true;
}

class HeartSampleFixture {
    var when;var heartRate;
    function initialize(stamp,value) {when=new Time.Moment(stamp);heartRate=value;}
}

(:test)
function missingAndStaleHeartMustNotBecomeLive(logger) {
    Test.assert(LiveData.recentHeart(null,1000)==null);
    Test.assert(LiveData.recentHeart(new HeartSampleFixture(819,76),1000)==null);
    Test.assert(LiveData.recentHeart(new HeartSampleFixture(1001,76),1000)==null);
    Test.assertEqual(LiveData.recentHeart(new HeartSampleFixture(820,76),1000),76);
    Test.assert(!LiveData.heartValid(0));Test.assert(!LiveData.heartValid(301));
    Test.assert(!LiveData.heartValid(null));Test.assert(LiveData.heartValid(76));
    return true;
}

(:test)
function garminDistanceUsesCentimetersAndMissingIsDistinctFromZero(logger) {
    Test.assertEqual(LiveData.distanceText(642000),"6.42");
    Test.assertEqual(LiveData.distanceText(0),"0.00");
    Test.assertEqual(LiveData.distanceText(null),"--");
    Test.assertEqual(LiveData.distanceText(-1),"--");
    Test.assertEqual(LiveData.numeric(null),"--");
    Test.assertEqual(LiveData.numeric(-42),"-42");
    Test.assert(LiveData.nonnegative(-1)==null);
    Test.assertEqual(LiveData.nonnegative(0),0);
    return true;
}

(:test)
function dayNightBoundaryUsesUtcAndLeapYears(logger) {
    Test.assertEqual(SolarMap.dayOfYear(2024,3,1),61);
    Test.assertEqual(SolarMap.dayOfYear(2026,3,1),60);
    Test.assertEqual(SolarMap.dayOfYear(2100,3,1),60);
    Test.assertEqual(SolarMap.dayOfYear(2000,3,1),61);
    Test.assertEqual(SolarMap.dayOfYear(2026,12,31),365);
    Test.assertEqual(SolarMap.subsolarLongitude(43200),0.0);
    Test.assertEqual(SolarMap.subsolarLongitude(0),180.0);
    Test.assertEqual(SolarMap.subsolarLongitude(21600),90.0);
    return true;
}
