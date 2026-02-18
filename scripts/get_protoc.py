#!/usr/bin/env python3
"""Download and extract protoc from GitHub releases.

Usage examples:
  python scripts/get_protoc.py                # uses default v33.5 and ./protoc
  python scripts/get_protoc.py --version 33.5 --outdir ./protoc

The script picks an asset appropriate to your OS (win64, linux-x86_64, osx-x86_64, osx-aarch_64)
and extracts the archive into the output directory. On success the protoc binary will be at
`<outdir>/bin/protoc` (or `protoc.exe` on Windows).
"""

import argparse
import platform
import shutil
import stat
import sys
import tempfile
import urllib.request
from pathlib import Path
import zipfile
import tarfile


def choose_filename(version: str) -> str:
    system = platform.system()
    machine = platform.machine().lower()
    ver = version.lstrip("v")
    if system == "Windows":
        return f"protoc-{ver}-win64.zip"
    if system == "Linux":
        return f"protoc-{ver}-linux-x86_64.zip"
    if system == "Darwin":
        # macOS: choose arm64 vs x86_64
        if machine in ("arm64", "aarch64"):
            return f"protoc-{ver}-osx-aarch_64.zip"
        return f"protoc-{ver}-osx-x86_64.zip"
    # fallback
    return f"protoc-{ver}-linux-x86_64.zip"


def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {dest}")
    with urllib.request.urlopen(url) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} when downloading {url}")
        # stream to file
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)


def try_extract(archive: Path, outdir: Path):
    print(f"Extracting {archive} -> {outdir}")
    outdir.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive, "r") as z:
            z.extractall(outdir)
    else:
        # try tar
        try:
            with tarfile.open(archive, "r:*") as t:
                t.extractall(outdir)
        except tarfile.ReadError:
            raise RuntimeError("Unknown archive format: {archive}")


def make_executable(path: Path):
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass


def main():
    p = argparse.ArgumentParser(
        description="Download protoc from GitHub releases and extract locally."
    )
    p.add_argument(
        "--version",
        default="33.5",
        help="protoc version (e.g. 33.5). Tag used is v<version>.",
    )
    p.add_argument(
        "--outdir", default="./protoc", help="output directory to extract into"
    )
    p.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="re-download and overwrite existing",
    )
    args = p.parse_args()

    tag = f"v{args.version.lstrip('v')}"
    filename = choose_filename(version=tag)
    base = f"https://github.com/protocolbuffers/protobuf/releases/download/{tag}"
    url = f"{base}/{filename}"

    outdir = Path(args.outdir).resolve()
    bin_path = outdir / "bin"
    protoc_path = bin_path / (
        "protoc.exe" if platform.system() == "Windows" else "protoc"
    )

    if protoc_path.exists() and not args.force:
        print(f"protoc already present at {protoc_path}")
        print("Use --force to re-download")
        return 0

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        archive = td / filename
        try:
            download(url=url, dest=archive)
        except Exception as e:
            print(f"Download failed: {e}")
            print("Checked URL:", url)
            sys.exit(2)

        try:
            try_extract(archive=archive, outdir=outdir)
        except Exception as e:
            print(f"Extraction failed: {e}")
            sys.exit(3)

    # ensure protoc is executable
    if protoc_path.exists():
        make_executable(protoc_path)
        print(f"protoc available at: {protoc_path}")
        print(
            "You can add it to PATH, e.g. `export PATH=$PWD/protoc/bin:$PATH` (or on Windows, add to PATH)"
        )
        return 0
    else:
        print(
            f"Extraction completed but protoc not found at expected location {protoc_path}"
        )
        print("List extracted files:")
        for pth in sorted(outdir.rglob("*")):
            print(pth.relative_to(outdir))
        sys.exit(4)


if __name__ == "__main__":
    raise SystemExit(main())
