import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.Timer;
import Toybox.WatchUi;

class OfflineSearchView extends WatchUi.View {
    var v;var query="";var state=0;var pending=false;var timer=null;var shown=false;
    var first=0;var last=-1;var page=0;var text=null;var offset=0;var previousName="";var previousPy="";
    var closeAfterSelection=false;var latin=true;var results as Array<Array> = [];var processed=0;var message="";
    (:extendedCode)
    function initialize(view){View.initialize();v=view;}
    (:extendedCode)
    function start(input) {
        query="";var chars=input.toLower().toCharArray();
        for(var i=0;i<chars.size();i++){if(chars[i]!=' '){query+=chars[i].toString();}}
        if(query.length()<2){state=0;message="至少输入两个字母或汉字";return;}
        latin=true;chars=query.toCharArray();for(var i=0;i<chars.size();i++){if(chars[i].toNumber()>127){latin=false;}}
        first=0;last=SearchData.PAGE_N-1;
        if(latin) {
            var code=chars[0].toNumber()*128+chars[1].toNumber();
            var index=Application.loadResource(SearchData.index()) as String;var lo=0;var hi=SearchData.PREFIX_N-1;var found=false;
            while(lo<=hi){var mid=((lo+hi)/2).toNumber();var c=index.substring(mid*6,mid*6+2).toCharArray();var value=c[0].toNumber()*128+c[1].toNumber();
                if(value==code){first=NavCodec.number(index,mid*6+2,2);last=NavCodec.number(index,mid*6+4,2);found=true;break;}
                if(value<code){lo=mid+1;}else{hi=mid-1;}
            }
            if(!found){last=-1;}
        }
        page=first;offset=0;text=null;previousName="";previousPy="";processed=0;results=[];state=1;v.searchQuery=query;try{Application.Storage.setValue("lastQuery",query);}catch(e){}
    }
    (:extendedCode)
    function onShow(){shown=true;if(state==1 || closeAfterSelection){if(timer==null){timer=new Timer.Timer();}timer.start(method(:tick),50,true);}}
    (:extendedCode)
    function onHide(){shown=false;if(timer!=null){timer.stop();}}
    (:extendedCode)
    function input(){WatchUi.pushView(new WatchUi.TextPicker(v.searchQuery),new OfflineTextDelegate(self),WatchUi.SLIDE_UP);}
    (:extendedCode)
    function addResult(name,x,y){
        for(var i=0;i<results.size();i++){if(results[i][0]==name && (results[i][1]-x).abs()<200 && (results[i][2]-y).abs()<200){return;}}
        var px=v.gx==null?v.cx:v.gx;var py=v.gy==null?v.cy:v.gy;var dx=x-px;var dy=y-py;var distance=dx*dx+dy*dy;
        var at=results.size();for(var i=0;i<results.size();i++){if(distance<results[i][3]){at=i;break;}}
        if(at>=20){return;}
        results.add([name,x,y,distance]);
        for(var i=results.size()-1;i>at;i--){results[i]=results[i-1];}results[at]=[name,x,y,distance];
        if(results.size()>20){results=results.slice(0,20);}
    }
    (:extendedCode)
    function tick() as Void {
        if(closeAfterSelection){timer.stop();v.pendingDestination=true;WatchUi.popView(WatchUi.SLIDE_DOWN);return;}
        try{
            var budget=0;
            while(page<=last && budget<40){
                if(text==null){text=Application.loadResource(SearchData.page(page) as ResourceId) as String;offset=0;previousName="";previousPy="";}
                if(offset>=text.length()){text=null;page++;continue;}
                var size=NavCodec.number(text,offset,2);var record=text.substring(offset+2,offset+2+size-1);offset+=2+size;budget++;processed++;
                var split=record.find("|");var namePrefix=NavCodec.number(record,0,1);
                var name=previousName.substring(0,namePrefix)+record.substring(1,split);
                var tail=record.substring(split+1,record.length());var split2=tail.find("|");var pyPrefix=NavCodec.number(tail,0,1);
                var py=previousPy.substring(0,pyPrefix)+tail.substring(1,split2);previousName=name;previousPy=py;
                var match=latin?py.find(query)==0:name.find(query)!=null;
                if(match){var pos=tail.substring(split2+1,tail.length());addResult(name,2*NavCodec.number(pos,0,3),2*NavCodec.number(pos,3,3));}
            }
            WatchUi.requestUpdate();
            if(page>last){timer.stop();text=null;state=2;
                if(results.size()==0){message="没有找到\n请试完整拼音前缀\nGPS重新输入";WatchUi.requestUpdate();return;}
                var menu=new WatchUi.Menu2({:title=>"结果"});
                for(var i=0;i<results.size();i++){var r=results[i];menu.addItem(new WatchUi.MenuItem(r[0],(Math.sqrt(r[3])/1000).format("%.1f")+"km",i,{}));}
                WatchUi.pushView(menu,new SearchResultDelegate(self),WatchUi.SLIDE_UP);
            }
        }catch(e){if(timer!=null){timer.stop();}text=null;state=2;message="索引读取失败\n"+e.getErrorMessage();WatchUi.requestUpdate();}
    }
    (:extendedCode)
    function onUpdate(dc){
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.clear();
        var label=state==1?"离线检索\n"+query+"\n"+((page-first)*100/MathHelper.maximum(1,last-first+1)).toNumber()+"%\nBACK取消":
            (message.length()>0?message:"离线地址搜索\nGPS输入中文或拼音\n例如 tiananmen\n全程不需要手机");
        BodyText.draw(dc,label);
    }
}
class OfflineTextDelegate extends WatchUi.TextPickerDelegate {
    var owner;
    (:extendedCode)
    function initialize(view){TextPickerDelegate.initialize();owner=view;}
    (:extendedCode)
    function onTextEntered(text as String,changed as Boolean) as Boolean {owner.start(text);return true;}
    (:extendedCode)
    function onCancel() as Boolean {return true;}
}
class SearchInputDelegate extends WatchUi.BehaviorDelegate {
    var owner;
    (:extendedCode)
    function initialize(view){BehaviorDelegate.initialize();owner=view;}
    (:extendedCode)
    function onSelect(){if(owner.state!=1){owner.input();}return true;}
    (:extendedCode)
    function onBack(){owner.onHide();owner.text=null;owner.results=[];WatchUi.popView(WatchUi.SLIDE_DOWN);return true;}
}
class SearchResultDelegate extends WatchUi.Menu2InputDelegate {
    var owner;
    (:extendedCode)
    function initialize(view){Menu2InputDelegate.initialize();owner=view;}
    (:extendedCode)
    function onSelect(item){
        var row=owner.results[item.getId() as Number];var v=owner.v;
        v.destination=[row[0],row[1],row[2]];owner.results=[];owner.text=null;
        owner.closeAfterSelection=true;WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
    }
}
class DestinationDelegate extends WatchUi.Menu2InputDelegate {
    var v;
    (:extendedCode)
    function initialize(view){Menu2InputDelegate.initialize();v=view;}
    (:extendedCode)
    function onSelect(item){
        var id=item.getId();WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        if(id==:view){v.cx=v.destination[1];v.cy=v.destination[2];v.follow=false;v.mode=0;WatchUi.requestUpdate();}
        if(id==:route){var view=new RoutingView(v);WatchUi.pushView(view,new RoutingInputDelegate(view),WatchUi.SLIDE_UP);}
    }
}
class RoutingInputDelegate extends WatchUi.BehaviorDelegate {
    var owner;
    (:extendedCode)
    function initialize(view){BehaviorDelegate.initialize();owner=view;}
    (:extendedCode)
    function onBack(){owner.onHide();owner.engine.release();owner.engine.plan.clear();WatchUi.popView(WatchUi.SLIDE_DOWN);return true;}
}
module BodyText {
    (:extendedCode)
    function draw(dc,text){
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);var chars=text.toCharArray();var line="";var y=56;var lineHeight=dc.getFontHeight(Graphics.FONT_XTINY)+1;
        for(var i=0;i<chars.size();i++){
            var c=chars[i].toString();
            if(c=="\n"){dc.drawText(88,y,Graphics.FONT_XTINY,line,Graphics.TEXT_JUSTIFY_CENTER);line="";y+=lineHeight;continue;}
            if(dc.getTextWidthInPixels(line+c,Graphics.FONT_XTINY)>145){dc.drawText(88,y,Graphics.FONT_XTINY,line,Graphics.TEXT_JUSTIFY_CENTER);line="";y+=lineHeight;}
            line+=c;
        }dc.drawText(88,y,Graphics.FONT_XTINY,line,Graphics.TEXT_JUSTIFY_CENTER);
    }
}
