# 商店图与文案（墨刻 1.3.0 · 寰游时刻 2.2.0 · 山境 1.2.0 · Tide Grid · Signal LCD）

- `captures/`：模拟器预览包截图（演示数据），每张是 1:1 的屏幕像素，不经重绘。
- `text.json`：图上的中英文标题、说明和标签。
- `copy-zh-en.json`：商店标题、简介、更新说明的中英文定稿；其余 26 种语言在定稿后据此翻译。
- `build_media.py`：用 HTML 排版、无头 Chrome 渲染，输出到 `out/<应用>/`：
  - `cover-500.png` 封面 500×500；
  - `hero-<语言>-1440x720.jpg` 横幅；
  - `0N-*-<语言>.jpg` 截图 1440×1280，每张小于 150 KB（Garmin 上限）。
- `contact_sheet.py`：每款每种语言一张总览图，方便审阅。

规则：
- 低分辨率 MIP 截图只按整数倍做最近邻放大，非整数倍用平滑缩放。
- 黑白本能屏截图按真机二值化。
- 表壳为中性造型，不使用 Garmin 机身图片或标志。

```bash
python build_media.py moke retro alpine tide signal
python contact_sheet.py
```

Tide Grid 与 Signal LCD（首发）：横幅文案和两张组合页的标题放在 `i18n/tide.json`、`i18n/signal.json`（`heroes` 为 26 种语言，`combo` 为中英），图内中英文与数据卡片在 `text.json`。截图来自各自的演示包（Tide Grid `tools/build.py --preview`，Signal LCD `tools/build.py --demo`），从模拟器窗口按 1:1 屏幕像素裁出。脚本在 Windows、macOS 和 Linux（`google-chrome`）上都能运行。
