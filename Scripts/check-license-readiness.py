#!/usr/bin/env python3
"""Fail closed or check the exact public candidate with accepted residual risk."""
import argparse
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path


def unresolved_findings(inventory):
    """Reject malformed evidence rather than treating it as an empty review."""
    if not isinstance(inventory, dict) or "unresolved" not in inventory:
        raise ValueError("Inventory must explicitly contain unresolved findings")
    findings = inventory["unresolved"]
    if not isinstance(findings, list) or any(
        not isinstance(item, str) or not item.strip() for item in findings
    ):
        raise ValueError("Unresolved findings must be a list of nonempty strings")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-artifact", type=Path, help="the exact accepted nine-variant ZIP")
    parser.add_argument("--typst-assets", type=Path, help="the locked typst-assets 0.15.1 .crate")
    parser.add_argument("--excluded-book", type=Path, help="original historical NewCM10-Book.otf reference")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        inventory = json.loads((root / "Notices/Rust/inventory.json").read_text())
        findings = unresolved_findings(inventory)
        if args.public_artifact:
            if not args.typst_assets or not args.excluded_book:
                raise ValueError("Public-candidate mode requires both checksum-verified font-reference inputs")
            from public_release_check import check_public_candidate
            commits, blobs, variants = check_public_candidate(root, inventory, args.public_artifact,
                                                               args.typst_assets, args.excluded_book)
            print(f"Public candidate checked: {commits} commits, {blobs} blobs, {variants} binary variants")
            print("The release owner accepted the documented krilla residual risk; independent legal review was not performed.")
            print("The historical private NewCM distribution remains a separate unresolved matter.")
            return 0
        if args.typst_assets or args.excluded_book:
            raise ValueError("Font-reference inputs require --public-artifact")
    except (OSError, ValueError, TypeError, KeyError, tarfile.TarError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print(f"License release gate is blocked: invalid evidence: {error}")
        return 1
    if findings:
        print("License release gate is blocked:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("No unresolved license findings in the recorded inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
