import Toybox.Application;
import Toybox.ActivityMonitor;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Test;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

(:test)
function refreshIntervals(logger){
    Test.assert(PowerPolicy.due(-1,100,300));
    Test.assert(!PowerPolicy.due(100,399,300));
    Test.assert(PowerPolicy.due(100,400,300));
    Test.assert(PowerPolicy.due(400,100,300)); // Clock moved backwards.
    var history=0;var weather=0;var h=-1;var w=-1;
    for(var second=0;second<3600;second+=60){
        if(PowerPolicy.due(h,second,PowerPolicy.historyPeriod(0))){history++;h=second;}
        if(PowerPolicy.due(w,second,PowerPolicy.weatherPeriod(0))){weather++;w=second;}
    }
    Test.assertEqual(history,12);Test.assertEqual(weather,2);
    Test.assertEqual(PowerPolicy.historyPeriod(1),60);
    Test.assertEqual(PowerPolicy.weatherPeriod(1),300);
    return true;
}

(:test)
function secondsSleepPolicy(logger){
    for(var mode=0;mode<3;mode++){
        Test.assert(!PowerPolicy.seconds(false,mode,true));
        Test.assert(!PowerPolicy.seconds(false,mode,false));
    }
    Test.assert(!PowerPolicy.seconds(true,0,false));
    Test.assert(!PowerPolicy.seconds(true,0,true));
    Test.assert(PowerPolicy.seconds(true,1,false));
    Test.assert(!PowerPolicy.seconds(true,1,true));
    Test.assert(PowerPolicy.seconds(true,2,false));
    Test.assert(PowerPolicy.seconds(true,2,true));
    return true;
}

(:test)
function budgetFallbackPreservesVisibility(logger){
    var view=new InstinctFaceView();view._secondsEnabled=true;view._sleeping=false;
    view._secondsMode=0;view.disablePartialSeconds();
    Test.assert(!PowerPolicy.seconds(view._secondsEnabled,view._secondsMode,view._sleeping));
    view._secondsMode=1;view.disablePartialSeconds();Test.assertEqual(view._secondsMode,1);
    view._secondsMode=2;view.disablePartialSeconds();Test.assertEqual(view._secondsMode,1);
    view._sleeping=true;Test.assert(!PowerPolicy.seconds(true,view._secondsMode,true));
    view._secondsEnabled=false;view.disablePartialSeconds();
    Test.assert(!PowerPolicy.seconds(false,view._secondsMode,false));
    view.suspend();return true;
}

(:test)
function invalidSettingRecovery(logger){
    var key="topOneStyle";var previous=Application.Properties.getValue(key);
    Application.Properties.setValue(key,6);Test.assertEqual(FacePrefs.get(key),0);
    Application.Properties.setValue(key,5);Test.assertEqual(FacePrefs.get(key),5);
    Application.Properties.setValue(key,previous);
    Test.assertEqual(PrefsDefaults.max("bottomRightStyle"),6);
    Test.assertEqual(PrefsDefaults.max("circleStyle"),3);
    Test.assertEqual(PrefsDefaults.max("chartStyle"),2);
    Test.assertEqual(PrefsDefaults.max("dateFormat"),7);
    Test.assertEqual(PrefsDefaults.max("timeSeparator"),2);
    Test.assertEqual(PrefsDefaults.max("chartLabelFont"),3);
    return true;
}

(:test)
function settingsBoundsMatchCatalog(logger){
    for(var group=0;group<SettingsCatalog.COUNT;group++){
        for(var page=0;page<SettingsCatalog.pages(group);page++){
            var rows=SettingsCatalog.rows(group,page);
            for(var i=0;i<rows.size();i++){
                var row=rows[i] as Array;
                if(row[2]==1){continue;}
                var expected=row[2]==2 ? 1000000 : SettingsCatalog.choices(row[4]).size()-1;
                Test.assertEqual(PrefsDefaults.max(row[0]),expected);
            }
            rows=[];
        }
    }
    return true;
}

