# 两款表盘经验索引

项目：WristInk，GitHub `https://github.com/jiayibyte/wristink`。以下路径相对仓库根目录；技能离开此仓库仍可使用通用流程，不应在用户未请求时下载整个仓库。

| 需求 | Moke 墨刻 | Retro World 寰游时刻 |
| --- | --- | --- |
| 布局/字体 | `source/FaceLayout.mc`、`scripts/font_rasterizer.py`、`assets/fonts/layout-metrics.json` | `tools/retro_style.py`、`tools/assets.py`、`tools/device_profiles.py` |
| 屏幕适配 | `scripts/generate-mip-targets.py`、`source/DeviceDrawing.mc` | `tools/device_profiles.py`、`source/DeviceDrawing.mc` |
| 数据刷新 | `source/PowerPolicy.mc`、`source/LiveHeart.mc`、`source/InstinctFaceView.mc` | `source/LiveData.mc`、`source/Environment.mc`、`source/RetroWorld.mc` |
| 图标 | `assets/icons/SOURCE.txt`、`scripts/make-garmin-icons.py` | `assets/garmin-weather/`、`assets/garmin-sun/`、`source/WeatherIcons.mc` |
| 内存/省电 | `tests/power/`、`scripts/check-power.py`、字体缓存 | `source/AlwaysOn.mc`、`source/SolarMap.mc`、`source/Benchmark.mc` |
| 原生回归 | `scripts/probe-mip-runtime.py` | `tools/run_probes.py`、`tests/NativeAtlasTests.mc` |

表内路径分别位于 `moke/` 与 `retro-world/` 内。复用前核对当前代码和设备能力，不整体复制所有用户设置、图形元素或旧适配常量。

## 可借鉴，但不是视觉标准答案

Moke用母版轮廓原生光栅化、固定布局metrics、按可见数据需求读取，是可复用方向；字体族/多个字号和图标混用会让视觉重量不统一。缓存仅保留极少字体可省RAM，但多区域多字体同帧切换时可能反复加载，需测量。

Retro World原生配置、图形API兼容、实际atlas stride、地图缓存和数据缺失行为可借鉴。其彩屏仍大量沿用低分辨率二值资源，最近邻放大保留了像素块；粗主时间、细标签、密边框/刻度存在比例不协调。适配成功不等于用户喜欢，不应把当前渲染称为高保真终版。

## 已验证修复（2026-10-28）

- Venu Sq2半像素取整导致数字串格：实际atlas尺寸取stride。
- 旧BufferedBitmap无getWidth：用getDc尺寸回退。
- 旧Venu/MIP自定义palette兼容失败：现代分支有界palette、旧分支原生默认。
- AOD继承粗笔画破坏轮廓：每阶段显式恢复penWidth。
- Instinct3圆窗需按具体SDK开孔光学校正；不可全型号套偏移。
- 极小字号0/8混同：从3×5母版重新适配，保留关键中横。

Retro World 2.0.0记录过112 SDK目标/183变体编译、17代表设备8帧原生诊断、4目标各19测试；这些是当次技术证据，**不是长期实表耗电、全机型视觉接受或当前源码永远通过的保证**。Moke的本次审阅以源码和已有设计预览为主，不冒称重新完成实表回归。
