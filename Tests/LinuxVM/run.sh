#!/bin/sh
set -eu
binary=${1:?"Usage: run.sh <static Linux consumer> <Alpine 3.22.8 aarch64 ISO>"}
iso=${2:?"Usage: run.sh <static Linux consumer> <Alpine 3.22.8 aarch64 ISO>"}
: "${SWIFT_TYPST_TOOLCHAIN_BIN:?Set to the swift.org 6.4.2 toolchain usr/bin}"
: "${SWIFT_TYPST_LINUX_SYSROOT:?Set to the 6.4.2 Linux SDK musl aarch64 sysroot}"
vm_dir=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/swift-typst-vm.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
expected=dd3cec79d32a726d40bace8fc97c2d04f58d7da9dd9084e62a817ed6228181b7
actual=$(shasum -a 256 "$iso" | cut -d ' ' -f 1)
test "$actual" = "$expected" || { echo "Alpine ISO checksum mismatch" >&2; exit 1; }
"$SWIFT_TYPST_TOOLCHAIN_BIN/clang" --target=aarch64-unknown-linux-musl \
  --sysroot="$SWIFT_TYPST_LINUX_SYSROOT" -resource-dir "$SWIFT_TYPST_LINUX_SYSROOT/usr/lib/swift/clang" \
  -fuse-ld=lld -rtlib=compiler-rt -unwindlib=none -static -O2 "$vm_dir/init.c" -o "$work/init"
# The guest has 512 MiB; debug symbols in a Rust static library can make the
# consumer larger than that. Strip a temporary copy and preserve the original.
"$SWIFT_TYPST_TOOLCHAIN_BIN/llvm-objcopy" --strip-debug "$binary" "$work/Consumer"
python3 "$vm_dir/prepare.py" "$iso" "$work/init" "$work/Consumer" "$work"
swiftc "$vm_dir/Host.swift" -framework Virtualization -o "$work/host"
codesign --force --sign - --entitlements "$vm_dir/entitlements.plist" "$work/host"
output=$("$work/host" "$work/Image" "$work/initramfs.gz")
printf '%s\n' "$output"
case "$output" in
  *"consumer: PDF and diagnostics OK"*"SWIFT_TYPST_CONSUMER_EXIT=0"*"VM_GUEST_STOPPED"*) ;;
  *) echo "Linux VM consumer test did not pass" >&2; exit 1 ;;
esac
