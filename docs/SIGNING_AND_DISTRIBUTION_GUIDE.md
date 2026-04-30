# BDD Studio Signing and Distribution Guide

This guide explains how to create student-friendly packages and how code signing works on macOS, Windows, and Linux.

## Goal

Students should be able to do this:

```text
Download package for their OS
Unzip or extract
Double-click launcher
Browser opens BDD Studio
```

No Python install. No pip. No Homebrew. No separate Graphviz install.

## Recommended Release Artifacts

Publish these files on each GitHub release:

```text
BDDStudio-macos-arm64.zip
BDDStudio-macos-x64.zip
BDDStudio-windows-x64.zip
BDDStudio-linux-x64.tar.gz
SHA256SUMS.txt
```

Optional signed artifacts:

```text
BDDStudio-macos-arm64-signed.zip
BDDStudio-macos-x64-signed.zip
BDDStudio-windows-x64-signed.zip
BDDStudio-linux-x64.tar.gz.asc
```

## Packaging Technology

BDD Studio is Python-based, so the recommended first packaging method is:

```text
PyInstaller onedir
```

Why `onedir` instead of `onefile`?

`onedir` creates a folder containing the executable and all required Python runtime files. This is more reliable when bundling Graphviz. Students still download a single ZIP, so the user experience is simple.

## Graphviz Bundling

Graphviz is more than the `dot` executable. It often needs libraries and plugins.

The portable packaging scripts try to include Graphviz automatically. If rendering fails in a portable package, the likely cause is missing Graphviz libraries or plugins.

BDD Studio should look for Graphviz in this order:

```text
1. BDDSTUDIO_DOT environment variable
2. local portable bundle path: ./graphviz/bin/dot or ./graphviz/bin/dot.exe
3. system PATH: dot
```

## macOS Signing and Notarization

For the smoothest macOS experience, you need:

1. Apple Developer Program membership.
2. Developer ID Application certificate.
3. App-specific password or App Store Connect API key.
4. `codesign` and `xcrun notarytool` from Xcode command-line tools.

### Get a Developer ID Application Certificate

In Apple Developer account:

```text
Certificates, Identifiers & Profiles
Create Certificate
Developer ID Application
Download and install in Keychain
```

Find certificate name:

```bash
security find-identity -v -p codesigning
```

It looks like:

```text
Developer ID Application: Your Name (TEAMID)
```

### Notarization Credentials

Create an app-specific password for your Apple ID, or use an App Store Connect API key.

For app-specific password flow:

```bash
export APPLE_TEAM_ID="YOURTEAMID"
export APPLE_ID="your.email@example.edu"
export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export DEVELOPER_ID_APP="Developer ID Application: Your Name (YOURTEAMID)"
```

Then:

```bash
packaging/macos/sign_and_notarize.sh release/BDDStudio-macos-arm64.zip
```

### Best macOS User Experience

The best macOS package is eventually:

```text
BDD Studio.app inside BDDStudio.dmg
```

Then sign and notarize the `.app` and staple the `.dmg`.

Portable ZIPs are acceptable for classroom distribution, but macOS Gatekeeper may still warn. Students may need:

```text
Right-click → Open
```

or:

```bash
xattr -dr com.apple.quarantine BDDStudio-macos-arm64
```

## Windows Code Signing

For Windows, you need a code-signing certificate.

Options:

```text
OV certificate: cheaper, SmartScreen reputation builds over time
EV certificate: more expensive, better SmartScreen reputation
```

You usually buy from a certificate authority such as DigiCert, Sectigo, GlobalSign, SSL.com, etc.

Signing uses Microsoft SignTool from the Windows SDK.

Example with a `.pfx` certificate:

```powershell
powershell -ExecutionPolicy Bypass -File packaging/windows/sign_windows.ps1 `
  -BundleDir release/BDDStudio-windows-x64 `
  -CertPath C:\certs\codesign.pfx `
  -CertPassword "YOUR_PASSWORD"
```

Then ZIP the signed folder.

### Windows SmartScreen

Even signed apps may show warnings at first. SmartScreen reputation improves as more users download and run the signed application.

EV certificates usually reduce friction more than OV certificates.

## Linux Signing

Linux has no single universal app-signing system.

Recommended first approach:

```bash
shasum -a 256 BDDStudio-linux-x64.tar.gz > BDDStudio-linux-x64.tar.gz.sha256
gpg --armor --detach-sign BDDStudio-linux-x64.tar.gz
```

Upload:

```text
BDDStudio-linux-x64.tar.gz
BDDStudio-linux-x64.tar.gz.sha256
BDDStudio-linux-x64.tar.gz.asc
```

Later options:

```text
AppImage
Flatpak
.deb package
APT repository
```

## GitHub Actions Secrets

For automated signing, store secrets in:

```text
GitHub repo → Settings → Secrets and variables → Actions
```

Suggested secrets:

### macOS

```text
APPLE_TEAM_ID
APPLE_ID
APPLE_APP_PASSWORD
DEVELOPER_ID_APP
MACOS_CERTIFICATE_P12_BASE64
MACOS_CERTIFICATE_PASSWORD
```

### Windows

```text
WINDOWS_CERT_PFX_BASE64
WINDOWS_CERT_PASSWORD
```

Be careful with certificate secrets. Use protected release workflows and limit who can trigger releases.

## Recommended Roadmap

### Phase 1

- Portable unsigned ZIP/TAR.GZ bundles
- GitHub release assets
- SHA256 checksums

### Phase 2

- macOS signed and notarized `.app`/`.dmg`
- Windows signed `.exe`/ZIP
- Linux GPG-signed archives

### Phase 3

- Native installers:
  - macOS `.dmg`
  - Windows `.msi` or Inno Setup installer
  - Linux AppImage or Flatpak

## Student Instructions for Unsigned Packages

### macOS

If blocked:

```text
Right-click BDD Studio.command
Choose Open
Confirm Open
```

### Windows

If SmartScreen appears:

```text
More info
Run anyway
```

### Linux

```bash
chmod +x run-bddstudio.sh
./run-bddstudio.sh
```