(:test)
function rootMenuPagination(logger){
    var expected=[8,9,3]; // Six groups plus navigation/reset, then the last group.
    for(var page=0;page<3;page++){
        var menu=new FaceSettingsMenu(page);var count=0;
        while(menu.deleteItem(0)==true){count++;}
        Test.assertEqual(count,expected[page]);menu=null;
    }
    return true;
}

(:test)
class HistorySample {
    var when;var heartRate;
    function initialize(stamp,rate){when=stamp==null ? null : new Time.Moment(stamp);heartRate=rate;}
}
(:test)
class HistoryFixture {
    var _samples as Array;var _index=0;
    function initialize(samples as Array){_samples=samples;}
    function next(){if(_index>=_samples.size()){return null;}var value=_samples[_index];_index+=1;return value;}
}
(:test)
function historyGapsAndInvalidValues(logger){
    var iterator=new HistoryFixture([
        new HistorySample(1040,60),new HistorySample(1090,90),new HistorySample(1100,120),
        new HistorySample(1039,200),new HistorySample(1101,240),new HistorySample(null,150),
        new HistorySample(1080,ActivityMonitor.INVALID_HR_SAMPLE),new HistorySample(1081,301)]);
    var result=HeartAnalytics.window(iterator,new Time.Moment(1100),1);
    var values=result[:values] as Array;var limits=result[:range] as Array;
    Test.assertEqual(values.size(),48);Test.assertEqual(values[0],60);Test.assertEqual(values[47],120);
    Test.assert(values[1]==null);Test.assertEqual(limits[0],60);Test.assertEqual(limits[1],120);
    Test.assert(TrendData.valid(19,0));Test.assert(!TrendData.valid(19,-1));Test.assert(!TrendData.valid(19,101));
    Test.assert(TrendData.valid(18,-50));Test.assert(!TrendData.valid(28,0));Test.assert(TrendData.valid(28,101300));
    limits=HeartAnalytics.range([-50,0,20],18);Test.assertEqual(limits[0],-50);Test.assertEqual(limits[1],20);
    return true;
}

(:test)
function sparseHeartHistoryConnects(logger){
    // Normal 60/120-second history is sparse in a 48-column chart. Missing
    // buckets between actual readings must not turn the line into isolated dots.
    for(var minutes=15;minutes<=60;minutes*=2){
        for(var cadence=60;cadence<=120;cadence+=60){
            var finish=10000;var start=finish-minutes*60;var samples=[];
            // Newest-first, matching the production history request.
            for(var n=4;n>=0;n--){samples.add(new HistorySample(start+60+n*cadence,60+n*10));}
            var result=HeartAnalytics.window(new HistoryFixture(samples),new Time.Moment(finish),minutes);
            var values=result[:values] as Array;var limits=result[:range] as Array;
            var first=(60*48/(minutes*60)).toNumber();
            var last=((60+4*cadence)*48/(minutes*60)).toNumber();
            for(var i=first;i<=last;i++){Test.assert(values[i]!=null);Test.assert(values[i]>=60 && values[i]<=100);}
            if(first>0){Test.assert(values[first-1]==null);}
            Test.assert(values[last+1]==null);
            Test.assertEqual(limits[0],60);Test.assertEqual(limits[1],100);
        }
    }
    return true;
}

(:test)
function heartHistoryPreservesTrueGaps(logger){
    var start=1000;var now=new Time.Moment(1900);
    var result=HeartAnalytics.window(new HistoryFixture([
        new HistorySample(start+60,60),
        new HistorySample(start+120,ActivityMonitor.INVALID_HR_SAMPLE),
        new HistorySample(start+180,80),new HistorySample(start+300,100),
        new HistorySample(start+660,90)]),now,15);
    var values=result[:values] as Array;
    Test.assert(values[0]==null); // Never extend a line outside measured history.
    Test.assert(values[6]==null); // Explicit invalid sample remains a real break.
    Test.assert(values[12]!=null); // Ordinary sparse interval remains connected.
    Test.assert(values[25]==null); // Six-minute missing-history gap stays empty.
    Test.assert(values[47]==null);
    return true;
}

