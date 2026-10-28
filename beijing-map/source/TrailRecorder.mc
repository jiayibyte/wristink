import Toybox.ActivityRecording;
import Toybox.Activity;
import Toybox.Application;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;

class TrailRecorder {
    const CAP=1024;
    var points as ByteArray;
    var count=0;var head=0;
    var lastX=null;var lastY=null;var lastAt=0;var lastSave=0;
    var session=null;var recording=true;var failed=false;
    var distance=0.0;var spacing=6.0;
    var elapsedBase=0;var timerStarted=null;
    (:extendedCode)
    function initialize() { points=new [CAP*7]b; }
    function put24(i,n) {points[i]=(n>>16)&255;points[i+1]=(n>>8)&255;points[i+2]=n&255;}
    function get24(i) {return (points[i]<<16)+(points[i+1]<<8)+points[i+2];}
    (:extendedCode)
    function start() {
        recording=true;failed=false;
        if(session!=null){return;}
        try {
            session=ActivityRecording.createSession({:name=>"Beijing Walk",:sport=>Activity.SPORT_WALKING,:subSport=>Activity.SUB_SPORT_GENERIC});
            session.start();
            timerStarted=System.getTimer();
        } catch(e) {session=null;failed=true;recording=false;}
    }
    function addFix(x,y,at) {
        if(!recording){return;}
        if(session==null){start();if(!recording){return;}}
        if(lastX!=null) {
            var dx=x-lastX;var dy=y-lastY;var d=Math.sqrt(dx*dx+dy*dy);
            if(at==lastAt || d<spacing){return;}
            if(at-lastAt<2){return;}
            if(at-lastAt<30 && d>100+30*(at-lastAt)){return;}
            if(at-lastAt<=60){distance+=d;}
        }
        if(count==CAP){
            for(var k=0;k<CAP/2;k++){
                var src=k*14;var dst=k*7;var gap=points[src+6];
                if(k>0 && points[src-1]>0){gap=1;}
                for(var j=0;j<7;j++){points[dst+j]=points[src+j];}points[dst+6]=gap;
            }
            count=CAP/2;head=0;spacing*=2;
        }
        var i=((head+count)%CAP)*7;
        put24(i,(x/2).toNumber());put24(i+3,(y/2).toNumber());
        points[i+6]=(lastX==null || at-lastAt>60)?1:0;
        if(count<CAP){count++;}else{head=(head+1)%CAP;}
        lastX=x;lastY=y;lastAt=at;
        if(at-lastSave>=60){checkpoint();lastSave=at;}
    }
    (:extendedCode)
    function checkpoint() {
        if(count==0){return;}
        try {Application.Storage.setValue("latestTrail",[(points as ByteArray).slice(0,count*7),count,head,distance,elapsedSeconds()]);}catch(e){}
    }
    (:extendedCode)
    function finish() {
        elapsedBase=elapsedSeconds();timerStarted=null;recording=false;checkpoint();
        if(session!=null) {
            try{session.stop();if(!session.save()){failed=true;}else{System.println("TRACK_SAVED points="+count+" meters="+distance);}}catch(e){failed=true;}
            session=null;
        }
    }
    (:extendedCode)
    function reset() {
        finish();points=new [CAP*7]b;count=0;head=0;lastX=null;lastY=null;lastAt=0;distance=0.0;spacing=6.0;elapsedBase=0;timerStarted=null;recording=true;failed=false;
    }
    (:extendedCode)
    function restore() {
        var saved=Application.Storage.getValue("latestTrail");
        if(saved==null){return false;}
        var row=saved as Array;points=row[0] as ByteArray;count=row[1];head=row[2];distance=row[3];recording=false;
        elapsedBase=row.size()>4?row[4]:0;timerStarted=null;
        return count>0;
    }
    (:extendedCode)
    function elapsedSeconds() {
        if(timerStarted==null){return elapsedBase;}
        return elapsedBase+((System.getTimer()-timerStarted)/1000).toNumber();
    }
    function point(i) {
        var offset=((head+i)%CAP)*7;return [2*get24(offset),2*get24(offset+3),points[offset+6]];
    }
}
