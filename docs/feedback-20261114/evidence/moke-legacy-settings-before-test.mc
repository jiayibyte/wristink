import Toybox.Application;
import Toybox.Test;

class SettingsSuspensionProbe {
    var suspended=false;
    function suspend() {suspended=true;}
}

(:test)
function unsupportedNativeSettingsMustNotSuspendPhoneConfigurableFace(logger) {
    var app=Application.getApp();var original=app._view;
    var probe=new SettingsSuspensionProbe();app._view=probe;
    var settings=app.getSettingsView();app._view=original;
    Test.assert(settings==null);
    Test.assert(!probe.suspended);
    return true;
}