(:test)
class HeartPlotFixtureDc {
    var lines=0;var points=0;
    function setClip(x,y,w,h){}function clearClip(){}function setColor(ink,paper){}
    function drawLine(x1,y1,x2,y2){lines++;}function drawPoint(x,y){points++;}
    function drawText(x,y,font,text,justify){}function getFontHeight(font){return 7;}
}

(:test)
class BatteryFixtureDc {
    var code="";
    function setColor(ink,paper){}
    function drawText(x,y,font,text,justify){code=text;}
}

(:test)
function batteryStylePreservesLevels(logger){
    var dc=new BatteryFixtureDc();
    var input=[-1,0,12.49,12.5,25,50,99.99,100,101];
    var expected=["0","0","0","1","2","4","7","8","8"];
    for(var i=0;i<input.size();i++){
        NativeStyle.battery(dc,0,0,Graphics.COLOR_WHITE,Graphics.COLOR_BLACK,input[i]);
        Test.assertEqual(dc.code,expected[i]);
    }
    NativeStyle.reset();return true;
}

(:test)
function shaftArrowKeepsDirectionAndAnchor(logger){
    var input=[0,45,90,180,270,360,-90,359.9];var expected=[0,4,8,16,24,0,24,0];
    for(var i=0;i<input.size();i++){Test.assertEqual(NativeStyle.windIndex(input[i]),expected[i]);}
    var dc=new ShaftWindFixtureDc();NativeStyle.windArrow(dc,88,14,90,Graphics.COLOR_WHITE,Graphics.COLOR_BLACK);
    Test.assertEqual(dc.code,"8");Test.assertEqual(dc.x,81);Test.assertEqual(dc.y,7);
    NativeStyle.reset();return true;
}

(:test)
class ShaftWindFixtureDc {
    var code="";var x=0;var y=0;
    function setColor(ink,paper){}
    function drawText(xx,yy,font,text,justify){x=xx;y=yy;code=text;}
}

(:test)
function whiteHeartUpgradeAppliesOnce(logger){
    var bg=Application.Properties.getValue("circleBackground");var cells=Application.Properties.getValue("cellsSource");var ring=Application.Properties.getValue("ringSource");
    var marker=Application.Storage.getValue("plainWhiteHeartV6");
    Application.Storage.deleteValue("plainWhiteHeartV6");
    Application.Properties.setValue("circleBackground",0);Application.Properties.setValue("cellsSource",1);Application.Properties.setValue("ringSource",4);
    FacePrefs.migrate();
    Test.assertEqual(FacePrefs.get("circleBackground"),1);Test.assertEqual(FacePrefs.get("cellsSource"),0);Test.assertEqual(FacePrefs.get("ringSource"),0);
    Test.assertEqual(Application.Storage.getValue("plainWhiteHeartV6"),true);
    Application.Properties.setValue("circleBackground",0);Application.Properties.setValue("cellsSource",1);Application.Properties.setValue("ringSource",4);
    FacePrefs.migrate();
    Test.assertEqual(FacePrefs.get("circleBackground"),0);Test.assertEqual(FacePrefs.get("cellsSource"),1);Test.assertEqual(FacePrefs.get("ringSource"),4);
    Application.Properties.setValue("circleBackground",bg);Application.Properties.setValue("cellsSource",cells);Application.Properties.setValue("ringSource",ring);
    if(marker==null){Application.Storage.deleteValue("plainWhiteHeartV6");}else{Application.Storage.setValue("plainWhiteHeartV6",marker);}
    FacePrefs.reload();return true;
}

(:test)
class WhiteHeartFixtureDc {
    var ink;var clearInk;var textInk;var code="";var y=0;var bitmapCalls=0;var arcCalls=0;var rect=[];
    function setColor(a,b){ink=a;}function setClip(x,y,w,h){}function clearClip(){}
    function fillRectangle(x,y,w,h){rect=[x,y,w,h];clearInk=ink;}
    function getFontHeight(font){return 26;}
    function drawText(x,yy,font,text,justify){code=text;y=yy;textInk=ink;}
    function drawBitmap(x,y,bitmap){bitmapCalls++;}
    function setPenWidth(w){}function drawCircle(x,y,r){arcCalls++;}function drawArc(x,y,r,d,a,b){arcCalls++;}
}

