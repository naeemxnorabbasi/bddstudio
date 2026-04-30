# Linux Signing Notes

Linux desktop distribution does not have one universal signing/notarization system like macOS Gatekeeper or Windows SmartScreen.

Common options:

1. Publish SHA256 checksums.
2. Sign release archives with GPG.
3. Use AppImage and optionally sign the AppImage.
4. Publish `.deb` packages in an APT repository signed with a GPG key.
5. Publish Flatpak packages through Flathub.

For a class project, the practical first step is:

```bash
shasum -a 256 BDDStudio-linux-x64.tar.gz > BDDStudio-linux-x64.tar.gz.sha256
gpg --armor --detach-sign BDDStudio-linux-x64.tar.gz
```

Then upload:

```text
BDDStudio-linux-x64.tar.gz
BDDStudio-linux-x64.tar.gz.sha256
BDDStudio-linux-x64.tar.gz.asc
```

Students can verify:

```bash
shasum -a 256 -c BDDStudio-linux-x64.tar.gz.sha256
gpg --verify BDDStudio-linux-x64.tar.gz.asc BDDStudio-linux-x64.tar.gz
```
