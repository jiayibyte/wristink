// Read Garmin's existing data only when a visible region consumes it.
// No timers, active sensor subscriptions, GPS requests or network requests.
module PowerPolicy {
    const ACTIVITY=1;
    const LIVE=2;
    const STATS=4;
    const WEATHER=8;
    const SUN=16;
    const HEART=32;
    const RANGE=64;
    const BODY=128;
    const NOTIFICATIONS=256;
    function metric(kind){
        switch(kind){
            case 1:case 17:return STATS;
            case 2:case 3:case 4:case 5:case 12:case 20:case 21:
            case 22:case 23:case 24:case 25:case 26:case 27:return ACTIVITY;
            case 18:case 28:return LIVE;
            case 6:return HEART;
            case 7:case 10:case 13:case 16:return WEATHER;
            case 8:case 9:return WEATHER|SUN;
            case 11:return NOTIFICATIONS;
            case 15:return RANGE;
            case 19:return BODY;
        }
        return 0;
    }
    function progress(source){
        if(source==1){return BODY;}
        if(source==2){return STATS;}
        return source>=3 && source<=7 ? ACTIVITY : 0;
    }
    function due(last,now,period){return last<0 || now<last || now-last>=period;}
    function historyPeriod(profile){return profile==0 ? 300 : 60;}
    function weatherPeriod(profile){return profile==0 ? 1800 : 300;}
    function seconds(enabled,mode,sleeping){return enabled && (mode==2 || (mode==1 && !sleeping));}
    // Budget fallback may reduce continuous seconds, but must preserve hidden/off states.
    function budgetSeconds(mode){return mode==2 ? 1 : mode;}
}
