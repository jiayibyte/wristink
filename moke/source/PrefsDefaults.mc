// Small validated defaults: no full settings map is loaded while rendering.
module PrefsDefaults {
    function value(key) { switch(key) {
        case "dataSize":return 1;
        case "timeSize":return 1;
        case "secondsSize":return 1;
        case "moveSource":return 6;
        case "circle":return 6;
        case "circleSize":return 1;
        case "circleBackground":return 1;
        case "ringStyle":return 1;
        case "topCardImage":return 1;
        case "bottomCardImage":return 2;
        case "sideSize":return 1;
        case "topOne":return 7;
        case "topTwo":return 17;
        case "bottomLeft":return 2;
        case "bottomRight":return 15;
        case "bottomRightStyle":return 6;
        case "footerLeft":return 5;
        case "footerRight":return 18;
        case "chartMinutes":return 1;
    } return 0; }
    function max(key) {
        var suffix=key.length()>=4 ? key.substring(key.length()-4,key.length()) : "";
        if(suffix.equals("Goal")){return 1000000;}
        if(suffix.equals("Font") || suffix.equals("Size")){
            return key.equals("dataFont") || key.equals("dataSize") || key.equals("timeFont") || key.equals("timeSize") || key.equals("circleFont") || key.equals("circleSize") || key.equals("secondsFont") || key.equals("secondsSize") ? 2 : 3;
        }
        if(key.length()>=5 && key.substring(key.length()-5,key.length()).equals("Style")){return key.equals("cellsStyle") || key.equals("chartStyle") || key.equals("moveStyle") ? 2 : (key.equals("circleStyle") || key.equals("ringStyle") ? 3 : (key.equals("bottomRightStyle") ? 6 : 5));}
        switch(key){
            case "cellsSource":case "ringSource":case "moveSource":case "dateFormat":return 7;
            case "ringStart":return 3;
            case "timeSeparator":case "circleBackground":case "chartMinutes":case "heartRefresh":case "analogHandMode":return 2;
            case "secondsMode":return 3;
            case "topCardImage":case "bottomCardImage":return 20;
            case "timeFormat":case "temperatureUnit":case "distanceUnit":case "altitudeUnit":case "powerProfile":case "heartSource":return 1;
        }
        return 28;
    }
}
