# Implementation status — 19 November 2026

The bridge uses pinned Typst 0.15.1 and Rust 1.94.1 with a Cargo lockfile and
Swift 6.4.2. The synchronous PDF API supports in-memory projects, packages,
assets and fonts, structured diagnostics, PDF settings and size limits.

Local debug-build evidence for the current STIX production tree:

| Target | Production bridge evidence | Scope |
| --- | --- | --- |
| macOS arm64 | 21 Swift tests passed, including user font overrides and caller-supplied fonts. | Debug build; remote binary distribution remains unverified. |
| iOS arm64 simulator | PDF/math-font/diagnostic XCTest passed. | Simulator coverage. |
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

On 19 November 2026, the same PDF/math-font/diagnostic XCTest also passed on a
physical iPhone 14 Pro Max running iOS 27.2, using a locally built optimized
ARM64 iOS Rust bridge. The archive passed the eight-font exact-byte exclusion
check. This is one physical device and does not cover all iOS versions or models.

The locally built iOS archive and the archive from the successful clean-candidate
CI run have different SHA-256 values, even though their recorded source hashes,
Cargo.lock, Rust version, target and profile match. The CI archive's hash was
independently checked against its provenance. This was not a controlled rebuild:
local Xcode 27.2 was build `27B48`, CI used `27B52`, and other inputs such as
paths and SDK/compiler details were not fully normalized. The result prevents a
bit-reproducibility claim; it does not isolate the cause of the difference.
The two `ar` archives each contained 1,771 members in matching order, with the
same name/timestamp/owner/mode header fields; 949 member lengths and 1,043
member payloads differed. Payload comparisons include any extended archive-name
data, so this narrows the difference beyond simple archive-header timestamps
without attributing it to a particular toolchain component.

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

The clean STIX candidate's private [CI run](https://github.com/ThorFuchs/Swift-Typst-Internal/actions/runs/44583198656)
on root commit `1aa13efd4a7f675fe597d606426121623a39a973` passed all eight
platform jobs and the combined nine-variant artifact job on 19 November 2026.
The inner combined ZIP had SwiftPM SHA-256
`c27788475defb885943d978406ab787a87339314251b9a3305e5499207c1cf76`.
The explicit license release gate was not requested and was skipped; this is
not a release decision. A second [CI run](https://github.com/ThorFuchs/Swift-Typst-Internal/actions/runs/44587096602)
at `04a0f7fc770a438980217cc9d3ccc37aac994735`, including the manifest-switching
tooling and stress test, also passed all eight platform jobs, 13 packaging and
license-tool tests, and the combined nine-variant job. Both runs reported the
same inner combined ZIP SHA-256 above. The downloaded iOS device and simulator
archives from each run were separately checked against their recorded hashes and
were byte-identical between runs. Both iOS jobs reported Rust 1.94.1 and Xcode
27.2 build `27B52`. This is strong evidence for these two CI builds under their
recorded environments, not a guarantee across different SDKs or systems. The
second run also skipped the optional license release gate.

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
The release owner has accepted the remaining krilla provenance risk for one
specified public candidate; the finding remains unresolved and no independent
legal review is implied. The decision and its exact scope are in
[RELEASE-RISK-DECISION.md](RELEASE-RISK-DECISION.md). A separate scoped check
requires that decision, a clean public candidate history, checksum-verified
font references and the exact accepted nine-variant archive. The ordinary gate
remains conservative for other distributions, including the private history.
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
- Expand physical iOS coverage beyond the one tested device and validate any
  intended browser host. Complete stress, memory and malformed-input testing.
- Test the release-profile bundle's intended remote URL, checksum and a fresh
  no-Rust consumer on each supported platform after the binary is available.
  `Package.swift` is configured for that candidate URL, which must not be
  treated as verified until the public download and consumers pass.
- Pin and record SDKs, compiler flags and environment; perform independent
  rebuild comparisons before claiming bit-identical binaries. A deterministic
  ZIP and Cargo lockfile alone do not establish reproducible compilation.
