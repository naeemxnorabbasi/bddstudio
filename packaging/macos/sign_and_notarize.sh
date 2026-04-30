#!/bin/bash
set -euo pipefail

# Sign and notarize a macOS portable BDD Studio ZIP.
#
# Requirements:
#   Apple Developer Program membership
#   Developer ID Application certificate installed in Keychain
#   App-specific password or App Store Connect API key
#
# Environment variables:
#   APPLE_TEAM_ID
#   APPLE_ID
#   APPLE_APP_PASSWORD
#   DEVELOPER_ID_APP
#
# Example:
#   export APPLE_TEAM_ID="ABCDE12345"
#   export APPLE_ID="your.name@example.edu"
#   export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
#   export DEVELOPER_ID_APP="Developer ID Application: Your Name (ABCDE12345)"
#   packaging/macos/sign_and_notarize.sh release/BDDStudio-macos-arm64.zip

ZIP_PATH="${1:?Usage: sign_and_notarize.sh path/to/BDDStudio-macos-arm64.zip}"

if [ -z "${APPLE_TEAM_ID:-}" ] || [ -z "${APPLE_ID:-}" ] || [ -z "${APPLE_APP_PASSWORD:-}" ] || [ -z "${DEVELOPER_ID_APP:-}" ]; then
  echo "Missing required environment variables."
  echo "Set APPLE_TEAM_ID, APPLE_ID, APPLE_APP_PASSWORD, and DEVELOPER_ID_APP."
  exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

unzip -q "$ZIP_PATH" -d "$WORK"
APP_DIR="$(find "$WORK" -maxdepth 1 -type d -name 'BDDStudio-*' | head -n 1)"

echo "Signing files in $APP_DIR"

# Sign binaries, dylibs, and command launchers.
find "$APP_DIR" -type f \( -perm -111 -o -name "*.dylib" -o -name "*.so" -o -name "*.command" \) -print0 |
while IFS= read -r -d '' f; do
  codesign --force --timestamp --options runtime --sign "$DEVELOPER_ID_APP" "$f" || true
done

# Sign the main folder contents deeply as a fallback.
codesign --force --deep --timestamp --options runtime --sign "$DEVELOPER_ID_APP" "$APP_DIR" || true

SIGNED_ZIP="${ZIP_PATH%.zip}-signed.zip"
ditto -c -k --keepParent "$APP_DIR" "$SIGNED_ZIP"

echo "Submitting for notarization..."
xcrun notarytool submit "$SIGNED_ZIP" \
  --apple-id "$APPLE_ID" \
  --password "$APPLE_APP_PASSWORD" \
  --team-id "$APPLE_TEAM_ID" \
  --wait

echo "Notarization complete."
echo "Signed/notarized ZIP: $SIGNED_ZIP"

# Stapling applies best to .app/.pkg/.dmg. Portable ZIPs do not always support stapling.
echo "Note: For the smoothest macOS experience, consider packaging as a .app inside a .dmg and stapling the .dmg."
