import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

module FacePrefs {
    var revision=0;
    (:extendedCode)
    function migrate() {
        // Apply the requested heart-window redesign once; later edits remain user controlled.
        if (Application.Storage.getValue("whiteHeartDesign") != true) {
            Application.Properties.setValue("circle", 6);
            Application.Storage.setValue("whiteHeartDesign", true);
        }
        if (Application.Storage.getValue("referenceDetailsV2") != true) {
            if (Application.Properties.getValue("topTwo") == 8) { Application.Properties.setValue("topTwo", 1); }
            if (Application.Properties.getValue("bottomRight") == 3) { Application.Properties.setValue("bottomRight", 15); }
            if (Application.Properties.getValue("footerLeft") == 4) { Application.Properties.setValue("footerLeft", 5); }
            if (Application.Properties.getValue("footerRight") == 5) { Application.Properties.setValue("footerRight", 6); }
            Application.Storage.setValue("referenceDetailsV2", true);
        }
        if (Application.Storage.getValue("altitudeBatteryV3") != true) {
            if (Application.Properties.getValue("topTwo") == 1) { Application.Properties.setValue("topTwo", 17); }
            if (Application.Properties.getValue("topThree") == 16) { Application.Properties.setValue("topThree", 0); }
            if (Application.Properties.getValue("footerRight") == 6) { Application.Properties.setValue("footerRight", 18); }
            Application.Storage.setValue("altitudeBatteryV3", true);
        }
        if(NativeStyle.enabled() && (Application.Storage.getValue("referenceSpacingV4")==true || Application.Storage.getValue("referenceSpacingV5")==true)){
            Application.Properties.setValue("showMoveBar",true);
            if(Application.Properties.getValue("dateFont")==2 && Application.Properties.getValue("dateSize")==3){Application.Properties.setValue("dateFont",0);Application.Properties.setValue("dateSize",0);}
            if(Application.Properties.getValue("topThree")==16){Application.Properties.setValue("topThree",0);}
            if(Application.Properties.getValue("topCardImage")==0 && Application.Properties.getValue("bottomCardImage")==0 && Application.Properties.getValue("secondsMode")==1){Application.Properties.setValue("topCardImage",1);Application.Properties.setValue("bottomCardImage",2);Application.Properties.setValue("secondsMode",0);}
            Application.Storage.deleteValue("referenceSpacingV4");Application.Storage.deleteValue("referenceSpacingV5");
        }
        if(NativeStyle.enabled() && Application.Storage.getValue("plainWhiteHeartV6")!=true){
            Application.Properties.setValue("circleBackground",1);
            Application.Properties.setValue("cellsSource",0);
            Application.Properties.setValue("ringSource",0);
            Application.Storage.setValue("plainWhiteHeartV6",true);
        }
    }

    function reload() {
        // Invalidate the render plan without duplicating the property store in RAM.
        revision+=1;
    }
    function get(key) {
        var v=null;try{v=Application.Properties.getValue(key);}catch(e){}
        return v instanceof Number && v>=0 && v<=PrefsDefaults.max(key) ? v : PrefsDefaults.value(key);
    }
    function flag(key) {
        var v=null;try{v=Application.Properties.getValue(key);}catch(e){}return v instanceof Boolean ? v : true;
    }
    (:extendedCode)
    function set(key,value) {
        Application.Properties.setValue(key,value); reload();
        FontCatalog.reset(); WatchUi.requestUpdate();
    }
    (:extendedCode)
    function caption(row as Array) {
        var key=row[0];
        if(row[2]==1){return flag(key) ? FaceLocale.text(Rez.Strings.MenuOn) : FaceLocale.text(Rez.Strings.MenuOff);}
        var n=get(key);
        if(row[2]==2){return n==0 ? FaceLocale.text(Rez.Strings.MenuAuto) : n.toString();}
        return SettingsCatalog.label(row[4],n);
    }
    function fontFamily(key) {
        var n=get(key+"Font"); return n==0 ? get("dataFont") : n-1;
    }
    function fontSize(key) {
        var n=get(key+"Size"); return n==0 ? get("dataSize") : n-1;
    }
    (:extendedCode)
    function resetGroup(group) {
        var first=group<0 ? 0 : group;var last=group<0 ? SettingsCatalog.COUNT-1 : group;
        for(var g=first;g<=last;g++){
            for(var page=0;page<SettingsCatalog.pages(g);page++){
                var rows=SettingsCatalog.rows(g,page);
                for(var i=0;i<rows.size();i++){var row=rows[i] as Array;Application.Properties.setValue(row[0],row[3]);}
                rows=[];
            }
        }
        reload();FontCatalog.reset();WatchUi.requestUpdate();
    }
}

