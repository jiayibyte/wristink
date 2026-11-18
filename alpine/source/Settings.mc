import Toybox.Application;
import Toybox.Lang;
module Settings {
    var timeFormat=0;var scene=0;var circle=6;var smart=true;var seconds=true;
    var lowBattery=20;var stressLimit=75;var left=0;var middle=1;var right=2;
    var top=11;var upperLeft=11;var upperRight=11;var panelStyle=1;var festival=0;var skyDisplay=0;
    var weatherLink=0;var skyDecor=0;var mountain=0;var timeLeft=11;
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
        timeFormat=number("TimeFormat",0,0,2);scene=2;circle=number("CircleData",6,0,11);
        top=number("HeaderTop",11,0,11);upperLeft=number("HeaderLeft",11,0,11);upperRight=number("HeaderRight",11,0,11);
        lowBattery=20;stressLimit=75;
        left=number("Left",0,0,11);middle=number("Middle",1,0,11);right=number("Right",2,0,11);timeLeft=number("TimeLeft",11,0,11);
        smart=false;seconds=flag("Seconds",true);
        panelStyle=number("PanelStyle",1,0,3);mountain=number("Mountain",0,0,3);
        festival=1;
        skyDisplay=0;
        weatherLink=1;skyDecor=0;
    }
    function getSlot(key as String) as Number {
        switch(key) {case "CircleData":return circle;case "HeaderTop":return top;case "HeaderLeft":return upperLeft;case "HeaderRight":return upperRight;case "Left":return left;case "Middle":return middle;case "Right":return right;case "TimeLeft":return timeLeft;}
        return 11;
    }
    function setSlot(key as String,value) as Boolean {
        if(!(value instanceof Number) || value<0 || value>11 || !SlotCatalog.isSlot(key)) {return false;}
        Application.Properties.setValue(key,value);Application.Storage.setValue("DataSlotsVersion",2);load();return true;
    }
    // The Instinct field left of the time also redraws with the full frame.
    function headersUse(kind) {return top==kind || upperLeft==kind || (!Device.MONO && upperRight==kind) || (Device.MONO && timeLeft==kind);}
    function setPanelStyle(value) as Boolean {
        if(!(value instanceof Number) || value<0 || value>3) {return false;}
        Application.Properties.setValue("PanelStyle",value);load();return true;
    }
    function setFestival(value) as Boolean {
        if(!(value instanceof Number) || value<0 || value>5) {return false;}
        Application.Properties.setValue("Festival",value);load();return true;
    }
    function choice(key as String) as Number {
        switch(key) {case "Scene":return scene;case "WeatherLink":return weatherLink;case "SkyDecor":return skyDecor;case "TimeFormat":return timeFormat;case "SkyDisplay":return skyDisplay;case "PanelStyle":return panelStyle;case "Festival":return festival;case "Mountain":return mountain;}
        return 0;
    }
    function setChoice(key as String,value) as Boolean {
        if(key.equals("PanelStyle")) {return setPanelStyle(value);}
        if(!SlotCatalog.isChoice(key)) {return false;}
        var limit=-1;
        switch(key) {case "Mountain":limit=3;break;case "Scene":limit=17;break;case "WeatherLink":case "SkyDisplay":limit=1;break;case "SkyDecor":limit=3;break;case "TimeFormat":limit=2;break;}
        if(!(value instanceof Number) || value<0 || value>limit) {return false;}
        Application.Properties.setValue(key,value);load();return true;
    }
    function uses(kind) {return circle==kind || left==kind || middle==kind || right==kind || headersUse(kind);}
    function is24(system) {return timeFormat==0 ? system : timeFormat==2;}
    function shownHour(h,is24) {return is24 ? h : (h%12==0 ? 12 : h%12);}
}
