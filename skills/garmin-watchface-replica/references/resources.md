# 图标、字体与来源

## 来源优先级与边界

1. 当前官方 Connect IQ 文档公开的资源/API（若目标设备支持）。
2. Garmin 官方支持页的公开符号和设备参考图：适配的是公开图形，不等于导出了该型号固件私有字库。
3. 有明确许可证的字体/图标集或自行绘制母版。
4. 社区镜像仅作为有出处的参考；不能把“Garmin standard”文件名当成官方授权声明。

在需要精确原生样式但缺少公开资源时，给出已找到的官方参考和相似度限制；不得声称存在未经核实的私有接口。保留用户要求的样式，但视觉近似和逐像素一致要区分。未获用户授权，不因查资源而发帖/联系他人。

系统数据与系统图标是两条能力路径：Complications可提供支持的指标，但原生Complication的`getIcon()`返回null。数据接入和权限细节见[官方数据接入](official-data.md)。

每组资源记录原始URL、访问日期、文件哈希、来源类型、许可证状态、裁剪/阈值/目标像素尺寸、对应天气枚举。公开可见不等于开放许可证。项目已有来源说明时沿用并核实，技能只保存索引，不打包未知许可的固件/社区字体。

## WristInk已用资源

- 官方天气：`https://support.garmin.com/en-US/?faq=kArcrtjkiE55MEYli4FtK9`（inReach Mini 2 状态图标），13类源图及哈希见 `retro-world/assets/garmin-weather/sources.json`。9/11px适配见 `tools/garmin_weather.py`；不宣称Instinct固件逐像素相同。
- 官方日出日落：`https://support.garmin.com/en-US/?faq=agZJiZRjhX2adgWkBVOHI9`，`retro-world/assets/garmin-sun/source.json`；13×8半太阳方案是公开图形的原生格点适配。
- Moke社区图标出处与不明许可状态：`moke/assets/icons/SOURCE.txt`。不能与OFL字体许可混用。
- Noto Sans CJK / Rajdhani：项目保留OFL；优先从源轮廓生成目标字形。Natural Earth地图数据公有领域，仍保留来源。

## 图标适配验收

先去掉源图空白，再等比装入目标格。光学大小取墨迹，不是图片边框。天气图标需核对真实条件映射、未知/缺失回退、晴/少云昼夜变化，避免云滴反转或缩小后粘连。在原生屏幕比较图标笔画与旁边数字线宽，不能把高分辨率JPG直接缩成难辨黑团。

## 官方技术参考（2026-10-28核对，后续按目标SDK刷新）

- [Watch Faces](https://developer.garmin.com/connect-iq/articles/user-experience-guidelines/Watch_Faces.html)：屏幕家族、自定义字体、awake/sleep、partial update、AMOLED AOD。
- [Graphics](https://developer.garmin.com/connect-iq/articles/core-topics/Graphics.html)：图元抗锯齿、可缩放字体、位图/图形池。`setAntiAlias`针对图元，不自动改善低分辨率位图。
- [Resources](https://developer.garmin.com/connect-iq/articles/core-topics/Resources.html)：字体和资源编译。
- [Device Reference](https://developer.garmin.com/connect-iq/reference-guides/devices-reference/) 与本地SDK device packs：实际能力。

运行参数应核对安装SDK，而非照抄某次机器上的绝对目录。正常无需联网重抓已保留、来源明确的静态资产。
