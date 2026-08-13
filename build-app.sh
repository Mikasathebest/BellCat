#!/bin/zsh
set -euo pipefail

project_dir="${0:A:h}"
app_dir="$project_dir/BellCat.app"
binary_dir="$project_dir/.build/arm64-apple-macosx/release"

cd "$project_dir"
mkdir -p "$project_dir/.build/clang-cache" "$project_dir/.build/swiftpm-cache"

# Command Line Tools can briefly expose a newer Swift compiler beside an older
# default SDK while macOS updates are being staged. Prefer the stable 15.4 SDK
# when it is present, and keep all compiler caches inside the project.
stable_sdk="/Library/Developer/CommandLineTools/SDKs/MacOSX15.4.sdk"
if [[ -d "$stable_sdk" ]]; then
    export SDKROOT="$stable_sdk"
fi
export CLANG_MODULE_CACHE_PATH="$project_dir/.build/clang-cache"
export SWIFTPM_MODULECACHE_OVERRIDE="$project_dir/.build/swiftpm-cache"

swift build --disable-sandbox -c release --triple arm64-apple-macosx
mkdir -p "$app_dir/Contents/MacOS" "$app_dir/Contents/Resources"
cp "$binary_dir/BellCat" "$app_dir/Contents/MacOS/BellCat"
cp "$project_dir/AppResources/Info.plist" "$app_dir/Contents/Info.plist"
cp "$project_dir/AppResources/BellCat.icns" "$app_dir/Contents/Resources/BellCat.icns"
cp "$project_dir/AppResources/BellCatIcon-1024.png" "$app_dir/Contents/Resources/BellCatIcon-1024.png"
mkdir -p "$app_dir/Contents/Resources/Ambience"
cp "$project_dir"/AppResources/Ambience/*.mp3 "$app_dir/Contents/Resources/Ambience/"
cp "$project_dir/THIRD_PARTY_NOTICES.md" "$app_dir/Contents/Resources/THIRD_PARTY_NOTICES.md"
codesign --force --deep --sign - "$app_dir"

echo "Created $app_dir"
