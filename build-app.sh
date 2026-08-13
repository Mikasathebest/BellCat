#!/bin/zsh
set -euo pipefail

project_dir="${0:A:h}"
app_dir="$project_dir/BellCat.app"
binary_dir="$project_dir/.build/arm64-apple-macosx/release"

cd "$project_dir"
swift build -c release
mkdir -p "$app_dir/Contents/MacOS" "$app_dir/Contents/Resources"
cp "$binary_dir/BellCat" "$app_dir/Contents/MacOS/BellCat"
cp "$project_dir/AppResources/Info.plist" "$app_dir/Contents/Info.plist"
cp "$project_dir/AppResources/BellCat.icns" "$app_dir/Contents/Resources/BellCat.icns"
codesign --force --deep --sign - "$app_dir"

echo "Created $app_dir"
