#!/bin/sh
# Build native symbol graphs without downloading or linking the binary bridge.
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
output=${1:-"$root/.build/docc-site"}
work="$root/.build/docc-work"
mkdir -p "$work/graphs" "$work/modules" "$work/cache"
rm -f "$work/graphs"/*.json
arch=$(uname -m)
case "$arch" in arm64|x86_64) ;; *) echo "Unsupported macOS architecture: $arch" >&2; exit 1 ;; esac
xcrun swiftc -emit-module -module-name SwiftTypst -swift-version 6 \
  -target "$arch-apple-macosx14.0" \
  -I "$root/Sources/CTypstBridge/include" \
  -module-cache-path "$work/cache" \
  -emit-symbol-graph -emit-symbol-graph-dir "$work/graphs" \
  -emit-module-path "$work/modules/SwiftTypst.swiftmodule" \
  "$root"/Sources/SwiftTypst/*.swift
xcrun docc convert "$root/Sources/SwiftTypst/SwiftTypst.docc" \
  --additional-symbol-graph-dir "$work/graphs" \
  --fallback-display-name SwiftTypst \
  --fallback-bundle-identifier com.thorfuchs.SwiftTypst \
  --output-dir "$output" \
  --transform-for-static-hosting --hosting-base-path Swift-Typst \
  --warnings-as-errors
# Direct the project root to the module reference, with a usable no-JS link.
printf '%s\n' '<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=/Swift-Typst/documentation/swifttypst/"><title>SwiftTypst documentation</title><a href="/Swift-Typst/documentation/swifttypst/">SwiftTypst documentation</a></html>' > "$output/index.html"
touch "$output/.nojekyll"
test -s "$output/data/documentation/swifttypst.json"
for route in swifttypst swifttypst/gettingstarted swifttypst/projectsandresources swifttypst/diagnosticsandsafety swifttypst/typstcompiler; do
  test -s "$output/documentation/$route/index.html"
done
printf 'DocC site built at %s\n' "$output"
