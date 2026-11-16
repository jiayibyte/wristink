import Toybox.Application;
import Toybox.Lang;
module Settings {
    var timeFormat=0;var scene=0;var circle=6;var smart=true;var seconds=true;
    var lowBattery=20;var stressLimit=75;var left=0;var middle=1;var right=2;
    var top=11;var upperLeft=11;var upperRight=11;var panelStyle=1;var festival=0;
    function number(key as String,fallback as Number,lo as Number,hi as Number) as Number {
        var v=Application.Properties.getValue(key);
        return v instanceof Number && v>=lo && v<=hi ? v : fallback;
    }
    function flag(key as String,fallback as Boolean) as Boolean {var v=Application.Properties.getValue(key);return v instanceof Boolean ? v : fallback;}
    function legacyCircle(value as Number) as Number {return value==1 ? 4 : (value==2 ? 7 : 6);}
    function migrateSlots() {
        if(Application.Storage.getValue("DataSlotsVersion")==2) {return;}
        var current=number("CircleData",6,0,11);
        // The former default heart rate becomes weather. Preserve explicit legacy
        // battery/stress choices, without reinterpreting their old numeric IDs.
        if(current==6) {Application.Properties.setValue("CircleData",legacyCircle(number("Circle",0,0,2)));}
        Application.Storage.setValue("DataSlotsVersion",2);
    }
    function migrateHeaderDefaults() {
        if(Application.Storage.getValue("HeaderDefaultsVersion")==1) {return;}
        // Replace only the previous factory selections; retain custom choices.
        if(number("HeaderTop",11,0,11)==3) {Application.Properties.setValue("HeaderTop",11);}
        if(number("HeaderLeft",11,0,11)==4) {Application.Properties.setValue("HeaderLeft",11);}
        if(number("HeaderRight",11,0,11)==5) {Application.Properties.setValue("HeaderRight",11);}
        Application.Storage.setValue("HeaderDefaultsVersion",1);
    }
    function load() {
        migrateSlots();migrateHeaderDefaults();
        timeFormat=number("TimeFormat",0,0,2);scene=number("Scene",0,0,12);circle=number("CircleData",6,0,11);
        top=number("HeaderTop",11,0,11);upperLeft=number("HeaderLeft",11,0,11);upperRight=number("HeaderRight",11,0,11);
        lowBattery=number("LowBattery",20,5,50);stressLimit=number("StressLimit",75,25,100);
        left=number("Left",0,0,11);middle=number("Middle",1,0,11);right=number("Right",2,0,11);
        smart=flag("Smart",true);seconds=flag("Seconds",true);
        panelStyle=number("PanelStyle",1,0,3);
        festival=number("Festival",0,0,5);
    }
    function getSlot(key as String) as Number {
        switch(key) {case "CircleData":return circle;case "HeaderTop":return top;case "HeaderLeft":return upperLeft;case "HeaderRight":return upperRight;case "Left":return left;case "Middle":return middle;case "Right":return right;}
        return 11;
    }
    function setSlot(key as String,value) as Boolean {
        if(!(value instanceof Number) || value<0 || value>11 || !SlotCatalog.isSlot(key)) {return false;}
        Application.Properties.setValue(key,value);Application.Storage.setValue("DataSlotsVersion",2);load();return true;
    }
    function headersUse(kind) {return top==kind || upperLeft==kind || (!Device.MONO && upperRight==kind);}
    function setPanelStyle(value) as Boolean {
        if(!(value instanceof Number) || value<0 || value>3) {return false;}
        Application.Properties.setValue("PanelStyle",value);load();return true;
    }
    function setFestival(value) as Boolean {
        if(!(value instanceof Number) || value<0 || value>5) {return false;}
        Application.Properties.setValue("Festival",value);load();return true;
    }
    function uses(kind) {return circle==kind || left==kind || middle==kind || right==kind || headersUse(kind);}
    function is24(system) {return timeFormat==0 ? system : timeFormat==2;}
    function shownHour(h,is24) {return is24 ? h : (h%12==0 ? 12 : h%12);}
}
