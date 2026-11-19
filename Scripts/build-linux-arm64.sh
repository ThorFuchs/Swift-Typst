#!/bin/sh
set -eu
# Requires the exact, checksum-verified Swift 6.4.2 Static Linux SDK and Rust 1.94.1.
: "${SWIFT_TYPST_TOOLCHAIN_BIN:?Path to the Swift 6.4.2 toolchain usr/bin}"
: "${SWIFT_TYPST_SDKS_PATH:?Directory containing the Swift 6.4.2 SDK artifact bundle}"
: "${SWIFT_TYPST_LINUX_SYSROOT:?Path to the SDK's musl-1.2.5.sdk/aarch64}"
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
export PATH="$SWIFT_TYPST_TOOLCHAIN_BIN:$PATH"
export CC_aarch64_unknown_linux_musl="$SWIFT_TYPST_TOOLCHAIN_BIN/clang"
export AR_aarch64_unknown_linux_musl="$SWIFT_TYPST_TOOLCHAIN_BIN/llvm-ar"
export CFLAGS_aarch64_unknown_linux_musl="--target=aarch64-unknown-linux-musl --sysroot=$SWIFT_TYPST_LINUX_SYSROOT"
sh "$root/Scripts/build-artifact.sh" aarch64-unknown-linux-musl
swift build --package-path "$root/Tests/Consumer" --swift-sdks-path "$SWIFT_TYPST_SDKS_PATH" --swift-sdk aarch64-swift-linux-musl
