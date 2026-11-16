import Toybox.Lang;
// Calendar facts: Hong Kong Observatory, assets/festivals/dates.json.
// IDs: 0 ordinary, 1 Spring Festival, 2 Christmas, 3 Halloween, 4 Mid-Autumn.
module Festival {
 var spring as Array<Number> = [25, 43, 32, 22, 41, 29, 48, 37, 26, 44, 34, 23, 42, 31, 50, 39, 28, 46, 35, 24, 43];
 var autumn as Array<Number> = [275, 264, 253, 272, 261, 279, 268, 258, 277, 265, 255, 274, 263, 251, 270, 259, 278, 267, 256, 275, 264];
 function dayOfYear(year,month,day) {
  var before = [0,31,59,90,120,151,181,212,243,273,304,334] as Array<Number>;
  var leap=year%4==0 && (year%100!=0 || year%400==0);
  return before[month-1]+day+(leap && month>2 ? 1 : 0);
 }
 function choose(year,month,day,setting) {
  if(setting==1) {return 0;}
  if(setting>=2 && setting<=5) {return setting-1;}
  if(month==12 && day>=24 && day<=26) {return 2;}
  if(month==10 && day==31) {return 3;}
  if(year<2020 || year>2040 || month<1 || month>12 || day<1 || day>31) {return 0;}
  var index=year-2020;var doy=dayOfYear(year,month,day);
  // Eve through lunar Jan 7; Mid-Autumn on lunar Aug 15 (not a leap month).
  if(doy>=spring[index]-1 && doy<=spring[index]+6) {return 1;}
  return doy==autumn[index] ? 4 : 0;
 }
 function accent(holiday,fallback) {
  if(Device.MONO || holiday==0) {return fallback;}
  return holiday==1 ? 0xFFCC66 : (holiday==2 ? 0x99DDCC : (holiday==3 ? 0xFFAA55 : 0xDDCC99));
 }
}
