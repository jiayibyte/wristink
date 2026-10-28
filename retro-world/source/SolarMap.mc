import Toybox.Graphics;
import Toybox.Math;
import Toybox.Lang;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

module SolarMap {
    var _sin as Array<Float> = [];var _cos as Array<Float> = [];
    var _lonSin as Array<Float> = [];var _lonCos as Array<Float> = [];
    var _map;var _night;var _buffer;var _slot=-1;var _markerX=-2;var _markerY=-2;var _weatherKind=-1;var builds=0;var skin=-1;
    function initialize() {
        _sin=[];_cos=[];_lonSin=[];_lonCos=[];
        for(var row=0;row<29;row++) {
            var lat=(90-row*180/28.0)*Math.PI/180;
            _sin.add(Math.sin(lat));_cos.add(Math.cos(lat));
        }
        for(var x=0;x<89;x++) {
            var lon=(-180+x*360/88.0)*Math.PI/180;
            _lonSin.add(Math.sin(lon));_lonCos.add(Math.cos(lon));
        }
        _map=null;_night=null;skin=-1;_weatherKind=-1;
        _buffer=Graphics.createBufferedBitmap({:width=>89,:height=>29}).get();_slot=-1;_markerX=-2;_markerY=-2;
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
        var a=sunLon*Math.PI/180;var cs=Math.cos(a);var sn=Math.sin(a);var hours=[];
        for(var x=0;x<89;x++) {hours.add(_lonCos[x]*cs+_lonSin[x]*sn);}
        // Copy only night spans from the prebaked stippled bitmap. No per-pixel
        // drawing/trigonometry and no animation work from a seconds callback.
        for(var y=0;y<29;y++) {
            var vertical=_sin[y]*sd;var horizontal=_cos[y]*cd;
            var threshold=horizontal.abs()<0.000001 ? (vertical>=0 ? -2.0 : 2.0) : -vertical/horizontal;
            var runs=nightRuns(threshold,hours);
            for(var i=0;i<runs.size();i++) {
                dc.setClip(runs[i][0],y,runs[i][1],1);dc.drawBitmap(0,0,_night);
            }
        }
        dc.clearClip();
    }
    function marker(dc,lat,lon) {
        var p=project(lat,lon);if(p==null) {return;}
        var x=p[0];var y=p[1];
        // Compact target: 5x5 ring and center dot, with a 1-pixel white halo.
        dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillCircle(x,y,3);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.setPenWidth(1);
        dc.drawCircle(x,y,2);dc.drawPoint(x,y);
    }
    function paint(dc,now) {
        var slot=(now.value()/300).toNumber();
        var p=Environment.latitude!=null && Environment.longitude!=null ? project(Environment.latitude,Environment.longitude) : null;
        var mx=p==null ? -1 : p[0];var my=p==null ? -1 : p[1];
        var kind=Environment.category(Environment.condition);
        if(slot!=_slot || mx!=_markerX || my!=_markerY || kind!=_weatherKind) {
            var selected=MapStyle.forMoment(now);
            if(selected!=skin) {
                _map=null;_night=null;
                _map=WatchUi.loadResource(MapSkinResources.get(selected,false));
                _night=WatchUi.loadResource(MapSkinResources.get(selected,true));skin=selected;
            }
            var bdc=_buffer.getDc();bdc.clearClip();bdc.drawBitmap(0,0,_map);shadeNight(bdc,now);
            if(Environment.latitude!=null && Environment.longitude!=null) {marker(bdc,Environment.latitude,Environment.longitude);}
            _slot=slot;_markerX=mx;_markerY=my;_weatherKind=kind;builds++;
        }
        dc.setClip(17,56,89,29);dc.drawBitmap(17,56,_buffer);dc.clearClip();
    }
}
