import Toybox.Math;
module Scene {
    // Keep persisted IDs 0..12. 13 aurora; 14..17 pinned holiday backgrounds.
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
        if(Settings.weatherLink==0) {
            if(Data.weather==WeatherStyle.SNOW) {return 10;}
            if(Data.weather==WeatherStyle.FOG) {return 12;}
            if(Data.weather==WeatherStyle.CLOUDY) {return 11;}
            if(Data.rainy) {return 5;}
        }
        if(Data.goal()) {return base==4 ? 9 : 8;}
        return base;
    }
    function effectiveWeather(scene) {
        if(scene==5) {return WeatherStyle.RAIN;}if(scene==10) {return WeatherStyle.SNOW;}
        if(scene==11) {return WeatherStyle.CLOUDY;}if(scene==12) {return WeatherStyle.FOG;}
        if(scene==7 && (Settings.scene==7 || (Mode.DEMO && Mode.SCENE==7))) {return WeatherStyle.STORM;}
        return Settings.weatherLink==0 ? Data.weather : WeatherStyle.CLEAR;
    }
    function clouds(scene) {
        var w=effectiveWeather(scene);return w==Data.weather && Settings.weatherLink==0 ? Data.cloudCover : WeatherStyle.cover(w,null);
    }
    function artKey(scene) {
        var light=scene>=1 && scene<=4 ? scene : Sky.phase;
        return (scene==13 ? 100 : 0)+(light-1)*5+WeatherStyle.theme(effectiveWeather(scene),clouds(scene))+1;
    }
    function holiday(year,month,day) {
        var selected=Mode.DEMO && Mode.SCENE>0 ? Mode.SCENE : Settings.scene;
        if(selected>=14 && selected<=17) {return selected-13;}
        // A manually pinned background always wins over the auto holiday calendar.
        return selected==0 ? Festival.choose(year,month,day,Settings.festival) : 0;
    }
    function resourceKey(scene,holiday) {return artKey(scene)+(scene==13 ? 0 : holiday*20);}
    function moon(stamp) {var d=Sky.days(stamp);return Sky.moonLight(Sky.solar(d),Sky.lunar(d))[1]*29.53059;}
}
