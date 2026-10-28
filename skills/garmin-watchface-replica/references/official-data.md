# 佳明官方数据接入手册

核对基线：2026-10-28，Connect IQ SDK 9.2.0本地API文档与下方官方在线文档。API版本只是入口条件，不保证每台设备、每个字段都有值；每次实现仍需核对目标设备和固件。

## 数据入口与适用边界

表盘优先使用手表上的 `Toybox` 官方API及系统已缓存数据。不把截图示例值当成真实数据，不用未经公开的Garmin Connect接口、账户cookie或所谓“固件内部接口”补齐缺失字段。手机同步/系统天气服务负责上游更新；表盘读取缓存不能强制刷新它们。

一个显示字段应记录：**含义、API/字段、单位、权限、目标能力、来源时间、读取频率、过期策略、空值样式**。适配层返回 value / unit / source / observedAt / readAt / status 等语义，绘图层只格式化和画值；小内存设备用固定字段承载即可，不必每次分配字典。

## 常用字段对照

| 显示数据 | 官方入口/字段 | 单位与语义 | 注意事项 |
| --- | --- | --- | --- |
| 时间/日期 | `System.getClockTime()`；`Time.now()`；`Time.Gregorian.info()` | 时钟字段与时间戳；日期按本地时区格式化 | 12/24h取用户/系统设置；UTC时间戳用于年龄计算，不用字符串时间相减 |
| 步数/目标 | `ActivityMonitor.getInfo().steps / stepGoal` | 当日步数与系统目标 | 午夜重置；目标为0/缺失不能除零 |
| 距离 | `ActivityMonitor.getInfo().distance` | **厘米**，当日累计 | km=cm/100000；不要与运动会话的距离混用 |
| 热量 | `ActivityMonitor.getInfo().calories` | 当日kcal | 不擅自标成“仅活动热量”或某次运动消耗 |
| 楼层/活动分钟 | `floorsClimbed / floorsClimbedGoal / activeMinutesDay / activeMinutesWeek` | 楼层、日/周活动分钟结构 | 检查字段支持；不要把周目标当日目标。若按官方加权口径合成分钟，先核对中高强度权重 |
| 当前心率 | `Activity.getActivityInfo().currentHeartRate` | bpm，设备提供的当前信息 | 可缺失；读取不等于启动光学传感器，更不保证每秒有新样本 |
| 心率历史/曲线 | `ActivityMonitor.getHeartRateHistory(period,newestFirst)` | `HeartRateSample.heartRate / when` | Number为条数，Duration为时间窗；`INVALID_HR_SAMPLE`不可画成真实值 |
| 传感器心率历史 | `SensorHistory.getHeartRateHistory(options)` | `SensorSample.data / when` | 与上一接口的对象字段不同，不能读取`.heartRate` |
| 天气/体感/最高最低 | `Weather.getCurrentConditions()` 的 `temperature / feelsLikeTemperature / highTemperature / lowTemperature / condition` | 温度℃；condition为`Weather.CONDITION_*` | 最近缓存，可能整对象或单字段null；与机身传感器温度不同 |
| 风/湿度/降水概率 | 同上 `windSpeed / windBearing / relativeHumidity / precipitationChance` | m/s；方向角度；百分比 | km/h=m/s×3.6；北0东90。箭头表示来向还是去向需约定，不靠截图猜数据语义 |
| 天气时效/位置 | `observationTime / observationLocationPosition` | UTC观测时间与观测地点 | 观测地点不等于当前GPS位置；坐标字段需要Positioning权限 |
| 逐小时/逐日预报 | `Weather.getHourlyForecast() / getDailyForecast()` | 有限数组，字段见对应Forecast类 | 与当前天气分开；null/空数组均可发生，只保留需要的项 |
| 日出/日落 | `Weather.getSunrise(location,date) / getSunset(location,date)` | `Time.Moment`或null | API3.3.0起；指定位置和日期，返回值再按目标时区格式化；极昼/极夜不能编造时刻 |
| 最近位置 | `Position.getInfo().position / when / accuracy` | `Position.Location.toDegrees()` 得纬度、经度 | Positioning权限；最近已知信息不保证新鲜。正常表盘不主动调用定位事件启动GPS |
| 海拔/气压 | `Activity.getActivityInfo().altitude / ambientPressure` | 米、Pa | 负海拔有效；Pa÷100=hPa。局地气压与海平面气压不可混称 |
| 海拔/气压/机身温度历史 | `SensorHistory.getElevationHistory / getPressureHistory / getTemperatureHistory` | `SensorSample.data / when`；单位核对具体接口 | 机身温度受佩戴影响，不能标成天气气温或体温 |
| 电量/续航/充电 | `System.getSystemStats().battery / batteryInDays / charging` | %、天、bool | batteryInDays为系统值，API3.3.0且设备支持时才有；不可从百分比臆算天数 |
| 太阳能/内存 | 同上 `solarIntensity / freeMemory / usedMemory / totalMemory` | 太阳能字段描述充电效率0–100，内存字节 | solarIntensity可null或负值，不是照度lux；内存用于开发诊断，默认不向用户显示 |
| 压力/Body Battery | `SensorHistory.getStressHistory / getBodyBatteryHistory` | 最近历史样本，API3.3.0起 | 也可在支持设备用Complications当前值；不是原始传感器读数，0不能统一判无效 |
| 血氧 | `Activity.getActivityInfo().currentOxygenSaturation` 或 `SensorHistory.getOxygenSaturationHistory` | %；历史入口API3.2.0起 | 检查机型、测量时间和字段支持，不能暗示持续测量或用心率推算 |
| 通知/连接 | `System.getDeviceSettings()` 中 `notificationCount / phoneConnected` 等支持字段 | 通知数、连接状态 | 逐字段`has`/null检查；未连接不代表所有缓存立刻失效 |

