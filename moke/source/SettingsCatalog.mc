// Menu metadata is loaded one group at a time.
import Toybox.Lang;
import Toybox.WatchUi;
module SettingsCatalog {
    const COUNT = 13;
    (:extendedCode)
    function rowId(group,page) as ResourceId {switch(group*16+page){
        case 0:return Rez.JsonData.ConfigGroup0Page0;
        case 1:return Rez.JsonData.ConfigGroup0Page1;
        case 16:return Rez.JsonData.ConfigGroup1Page0;
        case 17:return Rez.JsonData.ConfigGroup1Page1;
        case 32:return Rez.JsonData.ConfigGroup2Page0;
        case 33:return Rez.JsonData.ConfigGroup2Page1;
        case 48:return Rez.JsonData.ConfigGroup3Page0;
        case 49:return Rez.JsonData.ConfigGroup3Page1;
        case 50:return Rez.JsonData.ConfigGroup3Page2;
        case 64:return Rez.JsonData.ConfigGroup4Page0;
        case 65:return Rez.JsonData.ConfigGroup4Page1;
        case 80:return Rez.JsonData.ConfigGroup5Page0;
        case 96:return Rez.JsonData.ConfigGroup6Page0;
        case 112:return Rez.JsonData.ConfigGroup7Page0;
        case 128:return Rez.JsonData.ConfigGroup8Page0;
        case 144:return Rez.JsonData.ConfigGroup9Page0;
        case 160:return Rez.JsonData.ConfigGroup10Page0;
        case 176:return Rez.JsonData.ConfigGroup11Page0;
        case 192:return Rez.JsonData.ConfigGroup12Page0;
    }return Rez.JsonData.ConfigGroup0Page0;}
    (:extendedCode)
    function pages(group){switch(group){
        case 0:return 2;
        case 1:return 2;
        case 2:return 2;
        case 3:return 3;
        case 4:return 2;
    }return 1;}
    const OPTIONS = [Rez.JsonData.ConfigOptions0,Rez.JsonData.ConfigOptions1,Rez.JsonData.ConfigOptions2,Rez.JsonData.ConfigOptions3,Rez.JsonData.ConfigOptions4,Rez.JsonData.ConfigOptions5,Rez.JsonData.ConfigOptions6,Rez.JsonData.ConfigOptions7,Rez.JsonData.ConfigOptions8,Rez.JsonData.ConfigOptions9,Rez.JsonData.ConfigOptions10,Rez.JsonData.ConfigOptions11,Rez.JsonData.ConfigOptions12,Rez.JsonData.ConfigOptions13,Rez.JsonData.ConfigOptions14,Rez.JsonData.ConfigOptions15,Rez.JsonData.ConfigOptions16,Rez.JsonData.ConfigOptions17,Rez.JsonData.ConfigOptions18,Rez.JsonData.ConfigOptions19,Rez.JsonData.ConfigOptions20,Rez.JsonData.ConfigOptions21,Rez.JsonData.ConfigOptions22,Rez.JsonData.ConfigOptions23,Rez.JsonData.ConfigOptions24,Rez.JsonData.ConfigOptions25,Rez.JsonData.ConfigOptions26,Rez.JsonData.ConfigOptions27,Rez.JsonData.ConfigOptions28,Rez.JsonData.ConfigOptions29,Rez.JsonData.ConfigOptions30];
    (:extendedCode)
    function label(index,value) as String {switch(index){
        case 19:return packedLabel(Rez.JsonData.ConfigLabels19,29,value);
        case 25:return packedLabel(Rez.JsonData.ConfigLabels25,21,value);
    }var labels=choices(index);return labels[value] as String;}
    (:extendedCode)
    function packedLabel(id as ResourceId,count,value) as String {var text=WatchUi.loadResource(id) as String;var width=(text.length()/count).toNumber();return text.substring(value*width,(value+1)*width); }
    (:extendedCode)
    function groups() as Array<String> { return WatchUi.loadResource(Rez.JsonData.ConfigGroups) as Array<String>; }
    (:extendedCode)
    function rows(group,page) as Array { return WatchUi.loadResource(rowId(group,page)) as Array; }
    (:extendedCode)
    function choices(index) as Array { return WatchUi.loadResource(OPTIONS[index]) as Array; }
}
