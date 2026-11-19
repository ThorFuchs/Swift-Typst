#!/usr/bin/env python3
"""Fail the release gate while the recorded license review has open findings."""
import json
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
    root = Path(__file__).resolve().parent.parent
    try:
        inventory = json.loads((root / "Notices/Rust/inventory.json").read_text())
        findings = unresolved_findings(inventory)
    except (OSError, ValueError) as error:
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
