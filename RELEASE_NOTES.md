# BellCat 2.0.0

BellCat 是一个原生 macOS 多阶段专注计时器和日程提醒应用。

## 亮点

- 在一个彩色交互圆环中呈现工作、休息及自定义阶段
- 点击或拖动圆环定位任务阶段和进度
- 自定义多阶段任务和日程提醒
- 支持通知提醒及连续三次的闹钟提醒
- 中文、英文、日语、西班牙语、法语、阿拉伯语和韩语界面
- 深色、浅色及跟随系统外观
- 自定义背景图片与透明度
- 全新起司猫闹钟应用图标

## 安装

macOS 用户可以下载 `BellCat-2.0.0-macOS-arm64.dmg`，打开后将 BellCat 拖到 Applications；也可以下载 ZIP 版本。Windows 用户下载 `BellCat-Windows-x64.zip`，Linux 用户下载 `BellCat-Linux-x64.tar.gz`。

当前构建为 Apple Silicon（M1/M2/M3/M4 及后续）版本，最低支持 macOS 13。

此版本采用临时签名，尚未使用 Apple Developer ID 公证。首次打开如果 macOS 阻止运行，请在 Finder 中右键 `BellCat.app`，选择“打开”，并再次确认。你也可以下载源码后运行 `./build-app.sh` 在本机重新构建。

首次启动请允许通知，否则计时器和日程提醒无法显示系统提醒。
