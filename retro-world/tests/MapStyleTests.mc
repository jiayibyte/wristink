import Toybox.Test;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Weather;
import Toybox.Graphics;
import Toybox.WatchUi;

(:test)
function allSkinResourcesRenderWithoutKeepingTheWholeLibraryInMemory(logger) {
    var buffer=DeviceDrawing.buffer(89,29,DeviceProfile.SCALE);var dc=DeviceDrawing.resolve(buffer).getDc();
    for(var skin=0;skin<MapStyle.COUNT;skin++) {
        var day=WatchUi.loadResource(MapSkinResources.get(skin,false));dc.drawBitmap(0,0,day);day=null;
        var night=WatchUi.loadResource(MapSkinResources.get(skin,true));dc.drawBitmap(0,0,night);night=null;
    }
    return true;
}

(:test)
function automaticSkinScheduleReachesAllSixteenAndHandlesWrappedDaylight(logger) {
    Test.assertEqual(MapStyle.minutes("06:04"),364);
    Test.assertEqual(MapStyle.minutes("17:18"),1038);
    Test.assert(MapStyle.minutes("--:--")==null);Test.assert(MapStyle.minutes("25:99")==null);
    Test.assertEqual(MapStyle.phase(370,364,1038),1);
    Test.assertEqual(MapStyle.phase(1030,364,1038),3);
    Test.assertEqual(MapStyle.phase(800,364,1038),2);
    Test.assertEqual(MapStyle.phase(1320,364,1038),0);
    Test.assertEqual(MapStyle.phase(60,1200,420),2); // Location's daylight crosses watch-local midnight.
    Test.assertEqual(MapStyle.phase(800,1200,420),0);
    Test.assertEqual(MapStyle.select(3,2,720),8);Test.assertEqual(MapStyle.select(3,0,1320),9);
    Test.assertEqual(MapStyle.select(5,2,720),14);Test.assertEqual(MapStyle.select(5,0,1320),15);
    var seen=[];for(var i=0;i<MapStyle.COUNT;i++) {seen.add(false);}
    for(var kind=0;kind<8;kind++) {
        for(var minute=0;minute<1440;minute+=5) {
            var skin=MapStyle.select(kind,MapStyle.phase(minute,364,1038),minute);
            Test.assert(skin>=0 && skin<MapStyle.COUNT);seen[skin]=true;
        }
    }
    for(var i=0;i<MapStyle.COUNT;i++) {Test.assert(seen[i]);}
    return true;
}

(:test)
function cachedPositionHandlesPolarSeasonsWhenSunTimesAreMissing(logger) {
    var lat=Environment.latitude;var lon=Environment.longitude;var condition=Environment.condition;
    var rise=Environment.sunrise;var set=Environment.sunset;
    Environment.latitude=90.0;Environment.longitude=0.0;Environment.condition=Weather.CONDITION_CLEAR;
    Environment.sunrise="--:--";Environment.sunset="--:--";
    var summer=MapStyle.forMoment(Gregorian.moment({:year=>2026,:month=>6,:day=>21,:hour=>12,:minute=>0,:second=>0}));
    var winter=MapStyle.forMoment(Gregorian.moment({:year=>2026,:month=>12,:day=>21,:hour=>12,:minute=>0,:second=>0}));
    Environment.latitude=lat;Environment.longitude=lon;Environment.condition=condition;
    Environment.sunrise=rise;Environment.sunset=set;
    Test.assert(summer!=3);Test.assertEqual(winter,3);
    return true;
}
