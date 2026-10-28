import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Timer;
import Toybox.WatchUi;

class NavError extends Lang.Exception {
    var message;
    (:extendedCode)
    function initialize(text){Exception.initialize();message=text;}
    (:extendedCode)
    function getErrorMessage(){return message;}
}
module NavCodec {
    function number(text,at,size) {
        var chars=text.substring(at,at+size).toCharArray();var n=0;
        for(var i=0;i<chars.size();i++){n=n*64+chars[i].toNumber()-33;}return n;
    }
    (:extendedCode)
    function geometryLength(text,at) {return 3+number(text,at+1,2)*(number(text,at,1)==0?4:6);}
}
class OfflinePages {
    var finePage=-1;var fineText=null;var macroPage=-1;var macroText=null;
    (:extendedCode)
    function initialize(){}
    (:extendedCode)
    function clear(){fineText=null;macroText=null;finePage=-1;macroPage=-1;}
    (:extendedCode)
    function fine(id) {
        macroText=null;macroPage=-1;var page=(id/NavData.FINE_PAGE).toNumber();
        if(page!=finePage){fineText=null;fineText=Application.loadResource(NavData.fine(page) as ResourceId) as String;finePage=page;}
        var count=NavData.FINE_PAGE;if((page+1)*count>NavData.FINE_N){count=NavData.FINE_N-page*NavData.FINE_PAGE;}
        var index=id%NavData.FINE_PAGE;var offset=NavCodec.number(fineText,index*3,3)+count*3;
        var end=index+1<count?NavCodec.number(fineText,(index+1)*3,3)+count*3:fineText.length();
        var record=fineText.substring(offset,end)+" ";return record.substring(0,record.length()-1);
    }
    (:extendedCode)
    function macro(id) {
        fineText=null;finePage=-1;var page=(id/NavData.MACRO_PAGE).toNumber();
        if(page!=macroPage){macroText=null;macroText=Application.loadResource(NavData.macro(page) as ResourceId) as String;macroPage=page;}
        var count=NavData.MACRO_PAGE;if((page+1)*count>NavData.MACRO_N){count=NavData.MACRO_N-page*NavData.MACRO_PAGE;}
        var index=id%NavData.MACRO_PAGE;var offset=NavCodec.number(macroText,index*3,3)+count*3;
        var end=index+1<count?NavCodec.number(macroText,(index+1)*3,3)+count*3:macroText.length();
        var record=macroText.substring(offset,end)+" ";return record.substring(0,record.length()-1);
    }
    (:extendedCode)
    function xy(record){return [2*NavCodec.number(record,0,3),2*NavCodec.number(record,3,3)];}
    (:extendedCode)
    function parent(record){return NavCodec.number(record,6,4);}
    (:extendedCode)
    function root(record){return NavCodec.number(record,10,3);}
    (:extendedCode)
    function macroEdges(record) {
        var edges=[];var n=NavCodec.number(record,13,2);var offset=15;
        for(var i=0;i<n;i++){
            var size=NavCodec.geometryLength(record,offset+14);
            edges.add([NavCodec.number(record,offset,3),NavCodec.number(record,offset+3,3),NavCodec.number(record,offset+6,4),NavCodec.number(record,offset+10,4),record.substring(offset+14,offset+14+size)]);
            offset+=14+size;
        }return edges;
    }
}
class RoutePlan {
    const CAP=3072;
    var points=null;var remainBytes=null;var boxes=null;var count=0;var length=0.0;var name="";var destX=0;var destY=0;
    var lastX=null;var lastY=null;var progress=0;var active=false;var cachePhase=0;var cacheIndex=0;var cacheTotal=0.0;var cachePrevious=null;var cacheGroup=0;var cachePoint=0;var cacheBounds as Array<Number> = [];
    (:extendedCode)
    function initialize(){}
    (:extendedCode)
    function begin(label,x,y){points=new [256*6]b;name=label;destX=x;destY=y;count=0;length=0.0;lastX=null;lastY=null;progress=0;active=false;}
    function put24(i,n){points[i]=(n>>16)&255;points[i+1]=(n>>8)&255;points[i+2]=n&255;}
    function get24(i){return (points[i]<<16)+(points[i+1]<<8)+points[i+2];}
    function point(i){return [get24(i*6)*2,get24(i*6+3)*2];}
    (:extendedCode)
    function add(x,y) {
        if(lastX!=null){var dx=(x-lastX).toFloat();var dy=(y-lastY).toFloat();var distance=Math.sqrt(dx*dx+dy*dy);if(distance<1){return;}length+=distance;}
        var replace=false;
        if(count>=2){
            var a=point(count-2);var b=point(count-1);var dx=(x-a[0]).toFloat();var dy=(y-a[1]).toFloat();var d2=dx*dx+dy*dy;
            if(d2>0){var cross=(b[0]-a[0])*dy-(b[1]-a[1])*dx;var dot=(b[0]-a[0])*dx+(b[1]-a[1])*dy;
                replace=dot>=0 && dot<=d2 && cross*cross<=9*d2;
            }
        }
        var i=replace?count-1:count;if(i>=CAP){throw new NavError("路线太复杂，请分段");}
        if((i+1)*6>points.size()){
            if(System.getSystemStats().freeMemory<12000){throw new NavError("路线太复杂，请选择中途地点分段");}
            points=points.addAll(new [MathHelper.minimum(1536,CAP*6-points.size())]b);
        }
        put24(i*6,(x/2).toNumber());put24(i*6+3,(y/2).toNumber());if(!replace){count++;}lastX=x;lastY=y;
    }
    (:extendedCode)
    function prepareSave(){
        points=(points as ByteArray).slice(0,count*6);
        remainBytes=new [count*2]b;boxes=new [((count+63)/64).toNumber()*12]b;
        cachePhase=1;cacheIndex=count-1;cacheTotal=0.0;cachePrevious=null;cacheGroup=0;cachePoint=0;cacheBounds=[16777215,16777215,0,0];
    }
    (:extendedCode)
    function cacheStep(){
        if(cachePhase==1){
            for(var work=0;work<24 && cacheIndex>=0;work++){
                var p=point(cacheIndex);
                if(cachePrevious!=null){var old=cachePrevious as Array;var dx=(p[0]-old[0]).toFloat();var dy=(p[1]-old[1]).toFloat();cacheTotal+=Math.sqrt(dx*dx+dy*dy);}
                var value=MathHelper.minimum(65535,(cacheTotal/4).toNumber());remainBytes[cacheIndex*2]=(value>>8)&255;remainBytes[cacheIndex*2+1]=value&255;cachePrevious=p;cacheIndex--;
            }
            if(cacheIndex<0){cachePrevious=null;cachePhase=2;}return false;
        }
        var groups=((count+63)/64).toNumber();
        for(var work=0;work<24 && cacheGroup<groups;work++){
            var x=get24(cachePoint*6);var y=get24(cachePoint*6+3);
            cacheBounds[0]=MathHelper.minimum(cacheBounds[0],x);cacheBounds[1]=MathHelper.minimum(cacheBounds[1],y);cacheBounds[2]=MathHelper.maximum(cacheBounds[2],x);cacheBounds[3]=MathHelper.maximum(cacheBounds[3],y);cachePoint++;
            if(cachePoint>=MathHelper.minimum(count,(cacheGroup+1)*64)){
                for(var k=0;k<4;k++){var offset=cacheGroup*12+k*3;var value=cacheBounds[k];boxes[offset]=(value>>16)&255;boxes[offset+1]=(value>>8)&255;boxes[offset+2]=value&255;}
                cacheGroup++;cachePoint=MathHelper.maximum(0,cacheGroup*64-1);cacheBounds=[16777215,16777215,0,0];
            }
        }return cacheGroup>=groups;
    }
    (:extendedCode)
    function box24(i){return (boxes[i]<<16)+(boxes[i+1]<<8)+boxes[i+2];}
    (:extendedCode)
    function save(){
        active=true;
        try{Application.Storage.setValue("routeTarget",[name,destX,destY]);}catch(e){}
        System.println("OFFLINE_ROUTE_SAVED points="+count+" meters="+length);
    }
    (:extendedCode)
    function clear(){points=null;remainBytes=null;boxes=null;count=0;active=false;}
    function draw(dc,cx,cy,scale){
        if(!active || count<2){return;}
        dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.setPenWidth(3);dc.setClip(0,0,176,176);
        var groups=((count+63)/64).toNumber();
        for(var group=0;group<groups;group++){
            var offset=group*12;
            if(2*box24(offset)>cx+88*scale || 2*box24(offset+6)<cx-88*scale || 2*box24(offset+3)>cy+88*scale || 2*box24(offset+9)<cy-88*scale){continue;}
            var previous=null;
            for(var i=MathHelper.maximum(0,group*64-1);i<MathHelper.minimum(count,(group+1)*64);i++){
                var p=point(i) as Array;var x=((p[0]-cx)/scale+88).toNumber();var y=(87-(p[1]-cy)/scale).toNumber();
                if(previous!=null){var a=previous as Array;dc.drawLine(a[0],a[1],x,y);}previous=[x,y];
            }
        }
        dc.setPenWidth(1);dc.clearClip();
    }
    function remaining(x,y){
        if(!active || count==0){return null;}
        var best=1e20;var next=progress;
        for(var i=progress;i<MathHelper.minimum(count,progress+80);i++){var p=point(i);var dx=(p[0]-x).toFloat();var dy=(p[1]-y).toFloat();var d=dx*dx+dy*dy;if(d<best){best=d;next=i;}}
        if(best>40000){return "偏离路线";}progress=next;
        var distance=((remainBytes[next*2]<<8)+remainBytes[next*2+1])*4;
        if(distance<40){return "接近路线终点";}return "剩余 "+(distance/1000).format("%.1f")+"km";
    }
}
module MathHelper {
    (:extendedCode)
    function minimum(a,b){return a<b?a:b;}
    (:extendedCode)
    function maximum(a,b){return a>b?a:b;}
}
class OfflineRouter {
    const MAX=640;const STRIDE=17;const HASH=2048;
    var pages;var state=null;var hash=null;var heap=null;var used=0;var heapCount=0;
    var start;var target;var sourceRoot;var targetRoot;var tx;var ty;var weight=2.5;
    var path as Array<Number> = [];var status="";var finished=false;var failed=false;
    var ranges as Array<Array> = [];var rangeIndex=0;var scanIndex=0;var nearest=-1;var best=62501.0;
    var buildStage=0;var leftChain as Array<Number> = [];var rightChain as Array<Number> = [];var cursor=0;var connectionTarget=0;var leftEnd=0;var rightEnd=0;var leftPos=0;var rightPos=0;var pendingEdge=null;
    var phase=0;var macroStep=0;var current=-1;var plan;var v;
    (:extendedCode)
    function initialize(view){v=view;pages=new OfflinePages();plan=new RoutePlan();}
    (:extendedCode)
    function get(i,size){var n=0;for(var k=0;k<size;k++){n=(n<<8)+state[i+k];}return n;}
    (:extendedCode)
    function put(i,size,n){for(var k=size-1;k>=0;k--){state[i+k]=n&255;n=n>>8;}}
    (:extendedCode)
    function hget(i){return (hash[i*2]<<8)+hash[i*2+1];}
    (:extendedCode)
    function hput(i,n){hash[i*2]=(n>>8)&255;hash[i*2+1]=n&255;}
    (:extendedCode)
    function slot(node){var s=(node*31)%HASH;while(hget(s)!=0 && get((hget(s)-1)*STRIDE,4)!=node){s=(s+1)%HASH;}return s;}
    (:extendedCode)
    function heapGet(i){return (heap[i*2]<<8)+heap[i*2+1];}
    (:extendedCode)
    function heapSet(i,n){heap[i*2]=(n>>8)&255;heap[i*2+1]=n&255;put(n*STRIDE+14,2,i);}
    (:extendedCode)
    function priority(n){return get(n*STRIDE+8,4);}
    (:extendedCode)
    function bubble(i){var n=heapGet(i);while(i>0){var p=((i-1)/2).toNumber();var pn=heapGet(p);if(priority(pn)<=priority(n)){break;}heapSet(i,pn);i=p;}heapSet(i,n);}
    (:extendedCode)
    function push(n){var i=heapCount;heapCount++;heapSet(i,n);bubble(i);}
    (:extendedCode)
    function pop(){
        var n=heapGet(0);heapCount--;if(heapCount>0){var last=heapGet(heapCount);var i=0;
            while(i*2+1<heapCount){var child=i*2+1;if(child+1<heapCount && priority(heapGet(child+1))<priority(heapGet(child))){child++;}if(priority(last)<=priority(heapGet(child))){break;}heapSet(i,heapGet(child));i=child;}heapSet(i,last);
        }put(n*STRIDE+14,2,65535);state[n*STRIDE+16]=1;return n;
    }
    (:extendedCode)
    function heuristic(node){var p=pages.xy(pages.macro(node));var dx=(p[0]-tx).toFloat();var dy=(p[1]-ty).toFloat();return Math.sqrt(dx*dx+dy*dy);}
    (:extendedCode)
    function addState(node,g,parent){
        if(used>=MAX){return false;}var i=used;used++;var offset=i*STRIDE;
        put(offset,4,node);put(offset+4,4,g);put(offset+8,4,(g+weight*heuristic(node)).toNumber());put(offset+12,2,parent);state[offset+16]=0;hput(slot(node),i+1);push(i);return true;
    }
    (:extendedCode)
    function startNearest(x,y){
        tx=x;ty=y;ranges=[];rangeIndex=0;scanIndex=0;nearest=-1;best=62501.0;
        for(var sy=Math.floor((y-250)/2000).toNumber();sy<=Math.floor((y+250)/2000).toNumber();sy++){
            var id=NavData.cells(sy);if(id==null){continue;}var row=Application.loadResource(id) as Dictionary;
            for(var sx=Math.floor((x-250)/2000).toNumber();sx<=Math.floor((x+250)/2000).toNumber();sx++){
                var key=sx.toString();if(row.hasKey(key)){ranges.add(row[key] as Array);}
            }
        }
    }
    (:extendedCode)
    function scanNearest(){
        var budget=0;
        while(rangeIndex<ranges.size() && budget<80){
            var range=ranges[rangeIndex];
            if(scanIndex>=range[1]){rangeIndex++;scanIndex=0;continue;}
            var id=range[0]+scanIndex;var p=pages.xy(pages.fine(id));var dx=(p[0]-tx).toFloat();var dy=(p[1]-ty).toFloat();var d=dx*dx+dy*dy;
            if(d<best){best=d;nearest=id;}scanIndex++;budget++;
        }return rangeIndex>=ranges.size();
    }
    (:extendedCode)
    function begin(){
        if(v.gx==null || System.getTimer()-v.fixTime>30000){error("请先到室外完成GPS定位");return;}
        v.releaseMap();v.nav.clear();status="寻找起点道路";startNearest(v.gx,v.gy);phase=1;
    }
    (:extendedCode)
    function setupSearch(){
        pages.clear();state=new [MAX*STRIDE]b;hash=new [HASH*2]b;heap=new [MAX*2]b;used=0;heapCount=0;
        var goal=pages.macro(targetRoot);var p=pages.xy(goal);tx=p[0];ty=p[1];addState(sourceRoot,0,65535);status="计算离线路线";
    }
    (:extendedCode)
    function searchStep(){
        for(var work=0;work<5;work++){
            if(heapCount==0){error("路网未连通，无法生成步行路线");return;}
            var index=pop();var node=get(index*STRIDE,4);
            if(node==targetRoot){
                path=[];var n=index;
                while(n!=65535){path.add(get(n*STRIDE,4));n=get(n*STRIDE+12,2);}
                var reverse=[];for(var i=path.size()-1;i>=0;i--){reverse.add(path[i]);}path=reverse;
                state=null;heap=null;hash=null;pages.clear();plan.begin(v.destination[0],v.destination[1],v.destination[2]);macroStep=0;current=start;phase=4;status="展开道路曲线";return;
            }
            var edges=pages.macroEdges(pages.macro(node)) as Array<Array>;var g=get(index*STRIDE+4,4);
            for(var i=0;i<edges.size();i++){
                var e=edges[i];var other=e[0];var newG=g+e[1];var existing=hget(slot(other));
                if(existing==0){if(!addState(other,newG,index)){error("路线范围较大，请选择中途地点分段");return;}}
                else {var n=existing-1;var offset=n*STRIDE;if(newG<get(offset+4,4)){
                    put(offset+4,4,newG);put(offset+8,4,(newG+weight*heuristic(other)).toNumber());put(offset+12,2,index);
                    if(state[offset+16]==1){state[offset+16]=0;push(n);}else{bubble(get(offset+14,2));}
                }}
            }
        }
    }
    (:extendedCode)
    function chain(n){
        var result=[];
        for(var i=0;i<4096;i++){result.add(n);var p=pages.parent(pages.fine(n));if(p==n){return result;}n=p;}
        throw new NavError("道路层级异常");
    }
    (:extendedCode)
    function emitGeometry(a,b,geo,reverse){
        var first=pages.xy(pages.fine(a));var last=pages.xy(pages.fine(b));
        var count=NavCodec.number(geo,1,2);var relative=NavCodec.number(geo,0,1)==0;var size=relative?4:6;
        if(!reverse){plan.add(first[0],first[1]);}else{plan.add(last[0],last[1]);}
        for(var k=0;k<count;k++){
            var j=reverse?count-1-k:k;var at=3+j*size;
            var x=relative?first[0]+2*(NavCodec.number(geo,at,2)-2048):2*NavCodec.number(geo,at,3);
            var y=relative?first[1]+2*(NavCodec.number(geo,at+2,2)-2048):2*NavCodec.number(geo,at+3,3);
            plan.add(x,y);
        }
        if(!reverse){plan.add(last[0],last[1]);}else{plan.add(first[0],first[1]);}
    }
    (:extendedCode)
    function parentEdge(child,reverse){var record=pages.fine(child);emitGeometry(child,pages.parent(record),record.substring(13,record.length()),reverse);}
    (:extendedCode)
    function connect(a,b){
        var left=chain(a) as Array;var right=chain(b) as Array;var i=left.size()-1;var j=right.size()-1;
        if(left[i]!=right[j]){throw new NavError("步行道路未连通");}
        while(i>0 && j>0 && left[i-1]==right[j-1]){i--;j--;}
        for(var k=0;k<i;k++){parentEdge(left[k],false);}
        for(var k=j-1;k>=0;k--){parentEdge(right[k],true);}
        if(a==b){var p=pages.xy(pages.fine(a));plan.add(p[0],p[1]);}
    }
    (:extendedCode)
    function expandStep(){
        if(buildStage==0){
            pendingEdge=null;
            if(macroStep+1<path.size()){
                var edges=pages.macroEdges(pages.macro(path[macroStep])) as Array<Array>;
                for(var i=0;i<edges.size();i++){if(edges[i][0]==path[macroStep+1]){pendingEdge=edges[i];break;}}
                if(pendingEdge==null){throw new NavError("道路连接缺失");}
                var edge=pendingEdge as Array;connectionTarget=edge[2];
            }else{connectionTarget=target;}
            leftChain=[];rightChain=[];cursor=current;buildStage=1;
            status="展开路线 "+macroStep+"/"+MathHelper.maximum(1,path.size()-1);
        }
        if(buildStage==1 || buildStage==2){
            for(var work=0;work<6;work++){
                if(buildStage==1){leftChain.add(cursor);if(leftChain.size()>4096){throw new NavError("道路层级异常");}}
                else{rightChain.add(cursor);if(rightChain.size()>4096){throw new NavError("道路层级异常");}}
                var parent=pages.parent(pages.fine(cursor));
                if(parent==cursor){
                    if(buildStage==1){buildStage=2;cursor=connectionTarget;}
                    else{buildStage=3;}
                    break;
                }
                cursor=parent;
            }return;
        }
        if(buildStage==3){
            var i=leftChain.size()-1;var j=rightChain.size()-1;
            if(leftChain[i]!=rightChain[j]){throw new NavError("步行道路未连通");}
            while(i>0 && j>0 && leftChain[i-1]==rightChain[j-1]){i--;j--;}
            leftEnd=i;rightEnd=j;leftPos=0;rightPos=j-1;buildStage=4;
        }
        if(buildStage==4){
            for(var work=0;work<2;work++){
                if(leftPos<leftEnd){parentEdge(leftChain[leftPos],false);leftPos++;continue;}
                if(rightPos>=0){parentEdge(rightChain[rightPos],true);rightPos--;continue;}
                if(current==connectionTarget){var p=pages.xy(pages.fine(current));plan.add(p[0],p[1]);}
                buildStage=5;break;
            }return;
        }
        if(buildStage==5){
            leftChain=[];rightChain=[];
            if(pendingEdge!=null){var edge=pendingEdge as Array;emitGeometry(edge[2],edge[3],edge[4],false);current=edge[3];macroStep++;pendingEdge=null;buildStage=0;}
            else{pages.clear();plan.prepareSave();phase=5;status="整理路线";}
        }
    }
    (:extendedCode)
    function error(text){failed=true;finished=true;status=text;state=null;hash=null;heap=null;pages.clear();plan.clear();}
    (:extendedCode)
    function step(){
        if(finished){return;}
        try{
            if(phase==1 && scanNearest()){
                if(nearest<0){error("当前位置250米内无可算路道路");return;}start=nearest;sourceRoot=pages.root(pages.fine(start));phase=2;status="寻找终点道路";startNearest(v.destination[1],v.destination[2]);
            }else if(phase==2 && scanNearest()){
                if(nearest<0){error("目的地250米内无可算路道路");return;}target=nearest;targetRoot=pages.root(pages.fine(target));
                var a=pages.macro(sourceRoot);var b=pages.macro(targetRoot);
                if(NavCodec.number(a,6,3)!=NavCodec.number(b,6,3)){error("起点与终点的步行道路未连通");return;}
                if(sourceRoot==targetRoot){path=[sourceRoot];pages.clear();plan.begin(v.destination[0],v.destination[1],v.destination[2]);current=start;phase=4;status="展开附近道路";}
                else{phase=3;setupSearch();}
            }else if(phase==3){searchStep();}else if(phase==4){expandStep();}else if(phase==5){if(plan.cacheStep()){plan.save();finished=true;status="路线完成";}}
        }catch(e){error(e.getErrorMessage());}
    }
    (:extendedCode)
    function release(){state=null;hash=null;heap=null;pages.clear();}
}
class RoutingView extends WatchUi.View {
    var v;var engine;var timer;var started=false;
    (:extendedCode)
    function initialize(view){View.initialize();v=view;engine=new OfflineRouter(v);}
    (:extendedCode)
    function onShow(){if(!started){engine.begin();started=true;}if(timer==null){timer=new Timer.Timer();}timer.start(method(:tick),50,true);}
    (:extendedCode)
    function onHide(){if(timer!=null){timer.stop();}}
    (:extendedCode)
    function tick() as Void {
        engine.step();WatchUi.requestUpdate();
        if(engine.finished){
            timer.stop();var failed=engine.failed;var message=engine.status;
            if(!failed){v.nav=engine.plan;}engine.release();
            WatchUi.popView(WatchUi.SLIDE_DOWN);
            if(failed){WatchUi.pushView(new TextView(message),new WatchUi.BehaviorDelegate(),WatchUi.SLIDE_UP);}
            else{v.follow=true;v.mode=0;WatchUi.requestUpdate();}
        }
    }
    (:extendedCode)
    function onUpdate(dc){dc.setColor(Graphics.COLOR_BLACK,Graphics.COLOR_WHITE);dc.clear();BodyText.draw(dc,"离线步行算路\n"+engine.status+"\nBACK取消");}
}
