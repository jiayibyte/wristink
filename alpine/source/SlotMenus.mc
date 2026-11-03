import Toybox.Lang;
import Toybox.WatchUi;

class SlotMenu extends WatchUi.Menu2 {
    function initialize() {
        Menu2.initialize({:title=>Rez.Strings.DataSlots});
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
        if(Settings.setSlot(_key,value)) {_row.setSubLabel(SlotCatalog.name(value));if(_face!=null) {_face.settingsChanged();}}
        WatchUi.popView(WatchUi.SLIDE_RIGHT);
    }
}
