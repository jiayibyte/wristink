// Generated sector palettes and textures, loaded only for the selected style.
import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.Lang;
module EnergyCatalog {
    function id(style,index) as ResourceId {switch(style*8+index){
        case 0:return Rez.Drawables.EnergyLevelV0N1;
        case 1:return Rez.Drawables.EnergyLevelV0N2;
        case 2:return Rez.Drawables.EnergyLevelV0N3;
        case 3:return Rez.Drawables.EnergyLevelV0N4;
        case 4:return Rez.Drawables.EnergyLevelV0N5;
        case 5:return Rez.Drawables.EnergyLevelV0N6;
        case 6:return Rez.Drawables.EnergyLevelV0N7;
        case 7:return Rez.Drawables.EnergyLevelV0N8;
        case 8:return Rez.Drawables.EnergyLevelV1N1;
        case 9:return Rez.Drawables.EnergyLevelV1N2;
        case 10:return Rez.Drawables.EnergyLevelV1N3;
        case 11:return Rez.Drawables.EnergyLevelV1N4;
        case 12:return Rez.Drawables.EnergyLevelV1N5;
        case 13:return Rez.Drawables.EnergyLevelV1N6;
        case 14:return Rez.Drawables.EnergyLevelV1N7;
        case 15:return Rez.Drawables.EnergyLevelV1N8;
        case 16:return Rez.Drawables.EnergyLevelV2N1;
        case 17:return Rez.Drawables.EnergyLevelV2N2;
        case 18:return Rez.Drawables.EnergyLevelV2N3;
        case 19:return Rez.Drawables.EnergyLevelV2N4;
        case 20:return Rez.Drawables.EnergyLevelV2N5;
        case 21:return Rez.Drawables.EnergyLevelV2N6;
        case 22:return Rez.Drawables.EnergyLevelV2N7;
        case 23:return Rez.Drawables.EnergyLevelV2N8;
        case 24:return Rez.Drawables.EnergyLevelV3N1;
        case 25:return Rez.Drawables.EnergyLevelV3N2;
        case 26:return Rez.Drawables.EnergyLevelV3N3;
        case 27:return Rez.Drawables.EnergyLevelV3N4;
        case 28:return Rez.Drawables.EnergyLevelV3N5;
        case 29:return Rez.Drawables.EnergyLevelV3N6;
        case 30:return Rez.Drawables.EnergyLevelV3N7;
        case 31:return Rez.Drawables.EnergyLevelV3N8;
    }return Rez.Drawables.EnergyLevelV0N1;}
    const X = [32, 32, 32, 32, 14, 5, 5, 5];
    const Y = [5, 5, 5, 5, 5, 5, 5, 5];
    function load(style,count) as Graphics.BitmapReference {
        return WatchUi.loadResource(id(style,count-1)) as Graphics.BitmapReference;
    }
}
