module FaceFormat {
    function dateText(d) {
        var english=FaceLocale.english();var index=d.day_of_week-1;
        var days=english ? "SunMonTueWedThuFriSat" : "日一二三四五六";
        var day=days.substring(index*(english ? 3 : 1),(index+1)*(english ? 3 : 1));
        var m=d.month.format("%02d");var n=d.day.format("%02d");var y=d.year.toString();
        var numeric=m+"/"+n;
        switch(FacePrefs.get("dateFormat")){
            case 1:return english ? numeric : d.month.toString()+"月"+d.day.toString()+"日";
            case 2:return y+"/"+numeric;
            case 3:return m+"-"+n+" "+(english ? "" : "周")+day;
            case 4:return day+" "+numeric;
            case 5:return numeric;
            case 6:return y+"-"+m+"-"+n;
            case 7:return english ? numeric+" "+day : d.month.toString()+"月"+d.day.toString()+"日 周"+day;
        }
        return numeric+" "+day;
    }
    function timeText(hour,minute) {
        if (FacePrefs.get("timeFormat")==1) { hour=hour%12; if(hour==0){hour=12;} }
        var sep=[":","."," "][FacePrefs.get("timeSeparator")];
        return hour.format(FacePrefs.flag("leadingZero") ? "%02d" : "%d")+sep+minute.format("%02d");
    }
    function compact(value) {
        if (value>=100000) { return (value/1000.0).format("%.0f")+"k"; }
        if (value>=10000) { return (value/1000).format("%d")+" "+(value%1000).format("%03d"); }
        return value.format("%.0f");
    }
    function shortNumber(value) {
        if (value==null) { return "--"; }
        if (value>=1000) { return (value/1000.0).format("%.1f")+"k"; }
        if (value!=value.toNumber()) { return value.format("%.1f"); }
        return value.format("%.0f");
    }
}
