import Toybox.System;
import Toybox.Time;
import Toybox.Weather;
import Toybox.WatchUi;
(:diagnostic)
class BenchClock {
    var hour=22;var min=8;var sec=0;
    function initialize(s) {sec=s;}
}
(:diagnostic)
module Benchmark {
    var ready=false;var done=false;var minimum=2147483647;var frames=0;var worst=0;var elapsed=0;
    var _start=0;var _initial=0;var _heavyWorst=0;var _heavyMs=0;var _awakeWorst=0;var _awakeMs=0;var _maps=0;var _reads=0;var _awakeMaps=0;var _awakeReads=0;
    function sample(view,dc,stamp,second) {
        var before=System.getTimer();view.updateAt(dc,new Time.Moment(stamp),new BenchClock(second));
        var dt=System.getTimer()-before;elapsed+=dt;frames++;if(dt>worst) {worst=dt;}
        var free=System.getSystemStats().freeMemory;if(free<minimum) {minimum=free;}
    }
    function run(view,dc) {
        // Exactly one real drawing update per callback, including asleep frames.
        if(frames==0) {_start=Time.now().value();_start-=_start%300;_initial=System.getSystemStats().freeMemory;}
        if(frames<3) {
            var kinds=[Weather.CONDITION_CLEAR,Weather.CONDITION_RAIN,Weather.CONDITION_SNOW];
            var t=_start+frames*600;Environment._readAt=t;Environment.temperature=24;Environment.condition=kinds[frames];
            Environment.latitude=39.9;Environment.longitude=116.4;Environment.sunrise="06:04";Environment.sunset="17:18";
            sample(view,dc,t,frames);
            if(frames==3) {_heavyWorst=worst;_heavyMs=elapsed;worst=0;elapsed=0;}
        } else if(frames<6) {
            var second=frames-3;sample(view,dc,_start+1800+second,second);
            if(second==0) {_maps=SolarMap.builds;_reads=Environment.reads;}
            if(frames==6) {_awakeWorst=worst;_awakeMs=elapsed;_awakeMaps=SolarMap.builds-_maps;_awakeReads=Environment.reads-_reads;worst=0;elapsed=0;}
        } else {
            if(frames==6) {view._sleeping=true;if(DeviceProfile.COLOR) {view._minute=-1;}}
            sample(view,dc,_start+2400+(frames-6)*60,0);
            if(frames==8) {
                var stats=System.getSystemStats();
                System.println("PERF_RESULT version=2.0.0 width="+DeviceProfile.WIDTH+" height="+DeviceProfile.HEIGHT+" dc_width="+dc.getWidth()+" dc_height="+dc.getHeight()+" color="+DeviceProfile.COLOR+" frames="+frames+" total="+stats.totalMemory+" initial_free="+_initial+" min_free="+minimum+" final_free="+stats.freeMemory+" heavy_max_ms="+_heavyWorst+" heavy_total_ms="+_heavyMs+" awake_max_ms="+_awakeWorst+" awake_total_ms="+_awakeMs+" sleep_max_ms="+worst+" sleep_total_ms="+elapsed+" awake_map_builds="+_awakeMaps+" awake_weather_reads="+_awakeReads);
                view._sleeping=false;view._minute=-1;view._environmentWake=true;Environment._readAt=-1;LiveData.heartAt=-1;done=true;
            }
        }
        WatchUi.requestUpdate();
    }
}
