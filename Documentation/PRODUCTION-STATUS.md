# Implementation status — 19 November 2026

The bridge uses pinned Typst 0.15.1 and Rust 1.94.1 with a Cargo lockfile and
Swift 6.4.2. The synchronous PDF API supports in-memory projects, packages,
assets and fonts, structured diagnostics, PDF settings and size limits.

Local debug-build evidence for the current STIX production tree:

| Target | Production bridge evidence | Scope |
| --- | --- | --- |
| macOS arm64 | 21 Swift tests passed, including user font overrides and caller-supplied fonts. | Debug build; remote binary distribution remains unverified. |
| iOS arm64 simulator | PDF/math-font/diagnostic XCTest passed. | Simulator only; no physical-device run. |
| wasm32 WASI | 20 Swift Testing tests passed; a separate consumer compiled a PDF with caller-supplied font bytes and bundled fonts disabled. | The filesystem-based font test is native-only; not a browser. |
| Linux ARM64/musl | A separate SwiftPM consumer ran in a networkless Alpine VM. | Debug build; not glibc or x86_64. |

All four archives passed the exact-byte check against eight historical NewCM
faces in this local run, including Book, and contained the five expected STIX
faces. Book is an optional verifier input; builds without it check seven
upstream reference files. These checks do not prove absence of transformed data.
Separate fresh SwiftPM consumers also used the locally packaged four-variant
debug ZIP on macOS and WASI without Cargo or manual linker flags. This is not a
test of a published remote URL.

Before the later source-delivery packaging change, an additional optimized Rust
release-profile archive for macOS ARM64 passed
the eight-font exclusion check and all 21 Swift tests (the Swift test target
itself used its default debug configuration). The optimized archive did not
produce the oversized `__eh_frame` linker warning observed with the debug
archive in this test. Two ZIPs assembled from the same release inputs had the
same SHA-256, `c2293e6ea7f6318bbc256ce3e3b10d588057f80fd66194cafb2c64136ea3393c`;
this checks repeatable packaging, not an independent binary rebuild. A fresh
macOS SwiftPM consumer also ran from this local release ZIP without Cargo or
manual linker flags.

After adding self-contained krilla source delivery, that same optimized bridge
archive was repackaged in an isolated working-tree copy after verifying that its
recorded binary inputs other than notices still match. The resulting macOS ZIP
contained the pinned krilla source and notices and a fresh no-Cargo consumer
passed. This verifies the packaging change on macOS, not a new nine-variant
release build or public URL. Older local bundles carry earlier notice provenance
and must be reassembled before packaging with the updated working tree.

An optimized WASI bridge subsequently passed the eight-font exclusion check
and 20 Swift Testing tests with Swift 6.4.2. A separate release-profile macOS
consumer passed 400 sequential and 240 task-group PDF/diagnostic checks using
valid documents and a small set of malformed or missing-resource inputs. The
reproducible probe is in [Tests/Stress](../Tests/Stress/README.md); these runs
are not a memory-leak study, exhaustive fuzzing or browser validation.
On this macOS ARM64 machine, one standalone run of the same 640-call workload
reported a maximum resident set of 27,754,496 bytes via `/usr/bin/time -l`.
This is one small-input process-level observation, not a peak-memory bound,
cross-platform comparison or evidence that repeated use cannot leak.

`.github/workflows/ci.yml` defines nine candidate variants: macOS ARM64/x86_64,
iOS ARM64 device/simulator, Linux glibc ARM64/x86_64, Linux musl ARM64/x86_64,
and WASI. It tests native Swift, iOS simulator and WASI; static Linux runs the
separate consumer. It merges candidates, verifies checksums and includes license
evidence. Workflow syntax and expressions were checked using actionlint 1.7.12.
The private development repository’s [Book-font CI run](https://github.com/ThorFuchs/Swift-Typst-Internal/actions/runs/44353419708)
passed all eight platform jobs and the combined nine-variant artifact job at
commit `96ef6af`. It built release-profile bridges and tested the respective
Swift consumers, including packaged ZIP consumers where applicable. The iOS
job ran the simulator test and built an unsigned device app; device compilation
is not a device runtime test. The manually invoked license release gate was not
requested in that run and remains blocked by the findings below. This CI run
predates the current STIX changes and does not validate them.
The former `swift-actions/setup-swift@v2` was removed: its hardcoded version
list ends at Swift 6.2.1 and rejects 6.4.2. The replacement is pinned by commit.

Cargo license evidence covers 298 packages and 181 distinct captured license or
notice texts, plus bundled-font and Rust standard-library notices. This is a
conservative dependency superset, not proof of every component in every binary.
The pinned krilla NOTICE refers to copied resvg code under MPL while the crate
metadata declares `MIT OR Apache-2.0`; its specific provenance and applicable
rights remain unresolved. Glidesort's published crate and pinned upstream
revision have no license file despite a declared `MIT OR Apache-2.0` license;
the evidence retains its author metadata and records the Apache-2.0 option.
Further tracing found the same `quad_to_curve` helper introduced in a
[2023 resvg commit](https://github.com/linebender/resvg/commit/95a469e5a4c90c2401f34fd8f06e8e49e7ea1fea)
by Yevhenii Reizner; the upstream [relicensing discussion](https://github.com/linebender/resvg/issues/838)
contains a later dual-license grant by `RazrFalcon`. This narrows the question
but does not establish the complete provenance or applicable terms of the
entire copied krilla method.
The current tree uses STIX Two in place of the NewCM faces. The
[font investigation](FONT-INVESTIGATION.md) documents the earlier Book work and
the compatibility impact. The GUST/LPPL question remains open for earlier Git
history and candidate artifacts; removing fonts from the current tree does not
remove them from prior commits.
Details, source snapshots and outstanding questions are in
[Notices/README.md](../Notices/README.md). `Scripts/check-license-readiness.py`
fails while those questions remain open. A manually requested CI release gate
runs this check; candidate archives are not publication approval.
The gate also rejects a missing or malformed `unresolved` field rather than
interpreting it as an empty review. This is a structural safeguard, not proof
that an empty list represents a complete legal review.
The private working tree also prepares self-contained krilla source delivery in
each artifact; the exact final public assets and the legal scope remain to be
reviewed. See [the distribution proposal](KRILLA-DISTRIBUTION-PROPOSAL.md).
The current provenance investigation, NewCM package findings, and controlled
math-font comparison are documented in
[RELEASE-LICENSE-EVIDENCE.md](RELEASE-LICENSE-EVIDENCE.md), with next steps in
[RELEASE-CLEARANCE-PLAN.md](RELEASE-CLEARANCE-PLAN.md).

Before release:

- Resolve the specific krilla/resvg provenance and applicable obligations and
  the GUST/LPPL questions for historical source and artifacts. Verify the
  curated font licenses and platform toolchain/SDK notices appropriate to the
  exact distributed products and consuming apps.
- Test a real iOS device and any intended browser host. Complete stress,
  memory and malformed-input testing.
- Produce and verify a release-profile bundle and test its immutable remote URL,
  checksum and fresh no-Rust consumer on each supported platform. `Package.swift`
  still names a local artifact rather than a published binary.
- Pin and record SDKs, compiler flags and environment; perform independent
  rebuild comparisons before claiming bit-identical binaries. A deterministic
  ZIP and Cargo lockfile alone do not establish reproducible compilation.
