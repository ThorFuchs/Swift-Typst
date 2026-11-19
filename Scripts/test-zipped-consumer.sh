#!/bin/sh
set -eu
archive=${1:?Usage: test-zipped-consumer.sh archive.zip [swift-run options...]}
shift
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
case "$archive" in /*) ;; *) archive="$PWD/$archive" ;; esac
work=$(mktemp -d "${TMPDIR:-/tmp}/swift-typst-zip-consumer.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
mkdir -p "$work/Package/Tests/Consumer"
cp -R "$root/Sources" "$work/Package/Sources"
cp "$root/Tests/Consumer/Package.swift" "$work/Package/Tests/Consumer/Package.swift"
cp -R "$root/Tests/Consumer/Sources" "$work/Package/Tests/Consumer/Sources"
cp -R "$root/Tests/SwiftTypstTests" "$work/Package/Tests/SwiftTypstTests"
cp "$archive" "$work/Package/CTypstBridge.zip"
python3 - "$root/Package.swift" "$work/Package/Package.swift" <<'PY'
from pathlib import Path
import sys
source = Path(sys.argv[1]).read_text()
old = 'path: "Artifacts/CTypstBridge.artifactbundle"'
if source.count(old) != 1:
    raise SystemExit("Unexpected package binary target declaration")
Path(sys.argv[2]).write_text(source.replace(old, 'path: "CTypstBridge.zip"'))
PY
# Do not add Cargo or arbitrary user tool directories to the consumer's PATH.
swift_bin=$(dirname "$(command -v swift)")
PATH="$swift_bin:/usr/bin:/bin:/usr/sbin:/sbin" \
  swift run --package-path "$work/Package/Tests/Consumer" "$@" Consumer
