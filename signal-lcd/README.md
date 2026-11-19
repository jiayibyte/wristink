# Signal LCD

Garmin Connect IQ 复古数字表盘。普通 fēnix、epix、Forerunner 和 Venu 使用连续烟灰色 LCD，分为进度刻度、点阵星期与斜体年月日、斜切七段时间。小秒数位于时间右侧，12 小时制的下午显示 P。主屏只显示 LCD 框内的内容。带独立实体圆窗的 Instinct MIP 默认在开孔内显示心率，Descent G1 的开孔默认显示电量。

## 配置

在 Connect IQ 手机应用的表盘设置里选择主题、大字字体、12/24 小时制、日期和小秒数。普通圆屏五个框外数据位可独立更换或关闭。带实体圆窗的 MIP 机型在左上方显示两列四格数据，四格和圆窗均可独立配置。电池数据位的 `Battery display` 可切换百分比和 Garmin 系统预计剩余天数，机型未报告预计天数时显示百分比。进度刻度默认显示当日步数达成率，可切换为爬楼层数目标、每周强度分钟目标、电量、当天已过时间或关闭。可读取的数据因设备及传感器设置而异，缺少有效读数的数据位显示 `--`。

彩屏默认使用 Amber Night，共有十四套配色，包含 Ice Blue、Phosphor Green、Copper、Crimson、Ocean Teal、Rose Quartz、Sepia Paper 和 Signal Yellow。黑白 MIP 可选 Black LCD 或 White LCD。Segment、Contour、Matrix 和小秒数均按原生尺寸生成。AMOLED 的大字及秒字使用灰阶边缘，MIP 的数字采用直立整像素笔画和规则切角，星期使用连续像素笔画。Instinct AMOLED 使用普通圆屏 LCD 布局。

数据图标按 Garmin 官方手册公开符号在原生像素网格上重绘。心率、电量和温度参考 [Instinct 3 Solar 状态图标](https://www8.garmin.com/manuals/webhelp/GUID-2C274FD2-F0C3-445C-B0AC-700FECCE12E9/EN-US/GUID-27C4910D-3C31-45B9-B6B2-8A4D35F83E09.html)，步数、热量、距离、楼层和通知参考 [vívosmart HR/HR+ 图标](https://www8.garmin.com/manuals/webhelp/vivosmarthr/EN-US/GUID-D3AEFEEF-1D51-4633-B790-0519D90F9EEE.html)，海拔和秒数参考 [Forerunner 965 控制菜单](https://www8.garmin.com/manuals/webhelp/GUID-0221611A-992D-495E-8DED-1DD448F7A066/EN-GB/GUID-700E76C4-F7E2-4984-8199-D59D6A31DFB9.html)。

## 照片中的标记

日期样式默认匹配照片的 `SUN '30- 6-30` 排法。表盘读取当前日期，演示包用 2030 年 6 月 30 日复现这个样例。[卡西欧 3565 指示器手册](https://support.casio.com/global/en/wat/manual/3565_en/UQIDSYofjcavyi.html)

日期上方的文字、小秒数上方的两个图标都能独立配置。默认分别显示系统提示音关闭、已连接手机和手表报告已设闹钟。还可以选择勿扰、活动通知、电量不超过 20%、震动关闭、手机未连接、已接入充电器或关闭。状态条件满足时才会显示，勿扰需要机型支持。

## 刷新与构建

小秒数默认关闭。开启后，小秒数和设为秒数的圆窗只在抬腕期间走秒，每次分别重绘各自的数字区域。MIP 待机按分钟刷新，同一分钟内抬腕或放下时按需更新秒数位置。各指标使用系统已有读数，天气缓存按需查询。AMOLED 常亮使用较小的暗灰色时间，逐分钟切换到互不重合的像素行。续航需在实体手表上长测。

从仓库根目录执行。需要 Connect IQ SDK、已安装目标设备包、开发者签名密钥、Python 3 和 Pillow。默认读取 SDK Manager 配置以及 `~/.Garmin/keys/developer_key.der`，可分别用 `CIQ_SDK`、`CIQ_HOME` 和 `CIQ_KEY` 指定路径。

```sh
python3 signal-lcd/tools/build.py epix2 fenix7 instinct3solar45mm
python3 signal-lcd/tools/build.py --export
python3 signal-lcd/tools/font_review.py signal-lcd/bin/font-review
```

[devices.json](devices.json) 记录支持的 SDK 目标，正式构建产物位于 `signal-lcd/bin/`。使用 `--demo` 可为模拟器生成独立 ID 的演示构建。表盘和设置使用英文，[store/listings.json](store/listings.json) 提供 28 个商店语言的标题、说明与更新日志。
