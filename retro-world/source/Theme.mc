import Toybox.Graphics;
import Toybox.Lang;

// Colour themes for AMOLED and colour MIP screens. Sprites are fonts and the
// panels are vectors, so a theme is only these six colours: paper, ink, panel
// frame, map land, second hand and the light label colour on black.
// Monochrome screens always use black and white.
module Theme {
    var index=-1;
    var paper=0xFFFFFF;var ink=0x000000;var frame=0xFFFFFF;var map=0x000000;var hand=0x000000;var label=0xFFFFFF;
    // Classic, Amber, Glacier, Mint, Night glow, Sakura.
    var AMOLED_COLORS as Array<Number> = [
        0xE8EDDC,0x000000,0x63B6A4,0x63B6A4,0xF07869,0xE8EDDC,
        0xF6C978,0x2A1700,0xF0A245,0xA85A1C,0xD9482B,0xF6D7A0,
        0xD4EBF7,0x0A2433,0x6CB4E4,0x2D7EBA,0xE25A4E,0xCFE8F5,
        0xD5F0D3,0x0E2A17,0x64C884,0x2B9255,0xE36B5A,0xD5F0D3,
        0x0D2230,0x5CF0E6,0x2C8C9A,0x3CC4BE,0xFF8A5C,0x9FE9E2,
        0xF8DCE4,0x3B1022,0xE68AA8,0xC45781,0xD23E5E,0xF8DCE4
    ];
    // The same themes from the 64-colour MIP panel palette, so nothing is quantised.
    var MIP_COLORS as Array<Number> = [
        0xFFFFAA,0x000000,0x00AAAA,0x00AAAA,0xFF5555,0xFFFFFF,
        0xFFAA55,0x000000,0xFFAA00,0xAA5500,0xAA0000,0xFFFFAA,
        0xAAFFFF,0x000055,0x55AAFF,0x0055AA,0xFF5555,0xAAFFFF,
        0xAAFFAA,0x005500,0x55AA55,0x00AA55,0xFF5555,0xAAFFAA,
        0x000055,0x55FFFF,0x00AAAA,0x00AAAA,0xFF5555,0x55FFFF,
        0xFFAAAA,0x550000,0xFF55AA,0xAA0055,0xAA0000,0xFFAAAA
    ];
    function load(i as Number) as Void {
        index=i;
        if(!DeviceProfile.COLOR) {paper=0xFFFFFF;ink=0x000000;frame=0xFFFFFF;map=0x000000;hand=0x000000;label=0xFFFFFF;return;}
        var table=DeviceProfile.AMOLED ? AMOLED_COLORS : MIP_COLORS;var b=i*6;
        paper=table[b];ink=table[b+1];frame=table[b+2];map=table[b+3];hand=table[b+4];label=table[b+5];
    }
    // Colours a cached buffer (dial centre, map) can contain.
    function palette() as Array<Number> {
        var out=[0x000000] as Array<Number>;var colors=[paper,ink,map,frame];
        for(var i=0;i<colors.size();i++) {
            var seen=false;for(var j=0;j<out.size();j++) {if(out[j]==colors[i]) {seen=true;}}
            if(!seen) {out.add(colors[i]);}
        }
        out.add(Graphics.COLOR_TRANSPARENT);return out;
    }
}
