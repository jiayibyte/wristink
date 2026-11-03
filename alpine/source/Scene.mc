import Toybox.Math;
module Scene {
    // 1 dawn, 2 day, 3 dusk, 4 night, 5 rain, 6 volcano, 7 lightning, 8 rainbow, 9 fireworks.
    function phase(minutes,rise,set) {
        var r=rise==null ? 360 : rise;var s=set==null ? 1080 : set;
        if(r>=s) {r=360;s=1080;} // Visual fallback only; never shown as an astronomical event.
        if(minutes>=r-30 && minutes<r+45) {return 1;}
        if(minutes>=s-45 && minutes<s+30) {return 3;}
        return minutes>=r && minutes<s ? 2 : 4;
    }
    function choose(minutes) {
        if(Mode.DEMO && Mode.SCENE>0) {return Mode.SCENE;}
        if(Settings.scene>0) {return Settings.scene;}
        var base=phase(minutes,Data.rise,Data.set);
        if(!Settings.smart) {return base;}
        if(Data.battery!=null && Data.battery<=Settings.lowBattery) {return 7;}
        if(Data.stress!=null && Data.stress>=Settings.stressLimit) {return 6;}
        if(Data.rainy) {return 5;}
        if(Data.goal()) {return base==4 ? 9 : 8;}
        return base;
    }
    function moon(stamp) {var days=(stamp-947182440)/86400.0;return days-Math.floor(days/29.53059)*29.53059;}
}
