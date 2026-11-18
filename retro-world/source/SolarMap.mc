import Toybox.Graphics;
import Toybox.Math;
import Toybox.Lang;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

module SolarMap {
    var _sin as Array<Float> = [];var _cos as Array<Float> = [];
    var _lonSin as Array<Float> = [];var _lonCos as Array<Float> = [];
    var _hours as Array<Float> = [];var _font;var _buffer;var _slot=-1;var _markerX=-2;var _markerY=-2;var _weatherKind=-1;var builds=0;var skin=-1;
    function initialize() {
        _sin=[];_cos=[];_lonSin=[];_lonCos=[];_hours=[];
        for(var row=0;row<29;row++) {
            var lat=(90-row*180/28.0)*Math.PI/180;
            _sin.add(Math.sin(lat));_cos.add(Math.cos(lat));
        }
        for(var x=0;x<89;x++) {
            var lon=(-180+x*360/88.0)*Math.PI/180;
            _lonSin.add(Math.sin(lon));_lonCos.add(Math.cos(lon));_hours.add(0.0);
        }
        _font=null;skin=-1;_weatherKind=-1;
        _buffer=DeviceDrawing.buffer(89,29,DeviceProfile.SCALE);_slot=-1;_markerX=-2;_markerY=-2;
    }
    function dayOfYear(year,month,day) {
        var lengths=[31,28,31,30,31,30,31,31,30,31,30,31];
        if(year%4==0 && (year%100!=0 || year%400==0)) {lengths[1]=29;}
        var result=day;for(var i=0;i<month-1;i++) {result+=lengths[i];}return result;
    }
    function subsolarLongitude(utcSeconds) {return 180-utcSeconds/240.0;}
    function project(lat,lon) as Array<Number>? {
        if(!Environment.validCoordinates([lat,lon])) {return null;}
        return [Math.round((lon+180)*88/360.0).toNumber(),Math.round((90-lat)*28/180.0).toNumber()];
    }
    function nightRuns(threshold,hours as Array<Float>) as Array<Array<Number>> {
        var runs=[];var start=-1;
        for(var x=0;x<hours.size();x++) {
            var night=hours[x]<threshold;
            if(night && start<0) {start=x;}
            if(!night && start>=0) {runs.add([start,x-start]);start=-1;}
        }
        if(start>=0) {runs.add([start,hours.size()-start]);}
        return runs;
    }
    function shadeNight(dc,now) {
        var d=Gregorian.utcInfo(now,Time.FORMAT_SHORT);var day=dayOfYear(d.year,d.month,d.day);
        var declination=23.44*Math.sin((day-80)*2*Math.PI/365.2422)*Math.PI/180;
        var sunLon=subsolarLongitude(d.hour*3600+d.min*60+d.sec);
        var sd=Math.sin(declination);var cd=Math.cos(declination);
        // Sun's column on the 88-column grid (x=0 and x=88 are the same meridian).
        var c=(sunLon+180)*88/360.0;c=c-Math.floor(c/88)*88;
        // Copy only night spans from the stippled night glyph. Each row's night
        // side is computed directly (one or two spans) instead of testing all
        // 89 columns: the 29 x 89 scan tripped the instruction watchdog on
        // Forerunner 55 during the map rebuild.
        for(var y=0;y<29;y++) {
            var vertical=_sin[y]*sd;var horizontal=_cos[y]*cd;
            var threshold=horizontal.abs()<0.000001 ? (vertical>=0 ? -2.0 : 2.0) : -vertical/horizontal;
            var runs=nightSpans(c,threshold);
            for(var i=0;i<runs.size();i++) {
                var start=runs[i][0];var width=runs[i][1];
                dc.setClip(start,y,width,1);dc.setColor(Theme.paper,Theme.paper);dc.fillRectangle(start,y,width,1);
                dc.setColor(Theme.map,Graphics.COLOR_TRANSPARENT);dc.drawText(0,0,_font,"n",Graphics.TEXT_JUSTIFY_LEFT);
            }
        }
        dc.clearClip();
    }
    // Night columns [start,width] of one row. A column is night when the cosine of
    // its longitude distance to the sun is below `threshold`, i.e. when that
    // distance exceeds acos(threshold): the day side is one interval around the
    // sun column `c`, repeated every 88 columns.
    function nightSpans(c,threshold) as Array<Array<Number>> {
        if(threshold<=-1) {return [] as Array<Array<Number>>;}
        if(threshold>1) {return [[0,89]] as Array<Array<Number>>;}
        var w=Math.acos(threshold)*88/(2*Math.PI);
        var runs=[] as Array<Array<Number>>;var x=0;
        for(var k=-1;k<=1;k++) {
            var lo=Math.ceil(c-w+88*k).toNumber();var hi=Math.floor(c+w+88*k).toNumber();
            if(lo<0) {lo=0;}if(hi>88) {hi=88;}
            if(lo>hi) {continue;}
            if(lo>x) {runs.add([x,lo-x]);}
            if(hi+1>x) {x=hi+1;}
        }
        if(x<=88) {runs.add([x,89-x]);}
        return runs;
    }
    function marker(dc,lat,lon) {
        var p=project(lat,lon);if(p==null) {return;}
        var x=p[0];var y=p[1];
        // Compact target: 5x5 ring and center dot, with a 1-pixel white halo.
        dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillCircle(x,y,3);
        dc.setColor(Theme.ink,Graphics.COLOR_WHITE);dc.setPenWidth(1);
        dc.drawCircle(x,y,2);dc.drawPoint(x,y);
    }
    function paint(dc,now) {
        var slot=(now.value()/300).toNumber();
        var p=Environment.latitude!=null && Environment.longitude!=null ? project(Environment.latitude,Environment.longitude) : null;
        var mx=p==null ? -1 : p[0];var my=p==null ? -1 : p[1];
        var kind=Environment.category(Environment.condition);
        var buffer=DeviceDrawing.resolve(_buffer);
        var lost=(buffer has :isCached) && !buffer.isCached();
        if(lost || slot!=_slot || mx!=_markerX || my!=_markerY || kind!=_weatherKind) {
            var selected=FaceSettings.mapSkin<0 ? MapStyle.forMoment(now) : FaceSettings.mapSkin;
            if(selected!=skin) {_font=null;_font=WatchUi.loadResource(MapSkinResources.get(selected));skin=selected;}
            // One font per skin: 'd' is the day map, 'n' the stippled night map, drawn in the theme's map colour.
            var bdc=DeviceDrawing.cache(buffer.getDc(),false);bdc.clearClip();
            bdc.setColor(Theme.paper,Theme.paper);bdc.clear();
            bdc.setColor(Theme.map,Graphics.COLOR_TRANSPARENT);bdc.drawText(0,0,_font,"d",Graphics.TEXT_JUSTIFY_LEFT);shadeNight(bdc,now);
            if(FaceSettings.showMarker && Environment.latitude!=null && Environment.longitude!=null) {marker(bdc,Environment.latitude,Environment.longitude);}
            _slot=slot;_markerX=mx;_markerY=my;_weatherKind=kind;builds++;
        }
        DeviceDrawing.sprite(dc,buffer,0,17,56,89,29,1);
    }
}
