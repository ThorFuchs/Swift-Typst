"""Verify the specifically accepted public candidate, without declaring legal clearance."""
import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path

from krilla_source import verify_krilla_source


KRILLA_FINDING = "krilla NOTICE references resvg MPL-licensed code; verify provenance and obligations"
HISTORICAL_FINDING = "GUST/LPPL NewCM fonts in historical Git and previous artifacts: review source and distribution obligations"
ASSET_SHA = "bcee505dac6702dd1c5e65aa2e94a6179d19ee09e2e5637d7313db91765dc4e0"
EXCLUDED = {
    "NewCMMath-Bold.otf": "c6c0e060da57d4f44274705afb956013047231dc62be5a4b02a351ab0dc43f2f",
    "NewCMMath-Book.otf": "2ea09ebc9167b1e1a66f31390dc917f2d4004ecfca72d51b28010e4ad6becd95",
    "NewCMMath-Regular.otf": "d66ac1cc91c55c24d3636ae2df1238076debdff51841f9893fc5419cc2df3df7",
    "NewCM10-Bold.otf": "40b0b32b63655fe802679ee4a14adb29c762a4712095d9c84cf7df7852b5152e",
    "NewCM10-Italic.otf": "a55d07607eec48889b6e7e7d51d7703c3beb915a39690f34fe01b4e2a744a9d6",
    "NewCM10-BoldItalic.otf": "fb53f43500c8ffbcc6dfdea5a519961d475543174ea2a0dcbe16c08510299fdf",
    "NewCM10-Regular.otf": "328698d764ccdf7acf6bc1088aefd83a237f6a1d8b812de1e77ac5e4483bf3d1",
    "NewCM10-Book.otf": "005f9b4e13b2a133df36d4ebfbb8f5fe402854bcb5882deb500b9c0f72b1bb49",
}
TRIPLES = {
    "arm64-apple-macosx", "x86_64-apple-macosx", "arm64-apple-ios",
    "arm64-apple-ios-simulator", "x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu",
    "x86_64-swift-linux-musl", "aarch64-swift-linux-musl", "wasm32-unknown-wasip1",
}
PREFIX = "CTypstBridge.artifactbundle/"


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for part in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def scan_stream(stream, excluded, included=None, chunk_size=4 * 1024 * 1024):
    """Check exact byte sequences across chunk boundaries and return content SHA-256."""
    included = included or {}
    patterns = list(excluded.values()) + list(included.values())
    overlap = max((len(p) for p in patterns), default=1) - 1
    tail = b""
    found = set()
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(chunk_size), b""):
        digest.update(chunk)
        window = tail + chunk
        for name, data in excluded.items():
            if data in window:
                raise ValueError(f"Excluded font found: {name}")
        for name, data in included.items():
            if name not in found and data in window:
                found.add(name)
        tail = window[-overlap:] if overlap else b""
    missing = set(included) - found
    if missing:
        raise ValueError("Expected STIX fonts missing: " + ", ".join(sorted(missing)))
    return digest.hexdigest()


def verify_decision(root, inventory, decision):
    if not isinstance(decision, dict) or decision.get("format") != 1:
        raise ValueError("Missing or malformed risk decision")
    expected = {
        "decision": "accepted-residual-risk", "decision_owner": "repository owner",
        "decision_date": "2026-11-19", "finding": KRILLA_FINDING,
        "public_history": "clean-candidate-only", "independent_legal_review": False,
        "tested_commit": "04a0f7fc770a438980217cc9d3ccc37aac994735",
        "artifact_sha256": "c27788475defb885943d978406ab787a87339314251b9a3305e5499207c1cf76",
        "artifact_url": "https://github.com/ThorFuchs/Swift-Typst/releases/download/bridge-v1.0.0/CTypstBridge.zip",
        "source_version": "1.0.0",
    }
    if any(decision.get(key) != value for key, value in expected.items()):
        raise ValueError("Decision does not match the specifically accepted candidate")
    findings = inventory.get("unresolved") if isinstance(inventory, dict) else None
    if (not isinstance(findings, list) or len(findings) != 2
            or any(not isinstance(item, str) for item in findings)
            or set(findings) != {KRILLA_FINDING, HISTORICAL_FINDING}):
        raise ValueError("Inventory contains missing, changed or additional findings")
    for key, relative in {
        "cargo_lock_sha256": "Rust/Cargo.lock",
        "krilla_crate_sha256": "Notices/Source/krilla/krilla-0.8.2.crate",
        "krilla_notice_sha256": "Notices/Upstream/krilla/NOTICE.md",
    }.items():
        if sha_file(root / relative) != decision.get(key):
            raise ValueError(f"Accepted source changed: {relative}")
    verify_krilla_source(root)


