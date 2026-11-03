import Toybox.Application;
import Toybox.Lang;
module Settings {
    var timeFormat=0;var scene=0;var circle=0;var smart=true;var seconds=true;
    var lowBattery=20;var stressLimit=75;var left=0;var middle=1;var right=2;
    function number(key,fallback,lo,hi) {
        var v=Application.Properties.getValue(key);
        return v instanceof Number && v>=lo && v<=hi ? v : fallback;
    }
    function flag(key,fallback) {var v=Application.Properties.getValue(key);return v instanceof Boolean ? v : fallback;}
    function load() {
        timeFormat=number("TimeFormat",0,0,2);scene=number("Scene",0,0,9);circle=number("Circle",0,0,2);
        lowBattery=number("LowBattery",20,5,50);stressLimit=number("StressLimit",75,25,100);
        left=number("Left",0,0,5);middle=number("Middle",1,0,5);right=number("Right",2,0,5);
        smart=flag("Smart",true);seconds=flag("Seconds",true);
    }
    function is24(system) {return timeFormat==0 ? system : timeFormat==2;}
    function shownHour(h,is24) {return is24 ? h : (h%12==0 ? 12 : h%12);}
}
