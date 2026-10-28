# 第三方资源声明

各项第三方许可仅适用于对应的字体、数据或其派生资源，不代表对整个项目采用同一许可证。

## 字体

- Rajdhani：Google Fonts / Indian Type Foundry，SIL Open Font License 1.1。许可保留于 `moke/licenses/OFL-Rajdhani.txt` 和 `retro-world/assets/fonts/OFL-Rajdhani.txt`。
- Noto Sans CJK：SIL Open Font License 1.1，见 `moke/licenses/OFL-NotoSansCJK.txt`。源字体位于 `moke/assets/fonts/`。
- Aileron 相关位图字形：来源与作者许可说明见 `moke/licenses/Aileron-notice.txt`。

## Natural Earth

Retro World 的陆地轮廓来自 [Natural Earth 1:110m land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson)，按照 [Natural Earth 使用条款](https://www.naturalearthdata.com/about/terms-of-use/) 属于公有领域。源 GeoJSON 保留在 `retro-world/assets/`。

## OpenStreetMap / Geofabrik

北京离线地图的数据 © OpenStreetMap contributors，通过 [Geofabrik 北京提取](https://download.geofabrik.de/asia/china/beijing.html) 获取，遵循 [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)。原数据时间戳为 2026-10-25T21:21:21Z。

当前打包数据库保留在 `beijing-map/resources/`；转换代码位于 `beijing-map/tools/`。原始数据获取与重建方法见 `beijing-map/data/README.md`。再分发时应保留 [OpenStreetMap 署名及许可](https://www.openstreetmap.org/copyright)，并履行适用的数据库再分发要求。

## Garmin

墨刻还使用社区保存的 Garmin 图标资源；来源记录保留在 `moke/assets/icons/SOURCE.txt` 及同目录的参考 JSON 中。原镜像没有附带许可证声明，这些图标不属于上文的 OFL 字体资源，不能据此认定获得了相同的再授权。

Garmin、Instinct 和 Connect IQ 是其各自权利人的商标。仓库不分发 Garmin SDK；开发者需自行安装。项目为独立实现，与 Garmin 无隶属关系。
