import Toybox.Lang;
import Toybox.WatchUi;

class SlotMenu extends WatchUi.Menu2 {
    var populated=false;var focus=0;
    function initialize() {
        Menu2.initialize({:title=>Rez.Strings.DataSlots});
        populate();
    }
    function onShow() {if(!populated) {populate();setFocus(focus);}}
    function onHide() {releaseItems();}
    function releaseItems() {while(deleteItem(0)==true) {}populated=false;}
    function populate() {
        for(var c=0;c<SlotCatalog.choiceKeys.size();c++) {
            var choiceKey=SlotCatalog.choiceKeys[c];
            addItem(new WatchUi.MenuItem(SlotCatalog.choiceTitles[c],SlotCatalog.choiceName(choiceKey,Settings.choice(choiceKey)),choiceKey,null));
        }
        for(var i=0;i<SlotCatalog.keys.size();i++) {
            var key=SlotCatalog.keys[i];if((Device.MONO && key.equals("HeaderRight")) || (!Device.MONO && key.equals("TimeLeft"))) {continue;}
            var title=key.equals("CircleData") ? (Device.MONO ? Rez.Strings.CircleSlot : Rez.Strings.WeatherSlot) : SlotCatalog.titles[i];
            addItem(new WatchUi.MenuItem(title,SlotCatalog.name(Settings.getSlot(key)),key,null));
        }
        populated=true;
    }
}
class SlotChoices extends WatchUi.Menu2 {
    function initialize(key,title) {
        var choice=SlotCatalog.isChoice(key);
        Menu2.initialize({:title=>title,:focus=>choice ? Settings.choice(key) : Settings.getSlot(key)});
        var entries=choice ? SlotCatalog.choices(key) : SlotCatalog.metrics;
        for(var i=0;i<entries.size();i++) {addItem(new WatchUi.MenuItem(entries[i],null,i,null));}
    }
    function onHide() {while(deleteItem(0)==true) {}}
}
class SlotMenuDelegate extends WatchUi.Menu2InputDelegate {
    var _face;var _menu;
    function initialize(face,menu) {Menu2InputDelegate.initialize();_face=face;_menu=menu;}
    function onSelect(item) {
        var key=item.getId() as String;var title=item.getLabel();
        _menu.focus=_menu.findItemById(key);
        _menu.releaseItems();
        var menu=new SlotChoices(key,title);
        WatchUi.pushView(menu,new SlotChoiceDelegate(key,_face),WatchUi.SLIDE_LEFT);
    }
}
class SlotChoiceDelegate extends WatchUi.Menu2InputDelegate {
    var _key;var _face;
    function initialize(key,face) {Menu2InputDelegate.initialize();_key=key;_face=face;}
    function onSelect(item) {
        var value=item.getId() as Number;var choice=SlotCatalog.isChoice(_key);
        if(choice ? Settings.setChoice(_key,value) : Settings.setSlot(_key,value)) {
            if(_face!=null) {_face.settingsChanged();}
        }
        WatchUi.popView(WatchUi.SLIDE_RIGHT);
    }
}
