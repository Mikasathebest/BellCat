# BellCat 2.5.1

This patch makes stage completion explicit and fixes the end-sound preview across macOS, Windows, and Linux.

## What’s new

- The 6-second end-sound preview now loops short system sounds and stops precisely after six seconds.
- When a focus or break stage reaches zero, its configured bell now rings continuously and the ring stays at `00:00`.
- BellCat no longer advances stages automatically. Pet the cat-head button to silence the bell, enter the next stage, and start its countdown.
- Replaced synthetic white noise with four natural recordings: ocean waves, window rain, pine-forest wind, and forest birds.
- Lowered built-in ambience playback levels for softer long sessions.
- Renamed the Pomodoro area and preset to **Focus** / **专注** in all seven languages.
- Replaced the Start button with the BellCat cat-head icon; petting animation now completes before the timer begins.
- Strengthened the draggable ring’s fading particle trail.
- Clicking any outer-ring segment now opens its saved color editor reliably.
- The opacity control now changes the entire app window from 20% to 100% and persists automatically.
- Added bundled audio attribution and licensing notices.

## Downloads

- macOS Apple Silicon: `BellCat-2.5.1-macOS-arm64.dmg` or ZIP
- Windows x64 installer: `BellCat-2.5.1-Windows-x64-Setup.exe`
- Linux x64: `BellCat-Linux-x64.tar.gz`

macOS builds are ad-hoc signed. If Gatekeeper blocks first launch, Control-click BellCat and choose **Open**.
