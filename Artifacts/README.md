# Bridge artifacts

SwiftPM consumes the locally generated `CTypstBridge.artifactbundle`. Install
Rust 1.94.1 and the desired Rust target, then from the repository root run:

```sh
sh Scripts/build-artifact.sh aarch64-apple-darwin
swift test
python3 Scripts/package-artifact.py .build/CTypstBridge.zip --require arm64-apple-macosx
swift package compute-checksum .build/CTypstBridge.zip
```

On Linux use `x86_64-unknown-linux-gnu` or `aarch64-unknown-linux-gnu`; iOS and
WASI mappings are in the build script. The default is Cargo's release profile;
set `SWIFT_TYPST_PROFILE=debug` for a faster local experiment. Add variants by
running the script for each target with the same Rust version, source snapshot,
and profile. Cross-compilation also needs the target's C compiler and SDK.

The bundle records source, lockfile and archive SHA-256 values. The packager
checks those values and writes a sorted ZIP with normalized timestamps. This
makes the package of *the same inputs* repeatable; it does not establish that
independent Rust/SDK builds are bit-identical. Compiler flags, SDK, OS and the
rest of the toolchain must also be controlled and audited for that claim.

Each variant includes `notices/Source/krilla/` with the unmodified source crate
and recipient instructions, as well as `notices/Upstream/krilla/` with the
captured upstream notices. Assembly and packaging validate the krilla archive
against the pinned Cargo.lock and reject missing or changed bundled evidence.
The included source is not evidence that all release rights or downstream
obligations have been resolved; see [the proposal](../Documentation/KRILLA-DISTRIBUTION-PROPOSAL.md).

The artifact is generated locally and ignored by Git. CI is configured for nine
candidate variants and merges them into a checksum-verified archive. A prior
Book-font run passed, but the current STIX production tree requires a fresh
matrix run; see [production status](../Documentation/PRODUCTION-STATUS.md).
Candidate artifacts are not release approval: the explicit release gate fails
while the license findings in `Notices/Rust/inventory.json` remain open.
A clean checkout needs Rust. Before release, assemble and validate all intended
variants, complete the third-party license audit, publish the ZIP at an immutable
URL, and update `Package.swift` with its SwiftPM checksum. Test that remote
artifact from a clean external consumer before promising no-Rust installation.

The font verifier checks each archive against the seven excluded faces present
in the pinned `typst-assets` source. To additionally check the historical Book
face, provide its original file with `SWIFT_TYPST_EXCLUDED_BOOK_FONT` while
building, or pass `--excluded-book <path>` to
`Scripts/verify-bundled-fonts.py`. This is an exact-byte check, not detection
of transformed font data.

For an ARM64 Linux cross-build from macOS, install the checksum-verified
[Swift 6.4.2 Static Linux SDK](https://www.swift.org/documentation/articles/static-linux-getting-started.html)
and set `SWIFT_TYPST_TOOLCHAIN_BIN`, `SWIFT_TYPST_SDKS_PATH`, and
`SWIFT_TYPST_LINUX_SYSROOT` to the matching toolchain and SDK locations. Then run
`sh Scripts/build-linux-arm64.sh`. The resulting static consumer can be run
with `sh Tests/LinuxVM/run.sh <consumer> <Alpine ISO>`; the VM helper checks the
Alpine 3.22.8 ARM64 ISO checksum and requires macOS virtualization support. It
strips debug symbols from a temporary copy to fit the guest; the original
consumer is not changed.