def load_references(assets, book):
    if sha_file(assets) != ASSET_SHA:
        raise ValueError("typst-assets crate checksum mismatch")
    refs = {}
    with tarfile.open(assets, "r:gz") as archive:
        for name, digest in EXCLUDED.items():
            if name == "NewCM10-Book.otf":
                data = book.read_bytes()
            else:
                data = archive.extractfile("typst-assets-0.15.1/files/fonts/" + name).read()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f"Invalid excluded-font reference: {name}")
            refs[name] = data
    return refs


def verify_history(root, refs, decision):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])
    if git("status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("Candidate source has unstaged, staged or untracked changes")
    tested_commit = decision["tested_commit"]
    subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", tested_commit, "HEAD"], check=True)
    changes = git("diff", "--name-only", tested_commit, "HEAD").decode().splitlines()
    allowed = {"README.md", "Package.swift", "Artifacts/README.md", "Scripts/check-license-readiness.py", "Scripts/public_release_check.py", "Tests/test_public_release_gate.py"}
    if any(not (name.startswith("Documentation/") or name in allowed) for name in changes):
        raise ValueError("Changes after the CI-tested commit exceed the accepted release scope")
    original = git("show", tested_commit + ":Package.swift").decode()
    local = '.binaryTarget(name: "CTypstBridge", path: "Artifacts/CTypstBridge.artifactbundle")'
    remote = f'.binaryTarget(name: "CTypstBridge", url: "{decision["artifact_url"]}", checksum: "{decision["artifact_sha256"]}")'
    if original.count(local) != 1 or (root / "Package.swift").read_text() != original.replace(local, remote):
        raise ValueError("Manifest differs from the accepted remote artifact declaration")
    commits = git("rev-list", "--all").splitlines()
    if not commits:
        raise ValueError("Candidate history is empty")
    blobs = set()
    compressed = set()
    for commit in commits:
        for row in git("ls-tree", "-r", "-z", commit.decode()).split(b"\0"):
            if row:
                meta, path = row.split(b"\t", 1)
                mode, kind, sha = meta.split()
                if kind != b"blob" or mode == b"120000":
                    raise ValueError("Unexpected Git object or symlink in candidate history")
                blobs.add(sha)
                if path.lower().endswith((b".crate", b".zip", b".tar", b".tgz", b".gz", b".xz", b".7z")):
                    compressed.add((path, sha))
    expected_crate = git("rev-parse", "HEAD:Notices/Source/krilla/krilla-0.8.2.crate").strip()
    if compressed != {(b"Notices/Source/krilla/krilla-0.8.2.crate", expected_crate)}:
        raise ValueError("Unexpected compressed file in candidate history")
    process = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"],
                             input=b"".join(sha + b"\n" for sha in sorted(blobs)),
                             capture_output=True, check=True)
    output = io.BytesIO(process.stdout)
    for sha in sorted(blobs):
        head = output.readline().split()
        if len(head) != 3 or head[0] != sha or head[1] != b"blob":
            raise ValueError("Unexpected Git blob response")
        length = int(head[2])
        data = output.read(length)
        if len(data) != length or output.read(1) != b"\n":
            raise ValueError("Truncated Git blob")
        for name, value in refs.items():
            if value in data:
                raise ValueError(f"Excluded font in public history: {name}")
    with tarfile.open(root / "Notices/Source/krilla/krilla-0.8.2.crate", "r:gz") as archive:
        for item in archive.getmembers():
            if item.isfile():
                scan_stream(archive.extractfile(item), refs)
            elif not item.isdir():
                raise ValueError("Unexpected link in the krilla source archive")
    return len(commits), len(blobs)


