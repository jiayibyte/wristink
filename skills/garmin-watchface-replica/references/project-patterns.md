# 两款表盘经验索引

项目：WristInk，GitHub `https://github.com/jiayibyte/wristink`。以下路径相对仓库根目录；技能离开此仓库仍可使用通用流程，不应在用户未请求时下载整个仓库。

| 需求 | Moke 墨刻 | Retro World 寰游时刻 |
| --- | --- | --- |
| 布局/字体 | `source/FaceLayout.mc`、`scripts/font_rasterizer.py`、`assets/fonts/layout-metrics.json` | `tools/retro_style.py`、`tools/assets.py`、`tools/device_profiles.py` |
| 屏幕适配 | `scripts/generate-mip-targets.py`、`source/DeviceDrawing.mc` | `tools/device_profiles.py`、`source/DeviceDrawing.mc` |
| 数据刷新 | `source/PowerPolicy.mc`、`source/LiveHeart.mc`、`source/InstinctFaceView.mc` | `source/LiveData.mc`、`source/Environment.mc`、`source/RetroWorld.mc` |
| 配置/语言 | `scripts/generate-mip-targets.py`、`resources-eng/`、`scripts/check-iq-package.py` | `source/FaceSettings.mc`、`source/DataFields.mc`、`tools/settings.py`、`tools/check_settings_package.py` |
| 区域太阳接口 | `scripts/generate-mip-targets.py` 及运行时 `has` 检查 | `source/SolarTimes.mc`、`source/Environment.mc`，官方优先/旧接口近似回退 |
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

Retro World 2.0.0记录过112 SDK目标/183变体编译、17代表设备8帧原生诊断、4目标各19测试；这些是当次技术证据，**不是长期实表耗电、全机型视觉接受或当前源码永远通过的保证**。当时Moke的审阅以源码和已有设计预览为主，不代表重新完成实表回归。

## 2026-11 配置与维护案例

Retro World 2.1.0 使用21项中英文设置、9个可选数据槽、MIP局部秒刷新和独立12/24小时制；`tests/SecondsTests.mc` 检查生命周期/设置/降级，`tools/build_scenario.py` 使用独立ID验证设置画面。圆窗新结论见 [设备适配](devices.md)，不要继续套用2.0的装饰圈偏移。

Moke 1.1.1 按最低地区API生成，默认英文并用简体中文覆盖；`scripts/probe-mip-runtime.py --live --locale eng|zhs` 区分正式/演示测试状态。实际源代码及当前目标包仍需现场核对。

已知商店ID仅用于定位，使用时核对当前作者/标题/版本：
- Retro World：`76e1c5f4-abe8-49ab-bcc0-44c2b1c1a267`。
- Moke：`08e3601d-b0b1-451a-a390-67543e39ae02`。

分别在 `https://apps.garmin.com/apps/<store-id>` 和 `https://apps.garmin.cn/apps/<store-id>` 查看。账号、下载量、评论数、审核及公开状态不固化在技能里；也不保存凭据或把过去批准当成新的授权。
