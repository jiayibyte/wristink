import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Timer;
import Toybox.WatchUi;
class BatchApp extends Application.AppBase {
    (:extendedCode)
    function initialize(){AppBase.initialize();}
    (:extendedCode)
    function getInitialView(){System.println("BATCH_PREWARM free="+System.getSystemStats().freeMemory);var name=Application.loadResource(Rez.Strings.AppName);System.println("BATCH_REZ_READY free="+System.getSystemStats().freeMemory);return [new BatchView()];}
}
class BatchView extends WatchUi.View {
    var v;var engine=null;var timer;var index=0;var started=0;var minimum=9999999;var phase=0;var injected=0;var began=0;
    var cases=[["天坛",116.4102,39.8810],["颐和园",116.2735,39.9990],["延庆",115.975,40.457],["密云",116.843,40.377]];
    (:extendedCode)
    function initialize(){
        View.initialize();v=new BeijingMapView();v.gx=(116.3913-115)*MapData.XDEG;v.gy=(39.9075-39)*MapData.YDEG;v.track.recording=false;
    }
    (:extendedCode)
    function onShow(){timer=new Timer.Timer();timer.start(method(:tick),50,true);}
    (:extendedCode)
    function onHide(){if(timer!=null){timer.stop();}}
    (:extendedCode)
    function tick() as Void {
        try{
            minimum=MathHelper.minimum(minimum,System.getSystemStats().freeMemory);
            if(phase==0){
                if(engine==null){var item=cases[index];v.destination=[item[0],(item[1]-115)*MapData.XDEG,(item[2]-39)*MapData.YDEG];v.fixTime=System.getTimer();engine=new OfflineRouter(v);started=System.getTimer();System.println("BATCH_BEFORE_BEGIN free="+System.getSystemStats().freeMemory);engine.begin();}
                engine.step();minimum=MathHelper.minimum(minimum,System.getSystemStats().freeMemory);
                if(engine.finished){
                    if(engine.failed){System.println("BATCH_ROUTE_FAIL "+cases[index][0]+" "+engine.status);stop();return;}
                    System.println("BATCH_ROUTE_OK "+cases[index][0]+" points="+engine.plan.count+" meters="+engine.plan.length+" ms="+(System.getTimer()-started)+" free="+System.getSystemStats().freeMemory);
                    engine.release();engine.plan.clear();engine=null;index++;
                    if(index==cases.size()){phase=1;v.track.reset();v.track.start();v.track.lastSave=Time.now().value()+1000000;began=System.getTimer();}
                }
            }else if(phase==1){
                var at=Time.now().value();
                for(var work=0;work<100 && injected<2600;work++){v.track.addFix(v.gx+injected*8,v.gy+Math.sin(injected/40.0)*100,at+injected*5);injected++;}
                if(injected>=2600 && System.getTimer()-began>=4000){
                    var beforeElapsed=v.track.elapsedSeconds();v.track.finish();var saved=!v.track.failed;var restored=v.track.restore();var first=v.track.point(0);var last=v.track.point(v.track.count-1);
                    var valid=restored && v.track.count>0 && v.track.count<=1024 && (first[0]-v.gx).abs()<=2 && (last[0]-(v.gx+2599*8)).abs()<50;
                    System.println("BATCH_TRAIL persisted="+restored+" valid="+valid+" points="+v.track.count+" fit_save_api="+saved+" min_free="+minimum);
                    var timerValid=beforeElapsed>=4 && v.track.elapsedSeconds()>=beforeElapsed && v.track.elapsedSeconds()<=beforeElapsed+1;
                    v.track.reset();timerValid=timerValid && v.track.elapsedSeconds()==0;
                    System.println("BATCH_TIMER elapsed="+beforeElapsed+" restored_and_reset="+timerValid);
                    System.println(valid && saved && timerValid?"BATCH_ALL_OK":"BATCH_TRAIL_FAIL");stop();
                }
            }
            WatchUi.requestUpdate();
        }catch(e){System.println("BATCH_EXCEPTION "+e.getErrorMessage());stop();}
    }
    (:extendedCode)
    function stop(){timer.stop();if(engine!=null){engine.release();}System.exit();}
    function onUpdate(dc){dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.clear();BodyText.draw(dc,"SIM自动测试\n路线 "+index+"/4\n轨迹点 "+injected+"\n剩余 "+System.getSystemStats().freeMemory);}
}