def verify_artifact(root, artifact, decision, refs):
    if sha_file(artifact) != decision["artifact_sha256"]:
        raise ValueError("Artifact does not match the accepted SHA-256")
    stix = {p.name: p.read_bytes() for p in (root / "Rust/fonts").glob("STIXTwo*.otf")}
    if len(stix) != 5:
        raise ValueError("Expected five STIX font faces")
    with zipfile.ZipFile(artifact) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or any(not n.startswith(PREFIX) or ".." in Path(n).parts for n in names):
            raise ValueError("Unexpected or duplicate artifact entries")
        info = json.loads(archive.read(PREFIX + "info.json"))
        variants = info["artifacts"]["CTypstBridge"]["variants"]
        records = json.loads(archive.read(PREFIX + "provenance.json"))
        if {tuple(v["supportedTriples"]) for v in variants} != {(x,) for x in TRIPLES} or set(records) != TRIPLES:
            raise ValueError("Candidate does not contain the nine expected variants")
        sources = [root / "LICENSE", root / "Rust/Cargo.toml", root / "Rust/Cargo.lock"]
        sources += sorted((root / "Rust/src").rglob("*.rs"))
        sources += sorted((root / "Rust/fonts").rglob("*"))
        vendor = root / "Rust/vendor"
        sources += sorted(vendor.rglob("*"))
        sources += sorted((root / "Sources/CTypstBridge/include").iterdir())
        sources += sorted((root / "Notices").rglob("*"))
        if vendor.is_symlink() or any(p.is_symlink() for p in sources):
            raise ValueError("Symlink in binary inputs")
        expected_sources = {str(p.relative_to(root)): sha_file(p) for p in sources if p.is_file()}
        notice_root = root / "Notices"
        expected_notices = {"notices/" + str(p.relative_to(notice_root)): p for p in notice_root.rglob("*") if p.is_file()}
        actual_notices = {n[len(PREFIX):] for n in names if n.startswith(PREFIX + "notices/") and not n.endswith("/")}
        if actual_notices != set(expected_notices):
            raise ValueError("Artifact notice and source files differ")
        for name, path in expected_notices.items():
            if hashlib.sha256(archive.read(PREFIX + name)).hexdigest() != sha_file(path):
                raise ValueError(f"Artifact notice or source differs: {name}")
        for triple in sorted(TRIPLES):
            record = records[triple]
            if record.get("profile") != "release" or record.get("cargoLockSHA256") != decision["cargo_lock_sha256"]:
                raise ValueError(f"Unexpected build provenance: {triple}")
            if record.get("sources") != expected_sources:
                raise ValueError(f"Binary inputs differ for {triple}")
            with archive.open(PREFIX + f"lib/{triple}/libswift_typst_bridge.a") as source:
                digest = scan_stream(source, refs, stix)
            if digest != record["archiveSHA256"]:
                raise ValueError(f"Archive checksum mismatch: {triple}")
    return len(TRIPLES)


def check_public_candidate(root, inventory, artifact, assets, book):
    decision = json.loads((root / "Documentation/RELEASE-RISK-DECISION.json").read_text())
    verify_decision(root, inventory, decision)
    refs = load_references(assets, book)
    commits, blobs = verify_history(root, refs, decision)
    variants = verify_artifact(root, artifact, decision, refs)
    return commits, blobs, variants
