import Toybox.Application;
import Toybox.WatchUi;

class TideGridApp extends Application.AppBase {
    private var face;

    function initialize() {
        AppBase.initialize();
    }

    function getInitialView() {
        face = new TideGridFace();
        return [face];
    }

    function onSettingsChanged() as Void {
        if (face != null) {
            face.reloadSettings();
            WatchUi.requestUpdate();
        }
    }

    function onStart(state) as Void {
        if (Application.Storage.getValue("TideLocationMigrated") != null) { return; }
        var legacy = Application.Properties.getValue("TideStation");
        if (Preferences.read("TidePlace", 0, TideCatalog.PORTS.size()+1) == 0 &&
            legacy != null && legacy.length() > 0) {
            for (var i = 0; i < TideCatalog.PORTS.size(); i++) {
                if (legacy.equals(TideCatalog.PORTS[i][4])) {
                    Application.Properties.setValue("TidePlace", i+1);
                    break;
                }
            }
        }
        Application.Storage.setValue("TideLocationMigrated", true);
    }
}
