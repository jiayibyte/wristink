import Toybox.Math;
import Toybox.Lang;
import Toybox.Test;

function coversColumn(runs as Array<Array<Number>>,column as Number) {
    for(var i=0;i<runs.size();i++) {if(column>=runs[i][0] && column<runs[i][0]+runs[i][1]) {return true;}}
    return false;
}

(:test)
function nightSpansFollowSolarNoonAndWrapAtDateLine(logger) {
    var noon=[];var midnight=[];
    for(var x=0;x<89;x++) {
        var longitude=-180+x*360/88.0;
        noon.add(Math.cos(longitude*Math.PI/180));
        midnight.add(Math.cos((longitude-180)*Math.PI/180));
    }
    // Equinox: Greenwich is lit at 12 UTC and dark at 00 UTC; the date line reverses.
    var a=SolarMap.nightRuns(0.0,noon);var b=SolarMap.nightRuns(0.0,midnight);
    Test.assert(!coversColumn(a,44));Test.assert(coversColumn(b,44));
    Test.assert(coversColumn(a,0));Test.assert(coversColumn(a,88));
    Test.assert(!coversColumn(b,0));Test.assert(!coversColumn(b,88));
    var count=0;
    for(var i=0;i<a.size();i++) {
        Test.assert(a[i][0]>=0 && a[i][1]>0 && a[i][0]+a[i][1]<=89);count+=a[i][1];
    }
    Test.assert(count>=42 && count<=47);
    // Thresholds outside the cosine range handle polar day/night without missing spans.
    Test.assertEqual(SolarMap.nightRuns(-2.0,noon).size(),0);
    var polar=SolarMap.nightRuns(2.0,noon);Test.assertEqual(polar.size(),1);
    Test.assertEqual(polar[0][0],0);Test.assertEqual(polar[0][1],89);
    return true;
}
