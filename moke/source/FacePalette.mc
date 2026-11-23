import Toybox.Graphics;
import Toybox.Lang;

// Colour themes for colour screens: Classic, Amber, Glacier, Mint, Night glow,
// Sakura (the same names as Retro World). The time keeps the plain foreground
// for contrast; icons, gauges, the trend line and seconds take the accent, the
// heart window takes the heart colour and the date the soft tint.
// Each theme row: accent, heart, soft on black; accent, heart on white.
// Monochrome screens and the Classic theme always use the foreground.
module FacePalette {
    // Built on demand: monochrome watches (Instinct 2S has ~10 KB to spare)
    // never call this, so the tables cost them no memory.
    // MIP values come from the 64-colour panel palette so nothing is quantised.
    function table() as Array<Number> {
        if(!DeviceProfile.AMOLED){return [
        0xFFAA00,0xFF5500,0xFFAA55,0xAA5500,0xAA0000,
        0x55AAFF,0xFF5555,0xAAFFFF,0x0055AA,0xAA0000,
        0x55FFAA,0xFF5555,0xAAFFAA,0x00AA55,0xAA0000,
        0x00FFFF,0xFF55AA,0x55FFFF,0x00AAAA,0xAA0055,
        0xFF55AA,0xFF5555,0xFFAAAA,0xAA0055,0xAA0000
        ];}
        return [
        0xF0A245,0xE5533A,0xF6D7A0,0xA85A1C,0xB03A22,
        0x6CB4E4,0xE25A4E,0xCFE8F5,0x2D7EBA,0xB0443B,
        0x64C884,0xE36B5A,0xD5F0D3,0x2B9255,0xB0443B,
        0x5CF0E6,0xFF8A5C,0x9FE9E2,0x2C8C9A,0xC2563A,
        0xE68AA8,0xD23E5E,0xF8DCE4,0xC45781,0xA02A48
        ];
    }
    // Accent and heart colours on a white heart window, whatever the face theme.
    var onLightAccent=Graphics.COLOR_BLACK;var onLightHeart=Graphics.COLOR_BLACK;
    var onDarkAccent=Graphics.COLOR_WHITE;var onDarkHeart=Graphics.COLOR_WHITE;
    function theme() as Number {
        if(!DeviceProfile.COLOR){return 0;}
        var i=FacePrefs.get("colorTheme");
        return i==null || i<1 || i>5 ? 0 : i;
    }
    // Sets FaceDraw.accent/heart/soft for the current foreground/background.
    function apply(dark as Boolean) as Void {
        var i=theme();
        if(i==0){
            onLightAccent=Graphics.COLOR_BLACK;onLightHeart=Graphics.COLOR_BLACK;
            onDarkAccent=Graphics.COLOR_WHITE;onDarkHeart=Graphics.COLOR_WHITE;
            FaceDraw.accent=FaceDraw.foreground;FaceDraw.heart=FaceDraw.foreground;FaceDraw.soft=FaceDraw.foreground;
            return;
        }
        var colours=table();var row=(i-1)*5;
        onDarkAccent=colours[row];onDarkHeart=colours[row+1];
        onLightAccent=colours[row+3];onLightHeart=colours[row+4];
        FaceDraw.accent=dark ? onDarkAccent : onLightAccent;
        FaceDraw.heart=dark ? onDarkHeart : onLightHeart;
        FaceDraw.soft=dark ? colours[row+2] : FaceDraw.foreground;
    }
    // Ink for a window whose paper is black or white.
    function accentOn(paper) {return paper==Graphics.COLOR_BLACK ? onDarkAccent : onLightAccent;}
    function heartOn(paper) {return paper==Graphics.COLOR_BLACK ? onDarkHeart : onLightHeart;}
}
