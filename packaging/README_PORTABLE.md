# BDD Studio Portable Release Packaging

This folder adds portable, student-friendly release packaging to BDD Studio.

Goal:

```text
Student downloads one ZIP/TAR.GZ for their operating system
Student unpacks it
Student double-clicks/runs the launcher
BDD Studio opens in the browser
```

The packages are built by GitHub Actions for:

```text
macOS Apple Silicon: BDDStudio-macos-arm64.zip
macOS Intel:         BDDStudio-macos-x64.zip
Windows x64:         BDDStudio-windows-x64.zip
Linux x64:           BDDStudio-linux-x64.tar.gz
```

## Important

Portable packages try to include:

- BDD Studio executable
- Python runtime embedded by PyInstaller
- BDD Studio package code
- examples/
- docs/
- launcher script
- Graphviz `dot` executable and supporting files when possible

Graphviz bundling is platform-specific and can be fragile. The scripts prefer a bundled Graphviz folder, then fall back to system `dot`.

## Commands

Local build:

```bash
python -m pip install -U pip
python -m pip install -e .
python -m pip install pyinstaller
pyinstaller --clean --noconfirm --name bddstudio bddstudio/cli/main.py
python packaging/make_portable_bundle.py --platform macos-arm64
```

GitHub Actions:

```bash
git tag v0.9.0
git push origin v0.9.0
```

The workflow `.github/workflows/portable-release.yml` builds and uploads release artifacts.
