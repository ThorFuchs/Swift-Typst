"""Classify Cargo package sources for the recorded license inventory."""
from __future__ import annotations

from pathlib import Path


def inventory_source(root: Path, package: dict) -> str | None:
    """Return the source identifier, or None only for our own bridge package.

    The artifact provenance covers `Rust/vendor`; reject other local path
    packages rather than silently omitting their license evidence.
    """
    if package.get("source") is not None:
        return package["source"]
    root = root.resolve()
    directory = Path(package["manifest_path"]).resolve().parent
    if directory == (root / "Rust").resolve():
        return None
    vendor = root / "Rust/vendor"
    if vendor.is_symlink() or not directory.is_relative_to(vendor.resolve()):
        raise ValueError(f"Local Cargo dependency outside Rust/vendor: {directory}")
    return "path:" + str(directory.relative_to(root))
