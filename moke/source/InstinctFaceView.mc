import Toybox.ActivityMonitor;
import Toybox.Activity;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;
import Toybox.Weather;

class InstinctFaceView extends WatchUi.WatchFace {
    var _weather=null; var _weatherAt=-1; var _sunset="--:--";var _sunrise="--:--";
    var _activity=null;var _altitudeValue=null;var _pressureValue=null;var _stats=null;var _heartValue=null;
    var _heartAt=-1;var _heartMode=0;var _heartSource=0;var _heartCircle=false;var _paintedHeart=null;var _partialHeartAllowed=true;
    var _history as Array<Number or Null> = [];
    var _range as Array<Number or Null> = [null,null];
    var _trend as Array<Number or Null> = [];
    var _trendRange as Array<Number or Null> = [null,null];
    var _historyAt=-1;var _bodyAt=-1;
    var _needs=0;var _planRevision=-1;var _trendKind=0;var _profile=0;
    var _secondsEnabled=false;var _secondsMode=0;var _sleeping=true;var _secondsVisible=false;
    var _cardTop=0;var _cardBottom=0;var _sideKind=0;
    var _frameMinute=-1;var _dataMinute=-1;var _forceFrame=true;var _frameTime=0;
    var _suspended=false;
    var _notificationCount=null;var _moonAt=-1;var _moonValue=0.0;
    var _sunDay=-1;var _sunLat=null;var _sunLon=null;var _sunWeatherAt=-1;
    function initialize(){WatchFace.initialize();FaceDraw.initialize();}
    function suspend(){_suspended=true;invalidate();}
    function invalidate(){
        _history=[];_trend=[];_range=[null,null];_trendRange=[null,null];
        _activity=null;_altitudeValue=null;_pressureValue=null;_weather=null;_stats=null;_heartValue=null;_heartAt=-1;
        _historyAt=-1;_weatherAt=-1;_bodyAt=-1;_sunDay=-1;_planRevision=-1;
        _sunset="--:--";_sunrise="--:--";
        _forceFrame=true;_frameMinute=-1;_dataMinute=-1;FaceDraw.enterSettings();
    }
    function onShow() as Void {_suspended=false;_forceFrame=true;DeviceProfile.hands(self,!_sleeping);}
    function onHide() as Void {DeviceProfile.releaseHands(self);suspend();}
    function onEnterSleep() as Void {_sleeping=true;DeviceProfile.hands(self,false);if(_secondsMode==1 && _secondsVisible){WatchUi.requestUpdate();}}
    function onExitSleep() as Void {_sleeping=false;DeviceProfile.hands(self,true);}
    function disablePartialSeconds(){_secondsMode=PowerPolicy.budgetSeconds(_secondsMode);if(_secondsVisible){WatchUi.requestUpdate();}}
    function disablePartialHeart(){_partialHeartAllowed=false;}
    function includeMetric(kind){_needs=_needs|PowerPolicy.metric(kind);}
    function buildPlan(){
        // A hidden/replaced region must not keep its old fonts, cards or chart in RAM.
        FaceDraw.enterSettings();
        _needs=0;_trendKind=0;_profile=FacePrefs.get("powerProfile");
        _heartMode=FacePrefs.get("heartRefresh");_heartSource=FacePrefs.get("heartSource");_heartCircle=FacePrefs.flag("showCircle") && FacePrefs.get("circle")==6;
        _cardTop=0;_cardBottom=0;_sideKind=0;
        if(FacePrefs.flag("showStatus")){
            _sideKind=FacePrefs.get("sideData");
            if(_sideKind==0){
                _cardTop=FacePrefs.flag("showBeijingCard") ? FacePrefs.get("topCardImage") : 0;
                _cardBottom=FacePrefs.flag("showAlipayCard") ? FacePrefs.get("bottomCardImage") : 0;
            }
        }
        _secondsMode=SidePanel.secondsMode(FacePrefs.get("secondsMode"),_cardTop,_cardBottom,_sideKind);
        _secondsEnabled=FacePrefs.flag("showSeconds");
        var keys=["topOne","topTwo","topThree","bottomLeft","footerLeft","footerRight"];
        for(var i=0;i<keys.size();i++){includeMetric(FacePrefs.get(keys[i]));}
        var right=FacePrefs.get("bottomRight");
        if(right!=0 && FacePrefs.flag("showHeartGraph") && FacePrefs.get("bottomRightStyle")==6 && TrendData.supported(right)){
            _trendKind=right;if(right==6 || right==15){_needs=_needs|PowerPolicy.RANGE;}
        }else{includeMetric(right);}
        if(FacePrefs.flag("showCircle")){
            includeMetric(FacePrefs.get("circle"));
            _needs=_needs|PowerPolicy.progress(FacePrefs.get("cellsSource"))|PowerPolicy.progress(FacePrefs.get("ringSource"));
        }
        includeMetric(_sideKind);
        if(FacePrefs.flag("showMoveBar")){_needs=_needs|PowerPolicy.progress(FacePrefs.get("moveSource"));}
        if(FacePrefs.flag("showWind")){_needs=_needs|PowerPolicy.WEATHER;}
        _historyAt=-1;_bodyAt=-1;_dataMinute=-1;_heartAt=-1;_planRevision=FacePrefs.revision;FaceDraw.releaseSeconds();FaceDraw.releaseLiveHeart();
    }
    function uses(mask){return (_needs&mask)!=0;}
    function readLiveHeart(stamp){
        if(PreviewMode.ENABLED){return PreviewMode.currentHeartRate(stamp);}
        var info=Activity.getActivityInfo();
        // Keep only two scalar values, not a second large Activity.Info object.
        if(uses(PowerPolicy.LIVE)){_altitudeValue=info.altitude;_pressureValue=info.ambientPressure;}
        return _heartSource==1 ? LiveHeart.recent(stamp) : info.currentHeartRate;
    }
    function refreshCurrentHeart(stamp){
        if(!LiveHeart.due(_heartAt,stamp)){return;}_heartAt=stamp;
        _heartValue=LiveHeart.normalize(readLiveHeart(stamp));
    }
    function updateLiveHeart(dc,stamp){
        if(!_heartCircle || !LiveHeart.secondTick(_heartMode,_sleeping)){return;}
        refreshCurrentHeart(stamp);
        if(_heartValue!=_paintedHeart){paintLiveHeart(dc,_heartValue);_paintedHeart=_heartValue;}
    }
    function paintLiveHeart(dc,value){FaceDraw.refreshLiveHeart(DeviceDrawing.circleTarget(dc),value);}
    function readData(now){
        var minute=(now.value()/60).toNumber();
        if(_dataMinute==minute){return;}_dataMinute=minute;
        _activity=uses(PowerPolicy.ACTIVITY) && !PreviewMode.ENABLED ? ActivityMonitor.getInfo() : null;
        _stats=uses(PowerPolicy.STATS) && !PreviewMode.ENABLED ? System.getSystemStats() : null;
        if(uses(PowerPolicy.HEART)){refreshCurrentHeart(now.value());}
        else if(uses(PowerPolicy.LIVE) && !PreviewMode.ENABLED){
            var info=Activity.getActivityInfo();_altitudeValue=info.altitude;_pressureValue=info.ambientPressure;
        }
        if(uses(PowerPolicy.NOTIFICATIONS) && !PreviewMode.ENABLED){_notificationCount=System.getDeviceSettings().notificationCount;}
        if(uses(PowerPolicy.BODY)){
            FaceDraw.bodyBattery=PreviewMode.ENABLED ? PreviewMode.bodyBattery() : FitnessProgress.latestBodyBattery();_bodyAt=now.value();
        }
        var historyDue=(uses(PowerPolicy.RANGE) || _trendKind!=0) && PowerPolicy.due(_historyAt,now.value(),PowerPolicy.historyPeriod(_profile));
        var weatherDue=uses(PowerPolicy.WEATHER) && PowerPolicy.due(_weatherAt,now.value(),PowerPolicy.weatherPeriod(_profile));
        // Make room for history aggregation / a new weather object before rebuilding the frame.
        if(historyDue || weatherDue){FaceDraw.enterSettings();}
        if(historyDue){refreshHeart(now);}
        if(weatherDue){refreshWeather(now);}
    }
    function onUpdate(dc as Graphics.Dc) as Void {updateAt(DeviceDrawing.target(dc),Time.now());}
    function updateAt(dc,now as Time.Moment) as Void {
        if(_suspended){return;}
        var frameStamp=(now.value()/60).toNumber();
        if(!_forceFrame && _planRevision==FacePrefs.revision && frameStamp==_frameMinute){updateLiveHeart(dc,now.value());updateSeconds(dc);return;}
        if(_planRevision!=FacePrefs.revision){buildPlan();}
        FaceDraw.releaseLiveHeart();
        _frameTime=now.value();readData(now);
        var clock=System.getClockTime();var d=Gregorian.info(now,Time.FORMAT_SHORT);
        if(uses(PowerPolicy.SUN)){refreshSun(now,d);}
        FaceDraw.setTheme(FacePrefs.flag("darkTheme"));
        FaceDraw.batteryPercent=PreviewMode.ENABLED ? 86 : (_stats!=null ? _stats.battery : 0);
        FaceDraw.cellsProgress=FacePrefs.flag("showCircle") ? progress(FacePrefs.get("cellsSource")) : null;
        FaceDraw.intensityProgress=FacePrefs.flag("showCircle") ? progress(FacePrefs.get("ringSource")) : null;
        WeatherIcons.current=WeatherIcons.category(PreviewMode.ENABLED ? PreviewMode.weatherCondition() : (_weather!=null ? _weather.condition : null));
        dc.clearClip();dc.setColor(FaceDraw.foreground,FaceDraw.background);dc.clear();
        
        slot(dc,"topOne",34,5,48,20);
        if(FacePrefs.flag("showWind")){drawWind(dc);}
        slot(dc,"topTwo",10,FaceLayout.POWER_ROW_Y,FacePrefs.get("topThree")==0 ? FaceLayout.POWER_ROW_WIDTH : 48,20);
        slot(dc,"topThree",FaceLayout.FEELS_X,FaceLayout.POWER_ROW_Y,48,20);
        if(FacePrefs.flag("showMoon")){
            var spare=FacePrefs.get("topThree")==0;
            FaceDraw.moon(dc,spare ? FaceLayout.MOON_X : 102,spare ? FaceLayout.MOON_Y : 54,moonPhase(),FaceDraw.foreground,FaceDraw.background);
        }
        if(FacePrefs.flag("showDate")){FaceDraw.date(dc,FaceFormat.dateText(d));}
        if(FacePrefs.flag("showMoveBar") && FacePrefs.get("moveSource")!=0){
            var p=progress(FacePrefs.get("moveSource"));
            FaceDraw.moveBar(dc,p,FacePrefs.get("topThree")!=0 && FacePrefs.flag("showMoon"));
        }
        var hour=PreviewMode.ENABLED ? 18 : clock.hour;var minute=PreviewMode.ENABLED ? 58 : clock.min;
        if(FacePrefs.flag("showTime")){FaceDraw.time(dc,hour,minute);}
        if(_sideKind!=0){FaceDraw.sideData(dc,_sideKind,metric(_sideKind));}
        else{FaceDraw.walletCards(dc,_cardTop,_cardBottom);}
        _secondsVisible=false;updateSeconds(dc);
        slot(dc,"bottomLeft",FaceLayout.STEP_X,FaceLayout.LOWER_Y,FaceLayout.STEP_WIDTH,20);
        var right=FacePrefs.get("bottomRight");
        if(right!=0 && FacePrefs.flag("showHeartGraph") && FacePrefs.get("bottomRightStyle")==6 && TrendData.supported(right)){
            FaceDraw.heartPanel(dc,_trend,_trendRange);
        }else{slot(dc,"bottomRight",FaceLayout.LOWER_RIGHT_X,FaceLayout.LOWER_Y,FaceLayout.LOWER_RIGHT_WIDTH,20);}
        FaceDraw.footerRow(dc,slotLabel("footerLeft"),slotRatio("footerLeft"),slotLabel("footerRight"),slotRatio("footerRight"));
        if(FacePrefs.flag("showCircle")){FaceDraw.circle(DeviceDrawing.circleTarget(dc),FacePrefs.get("circle"),slotLabel("circle"),_heartValue);_paintedHeart=_heartValue;}
        _frameMinute=frameStamp;_forceFrame=false;
    }
    function slot(dc,key,x,y,width,height){FaceDraw.slot(dc,key,slotLabel(key),slotRatio(key),x,y,width,height,null);}
    function slotLabel(key){
        var kind=FacePrefs.get(key);if(kind==0){return "";}
        var style=FacePrefs.get(key+"Style");
        if(style==2){var r=ratio(key);return r==null ? "--" : (r*100).format("%.0f")+"%";}
        if(style==3){var v=number(kind);var g=goal(key);return v==null || g==null ? "--" : FaceFormat.shortNumber(v)+"/"+FaceFormat.shortNumber(g);}
        return metric(kind);
    }
    function goal(key){
        var custom=FacePrefs.get(key+"Goal");if(custom>0){return custom;}
        var kind=FacePrefs.get(key);
        switch(kind){
            case 1:case 10:case 12:case 14:case 19:case 22:case 23:return 100;
            case 2:return PreviewMode.ENABLED ? 10000 : (_activity!=null ? _activity.stepGoal : null);
            case 4:return PreviewMode.ENABLED ? 20 : (_activity!=null ? _activity.floorsClimbedGoal : null);
            case 20:return PreviewMode.ENABLED ? PreviewMode.INTENSITY_WEEK_GOAL/7.0 : (_activity!=null && _activity.activeMinutesWeekGoal!=null ? _activity.activeMinutesWeekGoal/7.0 : null);
            case 21:return PreviewMode.ENABLED ? PreviewMode.INTENSITY_WEEK_GOAL : (_activity!=null ? _activity.activeMinutesWeekGoal : null);
            case 24:return 5;
        }
        return null;
    }
    function slotRatio(key){var style=FacePrefs.get(key+"Style");return style==4 || style==5 ? ratio(key) : null;}
    function ratio(key){var v=number(FacePrefs.get(key));var g=goal(key);return v==null || g==null || g<=0 ? null : v.toFloat()/g;}
    function progress(source){
        if(source==0){return null;}
        var a=_activity;
        if(source==1){return FitnessProgress.completion(FaceDraw.bodyBattery,100);}
        if(source==2){return FitnessProgress.completion(number(1),100);}
        if(source==3){return FitnessProgress.completion(number(2),PreviewMode.ENABLED ? 10000 : (a!=null ? a.stepGoal : null));}
        if(source==4){return PreviewMode.ENABLED ? PreviewMode.intensityProgress() : FitnessProgress.dailyRatio(a);}
        if(source==5){return FitnessProgress.completion(number(21),PreviewMode.ENABLED ? PreviewMode.INTENSITY_WEEK_GOAL : (a!=null ? a.activeMinutesWeekGoal : null));}
        if(source==6){return FitnessProgress.completion(number(24),5);}
        if(source==7){return FitnessProgress.completion(number(4),PreviewMode.ENABLED ? 20 : (a!=null ? a.floorsClimbedGoal : null));}
        return null;
    }
    function number(kind){
        var a=_activity;var n=null;
        if(kind==6){return _heartValue;}
        if(PreviewMode.ENABLED){n=PreviewMode.number(kind);}
        else{
            switch(kind){
                case 1:n=_stats!=null ? _stats.battery : null;break;
                case 2:n=a!=null ? a.steps : null;break;
                case 3:n=a!=null && a.distance!=null ? a.distance/100000.0 : null;break;
                case 4:n=a!=null ? a.floorsClimbed : null;break;
                case 5:n=a!=null ? a.calories : null;break;
                case 7:n=_weather!=null ? _weather.temperature : null;break;
                case 10:n=_weather!=null ? _weather.relativeHumidity : null;break;
                case 11:n=_notificationCount;break;
                case 12:n=a!=null && a.steps!=null && a.stepGoal!=null && a.stepGoal>0 ? 100.0*a.steps/a.stepGoal : null;break;
                case 13:n=_weather!=null && _weather.windSpeed!=null ? _weather.windSpeed*3.6 : null;break;
                case 14:n=(1-Math.cos(moonPhase()*2*Math.PI))*50;break;
                case 16:n=_weather!=null ? _weather.feelsLikeTemperature : null;break;
                case 17:n=_stats!=null && (_stats has :batteryInDays) ? _stats.batteryInDays : null;break;
                case 18:n=_altitudeValue;break;
                case 19:n=FaceDraw.bodyBattery;break;
                case 20:n=a!=null && a.activeMinutesDay!=null ? a.activeMinutesDay.total : null;break;
                case 21:n=a!=null && a.activeMinutesWeek!=null ? a.activeMinutesWeek.total : null;break;
                case 22:var r=FitnessProgress.dailyRatio(a);n=r!=null ? r*100 : null;break;
                case 23:n=a!=null && a.activeMinutesWeek!=null && a.activeMinutesWeekGoal!=null && a.activeMinutesWeekGoal>0 ? a.activeMinutesWeek.total*100.0/a.activeMinutesWeekGoal : null;break;
                case 24:n=a!=null && (a has :moveBarLevel) ? a.moveBarLevel : null;break;
                case 25:n=a!=null && (a has :timeToRecovery) ? a.timeToRecovery : null;break;
                case 26:n=a!=null && (a has :stressScore) ? a.stressScore : null;break;
                case 27:n=a!=null && (a has :respirationRate) ? a.respirationRate : null;break;
                case 28:n=_pressureValue!=null ? _pressureValue/100.0 : null;break;
            }
        }
        if(n==null){return null;}
        if(kind==17 && n<0){return null;}
        if(kind==26 && (n<0 || n>100)){return null;}
        if(kind==27 && n<=0){return null;}
        if((kind==7 || kind==16) && FacePrefs.get("temperatureUnit")==1){n=n*1.8+32;}
        if((kind==3 || kind==13) && FacePrefs.get("distanceUnit")==1){n=n/1.609344;}
        if(kind==18 && FacePrefs.get("altitudeUnit")==1){n=n*3.28084;}
        return n;
    }
    function metric(kind){
        if(kind==0){return "";}
        if(kind==8){return PreviewMode.ENABLED ? PreviewMode.metric(8) : _sunset;}
        if(kind==9){return PreviewMode.ENABLED ? PreviewMode.metric(9) : _sunrise;}
        if(kind==15){var low=_range[0];var high=_range[1];return low!=null && high!=null ? low.toString()+"-"+high.toString() : "--";}
        var n=number(kind);if(n==null){return "--";}
        var units=FacePrefs.flag("showUnits");
        switch(kind){
            case 3:return n.format("%.1f")+(units ? (FacePrefs.get("distanceUnit")==0 ? "km" : "mi") : "");
            case 7:case 16:return n.format("%.0f")+(units ? (FacePrefs.get("temperatureUnit")==1 ? "°F" : "°") : "");
            case 10:case 12:case 14:case 22:case 23:return n.format("%.0f")+"%";
            case 17:return Math.floor(n).format("%d")+(units ? FaceLocale.days() : "");
            case 18:return n.format("%.0f")+(units ? (FacePrefs.get("altitudeUnit")==0 ? "m" : "ft") : "");
            case 25:return n.format("%.0f")+(units ? "h" : "");
            case 28:return n.format("%.0f")+(units ? "hPa" : "");
            case 2:case 4:case 5:return FaceFormat.compact(n);
        }
        return n.format("%.0f");
    }
    function refreshHeart(now){
        // Drop the previous window before allocating the next set of buckets.
        _history=[];_trend=[];_range=[null,null];_trendRange=[null,null];
        _historyAt=now.value();
        var minutes=[15,30,60][FacePrefs.get("chartMinutes")];
        if(uses(PowerPolicy.RANGE)){
            if(PreviewMode.ENABLED){_history=PreviewMode.history();_range=HeartAnalytics.range(_history,6);}
            else{var result=HeartAnalytics.window(ActivityMonitor.getHeartRateHistory(new Time.Duration(minutes*60),true),now,minutes);_history=result[:values] as Array<Number or Null>;_range=result[:range] as Array<Number or Null>;}
        }
        if(_trendKind==6 || _trendKind==15){_trend=_history;_trendRange=_range;}
        else if(_trendKind!=0){
            if(PreviewMode.ENABLED){_trend=PreviewMode.trend(_trendKind);_trendRange=HeartAnalytics.range(_trend,_trendKind);}
            else{var result=TrendData.fetch(_trendKind,now,minutes);_trend=result[:values] as Array<Number or Null>;_trendRange=result[:range] as Array<Number or Null>;}
        }
    }
    function refreshWeather(now){_weatherAt=now.value();_weather=null;if(!PreviewMode.ENABLED){_weather=Weather.getCurrentConditions();}}
    function refreshSun(now,d){
        if(PreviewMode.ENABLED){return;}
        if(_weather==null || _weather.observationLocationPosition==null){
            _sunset="--:--";_sunrise="--:--";_sunDay=-1;return;
        }
        var day=d.year*10000+d.month*100+d.day;
        if(day==_sunDay && _sunWeatherAt==_weatherAt){return;}
        _sunWeatherAt=_weatherAt;
        var position=_weather.observationLocationPosition;var coords=position.toDegrees() as Array<Double>;
        // Recompute for a new local day or a changed weather location, not every minute.
        if(day!=_sunDay || coords[0]!=_sunLat || coords[1]!=_sunLon){
            _sunset=sunTime(Weather.getSunset(position,now));_sunrise=sunTime(Weather.getSunrise(position,now));
            _sunDay=day;_sunLat=coords[0];_sunLon=coords[1];
        }
    }
    function sunTime(moment){if(moment==null){return "--:--";}var d=Gregorian.info(moment,Time.FORMAT_SHORT);return d.hour.format("%02d")+":"+d.min.format("%02d");}
    function moonPhase(){
        if(PowerPolicy.due(_moonAt,_frameTime,3600)){var cycles=(_frameTime-947182440)/2551442.877;_moonValue=cycles-Math.floor(cycles);_moonAt=_frameTime;}
        return _moonValue;
    }
    function drawWind(dc){
        drawWindAt(dc,FaceLayout.WIND_X,14);
    }
    function drawWindAt(dc,center,cy){
        if(!PreviewMode.ENABLED && (_weather==null || _weather.windBearing==null)){dc.drawLine(center-4,cy,center+4,cy);return;}
        var bearing=PreviewMode.ENABLED ? 90 : _weather.windBearing;
        if(NativeStyle.enabled()){NativeStyle.windArrow(dc,center,cy,bearing,FaceDraw.foreground,FaceDraw.background);dc.setPenWidth(1);return;}
        var a=(bearing-90)*Math.PI/180;
        var x=center+6*Math.cos(a);var y=cy+6*Math.sin(a);dc.setPenWidth(2);
        dc.drawLine(center-5*Math.cos(a),cy-5*Math.sin(a),x,y);dc.drawLine(x,y,x-4*Math.cos(a-.7),y-4*Math.sin(a-.7));dc.drawLine(x,y,x-4*Math.cos(a+.7),y-4*Math.sin(a+.7));dc.setPenWidth(1);
    }
    function updateSeconds(dc){
        var show=PowerPolicy.seconds(_secondsEnabled,_secondsMode,_sleeping);
        if(!show && !_secondsVisible){return;}
        dc.setClip(DeviceProfile.SECONDS_LEFT,DeviceProfile.SECONDS_Y,DeviceProfile.SECONDS_WIDTH,DeviceProfile.SECONDS_HEIGHT);
        dc.setColor(FaceDraw.background,FaceDraw.background);dc.fillRectangle(DeviceProfile.SECONDS_LEFT,DeviceProfile.SECONDS_Y,DeviceProfile.SECONDS_WIDTH,DeviceProfile.SECONDS_HEIGHT);
        if(show){dc.setColor(FaceDraw.foreground,FaceDraw.background);FaceDraw.seconds(dc,System.getClockTime().sec);}
        dc.clearClip();_secondsVisible=show;
    }
    function onPartialUpdate(dc as Graphics.Dc) as Void {
        partialAt(DeviceDrawing.target(dc));
    }
    function partialAt(dc){
        if(_suspended || _forceFrame){return;}
        if(_partialHeartAllowed && _heartCircle && LiveHeart.secondTick(_heartMode,_sleeping)){updateLiveHeart(dc,Time.now().value());}
        if(!_secondsEnabled || _secondsMode!=2){return;}
        // Font is prepared by onUpdate; no resource loads or property reads on this path.
        dc.setClip(DeviceProfile.SECONDS_LEFT,DeviceProfile.SECONDS_Y,DeviceProfile.SECONDS_WIDTH,DeviceProfile.SECONDS_HEIGHT);
        dc.setColor(FaceDraw.background,FaceDraw.background);dc.fillRectangle(DeviceProfile.SECONDS_LEFT,DeviceProfile.SECONDS_Y,DeviceProfile.SECONDS_WIDTH,DeviceProfile.SECONDS_HEIGHT);
        dc.setColor(FaceDraw.foreground,FaceDraw.background);FaceDraw.seconds(dc,System.getClockTime().sec);
        dc.clearClip();_secondsVisible=true;
    }
}
