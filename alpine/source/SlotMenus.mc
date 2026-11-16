import Toybox.Lang;
import Toybox.WatchUi;

class SlotMenu extends WatchUi.Menu2 {
    function initialize() {
        Menu2.initialize({:title=>Rez.Strings.DataSlots});
        addItem(new WatchUi.MenuItem(Rez.Strings.PanelStyle,SlotCatalog.panelName(Settings.panelStyle),"PanelStyle",null));
        addItem(new WatchUi.MenuItem(Rez.Strings.Festival,SlotCatalog.festivalName(Settings.festival),"Festival",null));
        for(var i=0;i<SlotCatalog.keys.size();i++) {
            var key=SlotCatalog.keys[i];if(Device.MONO && key.equals("HeaderRight")) {continue;}
            var title=key.equals("CircleData") ? (Device.MONO ? Rez.Strings.CircleSlot : Rez.Strings.WeatherSlot) : SlotCatalog.titles[i];
            addItem(new WatchUi.MenuItem(title,SlotCatalog.name(Settings.getSlot(key)),key,null));
        }
    }
}
class SlotMenuDelegate extends WatchUi.Menu2InputDelegate {
    var _face;
    function initialize(face) {Menu2InputDelegate.initialize();_face=face;}
    function onSelect(item) {
        var key=item.getId() as String;
        if(key.equals("Festival")) {
            var holidays=new WatchUi.Menu2({:title=>Rez.Strings.Festival,:focus=>Settings.festival});
            for(var h=0;h<SlotCatalog.festivals.size();h++) {holidays.addItem(new WatchUi.MenuItem(SlotCatalog.festivals[h],null,h,null));}
            WatchUi.pushView(holidays,new SlotChoiceDelegate(key,item,_face),WatchUi.SLIDE_LEFT);return;
        }
        if(key.equals("PanelStyle")) {
            var styles=new WatchUi.Menu2({:title=>Rez.Strings.PanelStyle,:focus=>Settings.panelStyle});
            for(var s=0;s<SlotCatalog.panelStyles.size();s++) {styles.addItem(new WatchUi.MenuItem(SlotCatalog.panelStyles[s],null,s,null));}
            WatchUi.pushView(styles,new SlotChoiceDelegate(key,item,_face),WatchUi.SLIDE_LEFT);return;
        }
        var menu=new WatchUi.Menu2({:title=>item.getLabel(),:focus=>Settings.getSlot(key)});
        for(var i=0;i<12;i++) {menu.addItem(new WatchUi.MenuItem(SlotCatalog.metrics[i],null,i,null));}
        WatchUi.pushView(menu,new SlotChoiceDelegate(key,item,_face),WatchUi.SLIDE_LEFT);
    }
}
class SlotChoiceDelegate extends WatchUi.Menu2InputDelegate {
    var _key;var _row;var _face;
    function initialize(key,row,face) {Menu2InputDelegate.initialize();_key=key;_row=row;_face=face;}
    function onSelect(item) {
        var value=item.getId() as Number;
        if(_key.equals("Festival")) {
            if(Settings.setFestival(value)) {_row.setSubLabel(SlotCatalog.festivalName(value));if(_face!=null) {_face.settingsChanged();}}
            WatchUi.popView(WatchUi.SLIDE_RIGHT);return;
        }
        if(_key.equals("PanelStyle")) {
            if(Settings.setPanelStyle(value)) {_row.setSubLabel(SlotCatalog.panelName(value));if(_face!=null) {_face.settingsChanged();}}
            WatchUi.popView(WatchUi.SLIDE_RIGHT);return;
        }
        if(Settings.setSlot(_key,value)) {_row.setSubLabel(SlotCatalog.name(value));if(_face!=null) {_face.settingsChanged();}}
        WatchUi.popView(WatchUi.SLIDE_RIGHT);
    }
}
