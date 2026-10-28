import Toybox.Lang;
import Toybox.ActivityMonitor;
import Toybox.Time;

module HeartAnalytics {
    // Join normal sparse history readings, but never draw across an explicit
    // invalid sample or a long period without recorded heart-rate data.
    const MAX_LINE_GAP_SECONDS=180;
    // The chart is bounded to 48 buckets, while min/max include every valid sample.
    function window(iterator, now as Time.Moment, minutes) as Dictionary<Symbol, Array<Number or Null>> {
        var sums = [] as Array<Number>;
        var counts = [] as Array<Number>;
        var invalid = [] as Array<Boolean>;
        var first = [] as Array<Number or Null>;
        var last = [] as Array<Number or Null>;
        for (var i = 0; i < 48; i++) { sums.add(0); counts.add(0); invalid.add(false); first.add(null); last.add(null); }
        var low = null as Number or Null;
        var high = null as Number or Null;
        var finish = now.value();
        var period = minutes*60;
        var start = finish - period;
        var sample = iterator.next();
        while (sample != null) {
            var when = sample.when;
            // An undated sample cannot be placed at the right edge as if it were current.
            var stamp = when != null ? when.value() : start-1;
            if (stamp >= start && stamp <= finish) {
                var bucket = ((stamp - start) * 48 / period).toNumber();
                if (bucket > 47) { bucket = 47; }
                var rate = sample.heartRate;
                if (LiveHeart.valid(rate)) {
                    if (low == null || rate < low) { low = rate; }
                    if (high == null || rate > high) { high = rate; }
                    sums[bucket] += rate;
                    counts[bucket] += 1;
                    if(first[bucket]==null || stamp<first[bucket]){first[bucket]=stamp;}
                    if(last[bucket]==null || stamp>last[bucket]){last[bucket]=stamp;}
                }else{
                    invalid[bucket]=true;
                }
            }
            sample = iterator.next();
        }
        var values = [] as Array<Number or Null>;
        for (var i = 0; i < 48; i++) {
            if (counts[i] > 0) { values.add((sums[i] / counts[i]).toNumber()); }
            else { values.add(null); }
        }
        // Empty display buckets are not failed measurements. Fill only between
        // genuine nearby readings so the existing renderer can connect them.
        // Keep the range above based solely on measured samples.
        var previous=-1;var blocked=false;
        for(var i=0;i<48;i++){
            if(invalid[i]){blocked=true;}
            if(values[i]==null){continue;}
            if(previous>=0 && !blocked){
                var aTime=last[previous];var bTime=first[i];
                if(aTime!=null && bTime!=null && bTime>=aTime && bTime-aTime<=MAX_LINE_GAP_SECONDS){
                    var a=values[previous] as Number;var b=values[i] as Number;
                    for(var j=previous+1;j<i;j++){
                        values[j]=(a+(b-a).toFloat()*(j-previous)/(i-previous)).toNumber();
                    }
                }
            }
            previous=i;blocked=invalid[i];
        }
        return {:values => values, :range => [low, high]};
    }
    function range(values as Array<Number or Null>,kind) as Array<Number or Null> {
        var low = null as Number or Null;
        var high = null as Number or Null;
        for (var i = 0; i < values.size(); i++) {
            var rate = values[i];
            if (kind==6 || kind==15 ? !LiveHeart.valid(rate) : !TrendData.valid(kind,rate)) { continue; }
            if (low == null || rate < low) { low = rate; }
            if (high == null || rate > high) { high = rate; }
        }
        return [low, high];
    }

}