(:test)
function whiteHeartPartialUpdateKeepsWhiteDisc(logger){
    var keys=["circleBackground","cellsSource","ringSource","circleStyle","circleFont","circleSize","showCircleIcon"];
    var previous=[];for(var i=0;i<keys.size();i++){previous.add(Application.Properties.getValue(keys[i]));}
    var values=[1,0,0,0,0,1,true];for(var i=0;i<keys.size();i++){Application.Properties.setValue(keys[i],values[i]);}
    var bitmap=Graphics.createBufferedBitmap({:width=>1,:height=>1,:palette=>[Graphics.COLOR_BLACK,Graphics.COLOR_WHITE]});
    FaceDraw.prepareLiveHeart(bitmap.get().getDc(),Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
    Test.assert(FaceDraw._hrPlain);Test.assertEqual(bitmap.get().getDc().getFontHeight(FaceDraw._hrFontTwo),26);
    var progress=FaceDraw.cellsProgress;FaceDraw.cellsProgress=.75;var dc=new WhiteHeartFixtureDc();
    FaceDraw.refreshLiveHeart(dc,99);FaceDraw.refreshLiveHeart(dc,100);
    Test.assertEqual(dc.code,"100");Test.assertEqual(dc.clearInk,Graphics.COLOR_WHITE);Test.assertEqual(dc.textInk,Graphics.COLOR_BLACK);
    Test.assertEqual(dc.bitmapCalls,0);Test.assertEqual(dc.arcCalls,0);Test.assertEqual(dc.y,25);
    Test.assertEqual(dc.rect[0],121);Test.assertEqual(dc.rect[1],23);Test.assertEqual(dc.rect[2],47);Test.assertEqual(dc.rect[3],29);
    Application.Properties.setValue("showCircleIcon",false);FaceDraw.prepareLiveHeart(bitmap.get().getDc(),Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);
    FaceDraw.refreshLiveHeart(dc,99);Test.assertEqual(dc.y,18);Test.assertEqual(dc.rect[1],16);Test.assertEqual(dc.rect[3],30);
    FaceDraw.cellsProgress=progress;FaceDraw.enterSettings();
    for(var i=0;i<keys.size();i++){Application.Properties.setValue(keys[i],previous[i]);}
    FacePrefs.reload();return true;
}

(:test)
function sparseHeartHistoryDrawsLine(logger){
    var labels=Application.Properties.getValue("showChartLabels");
    var style=Application.Properties.getValue("chartStyle");
    Application.Properties.setValue("showChartLabels",false);Application.Properties.setValue("chartStyle",0);
    var result=HeartAnalytics.window(new HistoryFixture([
        new HistorySample(1100,60),new HistorySample(1220,90),new HistorySample(1340,70)]),new Time.Moment(1900),15);
    var dc=new HeartPlotFixtureDc();FaceDraw.heartPanel(dc,result[:values],result[:range]);
    Test.assert(dc.lines>2); // Two axes alone used to be the only lines drawn.
    Test.assert(dc.points>3);
    Application.Properties.setValue("showChartLabels",labels);Application.Properties.setValue("chartStyle",style);
    FaceDraw.enterSettings();return true;
}

(:test)
function suspendReleasesRenderResources(logger){
    var view=new InstinctFaceView();
    var previous=Application.Properties.getValue("timeFormat");Application.Properties.setValue("timeFormat",0);
    var bitmap=Graphics.createBufferedBitmap({:width=>1,:height=>1,:palette=>[Graphics.COLOR_BLACK,Graphics.COLOR_WHITE]});
    FaceDraw.time(bitmap.get().getDc(),18,58);
    Test.assertEqual(FontCatalog._fonts.size(),0); // The large time font must not survive into lower slots.
    Application.Properties.setValue("timeFormat",previous);
    FaceDraw._chart=WatchUi.loadResource(Rez.Fonts.Chart);
    FaceDraw._topCard=WatchUi.loadResource(CardArtwork.resource(1,false));
    NativeStyle.moon(bitmap.get().getDc(),7,7,.25,Graphics.COLOR_WHITE,Graphics.COLOR_BLACK);
    NativeStyle.activity(bitmap.get().getDc(),0,0,Graphics.COLOR_WHITE,Graphics.COLOR_BLACK);
    NativeStyle.windArrow(bitmap.get().getDc(),7,7,90,Graphics.COLOR_WHITE,Graphics.COLOR_BLACK);
    Test.assert(NativeStyle._moon!=null);Test.assert(NativeStyle._upper!=null);
    Test.assert(NativeStyle._wind!=null);
    view.suspend();
    Test.assert(FaceDraw._chart==null);Test.assert(FaceDraw._topCard==null);
    Test.assert(FaceDraw._energyBitmap==null);Test.assert(FaceDraw._hrFontTwo==null);
    Test.assert(NativeStyle._moon==null);Test.assert(NativeStyle._upper==null);
    Test.assert(NativeStyle._wind==null);
    Test.assert(view._weather==null);Test.assertEqual(view._planRevision,-1);
    return true;
}

(:test)
function exclusiveCardsAndSeconds(logger){
    for(var mode=0;mode<4;mode++){
        Test.assertEqual(SidePanel.secondsMode(mode,1,2,0),0);
        Test.assertEqual(SidePanel.secondsMode(mode,1,0,0),0);
        Test.assertEqual(SidePanel.secondsMode(mode,0,2,0),0);
        Test.assertEqual(SidePanel.secondsMode(mode,0,0,28),0);
    }
    Test.assertEqual(SidePanel.secondsMode(0,0,0,0),2);
    Test.assertEqual(SidePanel.secondsMode(1,0,0,0),1);
    Test.assertEqual(SidePanel.secondsMode(2,0,0,0),2);
    Test.assertEqual(SidePanel.secondsMode(3,0,0,0),0);
    Test.assertEqual(SidePanel.cardY(1,2,true),84);
    Test.assertEqual(SidePanel.cardY(1,2,false),104);
    Test.assertEqual(SidePanel.cardY(1,0,true),94);
    Test.assertEqual(SidePanel.cardY(0,2,false),94);
    return true;
}

(:test)
function packedMenuCaptions(logger){
    var rows=SettingsCatalog.rows(4,0);
    for(var i=0;i<rows.size();i++){
        var row=rows[i] as Array;
        if(row[0].equals("topCardImage")){
            Test.assert(SettingsCatalog.label(row[4],1).find(FaceLocale.english() ? "Beijing transit" : "北京公交卡")==0);
            Test.assert(SettingsCatalog.label(row[4],14).find(FaceLocale.english() ? "Paw" : "猫爪")==0);
            Test.assert(SettingsCatalog.label(row[4],20).find(FaceLocale.english() ? "Heart" : "爱心")==0);
        }
        if(row[0].equals("sideData")){Test.assert(SettingsCatalog.label(row[4],6).find(FaceLocale.english() ? "Heart rate" : "心率")==0);}
    }
    return true;
}

(:test)
function demandSources(logger){
    Test.assertEqual(PowerPolicy.metric(0),0);
    Test.assertEqual(PowerPolicy.metric(14),0); // Moon uses time, not a sensor.
    Test.assertEqual(PowerPolicy.metric(15),PowerPolicy.RANGE);
    Test.assertEqual(PowerPolicy.metric(19),PowerPolicy.BODY);
    Test.assertEqual(PowerPolicy.metric(18),PowerPolicy.LIVE);
    Test.assertEqual(PowerPolicy.metric(8),PowerPolicy.WEATHER|PowerPolicy.SUN);
    Test.assertEqual(PowerPolicy.progress(0),0);
    Test.assertEqual(PowerPolicy.progress(1),PowerPolicy.BODY);
    Test.assertEqual(PowerPolicy.progress(2),PowerPolicy.STATS);
    for(var source=3;source<=7;source++){Test.assertEqual(PowerPolicy.progress(source),PowerPolicy.ACTIVITY);}
    return true;
}

(:test)
class HeartTickView extends InstinctFaceView {
    var samples=0;var paints=0;var supplied=96;
    function initialize(){InstinctFaceView.initialize();}
    function readLiveHeart(stamp){samples++;return supplied;}
    function paintLiveHeart(dc,value){paints++;}
}

(:test)
function currentHeartEveryFiveSeconds(logger){
    var view=new HeartTickView();view._heartCircle=true;view._heartMode=0;view._sleeping=true;
    var bitmap=Graphics.createBufferedBitmap({:width=>1,:height=>1,:palette=>[Graphics.COLOR_BLACK,Graphics.COLOR_WHITE]});var dc=bitmap.get().getDc();
    view.updateLiveHeart(dc,100);view.updateLiveHeart(dc,100);
    Test.assertEqual(view.samples,1);Test.assertEqual(view.paints,1);
    view.updateLiveHeart(dc,101);view.updateLiveHeart(dc,104);
    Test.assertEqual(view.samples,1);Test.assertEqual(view.paints,1);
    view.updateLiveHeart(dc,105); // Unchanged value is read at five seconds, not repainted.
    Test.assertEqual(view.samples,2);Test.assertEqual(view.paints,1);
    view.supplied=100;view.updateLiveHeart(dc,110);
    Test.assertEqual(view.samples,3);Test.assertEqual(view.paints,2);Test.assertEqual(view._heartValue,100);
    view.supplied=null;view.updateLiveHeart(dc,115);
    Test.assert(view._heartValue==null);Test.assertEqual(view.paints,3);
    view._heartMode=2;view.updateLiveHeart(dc,120);Test.assertEqual(view.samples,4);
    view._heartMode=1;view.updateLiveHeart(dc,120);Test.assertEqual(view.samples,4);
    view._sleeping=false;view.supplied=98;view.updateLiveHeart(dc,120);
    Test.assertEqual(view.samples,5);Test.assertEqual(view.paints,4);
    view._heartCircle=false;view.updateLiveHeart(dc,125);Test.assertEqual(view.samples,5);
    view._heartCircle=true;view._heartMode=0;view.updateLiveHeart(dc,119); // Clock correction must not freeze sampling.
    Test.assertEqual(view.samples,6);Test.assertEqual(view.paints,4);
    view._forceFrame=false;view._secondsEnabled=false;view.disablePartialHeart();
    view.onPartialUpdate(dc);Test.assertEqual(view.samples,6);
    view.suspend();FaceDraw.enterSettings();return true;
}

(:test)
function currentHeartValidation(logger){
    Test.assert(LiveHeart.normalize(null)==null);Test.assert(LiveHeart.normalize(0)==null);
    Test.assert(LiveHeart.normalize(ActivityMonitor.INVALID_HR_SAMPLE)==null);
    Test.assertEqual(LiveHeart.normalize(99),99);
    Test.assertEqual(LiveHeart.text(99,0,0),"99");Test.assertEqual(LiveHeart.text(100,0,0),"100");
    Test.assertEqual(LiveHeart.text(null,0,0),"--");
    Test.assertEqual(LiveHeart.text(100,2,200),"50%");
    Test.assertEqual(LiveHeart.text(100,3,200),"100/200");
    Test.assertEqual(LiveHeart.text(100,2,0),"--");
    Test.assertEqual(LiveHeart.fromSample(new HistorySample(1000,96),1180),96);
    Test.assert(LiveHeart.fromSample(new HistorySample(1000,96),1181)==null);
    Test.assert(LiveHeart.fromSample(new HistorySample(1000,96),999)==null);
    Test.assert(LiveHeart.fromSample(new HistorySample(null,96),1000)==null);
    return true;
}

(:test)
class ReadCountingView extends InstinctFaceView {
    var reads=0;var historyReads=0;var weatherReads=0;
    function initialize(){InstinctFaceView.initialize();}
    function readData(now){reads++;InstinctFaceView.readData(now);}
    function refreshHeart(now){historyReads++;InstinctFaceView.refreshHeart(now);}
    function refreshWeather(now){weatherReads++;InstinctFaceView.refreshWeather(now);}
}

(:test)
function hiddenAndMinuteReuse(logger){
    var slots=["topOne","topTwo","topThree","bottomLeft","bottomRight","footerLeft","footerRight"];
    for(var i=0;i<slots.size();i++){Application.Properties.setValue(slots[i],0);}
    var flags=["showTime","showDate","showCircle","showStatus","showMoveBar","showWind","showMoon","showSeconds"];
    for(var i=0;i<flags.size();i++){Application.Properties.setValue(flags[i],false);}
    FacePrefs.reload();
    var view=new ReadCountingView();
    // A tiny real DC exercises the actual update gate without a full-screen RAM buffer.
    var bitmap=Graphics.createBufferedBitmap({:width=>1,:height=>1,:palette=>[Graphics.COLOR_BLACK,Graphics.COLOR_WHITE]});
    var dc=bitmap.get().getDc();
    var epoch=1792368000; // Aligned to the start of a minute.
    for(var second=0;second<120;second++){view.updateAt(dc,new Time.Moment(epoch+second));}
    Test.assertEqual(view.reads,2); // 120 callbacks, two full updates.
    Test.assertEqual(view._needs,0);
    Test.assertEqual(view.historyReads,0);Test.assertEqual(view.weatherReads,0);
    Test.assertEqual(view._bodyAt,-1);Test.assert(view._heartValue==null);
    var before=view.reads;
    for(var i=0;i<59;i++){view.onPartialUpdate(dc);}
    Test.assertEqual(view.reads,before);
    view.suspend();
    view.updateAt(dc,new Time.Moment(epoch+120));view.onPartialUpdate(dc);
    Test.assertEqual(view.reads,before); // A native settings menu may still deliver face callbacks.
    view.invalidate();view.updateAt(dc,new Time.Moment(epoch+120));
    Test.assertEqual(view.reads,before); // Phone settings must not resume a covered face.
    view.onShow();view.updateAt(dc,new Time.Moment(epoch+119));
    Test.assertEqual(view.reads,before+1);
    before=view.reads;
    // Same-minute preference changes must not be swallowed by the minute cache.
    Application.Properties.setValue("topOne",19);FacePrefs.reload();
    view.updateAt(dc,new Time.Moment(epoch+119));
    Test.assertEqual(view.reads,before+1);Test.assertEqual(view._needs,PowerPolicy.BODY);
    Test.assertEqual(FaceDraw.bodyBattery,PreviewMode.BODY_BATTERY);
    view.suspend();FaceDraw.enterSettings();
    return true;
}

(:test)
function bilingualDateAndUnits(logger){
    var previousLocale=FaceLocale._english;var previousFormat=Application.Properties.getValue("dateFormat");
    var d=Gregorian.info(new Time.Moment(1792368000),Time.FORMAT_SHORT);
    d.month=10;d.day=19;d.year=2026;d.day_of_week=2;
    FaceLocale._english=true;
    var expected=["10/19 Mon","10/19","2026/10/19","10-19 Mon","Mon 10/19","10/19","2026-10-19","10/19 Mon"];
    for(var i=0;i<8;i++){Application.Properties.setValue("dateFormat",i);Test.assertEqual(FaceFormat.dateText(d),expected[i]);}
    Test.assertEqual(FaceLocale.days(),"d");Test.assertEqual(FaceLocale.period(0),"AM");Test.assertEqual(FaceLocale.period(12),"PM");
    FaceLocale._english=false;Application.Properties.setValue("dateFormat",0);
    Test.assertEqual(FaceFormat.dateText(d),"10/19 一");Test.assertEqual(FaceLocale.days(),"天");Test.assertEqual(FaceLocale.period(12),"下午");
    FaceLocale._english=previousLocale;Application.Properties.setValue("dateFormat",previousFormat);return true;
}
