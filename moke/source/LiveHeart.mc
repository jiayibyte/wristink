import Toybox.ActivityMonitor;
module LiveHeart {
    const REFRESH_SECONDS=5;
    function due(last,stamp){return last<0 || stamp<last || stamp-last>=REFRESH_SECONDS;}
    var _recentAt=-1;var _recentStamp=-1;var _recentValue=null;
    function fromSample(sample,stamp){
        if(sample==null || sample.when==null || !valid(sample.heartRate)){return null;}
        var age=stamp-sample.when.value();return age>=0 && age<=180 ? sample.heartRate : null;
    }
    function recent(stamp){
        if(!(ActivityMonitor has :getHeartRateHistory)){return null;}
        if(_recentAt<0 || stamp<_recentAt || stamp-_recentAt>=5){
            _recentAt=stamp;var sample=ActivityMonitor.getHeartRateHistory(1,true).next();
            _recentValue=fromSample(sample,stamp);_recentStamp=sample!=null && sample.when!=null ? sample.when.value() : -1;
        }
        return stamp>=_recentStamp && stamp-_recentStamp<=180 ? _recentValue : null;
    }
    function valid(value){return value!=null && value>0 && value<=300 && (!(ActivityMonitor has :INVALID_HR_SAMPLE) || value!=ActivityMonitor.INVALID_HR_SAMPLE);}
    function normalize(value){return valid(value) ? value : null;}
    function secondTick(mode,sleeping){return mode==0 || (mode==1 && !sleeping);}
    function text(value,style,goal){
        if(value==null){return "--";}
        if(style==2 || style==3){
            if(goal<=0){return "--";}
            return style==2 ? (value*100.0/goal).format("%.0f")+"%" : FaceFormat.shortNumber(value)+"/"+FaceFormat.shortNumber(goal);
        }
        return value.format("%d");
    }
}
