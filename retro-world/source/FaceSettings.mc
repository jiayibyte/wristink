import Toybox.Application;
import Toybox.Lang;

module FaceSettings {
    var timeFormat=0;var leadingZero=false;var continuous=true;
    var showSeconds=true;var showNeedle=true;var showDate=true;
    var mapSkin=-1;var showMap=true;var showMarker=true;
    var manualLocation=false;var latitude=0.0;var longitude=0.0;
    var slots as Array<Number> = [1,2,3,4,5,6,7,8,9];
    function bounded(value,fallback,low,high) {
        return value instanceof Number && value>=low && value<=high ? value : fallback;
    }
    function number(key,fallback,low,high) {return bounded(Application.Properties.getValue(key),fallback,low,high);}
    function flag(key,fallback) {var v=Application.Properties.getValue(key);return v instanceof Boolean ? v : fallback;}
    function coordinate(key,limit) {
        var v=Application.Properties.getValue(key);
        return (v instanceof Number || v instanceof Float || v instanceof Double) && v>=-limit && v<=limit ? v : null;
    }
    function load() {
        timeFormat=number("TimeFormat",0,0,2);leadingZero=flag("LeadingZero",false);
        continuous=number("RefreshMode",1,0,1)==1;
        showSeconds=flag("ShowSeconds",true);showNeedle=flag("ShowNeedle",true);showDate=flag("ShowDate",true);
        mapSkin=number("MapSkin",-1,-1,15);showMap=flag("ShowMap",true);showMarker=flag("ShowMarker",true);
        manualLocation=flag("ManualLocation",false);latitude=coordinate("Latitude",90);longitude=coordinate("Longitude",180);
        for(var i=0;i<9;i++) {slots[i]=number("Field"+(i+1),i+1,0,14);}
    }
    function is24(systemValue) {return timeFormat==0 ? systemValue : timeFormat==2;}
    function shownHour(hour,is24) {return is24 ? hour : (hour%12==0 ? 12 : hour%12);}
    function hasHeart() {for(var i=0;i<slots.size();i++) {if(slots[i]==1) {return true;}}return false;}
}
