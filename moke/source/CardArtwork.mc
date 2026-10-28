// A single theme atlas holds the optional artwork; crop with Dc.setClip on MIP.
import Toybox.Lang;
module CardArtwork {
    function resource(kind,light) as ResourceId {
        if(kind==1){return Rez.Drawables.BeijingCard;}
        if(kind==2){return Rez.Drawables.AlipayCard;}
        return light ? Rez.Drawables.CardArtAtlasLight : Rez.Drawables.CardArtAtlasDark;
    }
}
