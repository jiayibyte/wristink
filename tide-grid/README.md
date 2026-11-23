# Tide Grid

Tide Grid 以获授权的 Casio GBX-100「TIME+TIDE ALL」液晶布局为参考。上半区显示港口、日出日落、潮汐曲线、月龄和潮汐周期，下半区是本地时间、日期、秒数和状态读数。彩色 MIP 和单色 MIP 默认黑底。适合彩色显示的设备可切换 12 套主题。

Instinct 3 Solar 等表款使用 SDK 设备包的实体圆窗中心，默认在两行分别显示下一次高潮时间与潮高。Instinct 3 AMOLED 的 45 和 50 mm 使用标准圆形 AMOLED 布局，高潮时间和潮高以两行读数显示在右上方。

## 设置

在 Garmin Connect IQ 应用中打开该表盘的设置。表盘与设置使用英文。

- **Chart** 可选七日步数、两小时心率、七日距离、七日热量、所选港口的潮汐预报，或隐藏图表。出厂默认选择潮汐。
- **Tide location** 默认用 **Automatic (near Garmin location)**。它先读手表最近一次的定位（不主动开启 GPS），没有时再用已同步且足够新的天气位置，按大圆距离从收录的验潮站里挑最近的一个，不限距离，所以安装后马上就有潮汐。表盘顶部会显示站名；离海很远时这个站可能相距数百公里，可在手机里按站名改选。没有任何可用坐标时显示 WAIT LOCATION。
- 也可以直接按名称选港，例如 **XIAMEN · CHINA**、**SAN FRANCISCO · USA** 或 **SYDNEY · AUSTRALIA**。手工选港后，预报在手表离线计算。默认 **Top title** 会显示所选或匹配到的英文站名。
- 顶部标题、左右上方各两格、图表两侧、主时间上方、时间右侧两格和底栏三格共 13 个数据位。每格都可换成日期、星期、电量、步数、心率、温度、距离、热量、海拔、楼层、通知、高潮或低潮时刻与潮高、月龄、潮汐周期、日出或日落，也可选 **Hidden**。数据由设备能力与已缓存样本决定。
- 默认三个特殊位置依次显示港口或图表标题（**Top title**）、本地时间标签 HOME（**Above main time**）和抬腕秒数（**Right of time · bottom**）。主时间的字形与制式可另选。
- **Clock font** 提供 Harbor 圆角、Dock 液晶粗体和 Beacon 七段，默认 Dock。**Clock format** 可跟随系统或固定 12、24 小时。**Seconds while awake** 默认开启，可关闭。
- **Theme** 在彩屏上提供 Deep Sea、Ember、Glacier、Kelp、Ink、Paper、Amber LCD、Ultraviolet、Signal Red、Lime Phosphor、Rose Quartz 和 Polar Light。单色及低色深设备提供 Ink 与 Paper。

## 默认读数对照

| 屏幕位置 | 演示内容 | 含义 |
| --- | --- | --- |
| 顶部 | CAPE TOWN | 演示港口名（收录站点之一）。正式运行显示所选或自动匹配的潮汐站英文名 |
| 左上 | 6:18 和 6:26P | 日出、日落时刻。P 表示下午 |
| 右上 | 3:03 和 196CM | 预测的下一次高潮时刻，以及相对于模型零位的预测高度 |
| 图表左侧 | 月亮图形和 1.0 | 月相与月龄，约为距上次新月 1.0 天 |
| 中间柱图 | 波形和高亮柱 | 12 小时潮汐走势，前 3 小时与后 9 小时。高亮柱标记当前时刻 |
| 图表右侧 | L、M 或 S | 按月相估算潮差趋势，分别为大、中、小 |
| 下半区 | HOME、P 10:58、SUN 30、50 | 本地时间、下午 10:58、星期日 30 日和秒数 |
| 最底一行 | 8426、74、86% | 今日步数、近时心率（每分钟 74 次）和剩余电量 |

## 字体与图标

三套时钟字体在各目标尺寸重新生成，各只包含十个数字与冒号。Dock 的 `1 0 : 5 8` 来自 Casio 参考图中逐字取出的独立墨迹，其他数字沿用它的笔画比例和圆切角。秒数使用独立的数字子集。单色屏使用整数像素，AMOLED 使用灰阶覆盖。小字和图标共享原生位图字体，图标底部对齐数字。

小字在 7px 时就是 5×7 点阵本身，原样使用。更大的 MIP 尺寸按整像素笔画重新构造字母和标点，不再把 5×7 点阵非整数倍拉伸，以免同一个字里出现 1px 和 2px 两种笔画。Instinct 上的图标同样按 5×7 母版 1:1 显示。AMOLED 上的小字以 4 倍超采样输出灰阶边缘。数据图标描自与 Signal LCD 共用的 11px 母版（[signal-lcd/tools/icons.py](../signal-lcd/tools/icons.py)），高潮、低潮和日历图标也在其中；天气和日出日落图形直接从已核验的源图做面积采样。月相圆盘、潮汐周期弧线和柱图在 AMOLED 上开启抗锯齿。

