import Toybox.Math;
module Scene {
    // 1 dawn, 2 day, 3 dusk, 4 night, 5 rain, 6 warm accent, 7 low-battery/storm, 8 rainbow, 9 fireworks, 10 snow, 11 overcast, 12 fog.
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
        var base=Sky.ready ? Sky.phase : phase(minutes,Data.rise,Data.set);
        if(!Settings.smart) {return base;}
        if(Data.battery!=null && Data.battery<=Settings.lowBattery) {return 7;}
        if(Data.stress!=null && Data.stress>=Settings.stressLimit) {return 6;}
        if(Data.weather==WeatherStyle.SNOW) {return 10;}
        if(Data.weather==WeatherStyle.FOG) {return 12;}
        if(Data.weather==WeatherStyle.CLOUDY) {return 11;}
        if(Data.rainy) {return 5;}
        if(Data.goal()) {return base==4 ? 9 : 8;}
        return base;
    }
    function effectiveWeather(scene) {
        if(scene==5) {return WeatherStyle.RAIN;}if(scene==10) {return WeatherStyle.SNOW;}
        if(scene==11) {return WeatherStyle.CLOUDY;}if(scene==12) {return WeatherStyle.FOG;}
        if(scene==7 && (Settings.scene==7 || (Mode.DEMO && Mode.SCENE==7))) {return WeatherStyle.STORM;}
        return Data.weather;
    }
    function clouds(scene) {
        var w=effectiveWeather(scene);return w==Data.weather ? Data.cloudCover : WeatherStyle.cover(w,null);
    }
    function artKey(scene) {
        var light=scene>=1 && scene<=4 ? scene : Sky.phase;
        return (light-1)*5+WeatherStyle.theme(effectiveWeather(scene),clouds(scene))+1;
    }
    function moon(stamp) {var d=Sky.days(stamp);return Sky.moonLight(Sky.solar(d),Sky.lunar(d))[1]*29.53059;}
}
