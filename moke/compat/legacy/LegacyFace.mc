// Compatibility renderer for early Connect IQ / 32 KB MIP watches.
// Unsupported health metrics stay unavailable; no invented system values or targets.
import Toybox.Application;
import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

(:classicPrefs)
module FacePrefs {
    var revision=0;var _cache;
    function reload(){revision+=1;_cache=null;}
    function prepare(){
        if(_cache!=null){return;}
        _cache=new [LegacyPrefsIndex.COUNT];
        var names=LegacyPrefsIndex.KEYS;for(var i=0;i<LegacyPrefsIndex.COUNT;i++){var word=names.substring(i*LegacyPrefsIndex.WIDTH,(i+1)*LegacyPrefsIndex.WIDTH);var key=word.substring(0,word.find(" "));word=null;_cache[i]=read(key);}
    }
    function read(key){try{return Application.getApp().getProperty(key);}catch(e){return null;}}
    function raw(key){var index=LegacyPrefsIndex.index(key);if(_cache!=null && index!=null){return _cache[index];}return read(key);}
    function get(key){var value=raw(key);return value instanceof Number && value>=0 && value<=PrefsDefaults.max(key) ? value : PrefsDefaults.value(key);}
    function flag(key){var value=raw(key);return value instanceof Boolean ? value : true;}
    function fontFamily(key){var n=get(key+"Font");return n==0 ? get("dataFont") : n-1;}
    function fontSize(key){var n=get(key+"Size");return n==0 ? get("dataSize") : n-1;}
}
class InstinctFaceApp extends Application.AppBase {
    var _view;
    function initialize(){AppBase.initialize();}
    function onStart(state){}
    function getInitialView(){_view=new LegacyFace();return LegacyPower.views(_view);}
    function getSettingsView(){if(_view!=null){_view.suspend();}return LegacyPower.settings();}
    function onSettingsChanged(){FacePrefs.reload();if(_view!=null){_view.invalidate();}WatchUi.requestUpdate();}
    function onStop(state){if(_view!=null){_view.invalidate();DeviceProfile.releaseHands(_view);}_view=null;FacePrefs.reload();}
}
class LegacyFace extends WatchUi.WatchFace {
    var _values as Array=[];var _history as Array=[];var _range as Array<Numeric or Null> =[null,null];var _historyAt=-1;var _weatherAt=-1;
    var _minute=-1;var _force=true;var _sleeping=true;var _heartAt=-1;var _painted=null;
    var _heartFont;var _secondsFont;var _ink;var _paper;var _circleInk;var _circlePaper;
    var _heartMode=0;var _heartSource=0;var _heartOn=false;var _partial=true;var _secondsMode=0;var _secondsOn=false;
    var _top=0;var _bottom=0;var _side=0;var _topImage;var _bottomImage;
    var _stepGoal=null;var _floorGoal=null;var _weekGoal=null;var _cells=null;var _ring=null;
    var _wind=null;var _condition=0;var _sunrise="--:--";var _sunset="--:--";var _moon=0.0;var _weather as Array=[];
    var _secondsVisible=false;
    var _heartStyle=0;var _heartGoal=0;var _cellsStyle=0;
    var _suspended=false;var _revision=-1;
    var _heartRange as Array<Numeric or Null> =[null,null];var _energy;var _energyKey=-1;var _energyCount=0;var _footerSize=-1;
    function initialize(){WatchFace.initialize();_values=new [29];}
    function invalidate(){_force=true;_minute=-1;_weatherAt=-1;_historyAt=-1;_history=[];_topImage=null;_bottomImage=null;_heartFont=null;_secondsFont=null;_energy=null;_energyKey=-1;FontCatalog.reset();}
    function suspend(){_suspended=true;invalidate();}
    function onShow(){_suspended=false;_force=true;DeviceProfile.hands(self,!_sleeping);}
    function onHide(){DeviceProfile.releaseHands(self);suspend();}
    function onEnterSleep(){_sleeping=true;DeviceProfile.hands(self,false);if(_secondsVisible && _secondsMode==1){WatchUi.requestUpdate();}}
    function onExitSleep(){_sleeping=false;DeviceProfile.hands(self,true);}
    function budgetExceeded(){_partial=false;if(_secondsMode==2){_secondsMode=1;}_force=true;WatchUi.requestUpdate();}
    function refreshHeart(stamp){
        if(!LiveHeart.due(_heartAt,stamp)){return;}_heartAt=stamp;
        var v=PreviewMode.ENABLED ? PreviewMode.currentHeartRate(stamp) : (_heartSource==1 ? LiveHeart.recent(stamp) : Activity.getActivityInfo().currentHeartRate);
        _values[6]=LiveHeart.normalize(v);
    }
    function readData(now){
        _heartSource=FacePrefs.get("heartSource");
        var a=ActivityMonitor.getInfo();var stats=System.getSystemStats();var info=Activity.getActivityInfo();
        for(var k=1;k<29;k++){_values[k]=PreviewMode.ENABLED ? PreviewMode.number(k) : null;}
        if(!PreviewMode.ENABLED){
            _values[1]=stats.battery;_values[2]=a.steps;_values[3]=a.distance!=null ? a.distance/100000.0 : null;_values[5]=a.calories;
            if(a has :floorsClimbed){_values[4]=a.floorsClimbed;}
            if(a has :moveBarLevel){_values[24]=a.moveBarLevel;}
            if(a has :timeToRecovery){_values[25]=a.timeToRecovery;}
            if(a has :stressScore){var stress=a.stressScore;_values[26]=stress!=null && stress>=0 && stress<=100 ? stress : null;}
            if(a has :respirationRate){_values[27]=a.respirationRate;}
            if(a has :activeMinutesDay){var day=a.activeMinutesDay;_values[20]=day!=null ? day.total : null;}
            if(a has :activeMinutesWeek){var week=a.activeMinutesWeek;_values[21]=week!=null ? week.total : null;}
            _stepGoal=a.stepGoal;_floorGoal=(a has :floorsClimbedGoal) ? a.floorsClimbedGoal : null;
            _weekGoal=(a has :activeMinutesWeekGoal) ? a.activeMinutesWeekGoal : null;
            _values[17]=(stats has :batteryInDays) ? stats.batteryInDays : null;
            _values[18]=info.altitude;_values[28]=(info has :ambientPressure) && info.ambientPressure!=null ? info.ambientPressure/100.0 : null;
            _values[19]=LegacyExtras.body();
            _values[11]=System.getDeviceSettings().notificationCount;
        }else{_stepGoal=10000;_floorGoal=20;_weekGoal=PreviewMode.INTENSITY_WEEK_GOAL;_values[19]=DeviceProfile.BODY ? PreviewMode.bodyBattery() : null;}
        _heartAt=-1;refreshHeart(now.value());
        _values[12]=ratio(_values[2],_stepGoal);if(_values[12]!=null){_values[12]*=100;}
        _values[22]=ratio(_values[20],_weekGoal!=null ? _weekGoal/7.0 : null);if(_values[22]!=null){_values[22]*=100;}
        _values[23]=ratio(_values[21],_weekGoal);if(_values[23]!=null){_values[23]*=100;}
        var cycles=(now.value()-947182440)/2551442.877;_moon=cycles-Math.floor(cycles);_values[14]=(1-Math.cos(_moon*2*Math.PI))*50;
        if(_weatherAt<0 || now.value()-_weatherAt>=(FacePrefs.get("powerProfile")==0 ? 1800 : 300)){
            _weatherAt=now.value();
            _weather=PreviewMode.ENABLED && DeviceProfile.WEATHER ? [24,56,13,25,90,4,"06:04","17:18"] : LegacyExtras.weather(now);
        }
        _values[7]=_weather[0];_values[10]=_weather[1];_values[13]=_weather[2];_values[16]=_weather[3];_wind=_weather[4];_condition=_weather[5];_sunrise=_weather[6];_sunset=_weather[7];
        if(_historyAt<0 || now.value()-_historyAt>=(FacePrefs.get("powerProfile")==0 ? 300 : 60)){readHistory(now);}
    }
    function readHistory(now){
        _historyAt=now.value();_history=[];_range=[null,null];
        var right=FacePrefs.get("bottomRight");var chart=FacePrefs.flag("showHeartGraph") && FacePrefs.get("bottomRightStyle")==6 && (right==6 || right==15 || right==18 || right==19 || right==28);var need=right==15 || (right==6 && chart);
        var keys=["topOne","topTwo","topThree","bottomLeft","footerLeft","footerRight","circle","sideData"];
        for(var i=0;i<keys.size();i++){var key=keys[i];if(key.equals("circle") && !FacePrefs.flag("showCircle")){continue;}if(key.equals("sideData") && !FacePrefs.flag("showStatus")){continue;}if(FacePrefs.get(key)==15){need=true;}}
        if(!need && !chart){return;}
        if(need && PreviewMode.ENABLED){_history=PreviewMode.history();}
        else if(need && (ActivityMonitor has :getHeartRateHistory)){
            var minutes=[15,30,60][FacePrefs.get("chartMinutes")];var iterator=ActivityMonitor.getHeartRateHistory(new Time.Duration(minutes*60),true);
            var sums=new [48];var counts=new [48];for(var i=0;i<48;i++){sums[i]=0;counts[i]=0;}
            var item=iterator.next();var start=now.value()-minutes*60;
            while(item!=null){
                var rate=item.heartRate;var stamp=item.when!=null ? item.when.value() : start-1;
                if(LiveHeart.valid(rate) && stamp>=start && stamp<=now.value()){
                    var b=((stamp-start)*48/(minutes*60)).toNumber();if(b>47){b=47;}sums[b]+=rate;counts[b]+=1;
                    if(_range[0]==null || rate<_range[0]){_range[0]=rate;}if(_range[1]==null || rate>_range[1]){_range[1]=rate;}
                }item=iterator.next();
            }
            _history=new [48];for(var i=0;i<48;i++){_history[i]=counts[i]>0 ? (sums[i]/counts[i]).toNumber() : null;}
        }
        for(var i=0;i<_history.size();i++){var rate=_history[i];if(LiveHeart.valid(rate)){if(_range[0]==null || rate<_range[0]){_range[0]=rate;}if(_range[1]==null || rate>_range[1]){_range[1]=rate;}}}
        _heartRange=_range;
        if(chart && (right==18 || right==19 || right==28)){
            if(PreviewMode.ENABLED){_history=PreviewMode.trend(right);_range=historyRange();}
            else{var result=LegacyExtras.trend(right,now,[15,30,60][FacePrefs.get("chartMinutes")]);_history=result[:values] as Array;_range=result[:range] as Array;}
        }
    }
    function historyRange(){var lo=null as Numeric or Null;var hi=null as Numeric or Null;for(var i=0;i<_history.size();i++){var v=_history[i] as Numeric or Null;if(v!=null){if(lo==null || v<lo){lo=v;}if(hi==null || v>hi){hi=v;}}}return [lo,hi];}
    function ratio(v,g){return v==null || g==null || g<=0 ? null : v.toFloat()/g;}
    function progress(source){
        switch(source){case 1:return ratio(_values[19],100);case 2:return ratio(_values[1],100);case 3:return ratio(_values[2],_stepGoal);case 4:return ratio(_values[20],_weekGoal!=null ? _weekGoal/7.0 : null);case 5:return ratio(_values[21],_weekGoal);case 6:return ratio(_values[24],5);case 7:return ratio(_values[4],_floorGoal);}return null;
    }
    function goal(key){var v=FacePrefs.get(key+"Goal");if(v>0){return v;}var k=FacePrefs.get(key);if(k==2){return _stepGoal;}if(k==4){return _floorGoal;}if(k==20){return _weekGoal!=null ? _weekGoal/7.0 : null;}if(k==21){return _weekGoal;}if(k==24){return 5;}return k==1 || k==10 || k==12 || k==14 || k==19 || k==22 || k==23 ? 100 : null;}
    function number(kind){
        var v=_values[kind];if(v==null){return null;}
        if(kind==17 && v<0){return null;}
        if((kind==7 || kind==16) && FacePrefs.get("temperatureUnit")==1){v=v*1.8+32;}
        if((kind==3 || kind==13) && FacePrefs.get("distanceUnit")==1){v/=1.609344;}
        if(kind==18 && FacePrefs.get("altitudeUnit")==1){v*=3.28084;}return v;
    }
    function label(kind){
        if(kind==8){return _sunset;}if(kind==9){return _sunrise;}if(kind==15){return _heartRange[0]!=null && _heartRange[1]!=null ? _heartRange[0].toString()+"-"+_heartRange[1].toString() : "--";}
        var v=number(kind);if(v==null){return "--";}var units=FacePrefs.flag("showUnits");
        switch(kind){
            case 3:return v.format("%.1f")+(units ? (FacePrefs.get("distanceUnit")==0 ? "km" : "mi") : "");
            case 7:case 16:return v.format("%.0f")+(units ? (FacePrefs.get("temperatureUnit")==0 ? "°" : "°F") : "");
            case 10:case 12:case 14:case 22:case 23:return v.format("%.0f")+"%";
            case 17:return Math.floor(v).format("%d")+(units ? FaceLocale.days() : "");
            case 18:return v.format("%.0f")+(units ? (FacePrefs.get("altitudeUnit")==0 ? "m" : "ft") : "");
            case 25:return v.format("%.0f")+(units ? "h" : "");case 28:return v.format("%.0f")+(units ? "hPa" : "");
            case 2:case 4:case 5:return FaceFormat.compact(v);
        }return v.format("%.0f");
    }
    function slotText(key){
        var kind=FacePrefs.get(key);if(kind==0){return "";}var style=FacePrefs.get(key+"Style");var r=ratio(number(kind),goal(key));var text=label(kind);
        if(style==2){text=r!=null ? (r*100).format("%.0f")+"%" : "--";}
        if(style==3){var v=number(kind);var g=goal(key);text=v!=null && g!=null ? FaceFormat.shortNumber(v)+"/"+FaceFormat.shortNumber(g) : "--";}
        return text;
    }
    function slot(dc,key,x,y,w,h){
        var kind=FacePrefs.get(key);if(kind==0){return;}var style=FacePrefs.get(key+"Style");var r=ratio(number(kind),goal(key));var text=slotText(key);
        var show=style!=1 && FacePrefs.flag("showIcons");var offset=show ? 19 : 0;
        var size=FacePrefs.fontSize(key)+2;if(_footerSize>=0 && (key.equals("footerLeft") || key.equals("footerRight")) && size>_footerSize){size=_footerSize;}
        var font=FontCatalog.fit(dc,"data",FacePrefs.fontFamily(key),size,text,w-offset,style>=4 ? h-4 : h-1);
        dc.setClip(x,y,w,h);dc.setColor(_ink,_paper);if(show){LegacyIcons.draw(dc,kind,x,y+2,_ink,_paper,_values[1],_condition);}
        dc.drawText(x+offset,y+1,font,text,Graphics.TEXT_JUSTIFY_LEFT);
        if(style==4 || style==5){var p=r!=null ? clamp(r) : 0;var gw=w-offset-1;if(style==4){dc.drawLine(x+offset,y+h-2,x+w-1,y+h-2);if(p>0){dc.fillRectangle(x+offset,y+h-4,Math.ceil(gw*p),2);}}
            else{var cell=(gw-7)/8;for(var i=0;i<8;i++){if(i<Math.ceil(p*8)){dc.fillRectangle(x+offset+i*(cell+1),y+h-4,cell,3);}else{dc.drawLine(x+offset+i*(cell+1),y+h-2,x+offset+i*(cell+1)+cell-1,y+h-2);}}}}
        dc.clearClip();
    }
    function clamp(v){return v<0 ? 0 : (v>1 ? 1 : v);}
    function footer(dc){
        _footerSize=-1;
        if(FacePrefs.flag("linkFooterFonts")){
            var left=slotText("footerLeft");var right=slotText("footerRight");var leftFamily=FacePrefs.fontFamily("footerLeft");var rightFamily=FacePrefs.fontFamily("footerRight");var lo=FacePrefs.flag("showIcons") && FacePrefs.get("footerLeftStyle")!=1 ? 19 : 0;var ro=FacePrefs.flag("showIcons") && FacePrefs.get("footerRightStyle")!=1 ? 19 : 0;var a=FacePrefs.fontSize("footerLeft")+2;var b=FacePrefs.fontSize("footerRight")+2;
            for(var i=a<b ? a : b;i>=0;i--){
                var lf=FontCatalog.data(leftFamily,i);var rf=FontCatalog.data(rightFamily,i);
                if(dc.getTextWidthInPixels(left,lf)<=64-lo && dc.getTextWidthInPixels(right,rf)<=58-ro && dc.getFontHeight(lf)<=16 && dc.getFontHeight(rf)<=16){_footerSize=i;lf=null;rf=null;break;}lf=null;rf=null;
            }
        }
        slot(dc,"footerLeft",30,149,64,20);slot(dc,"footerRight",98,149,58,20);
    }
    function cells(dc){
        if(_cells==null || _cells<=0){return;}var p=clamp(_cells);dc.setColor(_circleInk,_circlePaper);dc.setPenWidth(5);
        if(_cellsStyle==2){if(p>=1){dc.drawCircle(144,31,23);}else{dc.drawArc(144,31,23,Graphics.ARC_CLOCKWISE,90,90-360*p);}}
        else if(_energy!=null){dc.drawBitmap(113+EnergyCatalog.X[_energyCount-1],EnergyCatalog.Y[_energyCount-1],_energy);}
        else{for(var i=0;i<Math.ceil(p*8);i++){dc.drawArc(144,31,23,Graphics.ARC_CLOCKWISE,88-i*45,47-i*45);}}dc.setPenWidth(1);
    }
    function circle(dc){
        var bg=FacePrefs.get("circleBackground");_circlePaper=bg==1 || (bg==2 && _paper==Graphics.COLOR_WHITE) ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK;
        _circleInk=_circlePaper==Graphics.COLOR_WHITE ? Graphics.COLOR_BLACK : Graphics.COLOR_WHITE;
        dc.setColor(_circlePaper,_circlePaper);dc.fillCircle(144,31,31);_cells=progress(FacePrefs.get("cellsSource"));_ring=progress(FacePrefs.get("ringSource"));
        if(_cells!=null && _cells>0 && _cellsStyle!=2){var count=Math.ceil(clamp(_cells)*8).toNumber();var variant=_cellsStyle*2+(_circleInk==Graphics.COLOR_BLACK ? 1 : 0);var key=variant*9+count;if(key!=_energyKey){_energy=null;_energy=EnergyCatalog.load(variant,count);_energyKey=key;_energyCount=count;}}
        else{_energy=null;_energyKey=-1;}cells(dc);
        dc.setColor(_circleInk,_circlePaper);if(_ring!=null && _ring>0){var p=clamp(_ring);var start=[90,0,270,180][FacePrefs.get("ringStart")];var style=FacePrefs.get("ringStyle");dc.setPenWidth(style==0 ? 1 : (style==2 ? 3 : 2));if(style==3){for(var i=0;i<Math.ceil(p*8);i++){dc.drawArc(144,31,29,Graphics.ARC_CLOCKWISE,start-i*45-2,start-i*45-43);}}else if(p>=1){dc.drawCircle(144,31,29);}else{dc.drawArc(144,31,29,Graphics.ARC_CLOCKWISE,start,start-360*p);}dc.setPenWidth(1);}
        var kind=FacePrefs.get("circle");if(kind==0){return;}if(FacePrefs.flag("showCircleIcon") && FacePrefs.get("circleStyle")!=1){LegacyIcons.draw(dc,kind,137,11,_circleInk,_circlePaper,_values[1],_condition);}
        var text=label(kind);var style=FacePrefs.get("circleStyle");var r=ratio(number(kind),goal("circle"));if(style==2){text=r!=null ? (r*100).format("%.0f")+"%" : "--";}if(style==3){var g=goal("circle");text=g!=null && number(kind)!=null ? FaceFormat.shortNumber(number(kind))+"/"+FaceFormat.shortNumber(g) : "--";}
        _heartStyle=style;var target=goal("circle");_heartGoal=target!=null ? target : 0;
        _heartFont=FontCatalog.fit(dc,kind==6 && style<=1 ? "liveheart" : "data",FacePrefs.get("circleFont"),kind==6 && style<=1 ? FacePrefs.get("circleSize") : FacePrefs.get("circleSize")+2,kind==6 ? LiveHeart.text(300,style,_heartGoal) : text,34,23);dc.drawText(144,26,_heartFont,text,Graphics.TEXT_JUSTIFY_CENTER);_painted=_values[6];
    }
    function graph(dc){
        var low=_range[0];var high=_range[1];var chartStyle=FacePrefs.get("chartStyle");dc.setColor(_ink,_paper);dc.setClip(98,126,66,21);var labels=FacePrefs.flag("showChartLabels");var x=labels ? 116 : 99;var width=labels ? 46 : 63;
        if(labels){var selected=FacePrefs.get("chartLabelFont");var font=selected==0 ? WatchUi.loadResource(Rez.Fonts.Chart) : FontCatalog.fit(dc,"data",selected-1,1,"888",15,10);dc.drawText(113,126,font,high!=null ? high.toString() : "--",Graphics.TEXT_JUSTIFY_RIGHT);dc.drawText(113,137,font,low!=null ? low.toString() : "--",Graphics.TEXT_JUSTIFY_RIGHT);}
        dc.drawLine(x,127,x,143);dc.drawLine(x,143,x+width,143);var px=null;var py=null;
        if(low!=null && high!=null){for(var i=0;i<_history.size();i++){var value=_history[i];if(value==null){px=null;continue;}var xx=x+i.toFloat()*width/(_history.size()>1 ? _history.size()-1 : 1);var yy=high==low ? 135 : 143-(value-low).toFloat()*16/(high-low);if(chartStyle!=0){dc.drawLine(xx,yy,xx,143);}if(px!=null && chartStyle!=2){dc.drawLine(px,py,xx,yy);}px=xx;py=yy;}}
        dc.clearClip();
    }
    function onUpdate(nativeDc){
        if(_suspended){return;}
        var dc=DeviceDrawing.target(nativeDc);var now=Time.now();var minute=(now.value()/60).toNumber();
        if(_revision!=FacePrefs.revision){invalidate();_revision=FacePrefs.revision;}
        if(!_force && minute==_minute){partial(dc,now);return;}_force=false;_minute=minute;_heartFont=null;_secondsFont=null;_topImage=null;_bottomImage=null;FontCatalog.reset();_energy=null;_energyKey=-1;LegacyPower.prepare();
        _ink=FacePrefs.flag("darkTheme") ? Graphics.COLOR_WHITE : Graphics.COLOR_BLACK;_paper=_ink==Graphics.COLOR_WHITE ? Graphics.COLOR_BLACK : Graphics.COLOR_WHITE;
        _heartMode=FacePrefs.get("heartRefresh");_heartOn=FacePrefs.flag("showCircle") && FacePrefs.get("circle")==6;_cellsStyle=FacePrefs.get("cellsStyle");
        _side=FacePrefs.flag("showStatus") ? FacePrefs.get("sideData") : 0;_top=0;_bottom=0;
        if(FacePrefs.flag("showStatus") && _side==0){_top=FacePrefs.flag("showBeijingCard") ? FacePrefs.get("topCardImage") : 0;_bottom=FacePrefs.flag("showAlipayCard") ? FacePrefs.get("bottomCardImage") : 0;}
        _secondsMode=SidePanel.secondsMode(FacePrefs.get("secondsMode"),_top,_bottom,_side);_secondsOn=FacePrefs.flag("showSeconds");
        dc.clearClip();dc.setColor(_ink,_paper);dc.clear();if(!DeviceProfile.ANALOG){drawTime(dc);}readData(now);if(DeviceProfile.ANALOG){analog(dc,now);return;}slot(dc,"topOne",34,5,48,20);slot(dc,"topTwo",10,28,FacePrefs.get("topThree")==0 ? 58 : 48,20);slot(dc,"topThree",61,28,48,20);
        if(FacePrefs.flag("showWind") && _wind!=null){var a=(_wind-90)*Math.PI/180;var x=88+6*Math.cos(a);var y=14+6*Math.sin(a);dc.drawLine(88-5*Math.cos(a),14-5*Math.sin(a),x,y);dc.drawLine(x,y,x-4*Math.cos(a-.7),y-4*Math.sin(a-.7));dc.drawLine(x,y,x-4*Math.cos(a+.7),y-4*Math.sin(a+.7));}
        if(FacePrefs.flag("showMoon")){LegacyIcons.moon(dc,FacePrefs.get("topThree")==0 ? 76 : 102,FacePrefs.get("topThree")==0 ? 37 : 54,_moon,_ink,_paper);}
        var date=Gregorian.info(now,Time.FORMAT_SHORT);if(FacePrefs.flag("showDate")){var text=FaceFormat.dateText(date);var font=FontCatalog.fit(dc,"data",FacePrefs.fontFamily("date"),FacePrefs.fontSize("date")+2,text,FacePrefs.flag("showMoveBar") ? 59 : 100,FacePrefs.get("timeFormat")==1 ? 13 : 18);dc.drawText(8,49,font,text,Graphics.TEXT_JUSTIFY_LEFT);font=null;FontCatalog.reset();}
        if(FacePrefs.flag("showMoveBar") && FacePrefs.get("moveSource")!=0){move(dc,FacePrefs.get("topThree")!=0 && FacePrefs.flag("showMoon") ? 67 : 70,50,FacePrefs.get("topThree")!=0 && FacePrefs.flag("showMoon"));}

        if(_side!=0){var text=label(_side);dc.setClip(136,73,35,30);if(FacePrefs.flag("showIcons")){LegacyIcons.draw(dc,_side,146,73,_ink,_paper,_values[1],_condition);}dc.drawText(153,89,FontCatalog.fit(dc,"data",FacePrefs.fontFamily("side"),FacePrefs.fontSize("side")+1,text,32,14),text,Graphics.TEXT_JUSTIFY_CENTER);dc.clearClip();}
        else{if(_top!=0){_topImage=WatchUi.loadResource(LegacyCardArtwork.resource(_top,_paper==Graphics.COLOR_WHITE));card(dc,_top,SidePanel.cardY(_top,_bottom,true),_topImage,true);}if(_bottom!=0){_bottomImage=DeviceProfile.CLIP && _bottom>=3 && _top>=3 ? _topImage : WatchUi.loadResource(LegacyCardArtwork.resource(_bottom,_paper==Graphics.COLOR_WHITE));card(dc,_bottom,SidePanel.cardY(_top,_bottom,false),_bottomImage,false);}}
        slot(dc,"bottomLeft",12,128,82,20);var right=FacePrefs.get("bottomRight");if((right==6 || right==15 || right==18 || right==19 || right==28) && FacePrefs.flag("showHeartGraph") && FacePrefs.get("bottomRightStyle")==6){graph(dc);}else{slot(dc,"bottomRight",98,128,68,20);}
        footer(dc);if(FacePrefs.flag("showCircle")){circle(DeviceDrawing.circleTarget(dc));}
        if(_secondsOn && _secondsMode!=0){_secondsFont=FontCatalog.fit(dc,"data",FacePrefs.get("secondsFont"),4,"88",DeviceProfile.SECONDS_WIDTH-1,DeviceProfile.SECONDS_HEIGHT);}partial(dc,now);
    }
    function move(dc,x,y,compact){
        var source=FacePrefs.get("moveSource");var ratio=progress(source);
        var width=compact ? 3 : 4;var gap=compact ? 0 : 1;
        dc.setColor(_ink,_paper);
        if(source==2){dc.drawRectangle(x,y+3,8,6);dc.fillRectangle(x+8,y+5,1,2);}
        else if(source==1){dc.fillCircle(x+2,y+4,2);dc.fillCircle(x+6,y+4,2);dc.fillPolygon([[x,y+5],[x+8,y+5],[x+4,y+10]]);}
        else{
            dc.fillCircle(x+4,y+1,1);dc.drawLine(x+4,y+4,x+4,y+8);dc.drawLine(x+1,y+7,x+4,y+4);
            dc.drawLine(x+4,y+4,x+7,y+7);dc.drawLine(x+4,y+8,x+2,y+12);dc.drawLine(x+4,y+8,x+6,y+12);
        }
        if(ratio==null){dc.drawLine(x+15,y+6,x+18,y+6);dc.drawLine(x+22,y+6,x+25,y+6);return;}
        if(ratio<0){ratio=0;}if(ratio>1){ratio=1;}
        var style=FacePrefs.get("moveStyle");
        if(style==2){var label=(ratio*100).format("%.0f")+"%";dc.drawText(x+12,y+3,FontCatalog.fit(dc,"data",FacePrefs.fontFamily("move"),1,label,24,10),label,Graphics.TEXT_JUSTIFY_LEFT);return;}
        if(style==1){dc.drawRectangle(x+12,y+5,24,4);if(ratio>0){dc.fillRectangle(x+13,y+6,Math.ceil(22*ratio),2);}return;}
        var count=Math.ceil(ratio*5);
        for(var i=0;i<5;i++){var left=x+12+i*(width+gap);dc.drawRectangle(left,y+4,width,6);if(i<count){dc.fillRectangle(left+1,y+5,width-2,4);}}
    }
    function drawTime(dc){
        var clock=System.getClockTime();var hour=PreviewMode.ENABLED ? 18 : clock.hour;var min=PreviewMode.ENABLED ? 58 : clock.min;
        if(FacePrefs.flag("showTime")){var text=FaceFormat.timeText(hour,min);var font=FontCatalog.fit(dc,"time",FacePrefs.get("timeFont"),FacePrefs.get("timeSize"),text,124,56);dc.setClip(8,72,126,56);dc.drawText(9,72,font,text,Graphics.TEXT_JUSTIFY_LEFT);dc.clearClip();font=null;FontCatalog.reset();if(FacePrefs.get("timeFormat")==1){dc.drawText(8,63,FontCatalog.data(0,1),FaceLocale.period(hour),Graphics.TEXT_JUSTIFY_LEFT);}}
    }
    function analog(dc,now){
        slot(dc,"topOne",66,0,48,16);
        if(FacePrefs.flag("showDate")){var d=FaceFormat.dateText(Gregorian.info(now,Time.FORMAT_SHORT));dc.drawText(8,0,FontCatalog.fit(dc,"data",FacePrefs.fontFamily("date"),FacePrefs.fontSize("date")+2,d,56,16),d,Graphics.TEXT_JUSTIFY_LEFT);}
        var clock=System.getClockTime();var hour=PreviewMode.ENABLED ? 18 : clock.hour;var minute=PreviewMode.ENABLED ? 58 : clock.min;
        if(FacePrefs.flag("showTime")){var t=FaceFormat.timeText(hour,minute);dc.setClip(8,16,103,44);dc.drawText(9,16,FontCatalog.fit(dc,"time",FacePrefs.get("timeFont"),FacePrefs.get("timeSize"),t,103,44),t,Graphics.TEXT_JUSTIFY_LEFT);dc.clearClip();FontCatalog.reset();if(FacePrefs.get("timeFormat")==1){dc.drawText(80,61,FontCatalog.data(0,1),FaceLocale.period(hour),Graphics.TEXT_JUSTIFY_LEFT);}}
        if(FacePrefs.flag("showCircle")){circle(DeviceDrawing.circleTarget(dc));}
        if(_side!=0){var text=label(_side);dc.drawText(146,63,FontCatalog.fit(dc,"data",FacePrefs.fontFamily("side"),FacePrefs.fontSize("side")+1,text,58,14),text,Graphics.TEXT_JUSTIFY_CENTER);}
        else{if(_top!=0){_topImage=WatchUi.loadResource(LegacyCardArtwork.resource(_top,_paper==Graphics.COLOR_WHITE));card(dc,_top,63,_topImage,true);}if(_bottom!=0){_bottomImage=DeviceProfile.CLIP && _bottom>=3 && _top>=3 ? _topImage : WatchUi.loadResource(LegacyCardArtwork.resource(_bottom,_paper==Graphics.COLOR_WHITE));card(dc,_bottom,63,_bottomImage,false);}}
        slot(dc,"bottomLeft",12,128,82,20);var right=FacePrefs.get("bottomRight");if((right==6 || right==15 || right==18 || right==19 || right==28) && FacePrefs.flag("showHeartGraph") && FacePrefs.get("bottomRightStyle")==6){graph(dc);}else{slot(dc,"bottomRight",98,128,68,20);}footer(dc);
        slot(dc,"topTwo",22,164,48,16);slot(dc,"topThree",128,164,36,16);
        if(FacePrefs.flag("showMoon")){LegacyIcons.moon(dc,80,171,_moon,_ink,_paper);}if(FacePrefs.flag("showMoveBar") && FacePrefs.get("moveSource")!=0){move(dc,90,164,true);}
        if(_secondsOn && _secondsMode!=0){_secondsFont=FontCatalog.fit(dc,"data",FacePrefs.get("secondsFont"),4,"88",DeviceProfile.SECONDS_WIDTH-1,DeviceProfile.SECONDS_HEIGHT);}partial(dc,now);
    }
    function card(dc,kind,y,bitmap,isTop){var x=139;if(DeviceProfile.ANALOG){y=63;x=_top!=0 && _bottom!=0 ? (isTop ? 116 : 146) : 132;}if(kind<=2 || !DeviceProfile.CLIP){dc.drawBitmap(x,y,bitmap);}else{dc.setClip(x,y,28,13);dc.drawBitmap(x-(kind-3)*28,y,bitmap);dc.clearClip();}}
    function partial(dc,now){
        if(_heartOn && (_heartMode==0 || (_heartMode==1 && !_sleeping))){refreshHeart(now.value());var circleDc=DeviceDrawing.circleTarget(dc);if(_heartFont!=null && _values[6]!=_painted){circleDc.setClip(126,25,36,25);circleDc.setColor(_circlePaper,_circlePaper);circleDc.fillRectangle(126,25,36,25);cells(circleDc);circleDc.setColor(_circleInk,Graphics.COLOR_TRANSPARENT);circleDc.drawText(144,26,_heartFont,LiveHeart.text(_values[6],_heartStyle,_heartGoal),Graphics.TEXT_JUSTIFY_CENTER);circleDc.clearClip();_painted=_values[6];}}
        var show=_secondsFont!=null && _secondsOn && (_secondsMode==2 || (_secondsMode==1 && !_sleeping));
        if(show || _secondsVisible){dc.setClip(DeviceProfile.SECONDS_LEFT,DeviceProfile.SECONDS_Y,DeviceProfile.SECONDS_WIDTH,DeviceProfile.SECONDS_HEIGHT);dc.setColor(_paper,_paper);dc.fillRectangle(DeviceProfile.SECONDS_LEFT,DeviceProfile.SECONDS_Y,DeviceProfile.SECONDS_WIDTH,DeviceProfile.SECONDS_HEIGHT);if(show){dc.setColor(_ink,_paper);dc.drawText(DeviceProfile.SECONDS_X,DeviceProfile.SECONDS_Y,_secondsFont,System.getClockTime().sec.format("%02d"),Graphics.TEXT_JUSTIFY_CENTER);}dc.clearClip();_secondsVisible=show;}
    }
    function onPartialUpdate(nativeDc){if(_suspended || _force || !_partial){return;}partial(DeviceDrawing.target(nativeDc),Time.now());}
}
