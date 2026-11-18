"""One overview image per app and language: cover, hero and screenshots, scaled down for review."""
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent / 'out'
for app in ('moke', 'retro-world', 'alpine'):
    for lang in ('zh', 'en'):
        folder = OUT / app
        hero = folder / f'hero-{"zh_CN" if (app == "alpine" and lang == "zh") else lang}-1440x720.jpg'
        shots = sorted(folder.glob(f'0*-{lang}.jpg'))
        if not hero.exists() or not shots:
            continue
        cover = Image.open(folder / 'cover-500.png').convert('RGB').resize((360, 360))
        top = Image.open(hero).convert('RGB').resize((720, 360))
        thumbs = [Image.open(s).convert('RGB').resize((540, 480)) for s in shots]
        width = max(360 + 20 + 720, len(thumbs) * 560 - 20)
        sheet = Image.new('RGB', (width + 40, 360 + 20 + 480 + 40), '#2a2b2e')
        sheet.paste(cover, (20, 20)); sheet.paste(top, (400, 20))
        for i, t in enumerate(thumbs):
            sheet.paste(t, (20 + i * 560, 400))
        dest = OUT / f'overview-{app}-{lang}.jpg'
        sheet.save(dest, quality=88)
        print(dest.name, sheet.size)
