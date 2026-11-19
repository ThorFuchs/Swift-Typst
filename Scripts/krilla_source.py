"""Verify the pinned, unmodified krilla source included in bridge artifacts."""
import hashlib
import json
import re
import tarfile
from pathlib import Path


CRATE = Path("Notices/Source/krilla/krilla-0.8.2.crate")
CRATE_SHA256 = "27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33"
CONTENT_SHA256 = "9e59b2c77b73b36caedacfe80894d1cce7fd6fe6f7438ea24fda2019391a980c"
VCS_REVISION = "3ffdf0588cf98050aad6edba51ca70162e1fb5b5"


def verify_krilla_source(root):
    """Fail closed if the included source and pinned Cargo input disagree."""
    try:
        lock = (root / "Rust/Cargo.lock").read_text()
        blocks = [block for block in lock.split("[[package]]")
                  if re.search(r'^name = "krilla"$', block, re.MULTILINE)]
        if (len(blocks) != 1
                or not re.search(r'^version = "0\.8\.2"$', blocks[0], re.MULTILINE)
                or not re.search(r'^source = "registry\+https://github\.com/rust-lang/crates\.io-index"$', blocks[0], re.MULTILINE)
                or not re.search(r'^checksum = "' + CRATE_SHA256 + r'"$', blocks[0], re.MULTILINE)):
            raise ValueError("Cargo.lock does not pin the expected upstream krilla crate")
        path = root / CRATE
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != CRATE_SHA256:
            raise ValueError("krilla source archive checksum mismatch")
        with tarfile.open(path, "r:gz") as archive:
            content = archive.extractfile("krilla-0.8.2/src/content.rs").read()
            vcs = json.load(archive.extractfile("krilla-0.8.2/.cargo_vcs_info.json"))
        if hashlib.sha256(content).hexdigest() != CONTENT_SHA256 or vcs.get("git", {}).get("sha1") != VCS_REVISION:
            raise ValueError("krilla source identity mismatch")
        required = [root / "Notices/Source/krilla/README.md",
                    root / "Notices/Upstream/krilla/NOTICE.md",
                    root / "Notices/Upstream/krilla/LICENSE_APACHE",
                    root / "Notices/Upstream/krilla/LICENSE_MIT",
                    root / "Notices/Upstream/krilla/MPL-2.0-reference.txt"]
        if any(not path.is_file() or path.is_symlink() for path in required):
            raise ValueError("Required krilla source instructions or notices are missing")
    except (OSError, KeyError, AttributeError, tarfile.TarError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"Invalid krilla source evidence: {error}") from error
