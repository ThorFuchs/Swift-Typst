#!/usr/bin/env python3
"""Add one Rust-built static-library variant to the local SwiftPM bundle."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from krilla_source import verify_krilla_source

root = Path(__file__).resolve().parent.parent
verify_krilla_source(root)
parser = argparse.ArgumentParser()
parser.add_argument("triple")
parser.add_argument("archive", type=Path)
parser.add_argument("--rust-target", required=True)
parser.add_argument("--rust-version", required=True)
parser.add_argument("--profile", required=True)
args = parser.parse_args()
if not args.archive.is_file():
    raise SystemExit(f"archive does not exist: {args.archive}")
if not args.triple or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-.+" for c in args.triple):
    raise SystemExit("invalid target triple")

def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()

source_paths = [root / "LICENSE", root / "Rust" / "Cargo.toml", root / "Rust" / "Cargo.lock"]
source_paths += sorted((root / "Rust" / "src").rglob("*.rs"))
source_paths += sorted((root / "Rust" / "fonts").rglob("*"))
vendor = root / "Rust" / "vendor"
vendor_paths = sorted(vendor.rglob("*"))
if vendor.is_symlink() or any(path.is_symlink() for path in vendor_paths):
    raise SystemExit("Symlinks are not allowed in Rust/vendor")
source_paths += vendor_paths
source_paths += sorted((root / "Sources" / "CTypstBridge" / "include").iterdir())
source_paths += sorted((root / "Notices").rglob("*"))
sources = {str(p.relative_to(root)): digest(p) for p in source_paths if p.is_file()}

bundle = root / "Artifacts" / "CTypstBridge.artifactbundle"
provenance_path = bundle / "provenance.json"
provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
for triple, previous in provenance.items():
    if triple != args.triple and (previous.get("sources") != sources
            or previous.get("rustVersion") != args.rust_version
            or previous.get("profile") != args.profile):
        raise SystemExit(f"{triple} was built with different sources, toolchain, or profile; rebuild the bundle")
include = bundle / "include"
variant = bundle / "lib" / args.triple
include.mkdir(parents=True, exist_ok=True)
variant.mkdir(parents=True, exist_ok=True)
for name in ("module.modulemap", "typst_bridge.h"):
    shutil.copy2(root / "Sources" / "CTypstBridge" / "include" / name, include / name)
shutil.copy2(root / "Notices" / "typst-assets-0.15.1-NOTICE.txt", bundle / "typst-assets-NOTICE.txt")
shutil.copy2(root / "LICENSE", bundle / "LICENSE")
shutil.copytree(root / "Notices", bundle / "notices", dirs_exist_ok=True)
dest = variant / "libswift_typst_bridge.a"
if args.archive.resolve() != dest.resolve():
    shutil.copy2(args.archive, dest)

info_path = bundle / "info.json"
if info_path.exists():
    info = json.loads(info_path.read_text())
else:
    info = {"schemaVersion": "1.0", "artifacts": {
        "CTypstBridge": {"type": "staticLibrary", "version": "0.1.0", "variants": []}
    }}
variants = info["artifacts"]["CTypstBridge"]["variants"]
variants[:] = [item for item in variants if args.triple not in item["supportedTriples"]]
variants.append({
    "path": f"lib/{args.triple}/{dest.name}",
    "supportedTriples": [args.triple],
    "staticLibraryMetadata": {"headerPaths": ["include"], "moduleMapPath": "include/module.modulemap"},
})
variants.sort(key=lambda item: item["supportedTriples"][0])
info_path.write_text(json.dumps(info, indent=2) + "\n")

provenance[args.triple] = {
    "typst": "0.15.1", "rustTarget": args.rust_target, "rustVersion": args.rust_version,
    "profile": args.profile, "cargoLockSHA256": digest(root / "Rust" / "Cargo.lock"),
    "archiveSHA256": digest(dest), "sources": sources,
}
provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
print(f"Added {args.triple}: {dest}")
