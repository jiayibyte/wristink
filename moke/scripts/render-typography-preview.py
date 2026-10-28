"""Compare the same layout/data using the original and revised font atlases.

An offline pixel preview, explicitly not a simulator or physical-device capture.
"""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preview', ROOT/'scripts/render-design-preview.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
BACKUP = ROOT/'releases/pre-typography-2026-10-27/resources/fonts'
# Match the modern renderer's default family and selected resource sizes.
NAMES = {'data':'dataf0s14', 'compact-small':'dataf0s12',
         'time':'timef0s64', 'circle-value':'liveheartf0s22',
         'seconds':'secondf0s26'}


def render(root, dark, seconds=False):
    for key in preview.FONTS:
        preview.FONTS[key] = preview.Font(NAMES.get(key, key), root)
    return preview.render(dark, seconds)


if __name__ == '__main__':
    out = ROOT/'bin/typography'
    out.mkdir(exist_ok=True)
    face = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', 24, index=1)
    body = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc', 17, index=1)
    board = Image.new('RGB', (1200, 680), '#eceeea')
    d = ImageDraw.Draw(board)
    d.text((40, 25), '墨刻 · 圆角数字与原生像素优化', font=face, fill='#202720')
    items = [(BACKUP, True, '优化前', 'before-dark'),
             (ROOT/'resources/fonts', True, '优化后 · 黑底', 'after-dark'),
             (ROOT/'resources/fonts', False, '优化后 · 白底', 'after-light')]
    for i, (root, dark, label, name) in enumerate(items):
        x = 40+i*392
        d.text((x, 84), label, font=body, fill='#485248')
        image = render(root, dark)
        image.save(out/(name+'.png'))
        # Nearest display enlargement exposes the exact on/off pixels honestly.
        board.paste(image.resize((352,352),Image.Resampling.NEAREST), (x, 125))
    d.text((40, 525), '统一笔画 · 连续圆角 · 等宽数字 · 更均衡的冒号与小数据', font=body, fill='#384638')
    d.text((40, 565), '使用实际字体资源；相同布局和演示数据。原生 176 × 176，放大 2 倍展示。', font=body, fill='#596359')
    d.text((40, 600), '离线字形预览，非模拟器截图或实表照片；单色屏仍有像素边缘。', font=body, fill='#596359')
    board.save(out/'comparison.png')
    render(ROOT/'resources/fonts', True, True).save(out/'after-seconds.png')
    print(out/'comparison.png')
