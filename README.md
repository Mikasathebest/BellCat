# BellCat

一个带起司猫闹钟图标的原生 macOS 多阶段专注计时器与日程提醒应用。

![BellCat icon](AppResources/BellCatIcon-1024.png)

- 创建包含工作、休息和自定义阶段的任务；阶段在同一圆环中按时长分色显示
- 点击色段切换阶段，点击或拖动圆点在任务时间轴中定位
- 常见提示音与本地自选音频
- 设置未来事件的日期与时间
- 按分钟、小时或天设置提前提醒
- 通知模式提醒一次，闹钟模式连续提醒三次
- 提醒保存在本机，重新启动后仍然有效
- 可在应用右上角即时切换中文、英文、日语、西班牙语、法语、阿拉伯语和韩语
- 语言选择会保存在本机；阿拉伯语自动采用从右向左布局
- 随机显示莎士比亚、丘吉尔、福尔摩斯及大仲马名著中的座右铭
- 支持跟随系统、浅色、深色主题，以及自定义背景图片和透明度

## 运行

从 [Releases](../../releases) 下载 `BellCat-2.1.0-macOS-arm64.zip`，解压后将 `BellCat.app` 拖入“应用程序”。当前发行包适用于 Apple Silicon，最低支持 macOS 13。

也可以下载 `BellCat-2.1.0-macOS-arm64.dmg`，打开安装盘后将 BellCat 拖到 Applications。Windows 和 Linux 构建由 GitHub Actions 在相应平台上生成，并附加到 Release。

> 当前发行包采用临时签名，尚未使用 Apple Developer ID 公证。如果首次打开被 macOS 阻止，请在 Finder 中右键应用并选择“打开”。

如果需要重新构建 `.app`，在终端中运行：

```sh
chmod +x build-app.sh
./build-app.sh
```

在 Mac 的“终端”中进入本文件夹后运行：

```sh
swift run
```

也可以直接用 Xcode 打开 `Package.swift`，选择 **My Mac** 后运行。首次运行请允许通知；倒计时结束或日程提醒到期时会播放声音并发送 macOS 通知。

## 示例

要设置“2026 年 9 月 18 日乘飞机，提前 3 小时到浦东机场”：

1. 进入“日程提醒”，点击“新建提醒”。
2. 名称填写“到浦东机场”，事件时间选择航班起飞时间。
3. 提前量填写 `3 小时`，再选择“通知”或“闹钟”。

闹钟模式使用普通系统通知声音，每隔 15 秒提醒一次，共 3 次。它不会绕过 macOS 的“勿扰模式”。

## 构建要求

- macOS 13 或更高版本
- Apple Swift 5.9 或更高版本（Xcode Command Line Tools 或 Xcode）

Windows 与 Linux 版本的源码位于 [`CrossPlatform`](CrossPlatform)，基于 Python 标准 GUI 实现核心的多阶段计时、交互圆环、提醒、主题持久化和七语言界面。

## License

[MIT](LICENSE)
