import Toybox.Math;
import Toybox.Time;
import Toybox.Time.Gregorian;

// NOAA fractional-year approximation, used only when Garmin's sunrise/sunset
// API is absent. No GPS/network requests. Polar no-event results remain null.
// https://gml.noaa.gov/grad/solcalc/solareqns.PDF
module SolarTimes {
    function utcMinutes(year,month,day,lat,lon,rise) {
        if(!Environment.validCoordinates([lat,lon])) {return null;}
        var leap=year%4==0 && (year%100!=0 || year%400==0);
        var g=2*Math.PI/(leap ? 366 : 365)*(SolarMap.dayOfYear(year,month,day)-1);
        var eq=229.18*(0.000075+0.001868*Math.cos(g)-0.032077*Math.sin(g)-0.014615*Math.cos(2*g)-0.040849*Math.sin(2*g));
        var dec=0.006918-0.399912*Math.cos(g)+0.070257*Math.sin(g)-0.006758*Math.cos(2*g)+0.000907*Math.sin(2*g)-0.002697*Math.cos(3*g)+0.00148*Math.sin(3*g);
        var rad=lat*Math.PI/180;var divisor=Math.cos(rad)*Math.cos(dec);
        if(divisor.abs()<0.000001) {return null;}
        var cosine=(Math.cos(90.833*Math.PI/180)-Math.sin(rad)*Math.sin(dec))/divisor;
        if(cosine < -1 || cosine > 1) {return null;}
        var angle=Math.acos(cosine)*180/Math.PI;
        return 720-4*(lon+(rise ? angle : -angle))-eq;
    }
    function event(now,lat,lon,rise) {
        var d=Gregorian.info(now,Time.FORMAT_SHORT);
        var minutes=utcMinutes(d.year,d.month,d.day,lat,lon,rise);
        if(minutes==null) {return null;}
        // Gregorian.moment interprets fields as UTC. Keep the signed minutes
        // so events on adjacent UTC dates still convert to local time correctly.
        var midnight=Gregorian.moment({:year=>d.year,:month=>d.month,:day=>d.day,:hour=>0,:minute=>0,:second=>0});
        return new Time.Moment(midnight.value()+Math.round(minutes*60).toNumber());
    }
}
