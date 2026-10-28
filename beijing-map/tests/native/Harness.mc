import Toybox.Application;
import Toybox.System;
import Toybox.Timer;
import Toybox.WatchUi;
import Toybox.Graphics;
import Toybox.Position;

class HarnessApp extends Application.AppBase {
    var view;
    function initialize(){AppBase.initialize();}
    function getInitialView(){view=new FixtureMap();return [view,new MapDelegate(view)];}
    function onStop(state){System.println("HARNESS_STOP");}
}
class FixtureMap extends BeijingMapView {
    var first=false;
    function initialize(){
        BeijingMapView.initialize();gx=(116.3913-115)*MapData.XDEG;gy=(39.9075-39)*MapData.YDEG;cx=gx;cy=gy;
        fixTime=System.getTimer();heading=1.0;track.recording=false;searchQuery="tiantan";
        metrics=new FixtureMetrics();gpsQuality=Position.QUALITY_GOOD;track.elapsedBase=3723;track.distance=3420.0;
        var valid=DashboardDraw.duration(0).equals("00:00:00") && DashboardDraw.duration(3661).equals("01:01:01") && signalBars()==4;
        gpsQuality=Position.QUALITY_USABLE;valid=valid && signalBars()==3;
        gpsQuality=Position.QUALITY_POOR;valid=valid && signalBars()==1;
        fixTime=System.getTimer()-31000;valid=valid && signalBars()==0;
        fixTime=System.getTimer();gpsQuality=Position.QUALITY_GOOD;
        var missing=new WatchMetrics();valid=valid && missing.heartText().equals("--") && missing.stepsText().equals("--") && missing.dailyText().equals("--");
        var delegate=new MapDelegate(self);delegate.onPreviousPage();valid=valid && page==1;delegate.onNextPage();valid=valid && page==0;
        valid=valid && metrics.dailyText().equals("9.88") && metrics.batteryText().equals("83%");
        System.println("DASHBOARD_VALUES duration="+DashboardDraw.duration(3661)+" km="+metrics.dailyText()+" battery="+metrics.batteryText()+" bars="+signalBars());
        System.println(valid?"DASHBOARD_CHECKS_OK":"DASHBOARD_CHECKS_FAIL");
    }
    function onShow(){
        shown=true;fixTime=System.getTimer();if(statusTimer==null){statusTimer=new Timer.Timer();}
        if(first){first=false;statusTimer.start(method(:openSearch),150,false);}
        else if(pendingDestination){pendingDestination=false;statusTimer.start(method(:openDestination),100,false);}
        else{statusTimer.start(method(:heartbeat),1000,true);}
    }
    function openSearch() as Void {
        releaseMap();var entry=new OfflineSearchView(self);entry.start("tiantan");
        WatchUi.pushView(entry,new SearchInputDelegate(entry),WatchUi.SLIDE_UP);
    }
    function heartbeat() as Void {fixTime=System.getTimer();WatchUi.requestUpdate();}
    function onUpdate(dc){
        BeijingMapView.onUpdate(dc);
        if(page==0){dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.drawText(74,2,Graphics.FONT_XTINY,"SIM",Graphics.TEXT_JUSTIFY_CENTER);}
        else{dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.drawText(88,142,Graphics.FONT_XTINY,"SIM",Graphics.TEXT_JUSTIFY_CENTER);DashboardDraw.tabs(dc,page);}
        if(nav.active){System.println("HARNESS_ROUTE_OK points="+nav.count+" distance="+nav.length+" free="+System.getSystemStats().freeMemory);}
    }
}

// Synthetic values for visual inspection; never used by the production entry.
class FixtureMetrics extends WatchMetrics {
    function initialize(){WatchMetrics.initialize();steps=12345;dailyMetres=9876.0;battery=83.0;heartRate=76;}
    function refresh(){}
    function start(){}
    function stop(){}
}
