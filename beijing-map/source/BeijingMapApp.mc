import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.Position;
import Toybox.System;
import Toybox.Timer;
import Toybox.Time;
import Toybox.WatchUi;

class BeijingMapApp extends Application.AppBase {
    var view=null;
    (:extendedCode)
    function initialize() { AppBase.initialize(); }
    (:extendedCode)
    function getInitialView() { var appTitle=Application.loadResource(Rez.Strings.AppName);view=new BeijingMapView(); return [view,new MapDelegate(view)]; }
    (:extendedCode)
    function onStop(state) {System.println("APP_STOP");if(view!=null){view.shutdown();} }
}

module Places {
    // Approximate browse centres, not navigation destinations.
    var areas as Array<Array> = [
        ["东城",116.418,39.928], ["西城",116.366,39.913],
        ["朝阳",116.486,39.921], ["海淀",116.298,39.959],
        ["丰台",116.286,39.858], ["石景山",116.222,39.906],
        ["门头沟",116.102,39.941], ["房山",116.143,39.749],
        ["通州",116.657,39.909], ["顺义",116.655,40.130],
        ["昌平",116.231,40.221], ["大兴",116.338,39.729],
        ["怀柔",116.631,40.317], ["平谷",117.121,40.140],
        ["密云",116.843,40.377], ["延庆",115.975,40.457]
    ];
}

class BeijingMapView extends WatchUi.View {
    var cx; var cy;var page=0;var metrics;var gpsQuality=Position.QUALITY_NOT_AVAILABLE;
    var pendingDestination=false;var nav;var destination as Array=[];var searchQuery="";
    var gx=null; var gy=null;var heading=null;var fixStamp=null;var shown=false;var stopped=false;var track;
    var mode=0; var follow=true; var zoom=2;
    var scales as Array<Float> = [1.5,3.0,6.0,12.0,24.0]; // metres per pixel
    var fixTime=0; var status="浏览";
    var lastDraw=0; var frames=0;
    var bitmap=null; var queue as Array<Array> = []; var qIndex=0;
    
