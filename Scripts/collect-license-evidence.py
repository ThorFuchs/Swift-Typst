#!/usr/bin/env python3
"""Collect Cargo license evidence deterministically; this is not legal approval.

Input: cargo metadata --locked --format-version 1 on stdin.
Output: Notices/Rust/{inventory.json,texts/<sha256>}; --check compares files.
The graph deliberately includes build and target dependencies as a superset.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from license_paths import inventory_source

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
metadata = json.load(sys.stdin)
up = ROOT / "Notices/Upstream"
manifest = json.loads((up / "manifest.json").read_text())
actual_upstream = {"Upstream/" + str(p.relative_to(up)) for p in up.rglob("*")
                   if p.is_file() and p.name != "manifest.json"}
if actual_upstream != set(manifest):
    raise SystemExit("Upstream license evidence and provenance manifest differ")
for name, record in manifest.items():
    file = ROOT / "Notices" / name
    if file.is_symlink() or hashlib.sha256(file.read_bytes()).hexdigest() != record["sha256"]:
        raise SystemExit(f"Upstream license evidence checksum mismatch: {name}")
supplemental = {
    "LPPL-1.3c.txt": "c1ae6e179a6d28bbd5c483fbacc744acc75e922d598281dc3390aab26126e163",
    "NewComputerModern-8.1.1-License.txt": "8641346ee391ff97eb66c70f3d5d695792cf9c5b3c5d748c6158d49cf79646e3",
    "STIX-Two-OFL.txt": "0c8825913b60d858aacdb33c4ca6660a7d64b0d6464702efbb19313f5765861a",
}
for name, expected in supplemental.items():
    if hashlib.sha256((ROOT / "Notices" / name).read_bytes()).hexdigest() != expected:
        raise SystemExit(f"Supplemental font license checksum mismatch: {name}")
fallbacks = {
    "comemo-macros": "comemo", "glidesort": "glidesort", "krilla": "krilla",
    "krilla-svg": "krilla", "roman-numerals-rs": "roman-numerals", "wasmi": "wasmi",
    "wasmi_collections": "wasmi", "wasmi_core": "wasmi", "wasmi_ir": "wasmi",
    "wasmparser": "wasm-tools",
}
for package in metadata["packages"]:
    if package.get("repository") == "https://github.com/typst/typst":
        fallbacks[package["name"]] = "typst"

texts = {}
packages = []
for package in metadata["packages"]:
    try:
        source = inventory_source(ROOT, package)
    except (KeyError, ValueError) as error:
        raise SystemExit(f"Invalid Cargo package source: {error}")
    if source is None:
        continue
    directory = Path(package["manifest_path"]).parent
    candidates = []
    for file in directory.rglob("*"):
        if file.is_file() and not file.is_symlink() and file.name.lower().startswith(("license", "licence", "copying", "notice")):
            candidates.append(("crate/" + str(file.relative_to(directory)), file))
    if package.get("license_file"):
        file = directory / package["license_file"]
        if file.is_file():
            candidates.append(("crate/" + str(file.relative_to(directory)), file))
    if group := fallbacks.get(package["name"]):
        for file in sorted((up / group).iterdir()):
            if file.is_file() and file.name != "README.md":
                candidates.append(("upstream/" + group + "/" + file.name, file))
    # Glidesort's pinned repository has no LICENSE file; carry the exact license
    # declaration and a generic Apache text, and flag its attribution for review.
    if package["name"] == "glidesort":
        candidates.append(("reference/Apache-2.0", up / "typst/LICENSE"))
    evidence = []
    for origin, file in sorted(set(candidates), key=lambda pair: pair[0]):
        data = file.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        texts[digest] = data
        evidence.append({"origin": origin, "sha256": digest})
    if not package["license"] or not evidence:
        raise SystemExit(f"Missing license declaration or evidence: {package['name']} {package['version']}")
    vcs_file = directory / ".cargo_vcs_info.json"
    vcs = json.loads(vcs_file.read_text()) if vcs_file.exists() else None
    entry = {"name": package["name"], "version": package["version"],
             "source": source, "repository": package["repository"],
             "authors": package["authors"], "license": package["license"],
             "vcs": vcs, "evidence": evidence}
    if package["name"] == "glidesort":
        entry["licenseSelection"] = "Apache-2.0"
    packages.append(entry)
packages.sort(key=lambda p: (p["name"], p["version"], p["source"]))
index = {"format": 1, "scope": "Cargo metadata superset including build and target dependencies; not a legal approval",
         "cargoLockSHA256": hashlib.sha256((ROOT / "Rust/Cargo.lock").read_bytes()).hexdigest(),
         "unresolved": ["krilla NOTICE references resvg MPL-licensed code; verify provenance and obligations",
                        "GUST/LPPL NewCM fonts in historical Git and previous artifacts: review source and distribution obligations"],
         "packages": packages}
output = ROOT / "Notices/Rust"
expected = {Path("inventory.json"): (json.dumps(index, indent=2, sort_keys=True) + "\n").encode()}
expected.update({Path("texts") / f"{digest}.txt": content for digest, content in texts.items()})
if args.check:
    actual = {p.relative_to(output) for p in output.rglob("*") if p.is_file()}
    if actual != set(expected) or any((output / p).read_bytes() != data for p, data in expected.items()):
        raise SystemExit("Rust license evidence is missing or stale; regenerate and review")
else:
    if output.exists():
        raise SystemExit("Notices/Rust already exists; remove it explicitly before regeneration")
    for path, data in expected.items():
        dest = output / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
print(f"{len(packages)} packages, {len(texts)} distinct license/notice texts", file=sys.stderr)
