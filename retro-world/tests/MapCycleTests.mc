import Toybox.Math;
import Toybox.Lang;
import Toybox.Test;

function coversColumn(runs as Array<Array<Number>>,column as Number) {
    for(var i=0;i<runs.size();i++) {if(column>=runs[i][0] && column<runs[i][0]+runs[i][1]) {return true;}}
    return false;
}

(:test)
function directNightSpansMatchTheColumnScan(logger) {
    // The direct per-row computation must shade the same columns as testing each
    // column (the scan it replaced), up to rounding at the two boundaries.
    for(var hour=0;hour<24;hour+=3) {
        var sunLon=SolarMap.subsolarLongitude(hour*3600);var a=sunLon*Math.PI/180;
        var hours=[] as Array<Float>;
        for(var x=0;x<89;x++) {var lon=(-180+x*360/88.0)*Math.PI/180;hours.add(Math.cos(lon)*Math.cos(a)+Math.sin(lon)*Math.sin(a));}
        var c=(sunLon+180)*88/360.0;c=c-Math.floor(c/88)*88;
        var thresholds=[-0.9,-0.5,0.0,0.3,0.8];
        for(var t=0;t<thresholds.size();t++) {
            var scan=SolarMap.nightRuns(thresholds[t],hours);var direct=SolarMap.nightSpans(c,thresholds[t]);
            var a1=0;var a2=0;
            for(var i=0;i<scan.size();i++) {a1+=scan[i][1];}
            for(var i=0;i<direct.size();i++) {a2+=direct[i][1];}
            Test.assert((a1-a2).abs()<=2);
        }
    }
    Test.assertEqual(SolarMap.nightSpans(0.0,-2.0).size(),0);
    Test.assertEqual(SolarMap.nightSpans(0.0,2.0)[0][1],89);
    return true;
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