// Keep only one settings menu on the stack. Rebuild its parent on Back so
// a long choice list does not retain every ancestor on this 60 KB watch.
module FaceMenus {
    const PAGE_SIZE=6;
    (:extendedCode)
    function clear(menu){while(menu.deleteItem(0)==true){}}
    (:extendedCode)
    function root(){rootPage(0);}
    (:extendedCode)
    function rootPage(page){var menu=new FaceSettingsMenu(page);WatchUi.switchToView(menu,new FaceSettingsDelegate(menu,page),WatchUi.SLIDE_RIGHT);}
    (:extendedCode)
    function group(group){groupPage(group,0);}
    (:extendedCode)
    function groupPage(group,page){
        var rows=SettingsCatalog.rows(group,page);var totalPages=SettingsCatalog.pages(group);
        var menu=new WatchUi.Menu2({:title=>SettingsCatalog.groups()[group]});
        for(var i=0;i<rows.size();i++){var row=rows[i] as Array;menu.addItem(new WatchUi.MenuItem(row[1],FacePrefs.caption(row),i,{}));}
        if(page+1<totalPages){menu.addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuNext),null,"nextGroup",{}));}
        if(page>0){menu.addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuPrevious),null,"prevGroup",{}));}
        menu.addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuResetGroup),null,"resetGroup",{}));
        WatchUi.switchToView(menu,new SettingsGroupDelegate(group,rows,menu,page),WatchUi.SLIDE_IMMEDIATE);
    }
    (:extendedCode)
    function choices(group,row as Array,page,groupPage){
        var numeric=row[2]==2;
        var options=numeric ? [0,10,20,30,50,100,150,200,500,1000,2000,5000,8000,10000,12000,15000,20000,50000,100000] : SettingsCatalog.choices(row[4]);
        var current=FacePrefs.get(row[0]);var start=page*PAGE_SIZE;var end=start+PAGE_SIZE;
        if(end>options.size()){end=options.size();}
        var menu=new WatchUi.Menu2({:title=>row[1]});
        for(var i=start;i<end;i++){
            var value=numeric ? options[i] : i;
            var label=numeric ? (value==0 ? FaceLocale.text(Rez.Strings.MenuAuto) : value.toString()) : options[i];
            menu.addItem(new WatchUi.MenuItem(label,value==current ? FaceLocale.text(Rez.Strings.MenuSelected) : null,value,{}));
        }
        if(end<options.size()){menu.addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuNext),null,-1,{}));}
        if(page>0){menu.addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuPrevious),null,-2,{}));}
        WatchUi.switchToView(menu,new SettingsChoiceDelegate(group,row,page,menu,groupPage),WatchUi.SLIDE_IMMEDIATE);
    }
}
class FaceSettingsMenu extends WatchUi.Menu2 {
    (:extendedCode)
    function initialize(page){
        Menu2.initialize({:title=>FaceLocale.text(Rez.Strings.MenuTitle)});
        var groups=SettingsCatalog.groups();var start=page*FaceMenus.PAGE_SIZE;var end=start+FaceMenus.PAGE_SIZE;if(end>SettingsCatalog.COUNT){end=SettingsCatalog.COUNT;}
        for(var i=start;i<end;i++){addItem(new WatchUi.MenuItem(groups[i],null,i,{}));}
        if(end<SettingsCatalog.COUNT){addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuNext),null,"nextGroup",{}));}
        if(page>0){addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuPrevious),null,"prevGroup",{}));}
        addItem(new WatchUi.MenuItem(FaceLocale.text(Rez.Strings.MenuResetAll),null,"resetAll",{}));
    }
}
class FaceSettingsDelegate extends WatchUi.Menu2InputDelegate {
    var _menu;var _page;
    (:extendedCode)
    function initialize(menu,page){Menu2InputDelegate.initialize();_menu=menu;_page=page;}
    (:extendedCode)
    function release(){FaceMenus.clear(_menu);_menu=null;}
    (:extendedCode)
    function onSelect(item as WatchUi.MenuItem) as Void {
        var id=item.getId();
        if(id instanceof String){
            release();
            if(id.equals("nextGroup") || id.equals("prevGroup")){FaceMenus.rootPage(_page+(id.equals("nextGroup") ? 1 : -1));}
            else{FacePrefs.resetGroup(-1);WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);}
            return;
        }
        release();FaceMenus.group(id as Number);
    }
    (:extendedCode)
    function onBack() as Void {release();WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);}
}
class SettingsGroupDelegate extends WatchUi.Menu2InputDelegate {
    var _group;var _rows as Array;var _menu;var _page;
    (:extendedCode)
    function initialize(group,rows,menu,page){Menu2InputDelegate.initialize();_group=group;_rows=rows;_menu=menu;_page=page;}
    (:extendedCode)
    function release(){_rows=[];FaceMenus.clear(_menu);_menu=null;}
    (:extendedCode)
    function onSelect(item as WatchUi.MenuItem) as Void {
        var id=item.getId();
        if(id instanceof String){
            release();
            if(id.equals("nextGroup") || id.equals("prevGroup")){FaceMenus.groupPage(_group,_page+(id.equals("nextGroup") ? 1 : -1));}
            else{FacePrefs.resetGroup(_group);FaceMenus.rootPage((_group/FaceMenus.PAGE_SIZE).toNumber());}
            return;
        }
        var row=_rows[id as Number] as Array;var key=row[0] as String;
        if(row[2]==1){FacePrefs.set(key,!FacePrefs.flag(key));item.setSubLabel(FacePrefs.caption(row));return;}
        release();FaceMenus.choices(_group,row,0,_page);
    }
    (:extendedCode)
    function onBack() as Void {release();FaceMenus.rootPage((_group/FaceMenus.PAGE_SIZE).toNumber());}
}
class SettingsChoiceDelegate extends WatchUi.Menu2InputDelegate {
    var _group;var _row as Array;var _page;var _menu;var _groupPage;
    (:extendedCode)
    function initialize(group,row,page,menu,groupPage){Menu2InputDelegate.initialize();_group=group;_row=row;_page=page;_menu=menu;_groupPage=groupPage;}
    (:extendedCode)
    function onSelect(item as WatchUi.MenuItem) as Void {
        var id=item.getId() as Number;
        FaceMenus.clear(_menu);_menu=null;
        if(id<0){FaceMenus.choices(_group,_row,_page+(id==-1 ? 1 : -1),_groupPage);return;}
        FacePrefs.set(_row[0],id);_row=[];FaceMenus.groupPage(_group,_groupPage);
    }
    (:extendedCode)
    function onBack() as Void {_row=[];FaceMenus.clear(_menu);_menu=null;FaceMenus.groupPage(_group,_groupPage);}
}
