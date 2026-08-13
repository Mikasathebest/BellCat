# BellCat

[English](README.md) | 简体中文

一个带美短起司猫闹钟图标的多阶段专注计时器与日程提醒应用，支持 macOS、Windows 和 Linux。

![BellCat 图标](AppResources/BellCatIcon-1024.png)

## 功能

- 创建包含工作、休息和自定义阶段的任务，在同一个圆环中按时长分色显示
- 点击色段切换阶段，点击或拖动圆点在任务时间轴中定位
- 设置未来事件，按分钟、小时或天提前提醒
- 通知模式提醒一次，闹钟模式连续提醒三次
- 中文、英文、日语、西班牙语、法语、阿拉伯语和韩语界面
- 座右铭优先显示当前语言，并在下方保留英文原文
- 深色、浅色及跟随系统外观，支持自定义背景与透明度
- 任务、提醒、语言和主题设置持久保存

## 下载与安装

请前往 [Releases](../../releases/latest) 下载适合你的系统的版本。

### macOS

下载 `BellCat-2.1.1-macOS-arm64.dmg`，打开后将 BellCat 拖入 Applications。当前版本适用于 Apple Silicon，最低支持 macOS 13。

当前 macOS 包采用临时签名，尚未使用 Apple Developer ID 公证。如果首次打开被系统阻止，请在 Finder 中右键 BellCat 并选择“打开”。

### Windows

推荐下载 `BellCat-2.1.1-Windows-x64-Setup.exe`，双击后按安装向导完成安装。安装程序会创建开始菜单入口，并可选创建桌面快捷方式；不需要管理员权限。

便携版可以下载 `BellCat-Windows-x64.zip`，解压后直接运行 `BellCat.exe`。

### Linux

下载 `BellCat-Linux-x64.tar.gz`，解压并运行 `BellCat`。桌面通知需要系统安装 `libnotify`。

## 从源码构建 macOS 版本

要求 macOS 13 或更高版本，以及 Apple Swift 5.9 或更高版本：

```sh
chmod +x build-app.sh
./build-app.sh
```

也可以使用 Xcode 打开 `Package.swift` 并选择 **My Mac** 运行。

Windows 与 Linux 源码位于 [`CrossPlatform`](CrossPlatform)。

## License

[MIT](LICENSE)
