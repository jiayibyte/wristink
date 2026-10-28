import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

class InstinctFaceApp extends Application.AppBase {
    var _view;
    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
        FacePrefs.migrate();FacePrefs.reload();
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {
        _view=new InstinctFaceView();return [_view,new PowerDelegate(_view)];
    }

    function getSettingsView() as [Views] or [Views, InputDelegates] or Null {
        FaceDraw.enterSettings();
        if(_view!=null){_view.suspend();}
        var menu=new FaceSettingsMenu(0);return [menu,new FaceSettingsDelegate(menu,0)];
    }

    function onSettingsChanged() as Void {
        FacePrefs.reload();
        if(_view!=null){_view.invalidate();}else{FaceDraw.enterSettings();}
        WatchUi.requestUpdate();
    }

    function onStop(state as Dictionary?) as Void {
        // Leave room for the runtime to serialize properties on this 60 KB device.
        FaceDraw.enterSettings();
        if(_view!=null){_view.suspend();}
        _view=null;
    }
}

class PowerDelegate extends WatchUi.WatchFaceDelegate {
    var _view;
    function initialize(view){WatchFaceDelegate.initialize();_view=view;}
    function onPowerBudgetExceeded(powerInfo as WatchUi.WatchFacePowerInfo) as Void {
        // Keep the watch usable if an optional always-on seconds style exceeds its budget.
        _view.disablePartialSeconds();
        _view.disablePartialHeart();
    }
}
