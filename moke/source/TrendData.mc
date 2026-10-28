import Toybox.SensorHistory;
import Toybox.Time;
import Toybox.Lang;

module TrendData {
    function supported(kind) { return kind==6 || kind==15 || kind==19 || kind==18 || kind==28; }
    function valid(kind,value){
        if(value==null){return false;}
        if(kind==19){return value>=0 && value<=100;}
        if(kind==28){return value>0 && value<1000000;}
        return value>-10000 && value<1000000;
    }
    function fetch(kind,now,minutes) as Dictionary<Symbol, Array<Number or Null>> {
        var options={:period=>new Time.Duration(minutes*60),:order=>SensorHistory.ORDER_OLDEST_FIRST};
        var iterator=null;
        if(kind==19 && (SensorHistory has :getBodyBatteryHistory)){iterator=SensorHistory.getBodyBatteryHistory(options);}
        if(kind==18 && (SensorHistory has :getElevationHistory)){iterator=SensorHistory.getElevationHistory(options);}
        if(kind==28 && (SensorHistory has :getPressureHistory)){iterator=SensorHistory.getPressureHistory(options);}
        var values=[] as Array<Number or Null>;
        if(iterator==null){return {:values=>values,:range=>[null,null]};}
        var sums=[] as Array<Number>;var counts=[] as Array<Number>;
        for(var i=0;i<48;i++){sums.add(0);counts.add(0);}
        var low=null as Number or Null;var high=null as Number or Null;
        var finish=now.value();var period=minutes*60;var start=finish-period;
        var feet=kind==18 && FacePrefs.get("altitudeUnit")==1;
        var sample=iterator.next();
        while(sample!=null){
            if(sample.data!=null && sample.when!=null && sample.when.value()>=start && sample.when.value()<=finish){
                var v=sample.data;
                if(valid(kind,v)){
                    if(kind==28){v=v/100.0;}
                    if(feet){v=v*3.28084;}
                    var n=v.toNumber();
                    if(low==null || n<low){low=n;}if(high==null || n>high){high=n;}
                    var bucket=((sample.when.value()-start)*48/period).toNumber();if(bucket>47){bucket=47;}
                    sums[bucket]+=n;counts[bucket]+=1;
                }
            }
            sample=iterator.next();
        }
        for(var i=0;i<48;i++){values.add(counts[i]>0 ? (sums[i]/counts[i]).toNumber() : null);}
        return {:values=>values,:range=>[low,high]};
    }
}
