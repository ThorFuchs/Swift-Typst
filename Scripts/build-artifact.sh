#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
target=${1:?"Usage: build-artifact.sh <Rust target>"}
profile=${SWIFT_TYPST_PROFILE:-release}
case "$target" in
  aarch64-apple-darwin) triple=arm64-apple-macosx ;;
  x86_64-apple-darwin) triple=x86_64-apple-macosx ;;
  aarch64-apple-ios) triple=arm64-apple-ios ;;
  aarch64-apple-ios-sim) triple=arm64-apple-ios-simulator ;;
  x86_64-apple-ios) triple=x86_64-apple-ios-simulator ;;
  wasm32-wasip1) triple=wasm32-unknown-wasip1 ;;
  aarch64-unknown-linux-musl) triple=aarch64-swift-linux-musl ;;
  x86_64-unknown-linux-musl) triple=x86_64-swift-linux-musl ;;
  aarch64-unknown-linux-gnu) triple=aarch64-unknown-linux-gnu ;;
  x86_64-unknown-linux-gnu) triple=x86_64-unknown-linux-gnu ;;
  *) echo "Unsupported Rust target: $target" >&2; exit 1 ;;
esac
case "$profile" in
  release) cargo_profile=--release; output=release ;;
  debug) cargo_profile=; output=debug ;;
  *) echo "SWIFT_TYPST_PROFILE must be release or debug" >&2; exit 1 ;;
esac
rust_version=$(rustc --version)
case "$rust_version" in
  'rustc 1.94.1 '*) ;;
  *) echo "Expected rustc 1.94.1; found $rust_version" >&2; exit 1 ;;
esac
target_dir=${CARGO_TARGET_DIR:-"$root/.build/rust"}
export CARGO_TARGET_DIR="$target_dir"
# Pass deployment targets to target C code only. Setting the global Apple
# deployment target also affects host proc-macro dylibs built by Cargo.
case "$target" in
  aarch64-apple-darwin) export CFLAGS_aarch64_apple_darwin="${CFLAGS_aarch64_apple_darwin:--mmacosx-version-min=14.0}" ;;
  x86_64-apple-darwin) export CFLAGS_x86_64_apple_darwin="${CFLAGS_x86_64_apple_darwin:--mmacosx-version-min=14.0}" ;;
  aarch64-apple-ios) export CFLAGS_aarch64_apple_ios="${CFLAGS_aarch64_apple_ios:--miphoneos-version-min=17.0}" ;;
  aarch64-apple-ios-sim) export CFLAGS_aarch64_apple_ios_sim="${CFLAGS_aarch64_apple_ios_sim:--mios-simulator-version-min=17.0}" ;;
  x86_64-apple-ios) export CFLAGS_x86_64_apple_ios="${CFLAGS_x86_64_apple_ios:--mios-simulator-version-min=17.0}" ;;
esac
# The default release settings are recorded by Cargo.toml and the pinned toolchain.
cargo build --manifest-path "$root/Rust/Cargo.toml" --locked --target "$target" ${cargo_profile:+"$cargo_profile"}
python3 "$root/Scripts/verify-bundled-fonts.py" --rust-target "$target" \
  --archive "$target_dir/$target/$output/libswift_typst_bridge.a"
python3 "$root/Scripts/assemble-artifact.py" "$triple" \
  "$target_dir/$target/$output/libswift_typst_bridge.a" \
  --rust-target "$target" --rust-version "$rust_version" --profile "$profile"
