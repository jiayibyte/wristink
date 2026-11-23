# Signal LCD

Garmin Connect IQ 复古数字表盘。普通 fēnix、epix、Forerunner 和 Venu 使用连续烟灰色 LCD，分为进度刻度、点阵星期与斜体年月日、斜切七段时间。小秒数位于时间右侧，12 小时制的下午显示 P。主屏只显示 LCD 框内的内容。带独立实体圆窗的 Instinct MIP 默认在开孔内显示心率，Descent G1 的开孔默认显示电量。

## 配置

在 Connect IQ 手机应用的表盘设置里选择主题、大字字体、12/24 小时制、日期和小秒数。普通圆屏五个框外数据位可独立更换或关闭。带实体圆窗的 MIP 机型在左上方显示两列四格数据，四格和圆窗均可独立配置。这两列使用 13px 粗体圆角数字和固定宽度的图标列，同一列的数值从同一像素起排；右列止于圆窗边框环之前。圆窗内是 19px 粗体读数。温度显示为 `19°C`，放不下时显示 `19°`；四位以上的数在放不下时改为 `8.6K` 这类写法。电池数据位的 `Battery display` 可切换百分比和 Garmin 系统预计剩余天数，机型未报告预计天数时显示百分比。进度刻度默认显示当日步数达成率，可切换为爬楼层数目标、每周强度分钟目标、电量、当天已过时间或关闭。可读取的数据因设备及传感器设置而异，缺少有效读数的数据位显示 `--`。

彩屏默认使用 Amber Night，共有十四套配色，包含 Ice Blue、Phosphor Green、Copper、Crimson、Ocean Teal、Rose Quartz、Sepia Paper 和 Signal Yellow。黑白 MIP 可选 Black LCD 或 White LCD。Instinct AMOLED 使用普通圆屏 LCD 布局。

所有字体都在各目标尺寸上直接构造，不把已经光栅化的字形按非整数倍缩放。MIP 用整像素笔画：9–18px 的字统一 2px 笔画，拐角为对称圆角，斜线为等步长台阶。数字、星期字母和数值单位共用这套构造。AMOLED 用同一构造放大 4 倍绘制后再按面积采样，所有字体都带灰阶边缘，包括数值、标签、图标和常亮时间；LCD 外框圆角也开启抗锯齿。每个字体只打包表盘实际会用到的字符。

数据图标在 11px 网格上逐像素绘制，见 [tools/icons.py](tools/icons.py)：斜边都是 45° 台阶，方框四角去掉角点。MIP 按原像素显示；AMOLED 由同一母版描出平滑轮廓，高度为数字的五分之四。图形按 Garmin 官方手册公开符号重绘。心率、电量和温度参考 [Instinct 3 Solar 状态图标](https://www8.garmin.com/manuals/webhelp/GUID-2C274FD2-F0C3-445C-B0AC-700FECCE12E9/EN-US/GUID-27C4910D-3C31-45B9-B6B2-8A4D35F83E09.html)，步数、热量、距离、楼层和通知参考 [vívosmart HR/HR+ 图标](https://www8.garmin.com/manuals/webhelp/vivosmarthr/EN-US/GUID-D3AEFEEF-1D51-4633-B790-0519D90F9EEE.html)，海拔和秒数参考 [Forerunner 965 控制菜单](https://www8.garmin.com/manuals/webhelp/GUID-0221611A-992D-495E-8DED-1DD448F7A066/EN-GB/GUID-700E76C4-F7E2-4984-8199-D59D6A31DFB9.html)。

## 照片中的标记

日期样式默认匹配照片的 `SUN '30- 6-30` 排法。表盘读取当前日期，演示包用 2030 年 6 月 30 日复现这个样例。[卡西欧 3565 指示器手册](https://support.casio.com/global/en/wat/manual/3565_en/UQIDSYofjcavyi.html)

日期上方的文字、小秒数上方的两个图标都能独立配置。默认分别显示系统提示音关闭、已连接手机和手表报告已设闹钟。还可以选择勿扰、活动通知、电量不超过 20%、震动关闭、手机未连接、已接入充电器或关闭。状态条件满足时才会显示，勿扰需要机型支持。

## 刷新与构建

小秒数默认关闭。开启后，小秒数和设为秒数的圆窗只在抬腕期间走秒，每次分别重绘各自的数字区域。MIP 待机按分钟刷新，同一分钟内抬腕或放下时按需更新秒数位置。各指标使用系统已有读数，天气缓存按需查询。AMOLED 常亮使用较小的暗灰色时间，逐分钟切换到互不重合的像素行。续航需在实体手表上长测。

从仓库根目录执行。需要 Connect IQ SDK、已安装目标设备包、开发者签名密钥、Python 3 和 Pillow。默认读取 SDK Manager 配置以及 `~/.Garmin/keys/developer_key.der`，可分别用 `CIQ_SDK`、`CIQ_HOME` 和 `CIQ_KEY` 指定路径。Windows 上默认读取 `%APPDATA%\Garmin\ConnectIQ`，编译器使用 `monkeyc.bat`。

```sh
python3 signal-lcd/tools/build.py epix2 fenix7 instinct3solar45mm
python3 signal-lcd/tools/build.py --export
python3 signal-lcd/tools/build.py --test instinct3solar45mm fr55 epix2
monkeydo signal-lcd/bin/tests/fr55/SignalTests.prg fr55 -t
python3 signal-lcd/tools/font_review.py signal-lcd/bin/font-review
```

[devices.json](devices.json) 记录支持的 SDK 目标，正式构建产物位于 `signal-lcd/bin/`。使用 `--demo` 可为模拟器生成独立 ID 的演示构建，`--test` 会把 `tests/` 编进 `SignalTests.prg`，Windows 的 `monkeydo` 用 `/t`。测试覆盖秒数局部刷新、两位数月份的日期格位、缺少气压计等传感器时的全部数据项，以及数值缩写。Forerunner 55 这类没有气压计的手表没有 `floorsClimbed` 字段，直接读取会让表盘启动即崩溃，所以每个可选字段都先用 `has` 检查。构建前会清掉 monkeyc 的资源缓存，因为缓存按位置索引，字体列表一变就会把 `Rez.Fonts` 对应到错误的图集。

设置页的标题和选项字符串标为 `scope="settings"`，只进手机设置，不进手表安装包。表盘和设置使用英文，[store/listings.json](store/listings.json) 提供 28 个商店语言的标题、说明与更新日志。
