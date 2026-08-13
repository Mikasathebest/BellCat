<p align="center">
  <img src="AppResources/BellCatIcon-1024.png" width="180" alt="BellCat icon">
</p>

# BellCat

English · [简体中文](README.zh-CN.md)

BellCat is a calm multi-stage focus timer and reminder app for macOS, Windows, and Linux. It combines interactive routines, scheduled alerts, multilingual quotations, themes, and looping white noise in one focused desktop experience.

## Install

### One-click download

Download the latest version from [GitHub Releases](../../releases/latest):

- **macOS Apple Silicon:** open the DMG and drag BellCat to Applications.
- **Windows x64:** run `BellCat-*-Windows-x64-Setup.exe` for guided per-user installation.
- **Linux x64:** extract the TAR.GZ and run `BellCat`.

The macOS build is ad-hoc signed but not Apple-notarized. If Gatekeeper blocks it, Control-click BellCat and choose **Open**.

### Build from source

macOS requires Swift 5.9 or later:

```sh
chmod +x build-app.sh
./build-app.sh
```

Windows and Linux use the implementation in [`CrossPlatform`](CrossPlatform):

```sh
python3 -m pip install pygame
python3 CrossPlatform/bellcat.py
```

## License

[MIT](LICENSE)
