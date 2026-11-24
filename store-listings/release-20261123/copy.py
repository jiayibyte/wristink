"""Store copy for the 2026-11-23 updates: Moke 1.4.0, Retro World 2.2.1, Alpine 1.3.0.

Descriptions are the published ones with small, targeted edits; only the
"What's new" text is new. Run this file to write <app>.json next to it.
Theme names stay English outside Chinese because the settings are English there.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LANGS = ["cs", "da", "de", "el", "en", "es", "fi", "fr", "hr", "hu", "in", "it", "iw", "ja",
         "ko", "ms", "nb", "nl", "pl", "pt_BR", "pt_PT", "ru", "sk", "sl", "sv", "th", "zh_CN", "zh_TW"]

# ---------------------------------------------------------------- Moke 1.4.0
# The opening sentence called the face black-and-white; colour screens now get themes.
MOKE_OPENING = {
    "cs": ("Kontrastní černobílý datový ciferník", "Kontrastní datový ciferník"),
    "da": ("En kontrastrig sort-hvid dataurskive", "En kontrastrig dataurskive"),
    "de": ("Ein kontrastreiches Schwarz-Weiß-Datenzifferblatt", "Ein kontrastreiches Datenzifferblatt"),
    "el": ("Μια ασπρόμαυρη όψη δεδομένων με έντονη αντίθεση", "Μια όψη δεδομένων με έντονη αντίθεση"),
    "en": ("A bold black-and-white data watch face", "A bold, high-contrast data watch face"),
    "es": ("Una esfera de datos en blanco y negro, de alto contraste", "Una esfera de datos de alto contraste"),
    "fi": ("Selkeä mustavalkoinen tietokellotaulu", "Selkeä ja kontrastikas tietokellotaulu"),
    "fr": ("Un cadran de données noir et blanc très contrasté", "Un cadran de données très contrasté"),
    "hr": ("Kontrastni crno-bijeli podatkovni brojčanik", "Kontrastni podatkovni brojčanik"),
    "hu": ("Nagy kontrasztú, fekete-fehér adatkijelzős számlap", "Nagy kontrasztú, adatkijelzős számlap"),
    "in": ("Tampilan jam data hitam-putih berkontras tinggi", "Tampilan jam data berkontras tinggi"),
    "it": ("Un quadrante dati in bianco e nero ad alto contrasto", "Un quadrante dati ad alto contrasto"),
    "iw": ("לוח שעון נתונים בשחור-לבן עם ניגודיות גבוהה", "לוח שעון נתונים עם ניגודיות גבוהה"),
    "ja": ("白黒のはっきりしたデータ文字盤", "コントラストのはっきりしたデータ文字盤"),
    "ko": ("선명한 흑백 데이터 워치페이스", "선명한 고대비 데이터 워치페이스"),
    "ms": ("Muka jam data hitam putih berkontras tinggi", "Muka jam data berkontras tinggi"),
    "nb": ("En kontrastrik svart-hvit dataurskive", "En kontrastrik dataurskive"),
    "nl": ("Een zwart-witte datawijzerplaat met veel contrast", "Een datawijzerplaat met veel contrast"),
    "pl": ("Kontrastowa, czarno-biała tarcza danych", "Kontrastowa tarcza danych"),
    "pt_BR": ("Um mostrador de dados em preto e branco, de alto contraste", "Um mostrador de dados de alto contraste"),
    "pt_PT": ("Um mostrador de dados a preto e branco, de alto contraste", "Um mostrador de dados de alto contraste"),
    "ru": ("Контрастный чёрно-белый циферблат с данными", "Контрастный циферблат с данными"),
    "sk": ("Kontrastný čiernobiely dátový ciferník", "Kontrastný dátový ciferník"),
    "sl": ("Kontrastna črno-bela podatkovna številčnica", "Kontrastna podatkovna številčnica"),
    "sv": ("En kontrastrik svartvit dataurtavla", "En kontrastrik dataurtavla"),
    "th": ("หน้าปัดข้อมูลขาวดำคอนทราสต์สูง", "หน้าปัดข้อมูลคอนทราสต์สูง"),
    "zh_CN": ("黑白分明、一眼看清的数据表盘", "对比鲜明、一眼看清的数据表盘"),
    "zh_TW": ("黑白分明、一眼看清的數據錶盤", "對比鮮明、一眼看清的數據錶盤"),
}

# Appended to the "Dark or light theme, 12/24-hour time..." bullet.
MOKE_COLOUR = {
    "cs": " Barevné displeje MIP, AMOLED a LCD navíc nabízejí šest barevných motivů (výchozí Amber); trvale zapnutý displej AMOLED ukazuje jen malý ztlumený čas a datum.",
    "da": " Farve-MIP-, AMOLED- og LCD-ure får seks farvetemaer (standard Amber); AMOLED altid tændt viser kun et lille, dæmpet klokkeslæt og dato.",
    "de": " Farbige MIP-, AMOLED- und LCD-Uhren erhalten sechs Farbthemen (Standard: Amber); das Always-on-Display auf AMOLED zeigt nur eine kleine, gedimmte Uhrzeit mit Datum.",
    "el": " Οι έγχρωμες οθόνες MIP, AMOLED και LCD αποκτούν έξι χρωματικά θέματα (προεπιλογή Amber)· η μόνιμη προβολή AMOLED δείχνει μόνο μικρή, χαμηλωμένη ώρα και ημερομηνία.",
    "en": " Colour MIP, AMOLED and LCD watches add six colour themes (Amber by default); AMOLED always-on shows only a small, dim time and date.",
    "es": " Las pantallas MIP en color, AMOLED y LCD suman seis temas de color (Amber por defecto); la pantalla siempre activa de AMOLED solo muestra la hora y la fecha, pequeñas y atenuadas.",
    "fi": " Värillisissä MIP-, AMOLED- ja LCD-näytöissä on lisäksi kuusi väriteemaa (oletuksena Amber); AMOLEDin aina päällä -tila näyttää vain pienen, himmeän ajan ja päivämäärän.",
    "fr": " Les écrans MIP couleur, AMOLED et LCD ajoutent six thèmes de couleur (Amber par défaut) ; l’affichage permanent AMOLED ne montre qu’une petite heure atténuée et la date.",
    "hr": " Zasloni MIP u boji, AMOLED i LCD dobivaju šest tema boja (zadano Amber); stalno uključeni AMOLED zaslon prikazuje samo malo, zatamnjeno vrijeme i datum.",
    "hu": " A színes MIP-, AMOLED- és LCD-kijelzőkön hat színtéma is választható (alapértelmezés: Amber); az AMOLED mindig bekapcsolt módja csak kis, halvány időt és dátumot mutat.",
    "in": " Layar MIP berwarna, AMOLED, dan LCD mendapat enam tema warna (bawaan Amber); mode selalu aktif AMOLED hanya menampilkan jam dan tanggal kecil yang redup.",
    "it": " Gli schermi MIP a colori, AMOLED e LCD aggiungono sei temi colore (predefinito Amber); il display sempre attivo AMOLED mostra solo ora e data, piccole e attenuate.",
    "iw": " במסכי MIP צבעוניים, AMOLED ו-LCD נוספות שש ערכות צבע (ברירת המחדל Amber); תצוגה תמידית ב-AMOLED מציגה רק שעה ותאריך קטנים ומעומעמים.",
    "ja": "カラー MIP・AMOLED・LCD 画面では 6 種類のカラーテーマ（初期設定は Amber）も選べます。AMOLED の常時表示は暗めの小さな時刻と日付のみ。",
    "ko": " 컬러 MIP, AMOLED, LCD 화면에는 6가지 컬러 테마(기본 Amber)가 추가되며, AMOLED 상시 표시에는 어둡고 작은 시간과 날짜만 나타납니다.",
    "ms": " Skrin MIP berwarna, AMOLED dan LCD mendapat enam tema warna (lalai Amber); paparan sentiasa hidup AMOLED hanya menunjukkan masa dan tarikh kecil yang malap.",
    "nb": " Farge-MIP-, AMOLED- og LCD-klokker får seks fargetemaer (standard Amber); alltid på-skjermen på AMOLED viser bare et lite, dempet klokkeslett og dato.",
    "nl": " Kleuren-MIP-, AMOLED- en LCD-horloges krijgen zes kleurthema's (standaard Amber); always-on op AMOLED toont alleen een kleine, gedimde tijd en datum.",
    "pl": " Kolorowe ekrany MIP, AMOLED i LCD zyskują sześć motywów kolorystycznych (domyślnie Amber); tryb zawsze włączony na AMOLED pokazuje tylko małą, przyciemnioną godzinę i datę.",
    "pt_BR": " Telas MIP coloridas, AMOLED e LCD ganham seis temas de cor (Amber por padrão); a tela sempre ativa no AMOLED mostra só a hora e a data, pequenas e escurecidas.",
    "pt_PT": " Os ecrãs MIP a cores, AMOLED e LCD ganham seis temas de cor (Amber por predefinição); o ecrã sempre ligado no AMOLED mostra apenas a hora e a data, pequenas e escurecidas.",
    "ru": " На цветных MIP-, AMOLED- и LCD-экранах доступны шесть цветовых тем (по умолчанию Amber); в режиме Always-on на AMOLED видны только небольшие приглушённые время и дата.",
    "sk": " Farebné displeje MIP, AMOLED a LCD navyše ponúkajú šesť farebných motívov (predvolený Amber); trvalo zapnutý displej AMOLED zobrazuje len malý stlmený čas a dátum.",
    "sl": " Barvni zasloni MIP, AMOLED in LCD dobijo šest barvnih tem (privzeto Amber); stalno vklopljen zaslon AMOLED pokaže le majhen, zatemnjen čas in datum.",
    "sv": " Färg-MIP-, AMOLED- och LCD-klockor får sex färgteman (standard Amber); alltid på-läget på AMOLED visar bara en liten, nedtonad tid och datum.",
    "th": " หน้าจอ MIP สี AMOLED และ LCD มีธีมสีเพิ่ม 6 แบบ (ค่าเริ่มต้น Amber) ส่วนโหมดแสดงตลอดเวลาบน AMOLED จะแสดงเพียงเวลาและวันที่ขนาดเล็กแบบหรี่",
    "zh_CN": "彩色 MIP、AMOLED 和 LCD 屏另有 6 套彩色配色（默认琥珀）；AMOLED 常亮只显示暗色小号时间和日期。",
    "zh_TW": "彩色 MIP、AMOLED 和 LCD 螢幕另有 6 套彩色配色（預設琥珀）；AMOLED 常亮只顯示暗色小號時間和日期。",
}

THEMES_EN = "Classic, Amber (default), Glacier, Mint, Night glow, Sakura"
MOKE_NEW = {
    "cs": f"• Šest barevných motivů pro barevné displeje MIP, AMOLED a LCD: {THEMES_EN}. Čas zůstává bílý; ikony, ukazatele, graf a sekundy přebírají barvu motivu. Černobílé hodinky se nemění.\n• Nově na hodinkách AMOLED a LCD, např. epix, Venu, vivoactive a Forerunner 265/965.\n• Trvale zapnutý displej AMOLED ukazuje jen malý ztlumený čas a datum, každou minutu mírně posunuté.\n• Opraveno: některá nastavení změněná v aplikaci v telefonu se nepoužila.",
    "da": f"• Seks farvetemaer til farve-MIP-, AMOLED- og LCD-skærme: {THEMES_EN}. Klokkeslættet forbliver hvidt; ikoner, målere, grafen og sekunder får temafarven. Sort-hvide ure er uændrede.\n• Nu også på AMOLED- og LCD-ure som epix, Venu, vivoactive og Forerunner 265/965.\n• AMOLED altid tændt viser kun et lille, dæmpet klokkeslæt og dato, flyttet en smule hvert minut.\n• Rettet: nogle indstillinger ændret i telefonappen blev ikke anvendt.",
    "de": f"• Sechs Farbthemen für farbige MIP-, AMOLED- und LCD-Displays: {THEMES_EN}. Die Uhrzeit bleibt weiß; Symbole, Anzeigen, die Verlaufskurve und Sekunden übernehmen die Themenfarbe. Schwarz-Weiß-Uhren bleiben unverändert.\n• Jetzt auch für AMOLED- und LCD-Uhren wie epix, Venu, vivoactive und Forerunner 265/965.\n• Always-on auf AMOLED zeigt nur eine kleine, gedimmte Uhrzeit mit Datum, jede Minute leicht verschoben.\n• Behoben: Manche in der Handy-App geänderten Einstellungen wurden nicht übernommen.",
    "el": f"• Έξι χρωματικά θέματα για έγχρωμες οθόνες MIP, AMOLED και LCD: {THEMES_EN}. Η ώρα μένει λευκή· εικονίδια, δείκτες, γράφημα και δευτερόλεπτα παίρνουν το χρώμα του θέματος. Τα ασπρόμαυρα ρολόγια δεν αλλάζουν.\n• Πλέον και σε ρολόγια AMOLED και LCD, όπως epix, Venu, vivoactive και Forerunner 265/965.\n• Η μόνιμη προβολή AMOLED δείχνει μόνο μικρή, χαμηλωμένη ώρα και ημερομηνία, που μετακινούνται λίγο κάθε λεπτό.\n• Διορθώθηκε: ορισμένες ρυθμίσεις που άλλαζαν στην εφαρμογή του τηλεφώνου δεν εφαρμόζονταν.",
    "en": f"• Six colour themes for colour MIP, AMOLED and LCD screens: {THEMES_EN}. The time stays white; icons, gauges, the trend chart and seconds take the theme colour. Black-and-white watches are unchanged.\n• Now available on AMOLED and LCD watches such as epix, Venu, vivoactive and Forerunner 265/965.\n• AMOLED always-on shows only a small, dim time and date, shifted slightly each minute.\n• Fixed some settings changed in the phone app not being applied.",
    "es": f"• Seis temas de color para pantallas MIP en color, AMOLED y LCD: {THEMES_EN}. La hora sigue en blanco; iconos, indicadores, el gráfico y los segundos toman el color del tema. Los relojes en blanco y negro no cambian.\n• Ahora también en relojes AMOLED y LCD como epix, Venu, vivoactive y Forerunner 265/965.\n• La pantalla siempre activa de AMOLED solo muestra la hora y la fecha, pequeñas y atenuadas, con un leve desplazamiento cada minuto.\n• Corregido: algunos ajustes cambiados en la app del teléfono no se aplicaban.",
    "fi": f"• Kuusi väriteemaa värillisille MIP-, AMOLED- ja LCD-näytöille: {THEMES_EN}. Aika pysyy valkoisena; kuvakkeet, mittarit, käyrä ja sekunnit saavat teeman värin. Mustavalkoiset kellot eivät muutu.\n• Nyt myös AMOLED- ja LCD-kelloissa, kuten epix, Venu, vivoactive ja Forerunner 265/965.\n• AMOLEDin aina päällä -tila näyttää vain pienen, himmeän ajan ja päivämäärän, joka siirtyy hieman joka minuutti.\n• Korjattu: osa puhelinsovelluksessa muutetuista asetuksista ei tullut voimaan.",
    "fr": f"• Six thèmes de couleur pour les écrans MIP couleur, AMOLED et LCD : {THEMES_EN}. L’heure reste blanche ; icônes, jauges, courbe et secondes prennent la couleur du thème. Les montres noir et blanc ne changent pas.\n• Désormais disponible sur les montres AMOLED et LCD comme epix, Venu, vivoactive et Forerunner 265/965.\n• L’affichage permanent AMOLED ne montre qu’une petite heure atténuée et la date, légèrement décalées chaque minute.\n• Corrigé : certains réglages modifiés dans l’application du téléphone n’étaient pas appliqués.",
    "hr": f"• Šest tema boja za MIP zaslone u boji, AMOLED i LCD: {THEMES_EN}. Vrijeme ostaje bijelo; ikone, pokazivači, grafikon i sekunde poprimaju boju teme. Crno-bijeli satovi ostaju isti.\n• Sada i na AMOLED i LCD satovima kao što su epix, Venu, vivoactive i Forerunner 265/965.\n• Stalno uključeni AMOLED zaslon prikazuje samo malo, zatamnjeno vrijeme i datum, svake minute malo pomaknute.\n• Ispravljeno: neke postavke promijenjene u aplikaciji na telefonu nisu se primjenjivale.",
    "hu": f"• Hat színtéma színes MIP-, AMOLED- és LCD-kijelzőkhöz: {THEMES_EN}. Az idő fehér marad; az ikonok, mérők, a görbe és a másodpercek a téma színét kapják. A fekete-fehér órák nem változnak.\n• Mostantól AMOLED- és LCD-órákon is, például epix, Venu, vivoactive és Forerunner 265/965.\n• Az AMOLED mindig bekapcsolt módja csak kis, halvány időt és dátumot mutat, percenként kissé eltolva.\n• Javítva: a telefonos alkalmazásban módosított egyes beállítások nem léptek életbe.",
    "in": f"• Enam tema warna untuk layar MIP berwarna, AMOLED, dan LCD: {THEMES_EN}. Jam tetap putih; ikon, indikator, grafik, dan detik mengikuti warna tema. Jam hitam-putih tidak berubah.\n• Kini tersedia di jam AMOLED dan LCD seperti epix, Venu, vivoactive, dan Forerunner 265/965.\n• Mode selalu aktif AMOLED hanya menampilkan jam dan tanggal kecil yang redup, bergeser sedikit setiap menit.\n• Diperbaiki: beberapa pengaturan yang diubah di aplikasi ponsel tidak diterapkan.",
    "it": f"• Sei temi colore per schermi MIP a colori, AMOLED e LCD: {THEMES_EN}. L’ora resta bianca; icone, indicatori, grafico e secondi prendono il colore del tema. Gli orologi in bianco e nero restano invariati.\n• Ora disponibile anche su orologi AMOLED e LCD come epix, Venu, vivoactive e Forerunner 265/965.\n• Il display sempre attivo AMOLED mostra solo ora e data, piccole e attenuate, spostate leggermente ogni minuto.\n• Corretto: alcune impostazioni modificate nell’app del telefono non venivano applicate.",
    "iw": f"• שש ערכות צבע למסכי MIP צבעוניים, AMOLED ו-LCD: {THEMES_EN}. השעה נשארת לבנה; סמלים, מדים, הגרף והשניות מקבלים את צבע הערכה. שעונים בשחור-לבן לא משתנים.\n• זמין עכשיו גם בשעוני AMOLED ו-LCD כמו epix,‏ Venu,‏ vivoactive ו-Forerunner 265/965.\n• תצוגה תמידית ב-AMOLED מציגה רק שעה ותאריך קטנים ומעומעמים, שזזים מעט בכל דקה.\n• תוקן: חלק מההגדרות ששונו באפליקציה בטלפון לא הוחלו.",
    "ja": f"• カラー MIP・AMOLED・LCD 画面向けに 6 種類のカラーテーマ：{THEMES_EN}。時刻は白のまま、アイコン・ゲージ・グラフ・秒がテーマ色になります。白黒画面のウォッチは従来どおり。\n• epix、Venu、vivoactive、Forerunner 265/965 などの AMOLED・LCD ウォッチに対応。\n• AMOLED の常時表示は暗めの小さな時刻と日付のみで、毎分わずかに位置をずらします。\n• スマートフォンのアプリで変更した一部の設定が反映されない問題を修正。",
    "ko": f"• 컬러 MIP, AMOLED, LCD 화면용 컬러 테마 6가지: {THEMES_EN}. 시간은 흰색 그대로이며 아이콘, 게이지, 그래프, 초가 테마 색을 따릅니다. 흑백 시계는 그대로입니다.\n• epix, Venu, vivoactive, Forerunner 265/965 등 AMOLED·LCD 시계 지원.\n• AMOLED 상시 표시에는 어둡고 작은 시간과 날짜만 나타나며 매분 조금씩 위치가 바뀝니다.\n• 휴대폰 앱에서 바꾼 일부 설정이 적용되지 않던 문제 수정.",
    "ms": f"• Enam tema warna untuk skrin MIP berwarna, AMOLED dan LCD: {THEMES_EN}. Masa kekal putih; ikon, penunjuk, graf dan saat mengikut warna tema. Jam hitam putih tidak berubah.\n• Kini tersedia pada jam AMOLED dan LCD seperti epix, Venu, vivoactive dan Forerunner 265/965.\n• Paparan sentiasa hidup AMOLED hanya menunjukkan masa dan tarikh kecil yang malap, beralih sedikit setiap minit.\n• Dibaiki: sesetengah tetapan yang diubah dalam apl telefon tidak digunakan.",
    "nb": f"• Seks fargetemaer for farge-MIP-, AMOLED- og LCD-skjermer: {THEMES_EN}. Klokkeslettet forblir hvitt; ikoner, målere, grafen og sekunder får temafargen. Svart-hvite klokker er uendret.\n• Nå også på AMOLED- og LCD-klokker som epix, Venu, vivoactive og Forerunner 265/965.\n• Alltid på-skjermen på AMOLED viser bare et lite, dempet klokkeslett og dato, flyttet litt hvert minutt.\n• Rettet: noen innstillinger endret i telefonappen ble ikke tatt i bruk.",
    "nl": f"• Zes kleurthema's voor kleuren-MIP-, AMOLED- en LCD-schermen: {THEMES_EN}. De tijd blijft wit; pictogrammen, meters, de grafiek en seconden krijgen de themakleur. Zwart-witte horloges blijven ongewijzigd.\n• Nu ook op AMOLED- en LCD-horloges zoals epix, Venu, vivoactive en Forerunner 265/965.\n• Always-on op AMOLED toont alleen een kleine, gedimde tijd en datum, die elke minuut iets verschuiven.\n• Opgelost: sommige instellingen die in de telefoonapp werden gewijzigd, werden niet toegepast.",
    "pl": f"• Sześć motywów kolorystycznych dla kolorowych ekranów MIP, AMOLED i LCD: {THEMES_EN}. Godzina pozostaje biała; ikony, wskaźniki, wykres i sekundy przyjmują kolor motywu. Zegarki czarno-białe bez zmian.\n• Teraz także na zegarkach AMOLED i LCD, np. epix, Venu, vivoactive i Forerunner 265/965.\n• Tryb zawsze włączony na AMOLED pokazuje tylko małą, przyciemnioną godzinę i datę, co minutę lekko przesuwane.\n• Naprawiono: niektóre ustawienia zmienione w aplikacji na telefonie nie były stosowane.",
    "pt_BR": f"• Seis temas de cor para telas MIP coloridas, AMOLED e LCD: {THEMES_EN}. A hora continua branca; ícones, indicadores, o gráfico e os segundos usam a cor do tema. Relógios em preto e branco não mudam.\n• Agora também em relógios AMOLED e LCD como epix, Venu, vivoactive e Forerunner 265/965.\n• A tela sempre ativa no AMOLED mostra só a hora e a data, pequenas e escurecidas, deslocadas um pouco a cada minuto.\n• Corrigido: algumas configurações alteradas no app do celular não eram aplicadas.",
    "pt_PT": f"• Seis temas de cor para ecrãs MIP a cores, AMOLED e LCD: {THEMES_EN}. A hora mantém-se branca; ícones, indicadores, o gráfico e os segundos usam a cor do tema. Os relógios a preto e branco não mudam.\n• Agora também em relógios AMOLED e LCD como epix, Venu, vivoactive e Forerunner 265/965.\n• O ecrã sempre ligado no AMOLED mostra apenas a hora e a data, pequenas e escurecidas, deslocadas ligeiramente a cada minuto.\n• Corrigido: algumas definições alteradas na app do telemóvel não eram aplicadas.",
    "ru": f"• Шесть цветовых тем для цветных MIP-, AMOLED- и LCD-экранов: {THEMES_EN}. Время остаётся белым; значки, шкалы, график и секунды окрашиваются в цвет темы. На чёрно-белых часах ничего не меняется.\n• Теперь и на часах с AMOLED и LCD: epix, Venu, vivoactive, Forerunner 265/965 и других.\n• В режиме Always-on на AMOLED видны только небольшие приглушённые время и дата, каждую минуту слегка смещаясь.\n• Исправлено: некоторые настройки, изменённые в приложении на телефоне, не применялись.",
    "sk": f"• Šesť farebných motívov pre farebné displeje MIP, AMOLED a LCD: {THEMES_EN}. Čas zostáva biely; ikony, ukazovatele, graf a sekundy preberajú farbu motívu. Čiernobiele hodinky sa nemenia.\n• Teraz aj na hodinkách AMOLED a LCD, napr. epix, Venu, vivoactive a Forerunner 265/965.\n• Trvalo zapnutý displej AMOLED zobrazuje len malý stlmený čas a dátum, každú minútu mierne posunuté.\n• Opravené: niektoré nastavenia zmenené v aplikácii v telefóne sa nepoužili.",
    "sl": f"• Šest barvnih tem za barvne zaslone MIP, AMOLED in LCD: {THEMES_EN}. Čas ostane bel; ikone, merilniki, graf in sekunde prevzamejo barvo teme. Črno-bele ure ostanejo enake.\n• Zdaj tudi na urah AMOLED in LCD, kot so epix, Venu, vivoactive in Forerunner 265/965.\n• Stalno vklopljen zaslon AMOLED pokaže le majhen, zatemnjen čas in datum, ki se vsako minuto rahlo premakneta.\n• Popravljeno: nekatere nastavitve, spremenjene v aplikaciji na telefonu, niso bile uporabljene.",
    "sv": f"• Sex färgteman för färg-MIP-, AMOLED- och LCD-skärmar: {THEMES_EN}. Tiden förblir vit; ikoner, mätare, grafen och sekunder får temats färg. Svartvita klockor är oförändrade.\n• Nu även på AMOLED- och LCD-klockor som epix, Venu, vivoactive och Forerunner 265/965.\n• Alltid på-läget på AMOLED visar bara en liten, nedtonad tid och datum som flyttas lite varje minut.\n• Åtgärdat: vissa inställningar som ändrades i telefonappen tillämpades inte.",
    "th": f"• ธีมสี 6 แบบสำหรับหน้าจอ MIP สี AMOLED และ LCD: {THEMES_EN} เวลายังคงเป็นสีขาว ส่วนไอคอน มาตรวัด กราฟ และวินาทีจะใช้สีของธีม นาฬิกาจอขาวดำไม่เปลี่ยนแปลง\n• รองรับนาฬิกา AMOLED และ LCD เช่น epix, Venu, vivoactive และ Forerunner 265/965\n• โหมดแสดงตลอดเวลาบน AMOLED แสดงเพียงเวลาและวันที่ขนาดเล็กแบบหรี่ และขยับตำแหน่งเล็กน้อยทุกนาที\n• แก้ไขปัญหาการตั้งค่าบางรายการที่เปลี่ยนในแอปบนโทรศัพท์ไม่มีผล",
    "zh_CN": "• 彩色 MIP、AMOLED、LCD 屏新增 6 套配色：经典、琥珀（默认）、冰川、薄荷、夜光、樱花。时间保持白色，图标、进度、趋势线和秒数随配色变化；黑白屏不变。\n• 新增支持 epix、Venu、vivoactive、Forerunner 265/965 等 AMOLED 和 LCD 手表。\n• AMOLED 常亮只显示暗色小号时间和日期，每分钟轻微移位。\n• 修复手机上修改的部分设置没有生效。",
    "zh_TW": "• 彩色 MIP、AMOLED、LCD 螢幕新增 6 套配色：經典、琥珀（預設）、冰川、薄荷、夜光、櫻花。時間維持白色，圖示、進度、趨勢線和秒數隨配色變化；黑白螢幕不變。\n• 新增支援 epix、Venu、vivoactive、Forerunner 265/965 等 AMOLED 和 LCD 手錶。\n• AMOLED 常亮只顯示暗色小號時間和日期，每分鐘輕微移位。\n• 修正手機上修改的部分設定沒有生效。",
}

# ---------------------------------------------------------------- Retro World 2.2.1
RETRO_NEW = {
    "cs": "• Opraveno: na Instinct 2, Instinct 2S a Descent G1 ciferník místo spuštění zobrazil chybu.\n• Opraveno: na Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 a dalších starších hodinkách se nepoužila nastavení změněná v aplikaci v telefonu.",
    "da": "• Rettet: på Instinct 2, Instinct 2S og Descent G1 viste urskiven en fejl i stedet for at starte.\n• Rettet: på Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 og andre ældre ure blev indstillinger ændret i telefonappen ikke anvendt.",
    "de": "• Behoben: Auf Instinct 2, Instinct 2S und Descent G1 zeigte das Zifferblatt einen Fehler, statt zu starten.\n• Behoben: Auf Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 und anderen älteren Uhren wurden in der Handy-App geänderte Einstellungen nicht übernommen.",
    "el": "• Διορθώθηκε: στα Instinct 2, Instinct 2S και Descent G1 η όψη έδειχνε σφάλμα αντί να ξεκινά.\n• Διορθώθηκε: στα Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 και άλλα παλαιότερα ρολόγια δεν εφαρμόζονταν οι ρυθμίσεις που άλλαζαν στην εφαρμογή του τηλεφώνου.",
    "en": "• Fixed the watch face showing an error instead of starting on Instinct 2, Instinct 2S and Descent G1.\n• Fixed settings changed in the phone app not being applied on Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 and other older watches.",
    "es": "• Corregido: en Instinct 2, Instinct 2S y Descent G1 la esfera mostraba un error en lugar de iniciarse.\n• Corregido: en Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 y otros relojes más antiguos no se aplicaban los ajustes cambiados en la app del teléfono.",
    "fi": "• Korjattu: Instinct 2-, Instinct 2S- ja Descent G1 -kelloissa kellotaulu näytti virheen käynnistymisen sijaan.\n• Korjattu: Forerunner 245/745/945-, Venu-, Venu Sq-, vivoactive 4- ja muissa vanhemmissa kelloissa puhelinsovelluksessa muutetut asetukset eivät tulleet voimaan.",
    "fr": "• Corrigé : sur Instinct 2, Instinct 2S et Descent G1, le cadran affichait une erreur au lieu de démarrer.\n• Corrigé : sur Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 et d’autres montres plus anciennes, les réglages modifiés dans l’application du téléphone n’étaient pas appliqués.",
    "hr": "• Ispravljeno: na Instinct 2, Instinct 2S i Descent G1 brojčanik je umjesto pokretanja prikazivao pogrešku.\n• Ispravljeno: na Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 i drugim starijim satovima nisu se primjenjivale postavke promijenjene u aplikaciji na telefonu.",
    "hu": "• Javítva: Instinct 2, Instinct 2S és Descent G1 órákon a számlap indulás helyett hibát mutatott.\n• Javítva: Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 és más régebbi órákon a telefonos alkalmazásban módosított beállítások nem léptek életbe.",
    "in": "• Diperbaiki: di Instinct 2, Instinct 2S, dan Descent G1, tampilan jam menampilkan galat alih-alih berjalan.\n• Diperbaiki: di Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4, dan jam lama lainnya, pengaturan yang diubah di aplikasi ponsel tidak diterapkan.",
    "it": "• Corretto: su Instinct 2, Instinct 2S e Descent G1 il quadrante mostrava un errore invece di avviarsi.\n• Corretto: su Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 e altri orologi meno recenti le impostazioni modificate nell’app del telefono non venivano applicate.",
    "iw": "• תוקן: ב-Instinct 2,‏ Instinct 2S ו-Descent G1 לוח השעון הציג שגיאה במקום לפעול.\n• תוקן: ב-Forerunner 245/745/945,‏ Venu,‏ Venu Sq,‏ vivoactive 4 ובשעונים ישנים נוספים לא הוחלו הגדרות ששונו באפליקציה בטלפון.",
    "ja": "• Instinct 2、Instinct 2S、Descent G1 で文字盤が起動せずエラーを表示する問題を修正。\n• Forerunner 245/745/945、Venu、Venu Sq、vivoactive 4 などの旧機種で、スマートフォンのアプリで変更した設定が反映されない問題を修正。",
    "ko": "• Instinct 2, Instinct 2S, Descent G1에서 워치페이스가 실행되지 않고 오류가 표시되던 문제 수정.\n• Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 등 이전 시계에서 휴대폰 앱에서 바꾼 설정이 적용되지 않던 문제 수정.",
    "ms": "• Dibaiki: pada Instinct 2, Instinct 2S dan Descent G1, muka jam menunjukkan ralat dan tidak bermula.\n• Dibaiki: pada Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 dan jam lama lain, tetapan yang diubah dalam apl telefon tidak digunakan.",
    "nb": "• Rettet: på Instinct 2, Instinct 2S og Descent G1 viste urskiven en feil i stedet for å starte.\n• Rettet: på Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 og andre eldre klokker ble innstillinger endret i telefonappen ikke tatt i bruk.",
    "nl": "• Opgelost: op Instinct 2, Instinct 2S en Descent G1 toonde de wijzerplaat een foutmelding in plaats van te starten.\n• Opgelost: op Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 en andere oudere horloges werden instellingen uit de telefoonapp niet toegepast.",
    "pl": "• Naprawiono: na Instinct 2, Instinct 2S i Descent G1 tarcza zamiast się uruchomić pokazywała błąd.\n• Naprawiono: na Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 i innych starszych zegarkach nie były stosowane ustawienia zmienione w aplikacji na telefonie.",
    "pt_BR": "• Corrigido: no Instinct 2, Instinct 2S e Descent G1 o mostrador exibia um erro em vez de iniciar.\n• Corrigido: no Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 e outros relógios mais antigos, as configurações alteradas no app do celular não eram aplicadas.",
    "pt_PT": "• Corrigido: no Instinct 2, Instinct 2S e Descent G1 o mostrador apresentava um erro em vez de iniciar.\n• Corrigido: no Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 e outros relógios mais antigos, as definições alteradas na app do telemóvel não eram aplicadas.",
    "ru": "• Исправлено: на Instinct 2, Instinct 2S и Descent G1 циферблат показывал ошибку вместо запуска.\n• Исправлено: на Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 и других старых часах не применялись настройки, изменённые в приложении на телефоне.",
    "sk": "• Opravené: na Instinct 2, Instinct 2S a Descent G1 ciferník namiesto spustenia zobrazil chybu.\n• Opravené: na Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 a ďalších starších hodinkách sa nepoužili nastavenia zmenené v aplikácii v telefóne.",
    "sl": "• Popravljeno: na Instinct 2, Instinct 2S in Descent G1 je številčnica namesto zagona prikazala napako.\n• Popravljeno: na Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 in drugih starejših urah niso bile uporabljene nastavitve, spremenjene v aplikaciji na telefonu.",
    "sv": "• Åtgärdat: på Instinct 2, Instinct 2S och Descent G1 visade urtavlan ett fel i stället för att starta.\n• Åtgärdat: på Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 och andra äldre klockor tillämpades inte inställningar som ändrats i telefonappen.",
    "th": "• แก้ไขปัญหาหน้าปัดแสดงข้อผิดพลาดแทนที่จะทำงานบน Instinct 2, Instinct 2S และ Descent G1\n• แก้ไขปัญหาการตั้งค่าที่เปลี่ยนในแอปบนโทรศัพท์ไม่มีผลบน Forerunner 245/745/945, Venu, Venu Sq, vivoactive 4 และนาฬิการุ่นเก่าอื่น ๆ",
    "zh_CN": "• 修复本能 2、本能 2S 和 Descent G1 上表盘无法启动、显示错误。\n• 修复 Forerunner 245/745/945、Venu、Venu Sq、vivoactive 4 等较早机型上，手机里修改的设置不生效。",
    "zh_TW": "• 修正 Instinct 2、Instinct 2S 和 Descent G1 上錶面無法啟動、顯示錯誤。\n• 修正 Forerunner 245/745/945、Venu、Venu Sq、vivoactive 4 等較早機型上，手機中修改的設定不生效。",
}

# ---------------------------------------------------------------- Alpine 1.3.0
# Appended to the first bullet (the four mountain backgrounds).
ALPINE_SKY = {
    "cs": " Obloha se řídí skutečným časem a počasím: přes den Slunce, v noci Měsíc ve skutečné fázi a hvězdy.",
    "da": " Himlen følger det faktiske tidspunkt og vejret: Solen om dagen, Månen i sin rigtige fase og stjerner om natten.",
    "de": " Der Himmel folgt der echten Tageszeit und dem Wetter: tagsüber die Sonne, nachts der Mond in seiner echten Phase und Sterne.",
    "el": " Ο ουρανός ακολουθεί την πραγματική ώρα και τον καιρό: ο Ήλιος τη μέρα, η Σελήνη στην πραγματική της φάση και αστέρια τη νύχτα.",
    "en": " The sky follows the real time and weather: the Sun by day, the Moon in its real phase and stars at night.",
    "es": " El cielo sigue la hora real y el tiempo: el Sol de día y, de noche, la Luna en su fase real y las estrellas.",
    "fi": " Taivas seuraa todellista aikaa ja säätä: päivällä aurinko, yöllä kuu oikeassa vaiheessaan ja tähdet.",
    "fr": " Le ciel suit l’heure réelle et la météo : le Soleil le jour, la Lune dans sa phase réelle et les étoiles la nuit.",
    "hr": " Nebo prati stvarno doba dana i vrijeme: danju Sunce, noću Mjesec u stvarnoj mijeni i zvijezde.",
    "hu": " Az égbolt a valós időt és az időjárást követi: nappal a Nap, éjjel a Hold valódi fázisában és csillagok.",
    "in": " Langit mengikuti waktu dan cuaca sebenarnya: Matahari di siang hari, Bulan sesuai fasenya dan bintang di malam hari.",
    "it": " Il cielo segue l’ora reale e il meteo: il Sole di giorno, di notte la Luna nella sua fase reale e le stelle.",
    "iw": " השמיים עוקבים אחרי השעה ומזג האוויר בפועל: השמש ביום, והירח במופע האמיתי שלו וכוכבים בלילה.",
    "ja": "空は実際の時刻と天気に合わせて変わり、昼は太陽、夜は実際の月齢の月と星が出ます。",
    "ko": " 하늘은 실제 시간과 날씨를 따라 낮에는 해, 밤에는 실제 위상의 달과 별이 뜹니다.",
    "ms": " Langit mengikut masa dan cuaca sebenar: Matahari pada waktu siang, Bulan mengikut fasa sebenar dan bintang pada waktu malam.",
    "nb": " Himmelen følger det faktiske klokkeslettet og været: solen om dagen, månen i sin virkelige fase og stjerner om natten.",
    "nl": " De lucht volgt de echte tijd en het weer: overdag de zon, 's nachts de maan in haar echte fase en sterren.",
    "pl": " Niebo podąża za rzeczywistą porą dnia i pogodą: w dzień Słońce, w nocy Księżyc w prawdziwej fazie i gwiazdy.",
    "pt_BR": " O céu acompanha a hora real e o clima: o Sol de dia e, à noite, a Lua na fase real e as estrelas.",
    "pt_PT": " O céu acompanha a hora real e o tempo: o Sol de dia e, à noite, a Lua na fase real e as estrelas.",
    "ru": " Небо следует за реальным временем и погодой: днём Солнце, ночью Луна в настоящей фазе и звёзды.",
    "sk": " Obloha sa riadi skutočným časom a počasím: cez deň Slnko, v noci Mesiac v skutočnej fáze a hviezdy.",
    "sl": " Nebo sledi dejanskemu času in vremenu: podnevi Sonce, ponoči Luna v resnični meni in zvezde.",
    "sv": " Himlen följer verklig tid och väder: solen på dagen, månen i sin verkliga fas och stjärnor på natten.",
    "th": " ท้องฟ้าเปลี่ยนตามเวลาและสภาพอากาศจริง กลางวันมีดวงอาทิตย์ กลางคืนมีดวงจันทร์ตามข้างขึ้นข้างแรมจริงและดวงดาว",
    "zh_CN": "天空跟随真实时间和天气：白天有太阳，夜里有按真实月相显示的月亮和星星。",
    "zh_TW": "天空跟隨真實時間和天氣：白天有太陽，夜裡有依真實月相顯示的月亮和星星。",
}

ALPINE_NEW = {
    "cs": "• Obloha se nově řídí skutečným časem a počasím: barvy svítání, dne, soumraku a noci, přes den Slunce, v noci Měsíc ve skutečné fázi a hvězdy. Při oblačnu, dešti, sněžení a mlze je obloha šedá.\n• Slunce, Měsíc a hvězdy se černobíle zobrazují i na hodinkách Instinct.\n• Opraveno: některá nastavení změněná v aplikaci v telefonu se nepoužila.",
    "da": "• Himlen følger nu det faktiske tidspunkt og vejret: farver for daggry, dag, skumring og nat, Solen om dagen og Månen i sin rigtige fase med stjerner om natten. Ved skyer, regn, sne og tåge bliver himlen grå.\n• Instinct-ure viser også Sol, Måne og stjerner i sort-hvid.\n• Rettet: nogle indstillinger ændret i telefonappen blev ikke anvendt.",
    "de": "• Der Himmel folgt jetzt der echten Tageszeit und dem Wetter: Farben für Morgendämmerung, Tag, Abenddämmerung und Nacht, tagsüber die Sonne, nachts der Mond in seiner echten Phase mit Sternen. Bei Wolken, Regen, Schnee und Nebel wird der Himmel grau.\n• Auch Instinct-Uhren zeigen Sonne, Mond und Sterne – in Schwarz-Weiß.\n• Behoben: Manche in der Handy-App geänderten Einstellungen wurden nicht übernommen.",
    "el": "• Ο ουρανός ακολουθεί πλέον την πραγματική ώρα και τον καιρό: χρώματα αυγής, μέρας, σούρουπου και νύχτας, ο Ήλιος τη μέρα και η Σελήνη στην πραγματική της φάση με αστέρια τη νύχτα. Με συννεφιά, βροχή, χιόνι και ομίχλη ο ουρανός γίνεται γκρίζος.\n• Και τα ρολόγια Instinct δείχνουν Ήλιο, Σελήνη και αστέρια, σε ασπρόμαυρο.\n• Διορθώθηκε: ορισμένες ρυθμίσεις που άλλαζαν στην εφαρμογή του τηλεφώνου δεν εφαρμόζονταν.",
    "en": "• The sky now follows the real time and weather: dawn, day, dusk and night colours, the Sun by day and the Moon in its real phase with stars at night. Cloud, rain, snow and fog turn the sky grey.\n• Instinct watches show the Sun, Moon and stars too, in black and white.\n• Fixed some settings changed in the phone app not being applied.",
    "es": "• El cielo ahora sigue la hora real y el tiempo: colores de amanecer, día, atardecer y noche, el Sol de día y, de noche, la Luna en su fase real con estrellas. Con nubes, lluvia, nieve o niebla el cielo se vuelve gris.\n• Los relojes Instinct también muestran el Sol, la Luna y las estrellas, en blanco y negro.\n• Corregido: algunos ajustes cambiados en la app del teléfono no se aplicaban.",
    "fi": "• Taivas seuraa nyt todellista aikaa ja säätä: aamunkoiton, päivän, iltahämärän ja yön värit, päivällä aurinko ja yöllä kuu oikeassa vaiheessaan tähtien kera. Pilvisellä, sateella, lumisateella ja sumussa taivas muuttuu harmaaksi.\n• Myös Instinct-kellot näyttävät auringon, kuun ja tähdet mustavalkoisina.\n• Korjattu: osa puhelinsovelluksessa muutetuista asetuksista ei tullut voimaan.",
    "fr": "• Le ciel suit désormais l’heure réelle et la météo : couleurs de l’aube, du jour, du crépuscule et de la nuit, le Soleil le jour et la Lune dans sa phase réelle avec des étoiles la nuit. Nuages, pluie, neige et brouillard rendent le ciel gris.\n• Les montres Instinct affichent aussi le Soleil, la Lune et les étoiles, en noir et blanc.\n• Corrigé : certains réglages modifiés dans l’application du téléphone n’étaient pas appliqués.",
    "hr": "• Nebo sada prati stvarno doba dana i vrijeme: boje zore, dana, sumraka i noći, danju Sunce, a noću Mjesec u stvarnoj mijeni i zvijezde. Pri oblacima, kiši, snijegu i magli nebo postaje sivo.\n• I satovi Instinct prikazuju Sunce, Mjesec i zvijezde, crno-bijelo.\n• Ispravljeno: neke postavke promijenjene u aplikaciji na telefonu nisu se primjenjivale.",
    "hu": "• Az égbolt mostantól a valós időt és az időjárást követi: hajnali, nappali, alkonyati és éjszakai színek, nappal a Nap, éjjel a Hold valódi fázisában, csillagokkal. Felhős, esős, havas és ködös időben az ég szürke.\n• Az Instinct órák is mutatják a Napot, a Holdat és a csillagokat, fekete-fehérben.\n• Javítva: a telefonos alkalmazásban módosított egyes beállítások nem léptek életbe.",
    "in": "• Langit kini mengikuti waktu dan cuaca sebenarnya: warna fajar, siang, senja, dan malam, Matahari di siang hari, serta Bulan sesuai fasenya dan bintang di malam hari. Saat berawan, hujan, salju, atau berkabut, langit menjadi abu-abu.\n• Jam Instinct juga menampilkan Matahari, Bulan, dan bintang dalam hitam-putih.\n• Diperbaiki: beberapa pengaturan yang diubah di aplikasi ponsel tidak diterapkan.",
    "it": "• Il cielo ora segue l’ora reale e il meteo: colori di alba, giorno, tramonto e notte, il Sole di giorno e, di notte, la Luna nella sua fase reale con le stelle. Con nuvole, pioggia, neve e nebbia il cielo diventa grigio.\n• Anche gli orologi Instinct mostrano Sole, Luna e stelle, in bianco e nero.\n• Corretto: alcune impostazioni modificate nell’app del telefono non venivano applicate.",
    "iw": "• השמיים עוקבים עכשיו אחרי השעה ומזג האוויר בפועל: צבעי שחר, יום, דמדומים ולילה, השמש ביום, והירח במופע האמיתי שלו עם כוכבים בלילה. בעננים, גשם, שלג וערפל השמיים נעשים אפורים.\n• גם שעוני Instinct מציגים שמש, ירח וכוכבים, בשחור-לבן.\n• תוקן: חלק מההגדרות ששונו באפליקציה בטלפון לא הוחלו.",
    "ja": "• 空が実際の時刻と天気に合わせて変わるように：夜明け・昼・夕暮れ・夜の色、昼は太陽、夜は実際の月齢の月と星。曇り・雨・雪・霧の日は灰色の空になります。\n• Instinct シリーズでも太陽・月・星を白黒で表示。\n• スマートフォンのアプリで変更した一部の設定が反映されない問題を修正。",
    "ko": "• 하늘이 실제 시간과 날씨를 따릅니다: 새벽, 낮, 해 질 녘, 밤의 색, 낮에는 해, 밤에는 실제 위상의 달과 별. 흐림, 비, 눈, 안개일 때는 회색 하늘이 됩니다.\n• Instinct 시계에서도 해, 달, 별을 흑백으로 표시.\n• 휴대폰 앱에서 바꾼 일부 설정이 적용되지 않던 문제 수정.",
    "ms": "• Langit kini mengikut masa dan cuaca sebenar: warna subuh, siang, senja dan malam, Matahari pada waktu siang, serta Bulan mengikut fasa sebenar dengan bintang pada waktu malam. Semasa mendung, hujan, salji dan kabus, langit menjadi kelabu.\n• Jam Instinct juga menunjukkan Matahari, Bulan dan bintang dalam hitam putih.\n• Dibaiki: sesetengah tetapan yang diubah dalam apl telefon tidak digunakan.",
    "nb": "• Himmelen følger nå det faktiske klokkeslettet og været: farger for daggry, dag, skumring og natt, solen om dagen og månen i sin virkelige fase med stjerner om natten. Ved skyer, regn, snø og tåke blir himmelen grå.\n• Instinct-klokker viser også sol, måne og stjerner i svart-hvitt.\n• Rettet: noen innstillinger endret i telefonappen ble ikke tatt i bruk.",
    "nl": "• De lucht volgt nu de echte tijd en het weer: kleuren voor dageraad, dag, schemering en nacht, overdag de zon en 's nachts de maan in haar echte fase met sterren. Bij bewolking, regen, sneeuw en mist wordt de lucht grijs.\n• Ook Instinct-horloges tonen zon, maan en sterren, in zwart-wit.\n• Opgelost: sommige instellingen die in de telefoonapp werden gewijzigd, werden niet toegepast.",
    "pl": "• Niebo podąża teraz za rzeczywistą porą dnia i pogodą: barwy świtu, dnia, zmierzchu i nocy, w dzień Słońce, a w nocy Księżyc w prawdziwej fazie i gwiazdy. Przy zachmurzeniu, deszczu, śniegu i mgle niebo robi się szare.\n• Zegarki Instinct też pokazują Słońce, Księżyc i gwiazdy, w czerni i bieli.\n• Naprawiono: niektóre ustawienia zmienione w aplikacji na telefonie nie były stosowane.",
    "pt_BR": "• O céu agora acompanha a hora real e o clima: cores de amanhecer, dia, entardecer e noite, o Sol de dia e, à noite, a Lua na fase real com estrelas. Com nuvens, chuva, neve ou neblina o céu fica cinza.\n• Os relógios Instinct também mostram Sol, Lua e estrelas, em preto e branco.\n• Corrigido: algumas configurações alteradas no app do celular não eram aplicadas.",
    "pt_PT": "• O céu acompanha agora a hora real e o tempo: cores de madrugada, dia, entardecer e noite, o Sol de dia e, à noite, a Lua na fase real com estrelas. Com nuvens, chuva, neve ou nevoeiro o céu fica cinzento.\n• Os relógios Instinct também mostram o Sol, a Lua e as estrelas, a preto e branco.\n• Corrigido: algumas definições alteradas na app do telemóvel não eram aplicadas.",
    "ru": "• Небо теперь следует за реальным временем и погодой: цвета рассвета, дня, сумерек и ночи, днём Солнце, ночью Луна в настоящей фазе и звёзды. В облачность, дождь, снег и туман небо становится серым.\n• На часах Instinct тоже видны Солнце, Луна и звёзды — в чёрно-белом виде.\n• Исправлено: некоторые настройки, изменённые в приложении на телефоне, не применялись.",
    "sk": "• Obloha sa teraz riadi skutočným časom a počasím: farby úsvitu, dňa, súmraku a noci, cez deň Slnko, v noci Mesiac v skutočnej fáze a hviezdy. Pri oblačnosti, daždi, snežení a hmle je obloha sivá.\n• Slnko, Mesiac a hviezdy sa čiernobielo zobrazujú aj na hodinkách Instinct.\n• Opravené: niektoré nastavenia zmenené v aplikácii v telefóne sa nepoužili.",
    "sl": "• Nebo zdaj sledi dejanskemu času in vremenu: barve zore, dneva, mraka in noči, podnevi Sonce, ponoči pa Luna v resnični meni in zvezde. Ob oblačnosti, dežju, snegu in megli postane nebo sivo.\n• Tudi ure Instinct prikažejo Sonce, Luno in zvezde, črno-belo.\n• Popravljeno: nekatere nastavitve, spremenjene v aplikaciji na telefonu, niso bile uporabljene.",
    "sv": "• Himlen följer nu verklig tid och väder: färger för gryning, dag, skymning och natt, solen på dagen och månen i sin verkliga fas med stjärnor på natten. Vid moln, regn, snö och dimma blir himlen grå.\n• Även Instinct-klockor visar sol, måne och stjärnor, i svartvitt.\n• Åtgärdat: vissa inställningar som ändrades i telefonappen tillämpades inte.",
    "th": "• ท้องฟ้าเปลี่ยนตามเวลาและสภาพอากาศจริง: สีรุ่งอรุณ กลางวัน พลบค่ำ และกลางคืน กลางวันมีดวงอาทิตย์ กลางคืนมีดวงจันทร์ตามข้างขึ้นข้างแรมจริงและดวงดาว เมื่อมีเมฆ ฝน หิมะ หรือหมอก ท้องฟ้าจะเป็นสีเทา\n• นาฬิกา Instinct ก็แสดงดวงอาทิตย์ ดวงจันทร์ และดวงดาวแบบขาวดำ\n• แก้ไขปัญหาการตั้งค่าบางรายการที่เปลี่ยนในแอปบนโทรศัพท์ไม่มีผล",
    "zh_CN": "• 天空跟随真实时间和天气变化：黎明、白天、黄昏、夜晚各有配色，白天有太阳，夜里有按真实月相显示的月亮和星星；多云、雨、雪、雾时天空转灰。\n• 本能系列也会以黑白方式显示太阳、月亮和星星。\n• 修复手机上修改的部分设置没有生效。",
    "zh_TW": "• 天空跟隨真實時間和天氣變化：黎明、白天、黃昏、夜晚各有配色，白天有太陽，夜裡有依真實月相顯示的月亮和星星；多雲、雨、雪、霧時天空轉灰。\n• Instinct 系列也會以黑白方式顯示太陽、月亮和星星。\n• 修正手機上修改的部分設定沒有生效。",
}


def bullets(text):
    return [i for i, line in enumerate(text.split("\n")) if line.startswith("•")]


def patched(text, edits):
    for old, new in edits:
        assert text.count(old) == 1, (old, text.count(old))
        text = text.replace(old, new)
    return text


def main():
    copies = json.loads((REPO / "store-listings/copies.json").read_text())
    alpine = json.loads((REPO / "alpine/store/localizations.json").read_text())
    out = {"moke": {}, "retro-world": {}, "alpine": {}}
    for lang in LANGS:
        for table in (MOKE_OPENING, MOKE_COLOUR, MOKE_NEW, RETRO_NEW, ALPINE_SKY, ALPINE_NEW):
            assert lang in table, lang
        m = copies["moke"][lang]
        lines = patched(m["description"], [MOKE_OPENING[lang], ("94", "95")]).split("\n")
        i = bullets("\n".join(lines))[5]
        lines[i] += MOKE_COLOUR[lang]
        out["moke"][lang] = {"title": m["title"], "description": "\n".join(lines),
                             "whatsNew": "1.4.0\n" + MOKE_NEW[lang]}
        r = copies["retro-world"][lang]
        out["retro-world"][lang] = {"title": r["title"], "description": r["description"],
                                    "whatsNew": "2.2.1\n" + RETRO_NEW[lang]}
        a = alpine[lang]
        lines = a["description"].split("\n")
        lines[bullets(a["description"])[0]] += ALPINE_SKY[lang]
        out["alpine"][lang] = {"title": a["title"], "description": "\n".join(lines),
                               "whatsNew": "1.3.0\n" + ALPINE_NEW[lang]}
    for app, rows in out.items():
        for lang, row in rows.items():
            assert len(row["title"]) <= 50 and len(row["description"]) <= 4000 and len(row["whatsNew"]) <= 4000, (app, lang)
        (HERE / f"{app}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
        print(app, len(rows), "languages; longest description",
              max(len(r["description"]) for r in rows.values()), "whatsNew", max(len(r["whatsNew"]) for r in rows.values()))


if __name__ == "__main__":
    main()
