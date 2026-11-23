import Toybox.Application;
import Toybox.Lang;

module FaceSettings {
    var timeFormat=0;var leadingZero=false;var continuous=true;
    var showSeconds=true;var showNeedle=true;var showDate=true;
    var mapSkin=-1;var showMap=true;var showMarker=true;var theme=0;
    var manualLocation=false;var latitude=0.0;var longitude=0.0;
    var slots as Array<Number> = [1,2,3,4,5,6,7,8,9];
    // Garmin Connect / the store can hand values back as Long, Float or a
    // numeric String instead of the declared type. A strict instanceof check
    // silently reverted them to defaults. An undeclared key throws.
    function raw(key) {
        try {return Application.Properties.getValue(key);} catch(e) {return null;}
    }
    function toNumber(v) {
        if(v instanceof Number) {return v;}
        if(v instanceof Long || v instanceof Float || v instanceof Double || v instanceof String) {return v.toNumber();}
        if(v instanceof Boolean) {return v ? 1 : 0;}
        return null;
    }
    function bounded(value,fallback,low,high) {
        value=toNumber(value);
        return value!=null && value>=low && value<=high ? value : fallback;
    }
    function number(key,fallback,low,high) {return bounded(raw(key),fallback,low,high);}
    function flag(key,fallback) {
        var v=raw(key);
        if(v instanceof Boolean) {return v;}
        if(v instanceof String) {if(v.equals("true")) {return true;}if(v.equals("false")) {return false;}}
        var n=toNumber(v);return n==null ? fallback : n!=0;
    }
    function coordinate(key,limit) {
        var v=raw(key);
        if(v instanceof String) {v=v.toFloat();}
        return (v instanceof Number || v instanceof Long || v instanceof Float || v instanceof Double) && v>=-limit && v<=limit ? v : null;
    }
    function load() {
        timeFormat=number("TimeFormat",0,0,2);leadingZero=flag("LeadingZero",false);
        continuous=number("RefreshMode",1,0,1)==1;
        showSeconds=flag("ShowSeconds",true);showNeedle=flag("ShowNeedle",true);showDate=flag("ShowDate",true);
        mapSkin=number("MapSkin",-1,-1,15);theme=number("ColorTheme",0,0,5);showMap=flag("ShowMap",true);showMarker=flag("ShowMarker",true);
        manualLocation=flag("ManualLocation",false);latitude=coordinate("Latitude",90);longitude=coordinate("Longitude",180);
        for(var i=0;i<9;i++) {slots[i]=number("Field"+(i+1),i+1,0,14);}
    }
    function is24(systemValue) {return timeFormat==0 ? systemValue : timeFormat==2;}
    function shownHour(hour,is24) {return is24 ? hour : (hour%12==0 ? 12 : hour%12);}
    function hasHeart() {for(var i=0;i<slots.size();i++) {if(slots[i]==1) {return true;}}return false;}
}
