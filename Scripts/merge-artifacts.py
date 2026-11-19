#!/usr/bin/env python3
"""Merge individually packaged SwiftPM bridge variants into one bundle."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("output", type=Path, help="new CTypstBridge.artifactbundle directory")
parser.add_argument("inputs", type=Path, nargs="+", help="variant ZIPs")
args = parser.parse_args()
if args.output.name != "CTypstBridge.artifactbundle":
    raise SystemExit("Output must be named CTypstBridge.artifactbundle")
args.output.mkdir(parents=True, exist_ok=False)
prefix = "CTypstBridge.artifactbundle/"
common_files = ["include/module.modulemap", "include/typst_bridge.h", "typst-assets-NOTICE.txt", "LICENSE"]
common = None
baseline = None
variants = []
provenance = {}
version = None
for input_path in args.inputs:
    with zipfile.ZipFile(input_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SystemExit(f"Duplicate ZIP entries: {input_path}")
        info = json.loads(archive.read(prefix + "info.json"))
        artifact = info["artifacts"]["CTypstBridge"]
        records = json.loads(archive.read(prefix + "provenance.json"))
        if info["schemaVersion"] != "1.0" or artifact["type"] != "staticLibrary":
            raise SystemExit(f"Unexpected artifact format: {input_path}")
        if version is None:
            version = artifact["version"]
        elif version != artifact["version"]:
            raise SystemExit("Artifact versions differ")
        notice_files = [name[len(prefix):] for name in names if name.startswith(prefix + "notices/") and not name.endswith("/")]
        if not notice_files or any(".." in Path(name).parts or Path(name).is_absolute() for name in notice_files):
            raise SystemExit("Missing or unsafe license evidence")
        files = {name: archive.read(prefix + name) for name in common_files + notice_files}
        if common is None:
            common = files
            for name, contents in files.items():
                dest = args.output / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(contents)
        elif common != files:
            raise SystemExit("Artifact headers or notices differ")
        seen = set()
        for item in artifact["variants"]:
            if len(item["supportedTriples"]) != 1:
                raise SystemExit("Expected one target per variant")
            triple = item["supportedTriples"][0]
            if not re.fullmatch(r"[a-z0-9_.+\-]+", triple) or triple in provenance:
                raise SystemExit(f"Invalid or duplicate target: {triple}")
            expected_path = f"lib/{triple}/libswift_typst_bridge.a"
            if item["path"] != expected_path:
                raise SystemExit(f"Unexpected archive path: {item['path']}")
            if item.get("staticLibraryMetadata") != {"headerPaths": ["include"], "moduleMapPath": "include/module.modulemap"}:
                raise SystemExit("Unexpected static-library metadata")
            record = records[triple]
            identity = (record["sources"], record["rustVersion"], record["profile"], record["typst"])
            if baseline is None:
                baseline = identity
            elif baseline != identity:
                raise SystemExit("Source, toolchain or profile differs between variants")
            dest = args.output / expected_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            sha = hashlib.sha256()
            with archive.open(prefix + expected_path) as src, dest.open("wb") as out:
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    sha.update(chunk)
                    out.write(chunk)
            if sha.hexdigest() != record["archiveSHA256"]:
                raise SystemExit(f"Archive checksum mismatch: {triple}")
            variants.append(item)
            provenance[triple] = record
            seen.add(triple)
        if seen != set(records):
            raise SystemExit(f"Variant/provenance mismatch: {input_path}")
if not variants:
    raise SystemExit("No variants found")
variants.sort(key=lambda v: v["supportedTriples"][0])
result = {"schemaVersion": "1.0", "artifacts": {"CTypstBridge": {
    "type": "staticLibrary", "version": version, "variants": variants}}}
(args.output / "info.json").write_text(json.dumps(result, indent=2) + "\n")
(args.output / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
print(f"Merged {', '.join(sorted(provenance))} into {args.output}")
