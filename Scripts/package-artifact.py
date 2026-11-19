#!/usr/bin/env python3
"""Validate and package a locally built SwiftPM artifact deterministically."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from krilla_source import verify_krilla_source

root = Path(__file__).resolve().parent.parent
verify_krilla_source(root)
parser = argparse.ArgumentParser()
parser.add_argument("output", type=Path, help="output .zip path")
parser.add_argument("--require", action="append", default=[], metavar="TRIPLE")
parser.add_argument("--bundle", type=Path, default=root / "Artifacts" / "CTypstBridge.artifactbundle")
args = parser.parse_args()
bundle = args.bundle.resolve()
if bundle.name != "CTypstBridge.artifactbundle":
    raise SystemExit("Bundle must be named CTypstBridge.artifactbundle")


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


info = json.loads((bundle / "info.json").read_text())
variants = info["artifacts"]["CTypstBridge"]["variants"]
provenance = json.loads((bundle / "provenance.json").read_text())
triples = {v["supportedTriples"][0] for v in variants}
if triples != set(provenance) or len(triples) != len(variants):
    raise SystemExit("Artifact metadata and provenance do not agree")
if missing := set(args.require) - triples:
    raise SystemExit(f"Missing required variants: {', '.join(sorted(missing))}")
if not triples:
    raise SystemExit("No variants to package")
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
expected_sources = {str(p.relative_to(root)): digest(p) for p in source_paths if p.is_file()}
baseline = None
for variant in variants:
    triple = variant["supportedTriples"][0]
    record = provenance[triple]
    if variant["path"] != f"lib/{triple}/libswift_typst_bridge.a" or variant.get("staticLibraryMetadata") != {"headerPaths": ["include"], "moduleMapPath": "include/module.modulemap"}:
        raise SystemExit(f"Unexpected artifact metadata: {triple}")
    archive = (bundle / variant["path"]).resolve()
    if not archive.is_relative_to(bundle.resolve()) or digest(archive) != record["archiveSHA256"]:
        raise SystemExit(f"Archive checksum mismatch: {triple}")
    if record["sources"] != expected_sources or record["cargoLockSHA256"] != expected_sources["Rust/Cargo.lock"]:
        raise SystemExit(f"Sources or lockfile changed since {triple} was built")
    identity = (record["rustVersion"], record["profile"], record["typst"])
    if baseline is None:
        baseline = identity
    elif baseline != identity:
        raise SystemExit("Toolchain, profile or Typst version differs between variants")
for header in ("module.modulemap", "typst_bridge.h"):
    if digest(bundle / "include" / header) != digest(root / "Sources" / "CTypstBridge" / "include" / header):
        raise SystemExit(f"Artifact header differs from source: {header}")
if digest(bundle / "typst-assets-NOTICE.txt") != digest(root / "Notices" / "typst-assets-0.15.1-NOTICE.txt"):
    raise SystemExit("Bundled font notice differs from source")
if digest(bundle / "LICENSE") != digest(root / "LICENSE"):
    raise SystemExit("Bundled project license differs from source")
notice_root = root / "Notices"
notice_bundle = bundle / "notices"
expected_notices = {p.relative_to(notice_root) for p in notice_root.rglob("*") if p.is_file()}
actual_notices = {p.relative_to(notice_bundle) for p in notice_bundle.rglob("*") if p.is_file()}
if actual_notices != expected_notices or any(digest(notice_root / p) != digest(notice_bundle / p) for p in expected_notices):
    raise SystemExit("Bundled license evidence is missing, extra or modified")

args.output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    for path in sorted(bundle.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"Symlink not allowed: {path}")
        if not path.is_file():
            continue
        entry = zipfile.ZipInfo(str(Path(bundle.name) / path.relative_to(bundle)), (1980, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
        with path.open("rb") as source, output.open(entry, "w", force_zip64=True) as dest:
            shutil.copyfileobj(source, dest, 1024 * 1024)
print(f"Packaged {', '.join(sorted(triples))}: {args.output}")
print(f"SwiftPM checksum: {digest(args.output)}")
