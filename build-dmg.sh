#!/bin/zsh
set -euo pipefail

project_dir="${0:A:h}"
version="2.1.0"
app_path="$project_dir/BellCat.app"
dmg_path="$project_dir/BellCat-$version-macOS-arm64.dmg"
stage_dir="$(mktemp -d /private/tmp/bellcat-dmg.XXXXXX)"

cleanup() {
    /bin/rm -rf "$stage_dir"
}
trap cleanup EXIT

if [[ ! -d "$app_path" ]]; then
    echo "BellCat.app not found. Run ./build-app.sh first."
    exit 1
fi

ditto "$app_path" "$stage_dir/BellCat.app"
ln -s /Applications "$stage_dir/Applications"
hdiutil create \
    -volname "BellCat $version" \
    -srcfolder "$stage_dir" \
    -ov \
    -format UDZO \
    "$dmg_path"

echo "Created $dmg_path"
