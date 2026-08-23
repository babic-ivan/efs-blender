#!/bin/bash
# Builds EasyFormStudio-<verzija>.dmg from the built (ideally signed) app.
# Upotreba: build_files/utils/make_dmg.sh [putanja/do/EasyFormStudio.app] [izlazni.dmg]
set -euo pipefail

APP="${1:-$HOME/build_darwin/bin/EasyFormStudio.app}"
VERSION="$(defaults read "$(cd "$APP" && pwd)/Contents/Info" CFBundleShortVersionString 2>/dev/null || echo dev)"
OUT="${2:-$HOME/Desktop/EasyFormStudio-${VERSION}.dmg}"
VOLNAME="EasyFormStudio"

STAGE="$(mktemp -d)/dmg"
mkdir -p "$STAGE"
echo "Kopiram app (može potrajati)..."
ditto "$APP" "$STAGE/EasyFormStudio.app"
ln -s /Applications "$STAGE/Applications"

# Ikona volumena = ikona aplikacije
ICNS="$APP/Contents/Resources/blender_icon_legacy.icns"
if [ -f "$ICNS" ]; then
    cp "$ICNS" "$STAGE/.VolumeIcon.icns"
fi

rm -f "$OUT"
hdiutil create -volname "$VOLNAME" -srcfolder "$STAGE" -ov -format UDZO "$OUT"

# postavi custom icon flag na volumen (radi tek nakon mountanja kod korisnika,
# SetFile flag mora biti postavljen unutar image-a)
if [ -f "$STAGE/.VolumeIcon.icns" ]; then
    TMPRW="$(mktemp -d)/rw.dmg"
    hdiutil convert "$OUT" -format UDRW -o "$TMPRW" >/dev/null
    MNT="$(hdiutil attach "$TMPRW" -nobrowse | awk '/\/Volumes\//{print substr($0, index($0,"/Volumes/"))}')"
    SetFile -a C "$MNT" 2>/dev/null || true
    hdiutil detach "$MNT" >/dev/null
    rm -f "$OUT"
    hdiutil convert "$TMPRW" -format UDZO -o "$OUT" >/dev/null
    rm -f "$TMPRW"
fi

echo "GOTOVO: $OUT"
du -sh "$OUT"
