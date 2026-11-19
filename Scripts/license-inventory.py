#!/usr/bin/env python3
"""Summarize cargo metadata as an auditable dependency license inventory.

Run: cargo metadata --manifest-path Rust/Cargo.toml --locked --format-version 1 \
       | python3 Scripts/license-inventory.py > .build/license-inventory.json
The inventory is a metadata-based superset, not a legal compliance determination.
"""
import json
import sys

metadata = json.load(sys.stdin)
packages = []
for package in metadata["packages"]:
    if package["name"] == "swift-typst-bridge" and package["source"] is None:
        continue
    packages.append({
        "name": package["name"],
        "version": package["version"],
        "source": package["source"],
        "license": package["license"],
        "repository": package["repository"],
    })
packages.sort(key=lambda p: (p["name"], p["version"], p["source"] or ""))
json.dump({"format": 1, "note": "Cargo metadata superset; review actual target and license texts.",
           "packages": packages}, sys.stdout, indent=2, sort_keys=True)
sys.stdout.write("\n")
