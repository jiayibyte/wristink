# 墨刻 Moke

面向 Garmin MIP 屏幕的可配置数据表盘。功能概览见[主目录说明](../README.md#墨刻--百变数据表盘)。

## 构建

在项目主目录配置 Connect IQ SDK 9.2、JDK 19、Python 依赖和个人签名密钥后执行：

```sh
# 从仓库根目录运行：仅构建 Instinct 3 Solar 45 / 50 mm
zsh moke/scripts/build-instinct3.sh 1.1.0
```

正式侧载包为 `moke/bin/Moke-Instinct3.prg`，演示包为 `moke/bin/Moke-Instinct3-demo.prg`，商店包输出到 `moke/dist/`。两个尺寸使用同一个 SDK 构建目标；演示包包含模拟数据和独立应用 ID。

全 MIP 目标构建需要通过 SDK Manager 安装所需设备包。下列脚本会重新生成派生代码、位图资源、设备清单与 jungle 配置，并执行资源检查：

```sh
zsh moke/scripts/build-store.sh 1.1.0
```

`scripts/build.sh` 和 `scripts/build-preview.sh` 直接使用 `monkey.jungle` / `preview.jungle`，需先存在对应的 `generated/` 资源；全机型派生资源可用 `python3 moke/scripts/generate-mip-targets.py` 生成。该生成器依据本机已安装的设备包运行，结果可能随 SDK 设备库变化。

## 代码位置

- `source/`：主视图、绘制、布局、设置、心率、天气、字体和功耗策略。
- `compat/`、`profiles/`：兼容层和基础设备配置。
- `resources/`、`resources-eng/`：基础与英文资源。
- `assets/fonts/`、`licenses/`：字体源文件与许可。
- `config/`：设备、设置与布局配置。
- `scripts/`：资源生成、编译、布局检查及模拟器验证。
- `tests/power/`：SDK 功耗策略相关测试。

`generated/`、`build/` 为本地生成目录，不提交到 Git。对照旧版本的检查脚本需要本机保留的历史发布材料。

## 数据与设备差异

健康、天气、历史数据和机上设置能力随手表接口与内存变化；缺失数据使用占位符。天气来自系统缓存，表盘不主动启动 GPS。当前心率、历史曲线与演示数据不能混为一谈。

机型清单见 `manifest.xml` 与 `config/mip-devices.json`；这些是构建配置，不能作为全部机型已完成真机验证的证明。
