# 北京地图原始数据与处理中间文件

仓库已包含 `../resources/` 中编译所需的地图、地点搜索和路网资源。普通构建不需要重新下载原始数据。

当前数据来源为 [Geofabrik 北京 OSM 提取](https://download.geofabrik.de/asia/china/beijing.html)，原始时间戳为 **2026-10-25T21:21:21Z**。地图数据 © OpenStreetMap contributors，遵循 [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)。获取方式与署名见 [OpenStreetMap copyright](https://www.openstreetmap.org/copyright)。

更新数据时，从上述数据源下载北京 `.osm.pbf`，按提供的校验值核验后存为此目录下的 `beijing-full.osm.pbf`。下载的最新数据不保证与当前内置资源一致。

在 Python 虚拟环境中安装预处理依赖：

```sh
python -m pip install osmium networkx scipy pypinyin
```

随后按[项目说明](../README.md#重建与验证)中的顺序运行生成器。此目录下的大型 JSON、Pickle、PBF 与临时文件由 `.gitignore` 排除，避免把下载缓存和处理中间结果重复提交；重新生成资源后需重新运行数据校验及模拟器测试。
