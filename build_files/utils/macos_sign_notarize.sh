#!/bin/bash
# Codesign + notarize EasyFormStudio.app for distribution outside the App Store.
#
# Preduvjeti (jednokratno):
#  1. "Developer ID Application" certifikat:
#     - Keychain Access -> Certificate Assistant -> Request a Certificate From a CA (spremi CSR)
#     - developer.apple.com -> Certificates -> + -> Developer ID Application -> upload CSR
#     - preuzmi .cer i dvoklik (instalira se u Keychain)
#  2. Notarizacijski profil (app-specific lozinka s appleid.apple.com -> Sign-In & Security):
#     xcrun notarytool store-credentials efs-notary \
#         --apple-id "TVOJ_APPLE_ID" --team-id "7N327FKYXM" --password "xxxx-xxxx-xxxx-xxxx"
#
# Upotreba:
#   build_files/utils/macos_sign_notarize.sh [putanja/do/EasyFormStudio.app] ["Developer ID Application: Ivan Babic (TEAMID)"]
set -euo pipefail

APP="${1:-$HOME/build_darwin/bin/EasyFormStudio.app}"
IDENTITY="${2:-$(security find-identity -v -p codesigning | grep -o '"Developer ID Application:[^"]*"' | head -1 | tr -d '"')}"
PROFILE="${NOTARY_PROFILE:-efs-notary}"
ENTITLEMENTS="$(cd "$(dirname "$0")/../.." && pwd)/release/darwin/entitlements.plist"

if [ -z "$IDENTITY" ]; then
    echo "GRESKA: nema 'Developer ID Application' certifikata u Keychainu." >&2
    echo "Kreiraj ga na developer.apple.com (vidi upute na vrhu skripte)." >&2
    exit 1
fi

echo "App:        $APP"
echo "Identitet:  $IDENTITY"
echo "Entitlements: $ENTITLEMENTS"

sign() {
    codesign --force --timestamp --options runtime \
        --entitlements "$ENTITLEMENTS" --sign "$IDENTITY" "$1"
}

echo "== 1/5 Potpis ugnijezdenih binarija =="
# dylib/so unutar Resources (python moduli, wheelovi itd.)
find "$APP/Contents/Resources" -type f \( -name "*.dylib" -o -name "*.so" \) -print0 |
    while IFS= read -r -d '' f; do sign "$f"; done
# python executable
find "$APP/Contents/Resources" -type f -path "*/python/bin/*" -perm +111 -print0 |
    while IFS= read -r -d '' f; do sign "$f"; done

echo "== 2/5 Potpis thumbnailera =="
if [ -d "$APP/Contents/PlugIns/blender-thumbnailer.appex" ]; then
    sign "$APP/Contents/PlugIns/blender-thumbnailer.appex"
fi

echo "== 3/5 Potpis aplikacije =="
sign "$APP"
codesign --verify --deep --strict "$APP"
echo "Potpis OK"

echo "== 4/5 Notarizacija =="
ZIP="$(mktemp -d)/EasyFormStudio.zip"
ditto -c -k --keepParent "$APP" "$ZIP"
xcrun notarytool submit "$ZIP" --keychain-profile "$PROFILE" --wait
rm -f "$ZIP"

echo "== 5/5 Staple =="
xcrun stapler staple "$APP"
spctl --assess --type execute -v "$APP" && echo "GOTOVO: aplikacija je potpisana i notarizirana."
