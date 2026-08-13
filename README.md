# BellCat

English | [简体中文](README.zh-CN.md)

BellCat is a playful multi-stage focus timer and reminder app for macOS, Windows, and Linux, featuring an American Shorthair alarm-clock mascot.

![BellCat icon](AppResources/BellCatIcon-1024.png)

## Features

- Build routines with work, break, and custom stages, visualized as proportional segments on one interactive ring
- Click a segment to change stages, or click and drag the progress dot to seek through the routine
- Schedule future events with minute-, hour-, or day-based advance reminders
- Choose a single notification or a three-alert alarm mode
- Switch instantly between English, Chinese, Japanese, Spanish, French, Arabic, and Korean
- Show quotations in the selected language with the original English text underneath
- Use system, light, or dark appearance, plus a custom background image and opacity
- Persist routines, reminders, language, and theme preferences locally

## Download and install

Visit the [latest release](../../releases/latest) and choose the package for your platform.

### macOS

Download `BellCat-2.1.1-macOS-arm64.dmg`, open it, and drag BellCat into Applications. The current package supports Apple Silicon and requires macOS 13 or later.

The macOS package is ad-hoc signed but not yet notarized with an Apple Developer ID. If Gatekeeper blocks the first launch, Control-click BellCat in Finder, choose **Open**, and confirm.

### Windows

For the easiest installation, download `BellCat-2.1.1-Windows-x64-Setup.exe` and follow the installer. It adds a Start Menu shortcut, optionally creates a desktop shortcut, and installs per-user without administrator access.

For a portable copy, download `BellCat-Windows-x64.zip`, extract it, and run `BellCat.exe`.

### Linux

Download `BellCat-Linux-x64.tar.gz`, extract it, and run `BellCat`. Desktop notifications require `libnotify` on the host system.

## Build the macOS app from source

Requirements: macOS 13 or later and Apple Swift 5.9 or later through Xcode Command Line Tools or Xcode.

```sh
chmod +x build-app.sh
./build-app.sh
```

You can also open `Package.swift` in Xcode and run the **My Mac** destination.

The Windows and Linux implementation lives in [`CrossPlatform`](CrossPlatform).

## License

[MIT](LICENSE)
