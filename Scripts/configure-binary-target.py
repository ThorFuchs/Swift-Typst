#!/usr/bin/env python3
"""Switch the package between a local bridge and an explicitly pinned release ZIP."""
import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
LOCAL = '.binaryTarget(name: "CTypstBridge", path: "Artifacts/CTypstBridge.artifactbundle")'
REMOTE = re.compile(r'\.binaryTarget\(name: "CTypstBridge", url: "([^"\n]*)", checksum: "([0-9a-f]{64})"\)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local", action="store_true", help="use a locally built artifact")
    mode.add_argument("--remote-url", help="immutable HTTPS URL of a verified artifact ZIP")
    parser.add_argument("--checksum", help="SwiftPM SHA-256 checksum of the remote ZIP")
    parser.add_argument("--manifest", type=Path, default=ROOT / "Package.swift")
    args = parser.parse_args()
    if args.local:
        if args.checksum:
            parser.error("--checksum is only valid with --remote-url")
        replacement = LOCAL
    else:
        url = args.remote_url
        try:
            parts = urlsplit(url)
            port = parts.port
        except ValueError:
            parser.error("remote URL has an invalid host or port")
        if (not re.fullmatch(r"https://[A-Za-z0-9._~!$&'()*+,;=:@%/-]+", url)
                or not parts.hostname or parts.username is not None or parts.password is not None
                or port == 0 or not parts.path.endswith(".zip") or parts.query or parts.fragment):
            parser.error("remote URL must be an HTTPS ZIP URL without credentials, query, or fragment")
        if not args.checksum or not re.fullmatch(r"[0-9a-f]{64}", args.checksum):
            parser.error("--checksum must be a lowercase 64-character SHA-256")
        replacement = f'.binaryTarget(name: "CTypstBridge", url: "{url}", checksum: "{args.checksum}")'

    source = args.manifest.read_text()
    remotes = list(REMOTE.finditer(source))
    if source.count(LOCAL) + len(remotes) != 1:
        raise SystemExit("Expected exactly one supported CTypstBridge binary declaration")
    result = source.replace(LOCAL, replacement) if LOCAL in source else REMOTE.sub(lambda _: replacement, source)
    if result != source:
        args.manifest.write_text(result)
    print("Configured " + ("local bridge" if args.local else "remote bridge ZIP"))


if __name__ == "__main__":
    main()
