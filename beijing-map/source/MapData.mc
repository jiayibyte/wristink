import Toybox.Lang;
module MapData {
const XDEG=85276.067408; const YDEG=111320; const TILE=16000;
const MINX=2;const MAXX=13;const MINY=3;const MAXY=14;
(:extendedCode)
function chunks(tx,ty) { if(tx<MINX || tx>MAXX){return [];} var row;switch(ty) {
case 3: row=row3();break;
case 4: row=row4();break;
case 5: row=row5();break;
case 6: row=row6();break;
case 7: row=row7();break;
case 8: row=row8();break;
case 9: row=row9();break;
case 10: row=row10();break;
case 11: row=row11();break;
case 12: row=row12();break;
case 13: row=row13();break;
case 14: row=row14();break;
default:return [];} return (row as Array)[tx-MINX]; }
(:extendedCode)
function row3() { return [
[],
[Rez.JsonData.Tile_3_3_0],
[Rez.JsonData.Tile_4_3_0,Rez.JsonData.Tile_4_3_1,Rez.JsonData.Tile_4_3_2],
[Rez.JsonData.Tile_5_3_0],
[Rez.JsonData.Tile_6_3_0,Rez.JsonData.Tile_6_3_1],
[Rez.JsonData.Tile_7_3_0,Rez.JsonData.Tile_7_3_1,Rez.JsonData.Tile_7_3_2,Rez.JsonData.Tile_7_3_3],
[Rez.JsonData.Tile_8_3_0],
[],
[],
[],
[],
[],
]; }
(:extendedCode)
function row4() { return [
[Rez.JsonData.Tile_2_4_0,Rez.JsonData.Tile_2_4_1,Rez.JsonData.Tile_2_4_2,Rez.JsonData.Tile_2_4_3],
[Rez.JsonData.Tile_3_4_0,Rez.JsonData.Tile_3_4_1,Rez.JsonData.Tile_3_4_2,Rez.JsonData.Tile_3_4_3,Rez.JsonData.Tile_3_4_4,Rez.JsonData.Tile_3_4_5,Rez.JsonData.Tile_3_4_6,Rez.JsonData.Tile_3_4_7,Rez.JsonData.Tile_3_4_8,Rez.JsonData.Tile_3_4_9,Rez.JsonData.Tile_3_4_10,Rez.JsonData.Tile_3_4_11,Rez.JsonData.Tile_3_4_12,Rez.JsonData.Tile_3_4_13,Rez.JsonData.Tile_3_4_14,Rez.JsonData.Tile_3_4_15,Rez.JsonData.Tile_3_4_16],
[Rez.JsonData.Tile_4_4_0,Rez.JsonData.Tile_4_4_1,Rez.JsonData.Tile_4_4_2,Rez.JsonData.Tile_4_4_3,Rez.JsonData.Tile_4_4_4,Rez.JsonData.Tile_4_4_5,Rez.JsonData.Tile_4_4_6,Rez.JsonData.Tile_4_4_7,Rez.JsonData.Tile_4_4_8,Rez.JsonData.Tile_4_4_9,Rez.JsonData.Tile_4_4_10,Rez.JsonData.Tile_4_4_11,Rez.JsonData.Tile_4_4_12,Rez.JsonData.Tile_4_4_13,Rez.JsonData.Tile_4_4_14],
[Rez.JsonData.Tile_5_4_0,Rez.JsonData.Tile_5_4_1,Rez.JsonData.Tile_5_4_2,Rez.JsonData.Tile_5_4_3,Rez.JsonData.Tile_5_4_4,Rez.JsonData.Tile_5_4_5,Rez.JsonData.Tile_5_4_6,Rez.JsonData.Tile_5_4_7,Rez.JsonData.Tile_5_4_8],
[Rez.JsonData.Tile_6_4_0,Rez.JsonData.Tile_6_4_1,Rez.JsonData.Tile_6_4_2,Rez.JsonData.Tile_6_4_3,Rez.JsonData.Tile_6_4_4,Rez.JsonData.Tile_6_4_5,Rez.JsonData.Tile_6_4_6,Rez.JsonData.Tile_6_4_7],
[Rez.JsonData.Tile_7_4_0,Rez.JsonData.Tile_7_4_1,Rez.JsonData.Tile_7_4_2,Rez.JsonData.Tile_7_4_3,Rez.JsonData.Tile_7_4_4,Rez.JsonData.Tile_7_4_5,Rez.JsonData.Tile_7_4_6,Rez.JsonData.Tile_7_4_7],
[Rez.JsonData.Tile_8_4_0,Rez.JsonData.Tile_8_4_1,Rez.JsonData.Tile_8_4_2,Rez.JsonData.Tile_8_4_3,Rez.JsonData.Tile_8_4_4],
[Rez.JsonData.Tile_9_4_0,Rez.JsonData.Tile_9_4_1,Rez.JsonData.Tile_9_4_2,Rez.JsonData.Tile_9_4_3,Rez.JsonData.Tile_9_4_4],
[Rez.JsonData.Tile_10_4_0],
[],
[],
[],
]; }
(:extendedCode)
function row5() { return [
[Rez.JsonData.Tile_2_5_0,Rez.JsonData.Tile_2_5_1,Rez.JsonData.Tile_2_5_2,Rez.JsonData.Tile_2_5_3,Rez.JsonData.Tile_2_5_4,Rez.JsonData.Tile_2_5_5,Rez.JsonData.Tile_2_5_6,Rez.JsonData.Tile_2_5_7],
[Rez.JsonData.Tile_3_5_0,Rez.JsonData.Tile_3_5_1,Rez.JsonData.Tile_3_5_2,Rez.JsonData.Tile_3_5_3,Rez.JsonData.Tile_3_5_4,Rez.JsonData.Tile_3_5_5,Rez.JsonData.Tile_3_5_6,Rez.JsonData.Tile_3_5_7,Rez.JsonData.Tile_3_5_8,Rez.JsonData.Tile_3_5_9,Rez.JsonData.Tile_3_5_10,Rez.JsonData.Tile_3_5_11,Rez.JsonData.Tile_3_5_12,Rez.JsonData.Tile_3_5_13],
[Rez.JsonData.Tile_4_5_0,Rez.JsonData.Tile_4_5_1,Rez.JsonData.Tile_4_5_2,Rez.JsonData.Tile_4_5_3,Rez.JsonData.Tile_4_5_4,Rez.JsonData.Tile_4_5_5,Rez.JsonData.Tile_4_5_6,Rez.JsonData.Tile_4_5_7,Rez.JsonData.Tile_4_5_8,Rez.JsonData.Tile_4_5_9,Rez.JsonData.Tile_4_5_10,Rez.JsonData.Tile_4_5_11,Rez.JsonData.Tile_4_5_12,Rez.JsonData.Tile_4_5_13],
[Rez.JsonData.Tile_5_5_0,Rez.JsonData.Tile_5_5_1,Rez.JsonData.Tile_5_5_2,Rez.JsonData.Tile_5_5_3,Rez.JsonData.Tile_5_5_4,Rez.JsonData.Tile_5_5_5,Rez.JsonData.Tile_5_5_6,Rez.JsonData.Tile_5_5_7,Rez.JsonData.Tile_5_5_8,Rez.JsonData.Tile_5_5_9,Rez.JsonData.Tile_5_5_10,Rez.JsonData.Tile_5_5_11,Rez.JsonData.Tile_5_5_12,Rez.JsonData.Tile_5_5_13,Rez.JsonData.Tile_5_5_14,Rez.JsonData.Tile_5_5_15,Rez.JsonData.Tile_5_5_16],
[Rez.JsonData.Tile_6_5_0,Rez.JsonData.Tile_6_5_1,Rez.JsonData.Tile_6_5_2,Rez.JsonData.Tile_6_5_3,Rez.JsonData.Tile_6_5_4,Rez.JsonData.Tile_6_5_5,Rez.JsonData.Tile_6_5_6,Rez.JsonData.Tile_6_5_7,Rez.JsonData.Tile_6_5_8,Rez.JsonData.Tile_6_5_9,Rez.JsonData.Tile_6_5_10,Rez.JsonData.Tile_6_5_11,Rez.JsonData.Tile_6_5_12,Rez.JsonData.Tile_6_5_13,Rez.JsonData.Tile_6_5_14,Rez.JsonData.Tile_6_5_15,Rez.JsonData.Tile_6_5_16,Rez.JsonData.Tile_6_5_17],
[Rez.JsonData.Tile_7_5_0,Rez.JsonData.Tile_7_5_1,Rez.JsonData.Tile_7_5_2,Rez.JsonData.Tile_7_5_3,Rez.JsonData.Tile_7_5_4,Rez.JsonData.Tile_7_5_5,Rez.JsonData.Tile_7_5_6,Rez.JsonData.Tile_7_5_7,Rez.JsonData.Tile_7_5_8,Rez.JsonData.Tile_7_5_9,Rez.JsonData.Tile_7_5_10,Rez.JsonData.Tile_7_5_11,Rez.JsonData.Tile_7_5_12,Rez.JsonData.Tile_7_5_13,Rez.JsonData.Tile_7_5_14,Rez.JsonData.Tile_7_5_15,Rez.JsonData.Tile_7_5_16,Rez.JsonData.Tile_7_5_17],
[Rez.JsonData.Tile_8_5_0,Rez.JsonData.Tile_8_5_1,Rez.JsonData.Tile_8_5_2,Rez.JsonData.Tile_8_5_3,Rez.JsonData.Tile_8_5_4,Rez.JsonData.Tile_8_5_5,Rez.JsonData.Tile_8_5_6,Rez.JsonData.Tile_8_5_7,Rez.JsonData.Tile_8_5_8,Rez.JsonData.Tile_8_5_9],
[Rez.JsonData.Tile_9_5_0,Rez.JsonData.Tile_9_5_1,Rez.JsonData.Tile_9_5_2,Rez.JsonData.Tile_9_5_3,Rez.JsonData.Tile_9_5_4,Rez.JsonData.Tile_9_5_5,Rez.JsonData.Tile_9_5_6,Rez.JsonData.Tile_9_5_7,Rez.JsonData.Tile_9_5_8],
[Rez.JsonData.Tile_10_5_0,Rez.JsonData.Tile_10_5_1],
[],
[],
[],
]; }
(:extendedCode)
function row6() { return [
[Rez.JsonData.Tile_2_6_0,Rez.JsonData.Tile_2_6_1,Rez.JsonData.Tile_2_6_2,Rez.JsonData.Tile_2_6_3,Rez.JsonData.Tile_2_6_4,Rez.JsonData.Tile_2_6_5],
[Rez.JsonData.Tile_3_6_0,Rez.JsonData.Tile_3_6_1,Rez.JsonData.Tile_3_6_2,Rez.JsonData.Tile_3_6_3,Rez.JsonData.Tile_3_6_4,Rez.JsonData.Tile_3_6_5,Rez.JsonData.Tile_3_6_6,Rez.JsonData.Tile_3_6_7,Rez.JsonData.Tile_3_6_8,Rez.JsonData.Tile_3_6_9,Rez.JsonData.Tile_3_6_10,Rez.JsonData.Tile_3_6_11,Rez.JsonData.Tile_3_6_12,Rez.JsonData.Tile_3_6_13,Rez.JsonData.Tile_3_6_14,Rez.JsonData.Tile_3_6_15],
[Rez.JsonData.Tile_4_6_0,Rez.JsonData.Tile_4_6_1,Rez.JsonData.Tile_4_6_2,Rez.JsonData.Tile_4_6_3,Rez.JsonData.Tile_4_6_4,Rez.JsonData.Tile_4_6_5,Rez.JsonData.Tile_4_6_6,Rez.JsonData.Tile_4_6_7,Rez.JsonData.Tile_4_6_8,Rez.JsonData.Tile_4_6_9,Rez.JsonData.Tile_4_6_10,Rez.JsonData.Tile_4_6_11,Rez.JsonData.Tile_4_6_12,Rez.JsonData.Tile_4_6_13],
[Rez.JsonData.Tile_5_6_0,Rez.JsonData.Tile_5_6_1,Rez.JsonData.Tile_5_6_2,Rez.JsonData.Tile_5_6_3,Rez.JsonData.Tile_5_6_4,Rez.JsonData.Tile_5_6_5,Rez.JsonData.Tile_5_6_6,Rez.JsonData.Tile_5_6_7,Rez.JsonData.Tile_5_6_8,Rez.JsonData.Tile_5_6_9,Rez.JsonData.Tile_5_6_10,Rez.JsonData.Tile_5_6_11,Rez.JsonData.Tile_5_6_12,Rez.JsonData.Tile_5_6_13,Rez.JsonData.Tile_5_6_14,Rez.JsonData.Tile_5_6_15,Rez.JsonData.Tile_5_6_16,Rez.JsonData.Tile_5_6_17,Rez.JsonData.Tile_5_6_18,Rez.JsonData.Tile_5_6_19,Rez.JsonData.Tile_5_6_20,Rez.JsonData.Tile_5_6_21,Rez.JsonData.Tile_5_6_22],
[Rez.JsonData.Tile_6_6_0,Rez.JsonData.Tile_6_6_1,Rez.JsonData.Tile_6_6_2,Rez.JsonData.Tile_6_6_3,Rez.JsonData.Tile_6_6_4,Rez.JsonData.Tile_6_6_5,Rez.JsonData.Tile_6_6_6,Rez.JsonData.Tile_6_6_7,Rez.JsonData.Tile_6_6_8,Rez.JsonData.Tile_6_6_9,Rez.JsonData.Tile_6_6_10,Rez.JsonData.Tile_6_6_11,Rez.JsonData.Tile_6_6_12,Rez.JsonData.Tile_6_6_13,Rez.JsonData.Tile_6_6_14,Rez.JsonData.Tile_6_6_15,Rez.JsonData.Tile_6_6_16,Rez.JsonData.Tile_6_6_17,Rez.JsonData.Tile_6_6_18,Rez.JsonData.Tile_6_6_19,Rez.JsonData.Tile_6_6_20,Rez.JsonData.Tile_6_6_21,Rez.JsonData.Tile_6_6_22,Rez.JsonData.Tile_6_6_23,Rez.JsonData.Tile_6_6_24,Rez.JsonData.Tile_6_6_25,Rez.JsonData.Tile_6_6_26,Rez.JsonData.Tile_6_6_27,Rez.JsonData.Tile_6_6_28,Rez.JsonData.Tile_6_6_29,Rez.JsonData.Tile_6_6_30,Rez.JsonData.Tile_6_6_31,Rez.JsonData.Tile_6_6_32],
[Rez.JsonData.Tile_7_6_0,Rez.JsonData.Tile_7_6_1,Rez.JsonData.Tile_7_6_2,Rez.JsonData.Tile_7_6_3,Rez.JsonData.Tile_7_6_4,Rez.JsonData.Tile_7_6_5,Rez.JsonData.Tile_7_6_6,Rez.JsonData.Tile_7_6_7,Rez.JsonData.Tile_7_6_8,Rez.JsonData.Tile_7_6_9,Rez.JsonData.Tile_7_6_10,Rez.JsonData.Tile_7_6_11,Rez.JsonData.Tile_7_6_12,Rez.JsonData.Tile_7_6_13,Rez.JsonData.Tile_7_6_14,Rez.JsonData.Tile_7_6_15,Rez.JsonData.Tile_7_6_16,Rez.JsonData.Tile_7_6_17,Rez.JsonData.Tile_7_6_18,Rez.JsonData.Tile_7_6_19,Rez.JsonData.Tile_7_6_20,Rez.JsonData.Tile_7_6_21,Rez.JsonData.Tile_7_6_22,Rez.JsonData.Tile_7_6_23,Rez.JsonData.Tile_7_6_24,Rez.JsonData.Tile_7_6_25,Rez.JsonData.Tile_7_6_26,Rez.JsonData.Tile_7_6_27,Rez.JsonData.Tile_7_6_28,Rez.JsonData.Tile_7_6_29,Rez.JsonData.Tile_7_6_30,Rez.JsonData.Tile_7_6_31,Rez.JsonData.Tile_7_6_32,Rez.JsonData.Tile_7_6_33,Rez.JsonData.Tile_7_6_34,Rez.JsonData.Tile_7_6_35,Rez.JsonData.Tile_7_6_36,Rez.JsonData.Tile_7_6_37,Rez.JsonData.Tile_7_6_38,Rez.JsonData.Tile_7_6_39,Rez.JsonData.Tile_7_6_40,Rez.JsonData.Tile_7_6_41,Rez.JsonData.Tile_7_6_42,Rez.JsonData.Tile_7_6_43,Rez.JsonData.Tile_7_6_44,Rez.JsonData.Tile_7_6_45,Rez.JsonData.Tile_7_6_46,Rez.JsonData.Tile_7_6_47,Rez.JsonData.Tile_7_6_48,Rez.JsonData.Tile_7_6_49],
[Rez.JsonData.Tile_8_6_0,Rez.JsonData.Tile_8_6_1,Rez.JsonData.Tile_8_6_2,Rez.JsonData.Tile_8_6_3,Rez.JsonData.Tile_8_6_4,Rez.JsonData.Tile_8_6_5,Rez.JsonData.Tile_8_6_6,Rez.JsonData.Tile_8_6_7,Rez.JsonData.Tile_8_6_8,Rez.JsonData.Tile_8_6_9,Rez.JsonData.Tile_8_6_10,Rez.JsonData.Tile_8_6_11,Rez.JsonData.Tile_8_6_12,Rez.JsonData.Tile_8_6_13],
[Rez.JsonData.Tile_9_6_0,Rez.JsonData.Tile_9_6_1,Rez.JsonData.Tile_9_6_2,Rez.JsonData.Tile_9_6_3,Rez.JsonData.Tile_9_6_4,Rez.JsonData.Tile_9_6_5,Rez.JsonData.Tile_9_6_6,Rez.JsonData.Tile_9_6_7,Rez.JsonData.Tile_9_6_8],
[Rez.JsonData.Tile_10_6_0],
[],
[],
[],
]; }
(:extendedCode)
function row7() { return [
[Rez.JsonData.Tile_2_7_0,Rez.JsonData.Tile_2_7_1],
[Rez.JsonData.Tile_3_7_0,Rez.JsonData.Tile_3_7_1,Rez.JsonData.Tile_3_7_2,Rez.JsonData.Tile_3_7_3,Rez.JsonData.Tile_3_7_4,Rez.JsonData.Tile_3_7_5,Rez.JsonData.Tile_3_7_6,Rez.JsonData.Tile_3_7_7,Rez.JsonData.Tile_3_7_8,Rez.JsonData.Tile_3_7_9],
[Rez.JsonData.Tile_4_7_0,Rez.JsonData.Tile_4_7_1,Rez.JsonData.Tile_4_7_2,Rez.JsonData.Tile_4_7_3,Rez.JsonData.Tile_4_7_4,Rez.JsonData.Tile_4_7_5,Rez.JsonData.Tile_4_7_6,Rez.JsonData.Tile_4_7_7,Rez.JsonData.Tile_4_7_8,Rez.JsonData.Tile_4_7_9,Rez.JsonData.Tile_4_7_10,Rez.JsonData.Tile_4_7_11,Rez.JsonData.Tile_4_7_12,Rez.JsonData.Tile_4_7_13,Rez.JsonData.Tile_4_7_14],
[Rez.JsonData.Tile_5_7_0,Rez.JsonData.Tile_5_7_1,Rez.JsonData.Tile_5_7_2,Rez.JsonData.Tile_5_7_3,Rez.JsonData.Tile_5_7_4,Rez.JsonData.Tile_5_7_5,Rez.JsonData.Tile_5_7_6,Rez.JsonData.Tile_5_7_7,Rez.JsonData.Tile_5_7_8,Rez.JsonData.Tile_5_7_9,Rez.JsonData.Tile_5_7_10,Rez.JsonData.Tile_5_7_11,Rez.JsonData.Tile_5_7_12,Rez.JsonData.Tile_5_7_13,Rez.JsonData.Tile_5_7_14,Rez.JsonData.Tile_5_7_15,Rez.JsonData.Tile_5_7_16,Rez.JsonData.Tile_5_7_17,Rez.JsonData.Tile_5_7_18,Rez.JsonData.Tile_5_7_19],
[Rez.JsonData.Tile_6_7_0,Rez.JsonData.Tile_6_7_1,Rez.JsonData.Tile_6_7_2,Rez.JsonData.Tile_6_7_3,Rez.JsonData.Tile_6_7_4,Rez.JsonData.Tile_6_7_5,Rez.JsonData.Tile_6_7_6,Rez.JsonData.Tile_6_7_7,Rez.JsonData.Tile_6_7_8,Rez.JsonData.Tile_6_7_9,Rez.JsonData.Tile_6_7_10,Rez.JsonData.Tile_6_7_11,Rez.JsonData.Tile_6_7_12,Rez.JsonData.Tile_6_7_13,Rez.JsonData.Tile_6_7_14,Rez.JsonData.Tile_6_7_15,Rez.JsonData.Tile_6_7_16,Rez.JsonData.Tile_6_7_17,Rez.JsonData.Tile_6_7_18,Rez.JsonData.Tile_6_7_19,Rez.JsonData.Tile_6_7_20,Rez.JsonData.Tile_6_7_21],
[Rez.JsonData.Tile_7_7_0,Rez.JsonData.Tile_7_7_1,Rez.JsonData.Tile_7_7_2,Rez.JsonData.Tile_7_7_3,Rez.JsonData.Tile_7_7_4,Rez.JsonData.Tile_7_7_5,Rez.JsonData.Tile_7_7_6,Rez.JsonData.Tile_7_7_7,Rez.JsonData.Tile_7_7_8,Rez.JsonData.Tile_7_7_9,Rez.JsonData.Tile_7_7_10,Rez.JsonData.Tile_7_7_11,Rez.JsonData.Tile_7_7_12,Rez.JsonData.Tile_7_7_13,Rez.JsonData.Tile_7_7_14,Rez.JsonData.Tile_7_7_15,Rez.JsonData.Tile_7_7_16,Rez.JsonData.Tile_7_7_17,Rez.JsonData.Tile_7_7_18,Rez.JsonData.Tile_7_7_19,Rez.JsonData.Tile_7_7_20,Rez.JsonData.Tile_7_7_21,Rez.JsonData.Tile_7_7_22,Rez.JsonData.Tile_7_7_23,Rez.JsonData.Tile_7_7_24,Rez.JsonData.Tile_7_7_25],
[Rez.JsonData.Tile_8_7_0,Rez.JsonData.Tile_8_7_1,Rez.JsonData.Tile_8_7_2,Rez.JsonData.Tile_8_7_3,Rez.JsonData.Tile_8_7_4,Rez.JsonData.Tile_8_7_5,Rez.JsonData.Tile_8_7_6,Rez.JsonData.Tile_8_7_7,Rez.JsonData.Tile_8_7_8,Rez.JsonData.Tile_8_7_9],
[Rez.JsonData.Tile_9_7_0,Rez.JsonData.Tile_9_7_1,Rez.JsonData.Tile_9_7_2],
[Rez.JsonData.Tile_10_7_0,Rez.JsonData.Tile_10_7_1,Rez.JsonData.Tile_10_7_2],
[Rez.JsonData.Tile_11_7_0,Rez.JsonData.Tile_11_7_1,Rez.JsonData.Tile_11_7_2,Rez.JsonData.Tile_11_7_3],
[Rez.JsonData.Tile_12_7_0],
[],
]; }
(:extendedCode)
function row8() { return [
[],
[Rez.JsonData.Tile_3_8_0],
[Rez.JsonData.Tile_4_8_0,Rez.JsonData.Tile_4_8_1,Rez.JsonData.Tile_4_8_2,Rez.JsonData.Tile_4_8_3,Rez.JsonData.Tile_4_8_4,Rez.JsonData.Tile_4_8_5],
[Rez.JsonData.Tile_5_8_0,Rez.JsonData.Tile_5_8_1,Rez.JsonData.Tile_5_8_2,Rez.JsonData.Tile_5_8_3,Rez.JsonData.Tile_5_8_4,Rez.JsonData.Tile_5_8_5,Rez.JsonData.Tile_5_8_6,Rez.JsonData.Tile_5_8_7,Rez.JsonData.Tile_5_8_8,Rez.JsonData.Tile_5_8_9,Rez.JsonData.Tile_5_8_10,Rez.JsonData.Tile_5_8_11,Rez.JsonData.Tile_5_8_12],
[Rez.JsonData.Tile_6_8_0,Rez.JsonData.Tile_6_8_1,Rez.JsonData.Tile_6_8_2,Rez.JsonData.Tile_6_8_3,Rez.JsonData.Tile_6_8_4,Rez.JsonData.Tile_6_8_5,Rez.JsonData.Tile_6_8_6,Rez.JsonData.Tile_6_8_7,Rez.JsonData.Tile_6_8_8,Rez.JsonData.Tile_6_8_9,Rez.JsonData.Tile_6_8_10,Rez.JsonData.Tile_6_8_11,Rez.JsonData.Tile_6_8_12,Rez.JsonData.Tile_6_8_13,Rez.JsonData.Tile_6_8_14,Rez.JsonData.Tile_6_8_15,Rez.JsonData.Tile_6_8_16,Rez.JsonData.Tile_6_8_17,Rez.JsonData.Tile_6_8_18,Rez.JsonData.Tile_6_8_19],
[Rez.JsonData.Tile_7_8_0,Rez.JsonData.Tile_7_8_1,Rez.JsonData.Tile_7_8_2,Rez.JsonData.Tile_7_8_3,Rez.JsonData.Tile_7_8_4,Rez.JsonData.Tile_7_8_5],
[Rez.JsonData.Tile_8_8_0,Rez.JsonData.Tile_8_8_1,Rez.JsonData.Tile_8_8_2,Rez.JsonData.Tile_8_8_3,Rez.JsonData.Tile_8_8_4],
[Rez.JsonData.Tile_9_8_0,Rez.JsonData.Tile_9_8_1,Rez.JsonData.Tile_9_8_2,Rez.JsonData.Tile_9_8_3],
[Rez.JsonData.Tile_10_8_0,Rez.JsonData.Tile_10_8_1,Rez.JsonData.Tile_10_8_2,Rez.JsonData.Tile_10_8_3],
[Rez.JsonData.Tile_11_8_0,Rez.JsonData.Tile_11_8_1,Rez.JsonData.Tile_11_8_2,Rez.JsonData.Tile_11_8_3,Rez.JsonData.Tile_11_8_4],
[Rez.JsonData.Tile_12_8_0,Rez.JsonData.Tile_12_8_1,Rez.JsonData.Tile_12_8_2,Rez.JsonData.Tile_12_8_3],
[],
]; }
(:extendedCode)
function row9() { return [
[],
[],
[Rez.JsonData.Tile_4_9_0,Rez.JsonData.Tile_4_9_1,Rez.JsonData.Tile_4_9_2],
[Rez.JsonData.Tile_5_9_0,Rez.JsonData.Tile_5_9_1,Rez.JsonData.Tile_5_9_2,Rez.JsonData.Tile_5_9_3,Rez.JsonData.Tile_5_9_4,Rez.JsonData.Tile_5_9_5,Rez.JsonData.Tile_5_9_6,Rez.JsonData.Tile_5_9_7,Rez.JsonData.Tile_5_9_8,Rez.JsonData.Tile_5_9_9,Rez.JsonData.Tile_5_9_10,Rez.JsonData.Tile_5_9_11,Rez.JsonData.Tile_5_9_12,Rez.JsonData.Tile_5_9_13,Rez.JsonData.Tile_5_9_14,Rez.JsonData.Tile_5_9_15,Rez.JsonData.Tile_5_9_16,Rez.JsonData.Tile_5_9_17,Rez.JsonData.Tile_5_9_18,Rez.JsonData.Tile_5_9_19],
[Rez.JsonData.Tile_6_9_0,Rez.JsonData.Tile_6_9_1,Rez.JsonData.Tile_6_9_2,Rez.JsonData.Tile_6_9_3,Rez.JsonData.Tile_6_9_4,Rez.JsonData.Tile_6_9_5,Rez.JsonData.Tile_6_9_6,Rez.JsonData.Tile_6_9_7,Rez.JsonData.Tile_6_9_8,Rez.JsonData.Tile_6_9_9,Rez.JsonData.Tile_6_9_10,Rez.JsonData.Tile_6_9_11,Rez.JsonData.Tile_6_9_12,Rez.JsonData.Tile_6_9_13],
[Rez.JsonData.Tile_7_9_0,Rez.JsonData.Tile_7_9_1,Rez.JsonData.Tile_7_9_2],
[Rez.JsonData.Tile_8_9_0,Rez.JsonData.Tile_8_9_1,Rez.JsonData.Tile_8_9_2,Rez.JsonData.Tile_8_9_3,Rez.JsonData.Tile_8_9_4,Rez.JsonData.Tile_8_9_5,Rez.JsonData.Tile_8_9_6,Rez.JsonData.Tile_8_9_7],
[Rez.JsonData.Tile_9_9_0,Rez.JsonData.Tile_9_9_1,Rez.JsonData.Tile_9_9_2,Rez.JsonData.Tile_9_9_3,Rez.JsonData.Tile_9_9_4,Rez.JsonData.Tile_9_9_5],
[Rez.JsonData.Tile_10_9_0,Rez.JsonData.Tile_10_9_1,Rez.JsonData.Tile_10_9_2,Rez.JsonData.Tile_10_9_3],
[Rez.JsonData.Tile_11_9_0,Rez.JsonData.Tile_11_9_1,Rez.JsonData.Tile_11_9_2,Rez.JsonData.Tile_11_9_3,Rez.JsonData.Tile_11_9_4],
[Rez.JsonData.Tile_12_9_0],
[],
]; }
(:extendedCode)
function row10() { return [
[],
[Rez.JsonData.Tile_3_10_0],
[Rez.JsonData.Tile_4_10_0,Rez.JsonData.Tile_4_10_1,Rez.JsonData.Tile_4_10_2,Rez.JsonData.Tile_4_10_3],
[Rez.JsonData.Tile_5_10_0,Rez.JsonData.Tile_5_10_1,Rez.JsonData.Tile_5_10_2,Rez.JsonData.Tile_5_10_3,Rez.JsonData.Tile_5_10_4,Rez.JsonData.Tile_5_10_5,Rez.JsonData.Tile_5_10_6,Rez.JsonData.Tile_5_10_7,Rez.JsonData.Tile_5_10_8,Rez.JsonData.Tile_5_10_9],
[Rez.JsonData.Tile_6_10_0,Rez.JsonData.Tile_6_10_1,Rez.JsonData.Tile_6_10_2,Rez.JsonData.Tile_6_10_3,Rez.JsonData.Tile_6_10_4,Rez.JsonData.Tile_6_10_5,Rez.JsonData.Tile_6_10_6,Rez.JsonData.Tile_6_10_7,Rez.JsonData.Tile_6_10_8],
[Rez.JsonData.Tile_7_10_0,Rez.JsonData.Tile_7_10_1,Rez.JsonData.Tile_7_10_2],
[Rez.JsonData.Tile_8_10_0,Rez.JsonData.Tile_8_10_1,Rez.JsonData.Tile_8_10_2],
[Rez.JsonData.Tile_9_10_0,Rez.JsonData.Tile_9_10_1,Rez.JsonData.Tile_9_10_2,Rez.JsonData.Tile_9_10_3],
[Rez.JsonData.Tile_10_10_0,Rez.JsonData.Tile_10_10_1,Rez.JsonData.Tile_10_10_2],
[Rez.JsonData.Tile_11_10_0,Rez.JsonData.Tile_11_10_1,Rez.JsonData.Tile_11_10_2],
[Rez.JsonData.Tile_12_10_0],
[Rez.JsonData.Tile_13_10_0],
]; }
(:extendedCode)
function row11() { return [
[],
[Rez.JsonData.Tile_3_11_0],
[Rez.JsonData.Tile_4_11_0],
[Rez.JsonData.Tile_5_11_0],
[Rez.JsonData.Tile_6_11_0,Rez.JsonData.Tile_6_11_1],
[Rez.JsonData.Tile_7_11_0],
[Rez.JsonData.Tile_8_11_0,Rez.JsonData.Tile_8_11_1],
[Rez.JsonData.Tile_9_11_0,Rez.JsonData.Tile_9_11_1],
[Rez.JsonData.Tile_10_11_0,Rez.JsonData.Tile_10_11_1],
[Rez.JsonData.Tile_11_11_0,Rez.JsonData.Tile_11_11_1,Rez.JsonData.Tile_11_11_2,Rez.JsonData.Tile_11_11_3],
[Rez.JsonData.Tile_12_11_0,Rez.JsonData.Tile_12_11_1,Rez.JsonData.Tile_12_11_2],
[Rez.JsonData.Tile_13_11_0],
]; }
(:extendedCode)
function row12() { return [
[],
[],
[],
[Rez.JsonData.Tile_5_12_0],
[Rez.JsonData.Tile_6_12_0],
[Rez.JsonData.Tile_7_12_0],
[Rez.JsonData.Tile_8_12_0,Rez.JsonData.Tile_8_12_1],
[Rez.JsonData.Tile_9_12_0,Rez.JsonData.Tile_9_12_1],
[Rez.JsonData.Tile_10_12_0],
[Rez.JsonData.Tile_11_12_0],
[],
[],
]; }
(:extendedCode)
function row13() { return [
[],
[],
[],
[],
[],
[Rez.JsonData.Tile_7_13_0,Rez.JsonData.Tile_7_13_1],
[Rez.JsonData.Tile_8_13_0,Rez.JsonData.Tile_8_13_1],
[Rez.JsonData.Tile_9_13_0],
[Rez.JsonData.Tile_10_13_0],
[],
[],
[],
]; }
(:extendedCode)
function row14() { return [
[],
[],
[],
[],
[],
[],
[Rez.JsonData.Tile_8_14_0],
[],
[],
[],
[],
[],
]; }
}