    var activePacked=null;var activeOffset=8;var activeTx=0;var activeTy=0;
    var renderX=null;var renderY=null;var renderZoom=-1;
    var paintTimer=null;var painting=false;var statusTimer=null;
    (:extendedCode)
    function initialize() {
        View.initialize();track=new TrailRecorder();nav=new RoutePlan();metrics=new WatchMetrics();var q=Application.Storage.getValue("lastQuery");if(q!=null){searchQuery=q as String;}
        setCentre(116.3913,39.9075);
    }
    (:extendedCode)
    function setCentre(lon,lat) {
        cx=(lon-115)*MapData.XDEG;cy=(lat-39)*MapData.YDEG;
    }
    (:extendedCode)
    function onShow() {
        shown=true;metrics.start();
        Position.enableLocationEvents(Position.LOCATION_CONTINUOUS,method(:onPosition));
        onPosition(Position.getInfo());
        if(statusTimer==null){statusTimer=new Timer.Timer();}
        if(pendingDestination){pendingDestination=false;statusTimer.start(method(:openDestination),100,false);}else{statusTimer.start(method(:statusTick),1000,true);}
    }
    (:extendedCode)
    function onHide() {
        shown=false;
        if(paintTimer!=null){paintTimer.stop();painting=false;}
        if(statusTimer!=null){statusTimer.stop();}
    }
    (:extendedCode)
    function shutdown() {if(stopped){return;}stopped=true;onHide();Position.enableLocationEvents(Position.LOCATION_DISABLE,null);metrics.stop();track.finish();}
    function tick() as Void { WatchUi.requestUpdate(); }
    (:extendedCode)
    function openDestination() as Void {if(shown){showDestination();}}
    function statusTick() as Void { onPosition(Position.getInfo());if(!painting){WatchUi.requestUpdate();} }
    (:extendedCode)
    function prepareMap() {
        if(bitmap==null) { bitmap=Graphics.createBufferedBitmap({:width=>176,:height=>176,:palette=>[Graphics.COLOR_WHITE,Graphics.COLOR_BLACK]}).get(); }
        var canvas=bitmap.getDc();canvas.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);canvas.clear();
        queue=[];qIndex=0;activePacked=null;activeOffset=8;renderX=cx;renderY=cy;renderZoom=zoom;
        var scale=scales[zoom];var left=cx-88*scale;var right=cx+88*scale;var bottom=cy-88*scale;var top=cy+88*scale;
        for(var ty=Math.floor(bottom/MapData.TILE).toNumber();ty<=Math.floor(top/MapData.TILE).toNumber();ty++) {
            for(var tx=Math.floor(left/MapData.TILE).toNumber();tx<=Math.floor(right/MapData.TILE).toNumber();tx++) {
                var parts=MapData.chunks(tx,ty) as Array<ResourceId>;
                for(var k=0;k<parts.size();k++) { queue.add([parts[k],tx,ty]); }
            }
        }
    }

    function onPosition(info as Position.Info) as Void {
        gpsQuality=info.accuracy;
        if (info.position==null || info.accuracy==Position.QUALITY_NOT_AVAILABLE || info.accuracy==Position.QUALITY_LAST_KNOWN) { return; }
        var p=info.position.toDegrees();
        var x=(p[1]-115)*MapData.XDEG; var y=(p[0]-39)*MapData.YDEG;
        var at=info.when==null?Time.now().value():info.when.value();
        if(Time.now().value()-at>30){return;}
        var fresh=fixStamp==null || at>fixStamp;
        if(fresh){fixStamp=at;fixTime=System.getTimer();track.addFix(x,y,at);}
        var moved=gx==null || (x-gx).abs()>8 || (y-gy).abs()>8;
        if(info.heading!=null){heading=info.heading;}
        else if(gx!=null && moved){heading=Math.atan2(x-gx,y-gy);}
        gx=x;gy=y;
        var recenter=follow && !painting && ((cx-gx).abs()>scales[zoom]*15 || (cy-gy).abs()>scales[zoom]*15);
        if (recenter) { cx=gx;cy=gy; }
        if (shown && (moved || recenter || frames==0)) { WatchUi.requestUpdate(); }
    }
    (:extendedCode)
    function step(delta) {
        if (mode==0) { zoom=max(0,min(scales.size()-1,zoom+delta)); }
        else {
            follow=false;
            var dist=scales[zoom]*45;
            if (mode==1) { cy-=delta*dist; } else { cx+=delta*dist; }
            cx=max(MapData.MINX*MapData.TILE,min((MapData.MAXX+1)*MapData.TILE,cx));
            cy=max(MapData.MINY*MapData.TILE,min((MapData.MAXY+1)*MapData.TILE,cy));
        }
        WatchUi.requestUpdate();
    }
    function min(a,b) { return a<b?a:b; }
    function max(a,b) { return a>b?a:b; }
    function decode(chars as Array<Char>,i as Number) { return (chars[i].toNumber()-33)*64+chars[i+1].toNumber()-33; }
    function drawChunk(dc,chars as Array<Char>,tx,ty,scale) {
        var i=0;
        while(i<chars.size()) {
            var kind=chars[i].toNumber()-33;var n=decode(chars,i+1);i+=3;
            if(zoom>=4 && kind>=2) { i+=n*4;continue; }
            var px=0;var py=0;
            for(var j=0;j<n;j++) {
                var x=((tx*MapData.TILE+4*decode(chars,i)-cx)/scale+88).toNumber();
                var y=(87-(ty*MapData.TILE+4*decode(chars,i+2)-cy)/scale).toNumber(); i+=4;
                if(j>0 && !(max(px,x)<0 || min(px,x)>175 || max(py,y)<0 || min(py,y)>175)) {
                    if(kind<2) { dc.setPenWidth(kind==0?2:1); }
                    else { dc.setPenWidth(1); }
                    // All paths remain continuous so short segments cannot disappear.
                    dc.drawLine(px,py,x,y);
                }
                px=x;py=y;
            }
        }
    }
    function onUpdate(dc) {
        var began=System.getTimer();var scale=scales[zoom];
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.clear();metrics.refresh();
        if(page==1){drawDashboard(dc);drawSubscreen(dc);DashboardDraw.tabs(dc,page);return;}
        if(renderX!=cx || renderY!=cy || renderZoom!=zoom || bitmap==null) { prepareMap(); }
        var canvas=bitmap.getDc();canvas.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);canvas.setClip(0,0,176,176);
        var pointBudget=0;
        var scanned=0;
        while(activePacked==null && qIndex<queue.size() && scanned<4) {
            scanned++;var task=queue[qIndex];
            activePacked=Application.loadResource(task[0] as ResourceId) as String;
            activeOffset=8;activeTx=task[1];activeTy=task[2];
            var cell=activePacked.substring(0,8).toCharArray();
            var left=activeTx*MapData.TILE+4*decode(cell,0);var bottom=activeTy*MapData.TILE+4*decode(cell,2);
            var right=activeTx*MapData.TILE+4*decode(cell,4);var top=activeTy*MapData.TILE+4*decode(cell,6);
            if(left>cx+88*scale || right<cx-88*scale || bottom>cy+88*scale || top<cy-88*scale){activePacked=null;qIndex++;}
        }
        // Decode one short polyline at a time. Never expand a full tile into objects.
        while(activePacked!=null && pointBudget<240) {
            if(activeOffset>=activePacked.length()){activePacked=null;qIndex++;break;}
            var header=activePacked.substring(activeOffset,activeOffset+3).toCharArray();
            var n=decode(header,1);var end=activeOffset+3+n*4;
            var chars=activePacked.substring(activeOffset,end).toCharArray();
            drawChunk(canvas,chars,activeTx,activeTy,scale);
            activeOffset=end;pointBudget+=n;
        }
        canvas.clearClip();
        if(qIndex<queue.size()) {
            if(paintTimer==null) { paintTimer=new Timer.Timer(); }
            if(!painting) { paintTimer.start(method(:tick),50,true);painting=true; }
        } else if(paintTimer!=null && painting) { paintTimer.stop();painting=false; }
        var count=queue.size();
        dc.drawBitmap(0,0,bitmap);
        dc.clearClip();dc.setPenWidth(1);
        nav.draw(dc,cx,cy,scale);
        drawTrail(dc,scale);
        // GPS marker appears only for a measured fix, never at the browse centre.
        if(gx!=null && System.getTimer()-fixTime<30000) {
            var px=((gx-cx)/scale+88).toNumber();var py=(87-(gy-cy)/scale).toNumber();
            if(px>9 && px<167 && py>9 && py<167) {
                dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillCircle(px,py,6);
                dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);if(heading==null){dc.drawCircle(px,py,6);dc.fillCircle(px,py,2);}
                else {
                    var hx=Math.sin(heading);var hy=-Math.cos(heading);
                    var tip=[(px+hx*9).toNumber(),(py+hy*9).toNumber()];
                    var left=[(px-hx*5+hy*5).toNumber(),(py-hy*5-hx*5).toNumber()];
                    var right=[(px-hx*5-hy*5).toNumber(),(py-hy*5+hx*5).toNumber()];
                    dc.fillPolygon([tip,left,right]);
                }
            }
        }
        if(!follow) {
            dc.drawLine(84,87,92,87);dc.drawLine(88,83,88,91);
        }
        // District labels are browse anchors and only drawn when in view.
        for(var p=0;p<Places.areas.size();p++) {
            var area=Places.areas[p];
            var ax=(((area[1]-115)*MapData.XDEG-cx)/scale+88).toNumber();
            var ay=(87-((area[2]-39)*MapData.YDEG-cy)/scale).toNumber();
            if(ax>24 && ax<145 && ay>38 && ay<130) {
                dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillRectangle(ax-22,ay-7,44,17);
                dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.drawText(ax,ay-7,Graphics.FONT_XTINY,area[0],Graphics.TEXT_JUSTIFY_CENTER);
            }
        }
        // Keep only a compact scale badge; the map has no title or operation footer.
        var metres=scale*35;var rounded=metres>=1000?1000:(metres>=500?500:(metres>=200?200:(metres>=100?100:50)));
        var width=(rounded/scale).toNumber();
        dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillRectangle(15,125,max(width+6,49),24);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
        dc.drawLine(17,143,17+width,143);dc.drawLine(17,140,17,146);dc.drawLine(17+width,140,17+width,146);
        dc.drawText(17,125,Graphics.FONT_XTINY,rounded>=1000?"1km":rounded+"m",Graphics.TEXT_JUSTIFY_LEFT);
        if(nav.active && gx!=null && qIndex>=queue.size()) {
            dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillRectangle(15,152,146,22);
            dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.drawText(88,153,Graphics.FONT_XTINY,nav.remaining(gx,gy),Graphics.TEXT_JUSTIFY_CENTER);
        }
        drawSubscreen(dc);DashboardDraw.tabs(dc,page);
        frames++;
        System.println("MAP_FRAME part="+qIndex+"/"+count+" ms="+(System.getTimer()-began)+" free="+System.getSystemStats().freeMemory);
    }
    (:extendedCode)
    function switchTab(delta) {
        page=(page+delta+2)%2;
        if(page==1 && paintTimer!=null){paintTimer.stop();painting=false;}
        WatchUi.requestUpdate();System.println("TAB page="+page);
    }
    (:extendedCode)
    function signalBars() {
        if(gx==null || System.getTimer()-fixTime>=30000){return 0;}
        if(gpsQuality==Position.QUALITY_GOOD){return 4;}
        if(gpsQuality==Position.QUALITY_USABLE){return 3;}
        if(gpsQuality==Position.QUALITY_POOR){return 1;}
        return 0;
    }
    (:extendedCode)
    function drawSubscreen(dc) {
        // Draw last: physical secondary window is x113..175, y0..61.
        dc.setColor(Graphics.COLOR_WHITE,Graphics.COLOR_WHITE);dc.fillCircle(144,31,33);
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.setPenWidth(1);
        dc.drawRectangle(121,12,9,7);dc.fillRectangle(130,14,2,3);
        if(metrics.battery!=null){var filled=(metrics.battery*7/100).toNumber();if(filled>0){dc.fillRectangle(122,13,filled,5);}}
        var bars=signalBars();
        for(var i=0;i<4;i++){
            var h=3+i*2;var x=134+i*6;
            if(i<bars){dc.fillRectangle(x,19-h,4,h);}else{dc.drawRectangle(x,19-h,4,h);}
        }
        DashboardDraw.tinyTimer(dc,track.elapsedSeconds());
        dc.drawText(144,44,Graphics.FONT_XTINY,metrics.batteryText(),Graphics.TEXT_JUSTIFY_CENTER|Graphics.TEXT_JUSTIFY_VCENTER);
    }
    (:extendedCode)
    function drawDashboard(dc) {
        var clock=System.getClockTime();
        dc.drawText(65,12,Graphics.FONT_SMALL,clock.hour.format("%02d")+":"+clock.min.format("%02d"),Graphics.TEXT_JUSTIFY_CENTER);
        var trip=track.distance<1000?track.distance.format("%.0f")+"m":(track.distance/1000.0).format("%.1f")+"km";
        var detail=track.failed?"记录失败":(track.recording && track.session==null?"等待GPS":"本次"+trip);
        if(dc.getTextWidthInPixels(detail,Graphics.FONT_XTINY)>100){detail=trip;}
        dc.drawText(60,37,Graphics.FONT_XTINY,detail,Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawLine(12,63,163,63);dc.drawLine(88,68,88,146);dc.drawLine(12,108,163,108);
        dc.drawText(45,68,Graphics.FONT_XTINY,"心率",Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(128,68,Graphics.FONT_XTINY,"今日步数",Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(45,84,Graphics.FONT_XTINY,metrics.heartText(),Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(128,84,Graphics.FONT_XTINY,metrics.stepsText(),Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(45,111,Graphics.FONT_XTINY,"今日km",Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(128,111,Graphics.FONT_XTINY,"电量",Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(45,128,Graphics.FONT_XTINY,metrics.dailyText(),Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(128,128,Graphics.FONT_XTINY,metrics.batteryText(),Graphics.TEXT_JUSTIFY_CENTER);
    }
    (:extendedCode)
    function showMapControls() {
        page=0;var menu=new WatchUi.Menu2({:title=>"地图操作"});
        menu.addItem(new WatchUi.MenuItem("放大",null,:zoomIn,{}));
        menu.addItem(new WatchUi.MenuItem("缩小",null,:zoomOut,{}));
        menu.addItem(new WatchUi.MenuItem("向北平移",null,:north,{}));
        menu.addItem(new WatchUi.MenuItem("向南平移",null,:south,{}));
        menu.addItem(new WatchUi.MenuItem("向西平移",null,:west,{}));
        menu.addItem(new WatchUi.MenuItem("向东平移",null,:east,{}));
        WatchUi.pushView(menu,new MapControlsDelegate(self),WatchUi.SLIDE_UP);
    }
    function drawTrail(dc,scale) {
        dc.setClip(0,0,176,176);dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.setPenWidth(2);
        var prev=null;
        for(var i=0;i<track.count;i++){
            var p=track.point(i) as Array;var x=((p[0]-cx)/scale+88).toNumber();var y=(87-(p[1]-cy)/scale).toNumber();
            if(prev!=null && p[2]==0 && (i%2)==0){var before=prev as Array;dc.drawLine(before[0],before[1],x,y);}
            prev=[x,y];
        }
        dc.setPenWidth(1);dc.clearClip();
    }
    (:extendedCode)
    function releaseMap(){if(paintTimer!=null){paintTimer.stop();}painting=false;bitmap=null;queue=[];activePacked=null;renderZoom=-1;}
    (:extendedCode)
    function showDestination(){
        page=0;
        var menu=new WatchUi.Menu2({:title=>"目的地"});
        menu.addItem(new WatchUi.MenuItem("开始步行导航",destination[0],:route,{}));
        menu.addItem(new WatchUi.MenuItem("在地图上查看",destination[0],:view,{}));
        WatchUi.pushView(menu,new DestinationDelegate(self),WatchUi.SLIDE_UP);
    }
    (:extendedCode)
    function showMenu() {
        var menu=new WatchUi.Menu2({:title=>"地图"});
        menu.addItem(new WatchUi.MenuItem("GPS跟随",null,:gps,{}));
        menu.addItem(new WatchUi.MenuItem("地图缩放／平移",null,:controls,{}));
        menu.addItem(new WatchUi.MenuItem("离线地址搜索","中文或拼音前缀",:search,{}));
        if(nav.active){menu.addItem(new WatchUi.MenuItem("结束导航",nav.name,:endRoute,{}));}
        else{menu.addItem(new WatchUi.MenuItem("继续上次导航",null,:resumeRoute,{}));}
        menu.addItem(new WatchUi.MenuItem(track.recording?"结束并保存轨迹":"开始新轨迹",null,:track,{}));
        menu.addItem(new WatchUi.MenuItem("查看上次轨迹",null,:lastTrail,{}));
        menu.addItem(new WatchUi.MenuItem("选择地区",null,:areas,{}));
        menu.addItem(new WatchUi.MenuItem("回北京市中心",null,:centre,{}));
        menu.addItem(new WatchUi.MenuItem("使用说明",null,:help,{}));
        menu.addItem(new WatchUi.MenuItem("地图来源",null,:credits,{}));
        WatchUi.pushView(menu,new MapMenuDelegate(self),WatchUi.SLIDE_UP);
    }
}
class MapDelegate extends WatchUi.BehaviorDelegate {
    var v as BeijingMapView;
    (:extendedCode)
    function initialize(view) { BehaviorDelegate.initialize();v=view; }
    (:extendedCode)
    function onNextPage() {v.switchTab(1);return true;}
    (:extendedCode)
    function onPreviousPage() {v.switchTab(-1);return true;}
    (:extendedCode)
    function onSelect() {if(v.page==0){v.showMapControls();}else{WatchUi.requestUpdate();}return true;}
    (:extendedCode)
    function onMenu() {v.showMenu();return true;}
    (:extendedCode)
    function onBack() {
        if(v.page!=0){v.switchTab(-1);return true;}
        System.println("APP_BACK");v.shutdown();System.exit();return true;
    }
}
class MapMenuDelegate extends WatchUi.Menu2InputDelegate {
    var v as BeijingMapView;
    (:extendedCode)
    function initialize(view) {Menu2InputDelegate.initialize();v=view;}
    (:extendedCode)
    function onSelect(item) {
        var id=item.getId();
        if(id!=:track && id!=:help && id!=:credits){v.page=0;}
        if(id==:controls){WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);v.showMapControls();return;}
        if(id==:search){v.releaseMap();WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);var view=new OfflineSearchView(v);WatchUi.pushView(view,new SearchInputDelegate(view),WatchUi.SLIDE_UP);return;}
        if(id==:endRoute){v.nav.clear();WatchUi.popView(WatchUi.SLIDE_DOWN);return;}
        if(id==:resumeRoute){
            var target=Application.Storage.getValue("routeTarget");
            if(target!=null){v.destination=target as Array;v.pendingDestination=true;}
            WatchUi.popView(WatchUi.SLIDE_DOWN);return;
        }
        if(id==:track){if(v.track.recording){v.track.finish();}else{v.track.reset();}WatchUi.popView(WatchUi.SLIDE_DOWN);return;}
        if(id==:lastTrail){v.track.finish();if(v.track.restore()){var p=v.track.point(v.track.count-1);v.cx=p[0];v.cy=p[1];v.follow=false;}WatchUi.popView(WatchUi.SLIDE_DOWN);return;}
        if(id==:areas) {
            var m=new WatchUi.Menu2({:title=>"地区"});
            for(var i=0;i<Places.areas.size();i++){m.addItem(new WatchUi.MenuItem(Places.areas[i][0],null,i,{}));}
            WatchUi.pushView(m,new AreaDelegate(v),WatchUi.SLIDE_UP);return;
        }
        if(id==:help || id==:credits) {
            var text=id==:help?"UP/DOWN切换地图/数据\nGPS键打开地图操作\n长按MENU搜索/轨迹\nBACK返回地图或退出\n搜索支持中文/拼音\n路线为离线步行推荐":"© OpenStreetMap\ncontributors\nODbL 1.0\n道路简化8-12m\nWGS84坐标";
            WatchUi.pushView(new TextView(text),new WatchUi.BehaviorDelegate(),WatchUi.SLIDE_UP);return;
        }
        if(id==:gps){v.follow=true;if(v.gx!=null){v.cx=v.gx;v.cy=v.gy;}}
        if(id==:centre){v.follow=false;v.setCentre(116.3913,39.9075);}
        WatchUi.popView(WatchUi.SLIDE_DOWN);WatchUi.requestUpdate();
    }
}
class MapControlsDelegate extends WatchUi.Menu2InputDelegate {
    var v;
    (:extendedCode)
    function initialize(view){Menu2InputDelegate.initialize();v=view;}
    (:extendedCode)
    function onSelect(item){
        var id=item.getId();
        v.mode=(id==:north || id==:south)?1:((id==:west || id==:east)?2:0);
        v.step((id==:zoomIn || id==:north || id==:west)?-1:1);v.mode=0;
        WatchUi.popView(WatchUi.SLIDE_DOWN);
    }
}
class AreaDelegate extends WatchUi.Menu2InputDelegate {
    var v as BeijingMapView;
    (:extendedCode)
    function initialize(view) {Menu2InputDelegate.initialize();v=view;}
    (:extendedCode)
    function onSelect(item) {
        var p=Places.areas[item.getId() as Number];v.follow=false;v.setCentre(p[1],p[2]);v.mode=0;
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);WatchUi.popView(WatchUi.SLIDE_DOWN);WatchUi.requestUpdate();
    }
}
class TextView extends WatchUi.View {
    var text;
    (:extendedCode)
    function initialize(t){View.initialize();text=t;}
    function onUpdate(dc){dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.clear();BodyText.draw(dc,text);}
}
