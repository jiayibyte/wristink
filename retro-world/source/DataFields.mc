module DataFields {
    // All values come from the existing minute/environment caches. Only HR is
    // sampled on the tick path; no settings, weather or history reads there.
    function label(kind) {
        var names=["","HR","BAT","STEP","KCAL","ALT","DIST","WX","RISE","SET","BAT","GOAL","FLOOR","ACTIVE","MSG"];
        return names[kind];
    }
    function value(kind) {
        if(kind==0) {return "";}
        if(kind==1) {return LiveData.numeric(LiveData.heart);}
        if(kind==2) {return LiveData.daysText(LiveData.batteryDays)+"D";}
        if(kind==3) {return LiveData.numeric(LiveData.steps);}
        if(kind==4) {return LiveData.numeric(LiveData.calories);}
        if(kind==5) {return LiveData.numeric(LiveData.altitude)+"M";}
        if(kind==6) {return LiveData.distanceText(LiveData.distance)+"KM";}
        if(kind==7) {return LiveData.numeric(Environment.temperature)+"C";}
        if(kind==8) {return Environment.sunrise;}
        if(kind==9) {return Environment.sunset;}
        if(kind==10) {return LiveData.numeric(LiveData.battery)+"%";}
        if(kind==11) {return LiveData.numeric(LiveData.stepGoal);}
        if(kind==12) {return LiveData.numeric(LiveData.floors);}
        if(kind==13) {return LiveData.numeric(LiveData.activeMinutes);}
        return LiveData.numeric(LiveData.notifications);
    }
    function text(kind,compact) {
        var v=value(kind);return kind==0 || compact ? v : label(kind)+" "+v;
    }
}
