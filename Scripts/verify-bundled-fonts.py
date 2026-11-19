#!/usr/bin/env python3
"""Verify pinned fonts, feature selection, and known excluded bytes in one archive."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from font_archive import verify_font_bytes

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--rust-target", required=True)
parser.add_argument("--archive", type=Path)
parser.add_argument("--excluded-book", type=Path, default=os.environ.get("SWIFT_TYPST_EXCLUDED_BOOK_FONT"),
                    help="optional original NewCM10-Book 8.1.1 file for an additional exact-byte scan")
args = parser.parse_args()
font_dir = root / "Rust/fonts"
manifest = json.loads((font_dir / "manifest.json").read_text())
entries = manifest["fonts"]
names = [e["file"] for e in entries]
stix = {"STIXTwoMath-Regular.otf", "STIXTwoText-Regular.otf", "STIXTwoText-Italic.otf",
        "STIXTwoText-Bold.otf", "STIXTwoText-BoldItalic.otf"}
if len(names) != len(set(names)) or len(names) != 15 or not stix <= set(names) or any(n.startswith("NewCM") for n in names):
    raise SystemExit("Unexpected curated font set")
actual = {p.name for p in font_dir.iterdir() if p.suffix in (".otf", ".ttf")}
if actual != set(names):
    raise SystemExit("Font files differ from manifest")
for entry in entries:
    path = font_dir / entry["file"]
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        raise SystemExit(f"Font checksum mismatch: {entry['file']}")
world = (root / "Rust/src/world.rs").read_text()
embedded = re.findall(r'include_bytes!\("\.\./fonts/([^\"]+)"\)', world)
if embedded != names:
    raise SystemExit("Embedded font order differs from manifest")
tree = subprocess.run(["cargo", "tree", "--manifest-path", str(root / "Rust/Cargo.toml"), "--locked",
                       "--target", args.rust_target, "-i", "typst-assets", "-e", "features"],
                      check=True, capture_output=True, text=True).stdout
if 'typst-assets feature "fonts"' in tree:
    raise SystemExit("typst-assets/fonts is enabled and includes excluded fonts")
if args.archive:
    metadata = json.loads(subprocess.run(["cargo", "metadata", "--manifest-path", str(root / "Rust/Cargo.toml"),
                                          "--locked", "--format-version", "1"], check=True,
                                         capture_output=True, text=True).stdout)
    assets = [p for p in metadata["packages"] if p["name"] == "typst-assets" and p["version"] == "0.15.1"]
    if len(assets) != 1:
        raise SystemExit("Could not identify the exact typst-assets source")
    upstream = Path(assets[0]["manifest_path"]).parent / "files/fonts"
    excluded = {
        "NewCMMath-Bold.otf": "c6c0e060da57d4f44274705afb956013047231dc62be5a4b02a351ab0dc43f2f",
        "NewCMMath-Book.otf": "2ea09ebc9167b1e1a66f31390dc917f2d4004ecfca72d51b28010e4ad6becd95",
        "NewCMMath-Regular.otf": "d66ac1cc91c55c24d3636ae2df1238076debdff51841f9893fc5419cc2df3df7",
        "NewCM10-Bold.otf": "40b0b32b63655fe802679ee4a14adb29c762a4712095d9c84cf7df7852b5152e",
        "NewCM10-Italic.otf": "a55d07607eec48889b6e7e7d51d7703c3beb915a39690f34fe01b4e2a744a9d6",
        "NewCM10-BoldItalic.otf": "fb53f43500c8ffbcc6dfdea5a519961d475543174ea2a0dcbe16c08510299fdf",
        "NewCM10-Regular.otf": "328698d764ccdf7acf6bc1088aefd83a237f6a1d8b812de1e77ac5e4483bf3d1",
    }
    references = [(upstream / name, digest) for name, digest in excluded.items()]
    if args.excluded_book:
        references.append((Path(args.excluded_book), "005f9b4e13b2a133df36d4ebfbb8f5fe402854bcb5882deb500b9c0f72b1bb49"))
    reference_bytes = {}
    for path, expected in references:
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit(f"Excluded font reference checksum mismatch: {path.name}")
        reference_bytes[path.name] = data
    try:
        verify_font_bytes(args.archive, reference_bytes,
                          {name: (font_dir / name).read_bytes() for name in sorted(stix)})
    except ValueError as error:
        raise SystemExit(str(error))
    print(f"Verified curated fonts and {len(references)} excluded references: {args.rust_target}")
    if not args.excluded_book:
        print("Note: exact NewCM10-Book scan skipped; provide --excluded-book for that additional check")
else:
    print(f"Verified curated font sources: {args.rust_target}")
