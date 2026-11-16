# 本轮设置保存专项结果

未提交墨刻商店更新。

通过：空本地菜单不再挂起表盘；本能2/2S/2X/3的六项属性程序内写入、独立进程重启、切页与休眠恢复；原始与紧凑图标29种指标（含隐藏）两主题绘图命令完全一致；一轮90目标/184硬件变体导出与签名通过。

仍失败：官方编辑器保存完整墨刻配置后，UI提示Settings Saved，但PHONE_CHANGED与PHONE_AFTER仍为旧的darkTheme=true。独立最小应用的一项设置及同样94项设置表都能收到false，说明不能把失败归结于编辑器普遍故障或设置表本身。原始、紧凑代码、移除恒等坐标包装以及现代Properties读取路径均未最终消除此真实外部同步失败。此项阻止发布。

临时loadProperties和现代读取API尝试未保留。保留已验证的内存压缩、空天气保护与测试工作；恒等坐标包装移除仅验证编译与额外内存，不是完整发布验证。当前dist候选与最新工作树可能不一致，必须在剩余同步缺陷解决后重新构建和验签。

独立重启探针会在退出前按生产停止时相同的方式释放缓存；在2S上生命周期恢复采用不同回调，避免探针在单回调中重复整帧绘制触发看门狗。不得把程序内属性写入通过当成手机同步通过。

关键日志：phone-settings-live.log、phone-settings-reload.log、phone-settings-native-coordinates.log、phone-settings-properties-api.log、settings-control.log、settings-control-94.log；四个目标的final-phase与result文件保留。