温度旁使用 [Garmin 支持页公开的天气图形](https://support.garmin.com/en-US/?faq=kArcrtjkiE55MEYli4FtK9)，日出、日落改编自 [Garmin 的公开表盘图标](https://support.garmin.com/en-US/?faq=agZJiZRjhX2adgWkBVOHI9)。构建时核验项目中已有的源图哈希。其他读数使用原生像素重绘，原生 Complication 的图标不由 Connect IQ API 返回。

## 数据与刷新

- 步数、卡路里和距离取自 ActivityMonitor，其中周图显示最近六个完整自然日和今天的累计值。心率图根据设备提供的历史样本聚合为两小时内的十分钟区间。历史中的无效样本（255）既不进图表，也不会当作当前心率显示。
- 潮汐来自 [TICON-3 验潮站谐波常数](https://doi.org/10.1594/PANGAEA.951610)，手表使用 17 个分潮进行天文预报。柱图显示前三小时及未来九小时。潮高以谐波模型零位计，可为负值。潮汐时刻按手表时区显示，供参考。
- 首批 30 个站点包括中国大陆 10 站，另有基隆、高雄、日本、新加坡、澳大利亚、新西兰、加拿大、美国、英国、法国、葡萄牙及南非的部分站点。完整目录见 `assets/tide-ports.json`。四个已收录的旧 NOAA 站号会迁移到同名站点。
- 自动匹配每 15 分钟查看一次手表定位和佳明天气位置。已选站点的潮汐曲线每半小时重新计算。手工选港可全程离线，位置不上传。
- 主表盘按分钟更新。抬腕时只重画秒数小区，不重画整个表盘；入睡时立即清掉秒数，AMOLED 入睡时立即切到常亮画面，不会把全亮表盘留到下一分钟。无应用定时器或主动 GPS。天气仅用 Garmin 缓存，最多每 15 分钟读取一次。心率历史和潮汐图每 10 分钟重建。七日图的往日数据每天只读一次，今天的柱每 3 分钟更新。AMOLED 常亮只显示低亮时分。
- 月龄依据 [NASA 月相数据](https://eclipse.gsfc.nasa.gov/phase/phases1901.html) 和平均朔望月估算。L、M、S 表示根据月相估计的潮差趋势，潮高和高潮低潮时间由所选站点的谐波模型计算。
- 潮汐相关数据有显示时，日出日落按已选或已匹配的验潮站坐标交给 Garmin API 计算，显示表盘当日在该坐标发生的事件，时间用手表时区。未选到站点时，使用手表天气位置或支持机型提供的系统日出日落值。没有可用读数时显示 `--`。

## 构建、检查与商店

用 Garmin Connect IQ SDK Manager 安装 SDK 9.2 和目标设备包，另需 Python 3.10+、Pillow、JDK 及自己的 Garmin 开发者签名密钥。商店包验签需要 7-Zip。可通过 `CIQ_SDK`、`CIQ_DEVICES`、`CIQ_KEY` 覆盖本机默认路径。

```sh
cd tide-grid
python3 tools/build.py --device fenix847mm --device epix2 --device instinct3solar45mm
python3 tools/build.py --store
python3 tools/check_layout.py dist/layout-audit.json
python3 tools/font_review.py dist/fonts
python3 tools/render_preview.py dist
python3 tools/build.py --preview fenix847mm --test --font 1
monkeydo bin/tests-fenix847mm.prg fenix847mm -t
```

原生字体、清单和每机型布局由构建工具生成。清单按 SDK 设备包的分辨率、形状、区域最低 API 与 RAM 筛选，排除会穿过数据区的实体指针机型。正式包与演示包使用不同的应用 ID。获取指定设备和样式的纯演示数据包可用 `python3 tools/build.py --preview fenix847mm --fixture tide --theme 0 --font 1`。Windows 上默认读取 `%APPDATA%\Garmin\ConnectIQ`，编译器使用 `monkeyc.bat`，`monkeydo` 的测试参数为 `/t`。

为控制安装包体积，每个机型只打包本屏幕家族（AMOLED、彩色 MIP 或单色）的主题色，以一个十六进制字符串存进生成的 `Panel.PALETTE`。港口表的每个站点存成一条 `名称|纬度|经度|分潮|旧站号` 字符串，由 `TideCatalog.port(i)` 按需解析，比五元素常量数组少约三分之一。每次编译前清掉 monkeyc 的资源缓存。

验签后的 `dist/store-audit.json` 记录每一硬件变体的单机 PRG 字节数与 SHA-256。`store/localizations.json` 覆盖 Connect IQ 商店编辑器使用的 28 套文案，与表盘英文资源分开。

## 参考屏幕

- [Casio GBX-100-1 官方正面产品图](https://www.casio.com/us/watches/gshock/product.GBX-100-1/)
- [Module 3482 手册中的 TIME+TIDE ALL 放大图及 BIG TIDE 对照](https://support.casio.com/global/en/wat/manual/3482_en/VPCVSYfzpadkoc.html)
- [Casio G-LIDE 官方功能与 LCD 特写](https://gshock.casio.com/europe/products/g-lide/gbx-100/)

## 潮汐数据来源与再生成

站点常数来自 Hart-Davis、Dettmering、Seitz（2022）TICON-3（PANGAEA.951610），CC BY 4.0。项目挑选 30 个沿海站，添加英文显示名，截取主要分潮并压缩精度。[原始数据与许可](https://doi.org/10.1594/PANGAEA.951610)

再生成时，从原始 ZIP 取出 `TICON_3.txt`，在 Python 环境安装 uptide 1.2，然后运行 `python3 tools/extract_tides.py /path/to/TICON_3.txt`。常规表盘构建直接使用仓库中的 JSON，无须下载数据。平衡相位和交点修正以该库的天文系数为基准。
