import Toybox.Application;
import Toybox.Test;

class SettingsSuspensionProbe {
    var suspended=false;var invalidated=false;
    function suspend() {suspended=true;}
    function invalidate() {invalidated=true;}
}

(:test)
function unsupportedNativeSettingsMustNotSuspendPhoneConfigurableFace(logger) {
    var app=Application.getApp();var original=app._view;
    var previous=app.getProperty("darkTheme");
    var probe=new SettingsSuspensionProbe();app._view=probe;
    var settings=app.getSettingsView();
    app.setProperty("darkTheme",false);app.onSettingsChanged();
    var applied=!FacePrefs.flag("darkTheme");
    app._view=original;app.setProperty("darkTheme",previous);FacePrefs.reload();
    Test.assert(settings==null);
    Test.assert(!probe.suspended);
    Test.assert(probe.invalidated);Test.assert(applied);
    return true;
}
