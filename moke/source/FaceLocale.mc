import Toybox.WatchUi;
module FaceLocale {
    var _english=null;
    function english(){if(_english==null){_english=WatchUi.loadResource(Rez.Strings.LocaleEnglish).equals("true");}return _english;}
    (:extendedCode)
    function text(id){return WatchUi.loadResource(id);}
    function days(){return english() ? "d" : "天";}
    function period(hour){return english() ? (hour<12 ? "AM" : "PM") : (hour<12 ? "上午" : "下午");}
}
