#!/usr/bin/env python3
"""Make a local, deterministic krilla source-evidence bundle; does not grant rights."""
import argparse
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--crate", required=True, type=Path, help="original krilla 0.8.2 .crate from crates.io")
parser.add_argument("--output", required=True, type=Path, help="new ZIP path outside the repository")
args = parser.parse_args()
out = args.output.resolve()
if out == root or out.is_relative_to(root) or out.exists():
    raise SystemExit("Output must not exist and must be outside the repository")

def digest(data):
    return hashlib.sha256(data).hexdigest()

archive = args.crate.read_bytes()
if digest(archive) != "27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33":
    raise SystemExit("Crate does not match pinned Cargo.lock checksum")
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
    content = tar.extractfile("krilla-0.8.2/src/content.rs").read()
    vcs = json.load(tar.extractfile("krilla-0.8.2/.cargo_vcs_info.json"))
if digest(content) != "9e59b2c77b73b36caedacfe80894d1cce7fd6fe6f7438ea24fda2019391a980c":
    raise SystemExit("Unexpected krilla content source")
if vcs.get("git", {}).get("sha1") != "3ffdf0588cf98050aad6edba51ca70162e1fb5b5":
    raise SystemExit("Unexpected krilla source revision")
upstream = root / "Notices" / "Upstream" / "krilla"
names = ("NOTICE.md", "LICENSE_APACHE", "LICENSE_MIT", "MPL-2.0-reference.txt")
upstream_manifest = json.loads((root / "Notices" / "Upstream" / "manifest.json").read_text())
files = {"krilla-0.8.2.crate": archive}
for name in names:
    data = (upstream / name).read_bytes()
    if digest(data) != upstream_manifest["Upstream/krilla/" + name]["sha256"]:
        raise SystemExit(f"Modified krilla notice or license: {name}")
    files["notices/" + name] = data
manifest = {"format": 1, "status": "review only; no legal or release approval",
            "crateVersion": "0.8.2", "crateSource": "https://static.crates.io/crates/krilla/krilla-0.8.2.crate",
            "sourceRevision": vcs["git"]["sha1"], "contentRsSHA256": digest(content),
            "files": {name: digest(data) for name, data in sorted(files.items())}}
files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
files["README.txt"] = ("Experimental source-evidence bundle. The original crates.io archive is unmodified.\n"
                       "The applicability of the resvg/MPL notice and the obligations for distribution remain under review.\n"
                       "This archive is not a source offer, a legal determination, or a release approval.\n").encode()
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name, data in sorted(files.items()):
        entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
        z.writestr(entry, data)
print(f"Prepared review-only evidence: {out}")
print(f"SHA-256: {digest(out.read_bytes())}")
