import Toybox.Math;
import Toybox.Lang;

// Position/illumination formulas adapted from SunCalc 1.9.0 (BSD-2-Clause).
// Copyright (c) 2014 Vladimir Agafonkin. See assets/astronomy/LICENSE-SunCalc.txt.
// Heights and horizon crossing are astronomical approximations; screen arcs are illustrative.
module Sky {
    const PI=3.141592653589793d;const RAD=0.017453292519943295d;const E=0.40909994067971484d;
    var ready=false;var approximate=true;var phase=2;var moonPhase=0.5;var illumination=1.0;
    var sunVisible=false;var moonVisible=false;var sunProgress=0.5;var moonProgress=0.5;
    var sunAltitude=0.0;var moonAltitude=0.0;
    var _stamp=-1;var _minutes=-1;var _lat=null;var _lon=null;var _rise=null;var _set=null;
    function clamp(v,lo,hi) {return v<lo ? lo : (v>hi ? hi : v);}
    function wrap(v,period) {return v-Math.floor(v/period)*period;}
    function radians(degrees) {return wrap(degrees,360.0d)*RAD;}
    function days(stamp) {return stamp.toDouble()/86400.0d-10957.5d;}
    function validLocation(lat,lon) {return lat!=null && lon!=null && lat>=-90 && lat<=90 && lon>=-180 && lon<=180;}
    function equatorial(l as Numeric,b as Numeric) as Array<Numeric> {
        return [Math.atan2(Math.sin(l)*Math.cos(E)-Math.tan(b)*Math.sin(E),Math.cos(l)),Math.asin(clamp(Math.sin(b)*Math.cos(E)+Math.cos(b)*Math.sin(E)*Math.sin(l),-1,1))];
    }
    function solar(d as Numeric) as Array<Numeric> {
        var m=radians(357.5291d+0.98560028d*d);
        var c=RAD*(1.9148d*Math.sin(m)+0.02d*Math.sin(2*m)+0.0003d*Math.sin(3*m));
        return equatorial(m+c+102.9372d*RAD+PI,0.0d);
    }
    function lunar(d as Numeric) as Array<Numeric> {
        var l=radians(218.316d+13.176396d*d);var m=radians(134.963d+13.064993d*d);var f=radians(93.272d+13.229350d*d);
        var coords=equatorial(l+RAD*6.289d*Math.sin(m),RAD*5.128d*Math.sin(f));
        return [coords[0],coords[1],385001.0d-20905.0d*Math.cos(m)];
    }
    function moonLight(s as Array<Numeric>,m as Array<Numeric>) as Array<Numeric> {
        var phi=Math.acos(clamp(Math.sin(s[1])*Math.sin(m[1])+Math.cos(s[1])*Math.cos(m[1])*Math.cos(s[0]-m[0]),-1,1));
        var inc=Math.atan2(149598000.0d*Math.sin(phi),m[2]-149598000.0d*Math.cos(phi));
        var angle=Math.atan2(Math.cos(s[1])*Math.sin(s[0]-m[0]),Math.sin(s[1])*Math.cos(m[1])-Math.cos(s[1])*Math.sin(m[1])*Math.cos(s[0]-m[0]));
        return [(1+Math.cos(inc))/2,0.5d+0.5d*inc*(angle<0 ? -1 : 1)/PI];
    }
    // Result: geometric altitude, hour angle, progress from geometric rise to set.
    function horizontal(d as Numeric,lat as Numeric,lon as Numeric,coords as Array<Numeric>) as Array<Numeric> {
        var phi=lat*RAD;var h=wrap(radians(280.16d+360.9856235d*d)+lon*RAD-coords[0]+PI,2*PI)-PI;
        var altitude=Math.asin(clamp(Math.sin(phi)*Math.sin(coords[1])+Math.cos(phi)*Math.cos(coords[1])*Math.cos(h),-1,1));
        var cosRise=-Math.tan(phi)*Math.tan(coords[1]);
        var half=cosRise<=-1 || cosRise>=1 ? PI : Math.acos(cosRise);
        var progress=half<0.0001 ? 0.5 : clamp((h+half)/(2*half),0,1);
        return [altitude,h,progress];
    }
    function refraction(h) {
        h=h<0 ? 0 : h;
        return 0.0002967d/Math.tan(h+0.00312536d/(h+0.08901179d));
    }
    function phaseAt(alt,hourAngle) as Number {
        if(alt < -6*RAD) {return 4;}
        if(alt < 6*RAD) {return hourAngle<0 ? 1 : 3;}
        return 2;
    }
    function interval(minutes,rise,set) {
        var span=wrap(set-rise,1440.0d);var elapsed=wrap(minutes-rise,1440.0d);
        if(span<1 || elapsed>span) {return null;}
        return elapsed/span;
    }
    function refresh(stamp,minutes,lat,lon,rise,set) {
        var tick=(stamp/60).toNumber();
        if(ready && tick==_stamp && minutes==_minutes && lat==_lat && lon==_lon && rise==_rise && set==_set) {return;}
        _stamp=tick;_minutes=minutes;_lat=lat;_lon=lon;_rise=rise;_set=set;ready=true;
        var d=days(stamp);var s=solar(d);var m=lunar(d);var light=moonLight(s,m);
        illumination=light[0];moonPhase=light[1];approximate=!validLocation(lat,lon);
        if(!approximate) {
            var sun=horizontal(d,lat,lon,s);var moon=horizontal(d,lat,lon,m);
            sunAltitude=sun[0];moonAltitude=moon[0]+refraction(moon[0]);
            sunVisible=sunAltitude>=-0.833*RAD;moonVisible=moonAltitude>=0.133*RAD;
            sunProgress=sun[2];moonProgress=moon[2];phase=phaseAt(sunAltitude,sun[1]);
            // Prefer Garmin's official rise/set interval when both events are available.
            if(sunVisible && rise!=null && set!=null) {var progress=interval(minutes,rise,set);if(progress!=null) {sunProgress=progress;}}
        } else {
            // Location-free clock/phase illustration; never presented as measured rise/set times.
            var sr=rise==null ? 360 : rise;var ss=set==null ? 1080 : set;
            var sp=interval(minutes,sr,ss);sunVisible=sp!=null;sunProgress=sp==null ? 0.5 : sp;
            phase=Scene.phase(minutes,rise,set);
            var mr=wrap(360+moonPhase*1440,1440.0d);var mp=interval(minutes,mr,wrap(mr+720,1440.0d));
            moonVisible=mp!=null;moonProgress=mp==null ? 0.5 : mp;
            sunAltitude=sunVisible ? Math.sin(sunProgress*PI) : -1;
            moonAltitude=moonVisible ? Math.sin(moonProgress*PI) : -1;
        }
    }
}
