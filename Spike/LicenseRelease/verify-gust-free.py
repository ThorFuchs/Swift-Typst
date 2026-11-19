#!/usr/bin/env python3
"""Check exact known font bytes and features in one experimental archive.

This is evidence for the specified build, not proof of legal clearance or
absence of transformed/compressed font material.
"""
import argparse
import hashlib
import json
import mmap
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--candidate", required=True, type=Path)
parser.add_argument("--archive", required=True, type=Path)
parser.add_argument("--assets-dir", required=True, type=Path, help="typst-assets-0.15.1 Cargo source directory")
parser.add_argument("--rust-target", default="aarch64-apple-darwin")
args = parser.parse_args()
manifest = json.loads((root / "Rust/fonts/manifest.json").read_text())
old = [root / "Rust/fonts" / e["file"] for e in manifest["fonts"] if e["file"].startswith("NewCM")]
old.append(args.assets_dir / "files/fonts/NewCM10-Regular.otf")
if len(old) != 8 or any(not path.is_file() for path in old):
    raise SystemExit("Expected all eight original font files for comparison")
font_dir = args.candidate / "Rust/fonts"
new_manifest = json.loads((font_dir / "manifest.json").read_text())
names = [entry["file"] for entry in new_manifest["fonts"]]
if len(names) != len(set(names)):
    raise SystemExit("Duplicate candidate font entries")
actual = {path.name for path in font_dir.iterdir() if path.suffix in (".otf", ".ttf")}
if actual != set(names):
    raise SystemExit("Candidate font files differ from its manifest")
if any(name.startswith("NewCM") for name in names):
    raise SystemExit("NewCM remains in candidate manifest")
new = [font_dir / e["file"] for e in new_manifest["fonts"] if e["file"].startswith("STIX")]
if len(new) != 5 or any(not path.is_file() for path in new):
    raise SystemExit("Expected five STIX faces")
for entry in new_manifest["fonts"]:
    path = font_dir / entry["file"]
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        raise SystemExit(f"Candidate font checksum mismatch: {path.name}")
tree = subprocess.check_output(["cargo", "tree", "--manifest-path", str(args.candidate / "Rust/Cargo.toml"),
                                "--locked", "--offline", "--target", args.rust_target,
                                "-i", "typst-assets", "-e", "features"], text=True)
if 'typst-assets feature "fonts"' in tree:
    raise SystemExit("Upstream bundled fonts feature is enabled")
with args.archive.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
    for path in old:
        if data.find(path.read_bytes()) >= 0:
            raise SystemExit(f"Excluded original font found: {path.name}")
        print(f"absent: {path.name}")
    for path in new:
        if data.find(path.read_bytes()) < 0:
            raise SystemExit(f"Expected STIX face not found: {path.name}")
        print(f"present: {path.name}")
print("typst-assets/fonts disabled; exact-byte evidence only; not release clearance")
