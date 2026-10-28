import Toybox.Math;
import Toybox.Time;
import Toybox.Time.Gregorian;

module MapStyle {
    const COUNT=16;
    function minutes(text) {
        if(text==null || text.length()!=5 || !text.substring(2,3).equals(":")) {return null;}
        var h=text.substring(0,2).toNumber();var m=text.substring(3,5).toNumber();
        return h!=null && m!=null && h>=0 && h<24 && m>=0 && m<60 ? h*60+m : null;
    }
    function near(minute,point) {var d=(minute-point+1440)%1440;return d<=45 || d>=1395;}
    function phase(minute,rise,set) {
        if(rise==null || set==null || rise==set) {
            if(minute>=300 && minute<420) {return 1;}
            if(minute>=1020 && minute<1140) {return 3;}
            return minute>=420 && minute<1020 ? 2 : 0;
        }
        if(near(minute,rise)) {return 1;}
        if(near(minute,set)) {return 3;}
        var daylight=rise<set ? minute>=rise && minute<set : minute>=rise || minute<set;
        return daylight ? 2 : 0;
    }
    function select(kind,part,minute) {
        var night=part==0;
        if(kind==5) {return night ? 15 : 14;}
        if(kind==3) {return night ? 9 : 8;}
        if(kind==4) {return night ? 11 : 10;}
        if(kind==6) {return 12;}
        if(kind==7) {return 13;}
        if(kind==2) {return night ? 7 : 6;}
        if(part==1) {return 4;}
        if(part==3) {return 5;}
        if(night) {return 3;}
        if(kind==0) {return 0;}
        if(minute>=600 && minute<720) {return 1;}
        if(minute>=720 && minute<840) {return 0;}
        return 2;
    }
    function forMoment(now) {
        var local=Gregorian.info(now,Time.FORMAT_SHORT);var minute=local.hour*60+local.min;
        var rise=minutes(Environment.sunrise);var set=minutes(Environment.sunset);
        if(rise==set) {rise=null;set=null;}
        var part=phase(minute,rise,set);
        if((rise==null || set==null) && Environment.latitude!=null && Environment.longitude!=null) {
            // A last-known position also handles polar day/night when sun times are absent.
            var u=Gregorian.utcInfo(now,Time.FORMAT_SHORT);
            var day=SolarMap.dayOfYear(u.year,u.month,u.day);
            var declination=23.44*Math.sin((day-80)*2*Math.PI/365.2422)*Math.PI/180;
            var latitude=Environment.latitude*Math.PI/180;
            var sunLon=SolarMap.subsolarLongitude(u.hour*3600+u.min*60+u.sec);
            var elevation=Math.sin(latitude)*Math.sin(declination)+Math.cos(latitude)*Math.cos(declination)*Math.cos((Environment.longitude-sunLon)*Math.PI/180);
            part=elevation<0 ? 0 : 2;
        }
        return select(Environment.category(Environment.condition),part,minute);
    }
}