依据：[ActivityMonitor.Info](https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor/Info.html)、[Activity.Info](https://developer.garmin.com/connect-iq/api-docs/Toybox/Activity/Info.html)、[Weather](https://developer.garmin.com/connect-iq/api-docs/Toybox/Weather.html)、[CurrentConditions](https://developer.garmin.com/connect-iq/api-docs/Toybox/Weather/CurrentConditions.html)、[SensorHistory](https://developer.garmin.com/connect-iq/api-docs/Toybox/SensorHistory.html)、[System.Stats](https://developer.garmin.com/connect-iq/api-docs/Toybox/System/Stats.html)、[DeviceSettings](https://developer.garmin.com/connect-iq/api-docs/Toybox/System/DeviceSettings.html)、[Position.Info](https://developer.garmin.com/connect-iq/api-docs/Toybox/Position/Info.html)。

## 权限与能力检查

| 使用场景 | Manifest权限/能力 |
| --- | --- |
| SensorHistory历史数据 | `SensorHistory`权限；模块和具体方法都需目标支持 |
| Position.getInfo、天气观测坐标、Activity当前位置 | `Positioning`；未授权天气坐标可为null，不能把这个误判为“天气API坏了” |
| 系统Complications订阅 | `ComplicationSubscriber`；API4.2.0起，具体类型另有版本/机型限制 |
| 普通时间、ActivityMonitor统计、System电池、Weather当前温度 | 不为了这些读数一律添加GPS、网络或持续Sensor订阅权限；按当前SDK文档按需声明 |

`has`解决“符号是否存在”，null检查解决“当前有没有值”，权限声明解决“是否可访问”，三者不能互相替代。跨代兼容时先检查`Toybox has :Module`，再检查模块方法和对象成员。能力分支中不要在检查之前求值不支持的常量/字段；最低支持机型也必须编译和运行。

不把读取系统已生成的值和主动采集混淆。`Sensor`事件订阅、GPS定位事件、网络请求是另一个耗电和权限层级；复现截图本身不要求启动它们。

## 天气的正确处理

1. 低频读取`getCurrentConditions()`，同时保留`observationTime`和本次readAt；后者不能重置前者的年龄。
2. 逐字段处理null，使用条件枚举映射图标；温度0℃、风速0、湿度0不能当缺失。新字段如cloudCover、dewPoint、uvIndex等API5.1.0入口需额外能力检查。
3. 过期时使用占位或明确的旧数据标识；手机离线时允许仍有效缓存继续显示。不要把读取调用次数当网络更新次数。
4. 当前天气、小时预报、日预报分别缓存，只为可见UI读取。天气位置作为粗略地图备用位置时记录source=weather，不能标成当前GPS fix。
5. 晴/少云昼夜图标优先依据有效位置与日出日落；缺失时可按本地时段做**视觉回退**，不能伪造天文数据。先验证正常值，再验证无同步、空缓存、过期、单字段缺失和未知枚举。

## 心率与健康历史的正确处理

优先读目标支持且有效的当前值；无值时可退到最近历史样本，但必须携带sample.when并设定新鲜度限制。显示历史值时不宣称“实时”。关掉腕式心率、摘表、运动结束或设备重启后，数据可能缺失或变旧。

`ActivityMonitor.getHeartRateHistory(1,true)`取最近1条，并不表示1秒。曲线用`Time.Duration`定义时间窗，并按样本时间归桶；采样间隔随设备变化。空桶保留缺口，不能补0或跨断档画连续趋势。`SensorHistory`中的`:period`同样区分条数与Duration，`.next()`可为空。

处理每种数据自己的无效值和范围，避免通用`value > 0`过滤器：压力/Body Battery的0、零距离、负海拔与负气温可能有意义。历史图只扫描有限窗口，分桶数组复用，不在秒级路径扫描全天历史。

## 官方系统Complications

这条路线可读取系统复杂指标，不必自己重算佳明算法。先用`getComplications()`枚举当前可用ID，再用`getComplication(id)`读对象的`value`。原生类型可以构造`new Complications.Id(type)`；第三方ID不要猜。处理`ComplicationNotFoundException`、空值和订阅失败。

经SDK9.2文档确认的示例：`COMPLICATION_TYPE_HEART_RATE`、`STRESS`、`BODY_BATTERY`、`RESPIRATION_RATE`、`RECOVERY_TIME`、`VO2MAX_RUN`、`VO2MAX_BIKE`、`TRAINING_STATUS`（各常量均带`COMPLICATION_TYPE_`前缀）。**RECOVERY_TIME单位是分钟**。睡眠评分`COMPLICATION_TYPE_SLEEP_SCORE`从API6.0.2起，不应放进API4.2设备的无条件路径。

需要变化通知时注册`registerComplicationChangeCallback`再`subscribeToUpdates(id)`；只订阅正在显示的指标。退出或更换配置时取消不需要的订阅，重新启动时恢复订阅。回调只更新缓存并按显示模式请求必要绘制，不意味着可绕过AOD/低功耗限制。不要编造训练准备度、HRV等未在目标API中核实的常量，也不从其他指标推算这些官方专有评分。

读取系统指标不等于能导出它的原生图标。`Complication.getIcon()`文档说明它仅适用于用户Complication，原生系统Complication返回null；不能用它承诺获取所有佳明官方表盘图标。图标仍按[资源来源流程](resources.md)处理。依据：[Complication对象](https://developer.garmin.com/connect-iq/api-docs/Toybox/Complications/Complication.html#getIcon-instance_function)。

依据：[Complications API](https://developer.garmin.com/connect-iq/api-docs/Toybox/Complications.html)、[官方Complications说明](https://developer.garmin.com/connect-iq/core-topics/complications/)。核对时也可读本地`doc/docs/Core_Topics/Complications.html`，避免站点路径变化误判为能力不存在。

## 刷新和过期策略是产品选择

以下是现有两款实现可借鉴的起点，**不是Garmin保证的更新周期**：

| 数据 | 读取起点 | 缓存/失效 |
| --- | --- | --- |
| 当前心率 | 抬腕时约5秒一次，待机按分钟/显示需要 | 历史回退例：180秒内有效；不能因读取成功延长旧样本寿命 |
| 步数/热量/距离/电池 | 分钟更新或唤醒必要刷新 | 午夜、设置改变、单位变化；日统计按各自日期重置 |
| 天气 | 5–30分钟，唤醒时有最小间隔 | Retro World例：观测年龄上限3小时；按产品调整并告知旧数据策略 |
| 位置 | 随环境数据刷新读取已有信息 | Retro World例：已有fix2小时内才用，天气位置另记来源；0°/0°本身不是非法坐标 |
| 日出日落 | 日期/位置改变时计算 | 当地日期、时区、位置变化均应使缓存失效；null可表示无日出/日落 |
| 健康历史曲线 | 1–5分钟、窗口变化 | 有界条数与时间窗；保留缺口与样本时间 |
| AMOLED AOD | 只画低亮时间等必要内容 | 默认暂停天气、历史和地图读取；系统当前值仍由系统自行更新 |

## 实现与验收清单

为每个字段测试：接口不存在、对象null、成员null、无效哨兵、样本过期、未来时间戳/时钟回拨、正常0、负温度/海拔、单位切换、日期边界。位置增加精度、纬经范围与过期；日出日落增加跨时区和极昼极夜。

记录来源而非伪造精度。位置缺失就隐藏标记或显示未知；续航缺失显示`--D`；心率缺失显示`--`。未经用户要求，不输出真实健康或精确位置到日志、截图物料、网络和PR。

现有实现定位：`retro-world/source/LiveData.mc`（当前/历史心率、日统计、电池）、`Environment.mc`（天气、位置、日出日落）；`moke/source/PowerPolicy.mc`（按可见字段决定读取）、`LiveHeart.mc`、`TrendData.mc`。这些是历史先例，不代表所有能力检查/时区失效都已完整实现；新代码以本手册和目标SDK为准，并补实际测试。
