#!/usr/bin/env python3
"""
Create a portable BDD Studio release bundle after PyInstaller has built the executable.

Expected inputs:
  dist/bddstudio                 on macOS/Linux when PyInstaller --onedir is used
  dist/bddstudio/bddstudio       on macOS/Linux
  dist/bddstudio/bddstudio.exe   on Windows
  examples/
  docs/

Usage:
  python packaging/make_portable_bundle.py --platform macos-arm64
  python packaging/make_portable_bundle.py --platform windows-x64
  python packaging/make_portable_bundle.py --platform linux-x64

This script intentionally avoids hard-coding one Graphviz layout. It searches common
installation locations and copies a best-effort Graphviz folder into the bundle.
"""

from __future__ import annotations

import argparse
import os
import platform as py_platform
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)


def copy_file(src: Path, dst: Path, executable: bool = False) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if executable:
        dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def find_dot() -> Path | None:
    env = os.environ.get("BDDSTUDIO_DOT")
    if env and Path(env).exists():
        return Path(env)
    dot = shutil.which("dot")
    if dot:
        return Path(dot)
    return None


def bundle_graphviz(bundle_dir: Path) -> None:
    """Best-effort Graphviz bundling.

    Notes:
    - Windows official Graphviz installer commonly places everything under Graphviz/bin.
    - macOS Homebrew layouts differ for Apple Silicon and Intel.
    - Linux distro Graphviz often has many shared-library dependencies; bundling is best-effort.
    """
    dot = find_dot()
    gv_dir = bundle_dir / "graphviz"
    if not dot:
        print("WARNING: Graphviz dot not found. Bundle will rely on system Graphviz.")
        return

    print(f"Found dot: {dot}")

    if sys.platform.startswith("win"):
        bin_dir = dot.parent
        target_bin = gv_dir / "bin"
        target_bin.mkdir(parents=True, exist_ok=True)
        for item in bin_dir.iterdir():
            if item.is_file() and item.suffix.lower() in {".exe", ".dll"}:
                shutil.copy2(item, target_bin / item.name)
        return

    if sys.platform == "darwin":
        # Homebrew: /opt/homebrew/bin/dot -> ../Cellar/graphviz/VERSION/bin/dot or symlink
        real_dot = dot.resolve()
        graphviz_root = real_dot.parent.parent
        if (graphviz_root / "bin" / "dot").exists():
            copytree(graphviz_root, gv_dir)
            return
        target_bin = gv_dir / "bin"
        target_bin.mkdir(parents=True, exist_ok=True)
        shutil.copy2(real_dot, target_bin / "dot")
        os.chmod(target_bin / "dot", 0o755)
        print("WARNING: Copied only dot executable. If rendering fails, install Graphviz or improve bundling.")
        return

    # Linux
    target_bin = gv_dir / "bin"
    target_bin.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dot, target_bin / "dot")
    os.chmod(target_bin / "dot", 0o755)

    # Best-effort copy of Graphviz plugin directory if present
    for candidate in [
        Path("/usr/lib/graphviz"),
        Path("/usr/lib/x86_64-linux-gnu/graphviz"),
        Path("/usr/local/lib/graphviz"),
    ]:
        if candidate.exists():
            copytree(candidate, gv_dir / "lib" / "graphviz")
            break

    print("WARNING: Linux Graphviz bundling is best-effort. Test on a clean machine.")


def copy_common(bundle_dir: Path) -> None:
    if (ROOT / "examples").exists():
        copytree(ROOT / "examples", bundle_dir / "examples")
    if (ROOT / "docs").exists():
        copytree(ROOT / "docs", bundle_dir / "docs")
    if (ROOT / "README.md").exists():
        copy_file(ROOT / "README.md", bundle_dir / "README.md")
    if (ROOT / "LICENSE").exists():
        copy_file(ROOT / "LICENSE", bundle_dir / "LICENSE")
    copy_file(ROOT / "packaging" / "README_FIRST.txt", bundle_dir / "README_FIRST.txt")


def copy_pyinstaller_dist(bundle_dir: Path) -> None:
    dist_dir = ROOT / "dist" / "bddstudio"
    single_macos_linux = ROOT / "dist" / "bddstudio"
    single_windows = ROOT / "dist" / "bddstudio.exe"

    if dist_dir.exists() and dist_dir.is_dir():
        # onedir mode
        copytree(dist_dir, bundle_dir / "bddstudio")
        return

    if single_windows.exists():
        copy_file(single_windows, bundle_dir / "bddstudio.exe", executable=True)
        return

    if single_macos_linux.exists() and single_macos_linux.is_file():
        copy_file(single_macos_linux, bundle_dir / "bddstudio", executable=True)
        return

    raise FileNotFoundError(
        "Could not find PyInstaller output. Run one of:\n"
        "  pyinstaller --clean --noconfirm --name bddstudio bddstudio/cli/main.py\n"
        "  pyinstaller --clean --noconfirm --onefile --name bddstudio bddstudio/cli/main.py"
    )


def add_launcher(bundle_dir: Path, target_platform: str) -> None:
    if target_platform.startswith("macos"):
        copy_file(ROOT / "packaging" / "macos" / "BDD Studio.command",
                  bundle_dir / "BDD Studio.command",
                  executable=True)
    elif target_platform.startswith("windows"):
        copy_file(ROOT / "packaging" / "windows" / "BDD Studio.bat",
                  bundle_dir / "BDD Studio.bat")
    elif target_platform.startswith("linux"):
        copy_file(ROOT / "packaging" / "linux" / "run-bddstudio.sh",
                  bundle_dir / "run-bddstudio.sh",
                  executable=True)
    else:
        raise ValueError(f"unknown platform: {target_platform}")


def zip_dir(src: Path, out: Path) -> None:
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            z.write(p, p.relative_to(src.parent))


def tar_dir(src: Path, out: Path) -> None:
    if out.exists():
        out.unlink()
    with tarfile.open(out, "w:gz") as t:
        t.add(src, arcname=src.name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", required=True,
                    choices=["macos-arm64", "macos-x64", "windows-x64", "linux-x64"])
    ap.add_argument("--skip-graphviz", action="store_true")
    args = ap.parse_args()

    RELEASE.mkdir(exist_ok=True)
    bundle_name = f"BDDStudio-{args.platform}"
    bundle_dir = RELEASE / bundle_name

    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)

    copy_pyinstaller_dist(bundle_dir)
    copy_common(bundle_dir)
    add_launcher(bundle_dir, args.platform)
    if not args.skip_graphviz:
        bundle_graphviz(bundle_dir)

    if args.platform.startswith("linux"):
        archive = RELEASE / f"{bundle_name}.tar.gz"
        tar_dir(bundle_dir, archive)
    else:
        archive = RELEASE / f"{bundle_name}.zip"
        zip_dir(bundle_dir, archive)

    print(f"Created: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
