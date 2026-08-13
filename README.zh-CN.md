<p align="center">
  <img src="AppResources/BellCatIcon-1024.png" width="180" alt="BellCat 图标">
</p>

# BellCat

[English](README.md) · 简体中文

BellCat 是一款安静、专注的多阶段计时器与日程提醒应用，支持 macOS、Windows 和 Linux。它将交互式任务、定时提醒、多语言座右铭、主题和循环白噪声融合在同一个桌面体验中。

## 安装

### 一键下载安装

从 [GitHub Releases](../../releases/latest) 下载最新版：

- **macOS Apple Silicon：** 打开 DMG，将 BellCat 拖入 Applications。
- **Windows x64：** 运行 `BellCat-*-Windows-x64-Setup.exe`，按向导完成当前用户安装。
- **Linux x64：** 解压 TAR.GZ 后运行 `BellCat`。

macOS 构建采用临时签名，尚未经过 Apple 公证。如果 Gatekeeper 阻止打开，请右键 BellCat 并选择“打开”。

### 源码编译安装

macOS 需要 Swift 5.9 或更高版本：

```sh
chmod +x build-app.sh
./build-app.sh
```

Windows 和 Linux 使用 [`CrossPlatform`](CrossPlatform) 中的实现：

```sh
python3 -m pip install pygame
python3 CrossPlatform/bellcat.py
```

## License

[MIT](LICENSE)
