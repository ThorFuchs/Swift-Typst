# Math font fallback probe

This probe originally used the Book-era bridge with bundled fonts **disabled at runtime**,
Libertinus Serif Regular and STIX Two Math supplied by the caller. It compiles
one implicit and one explicit math-font document and prints warnings. Use
`pdffonts` on the PDFs to inspect the actual embedded font. For example on a Mac
with STIX Two Math installed:

```sh
swift run --package-path Spike/LicenseRelease FontProbe \
  Rust/fonts/LibertinusSerif-Regular.otf \
  /System/Library/Fonts/Supplemental/STIXTwoMath.otf /tmp/typst-font-probe
pdffonts /tmp/typst-font-probe/implicit.pdf
pdffonts /tmp/typst-font-probe/explicit.pdf
```

The second source explicitly sets `STIX Two Math`; the first exercises Typst's
default. The exact result depends on the supplied font files and toolchain.
This is a narrow behavior test: `useBundledFonts: false` does **not** remove
compiled-in fonts from a binary. It therefore does not prove a GUST-free
distribution or replace the broader corpus in the release plan. If a
font is selected for distribution, use a separately verified, pinned upstream
release and include its required license and copyright notices.

If `fonttools` is installed, compare cmap coverage as follows. Codepoint counts
alone do not prove actual math layout support or fallback quality:

```sh
python3 Spike/LicenseRelease/compare-cmap.py \
  /path/to/NewCMMath-Regular.otf /System/Library/Fonts/Supplemental/STIXTwoMath.otf
```

## Paired math-font corpus

`CorpusProbe` compiles the same six fixtures with exactly one math font at a
time. Both runs receive the same Libertinus and DejaVu text fonts, explicit
math font rule, fixed clock and page settings. This compares those selected
faces, not the complete production font family or the engine's default math
rule. The Book-era bridge contained GUST font bytes. The corpus covers
formulas, matrices, accents, multilingual text, rare arrows and four-page text.

For the recorded comparison, download the [publisher's STIX Two v2.13 b171
static OTF ZIP](https://github.com/stipub/stixfonts/releases/tag/v2.13b171)
into a temporary directory, verify its SHA-256 is
`b5ec34636e117ec97e71e6b89ad2718618184329bbb3d3be5d1e3b0f8ed52789`,
and extract it. The `STIXTwoMath-Regular.otf` used has SHA-256
`3a5f3f26f40d5698b3c62dd085d48d6663696a3f80825aab8b553d5097518e8c`.
The author supplies its [OFL license](https://github.com/stipub/stixfonts/blob/v2.13b171/OFL.txt).

```sh
swift run --package-path Spike/LicenseRelease CorpusProbe \
  Spike/LicenseRelease/Corpus /tmp/typst-corpus-output \
  /path/to/NewCMMath-Regular.otf /tmp/static_otf/STIXTwoMath-Regular.otf \
  Rust/fonts/LibertinusSerif-*.otf Rust/fonts/DejaVuSansMono*.ttf
python3 Spike/LicenseRelease/compare-corpus.py /tmp/typst-corpus-output
```

Use a new or empty output directory. Poppler's `pdffonts` and `pdftotext` are
required by the comparison. The report validates the selected embedded math
fonts, warnings, and the known rare-arrow fallback, then emits page counts,
raw-extracted-text differences and font inventories. Differences in extracted
text or geometry warrant inspection and are not automatically classified as
failures. They do not establish PDF accessibility or visual equivalence.

## Disposable STIX bridge candidate

This historical script requires a Book-era checkout. The current V1 source
already uses STIX, so it intentionally stops rather than producing a redundant
copy. In that earlier checkout it prepares a separate copy, checks the exact
STIX files and OFL text, removes
the seven selected NewCM fonts from that copy, embeds five STIX faces, and
installs a Typst library show-set recipe for the default math font. It does not
modify the repository's production bridge. It is a research candidate: the
notices and license gate are intentionally overinclusive and unresolved; the
existing production `build-artifact.sh` font verifier is specific to the Book
font and is not a verifier for this candidate. Do not publish the candidate.

Use Rust 1.94.1 and Swift 6.4.2 with the extracted official STIX fonts described
above, and `OFL.txt` from the same tagged release:

```sh
python3 Spike/LicenseRelease/prepare-gust-free.py \
  --stix-dir /tmp/static_otf --ofl /tmp/OFL.txt --output /tmp/typst-stix-candidate
CARGO_TARGET_DIR=/tmp/typst-stix-rust cargo build --locked \
  --manifest-path /tmp/typst-stix-candidate/Rust/Cargo.toml --target aarch64-apple-darwin
python3 /tmp/typst-stix-candidate/Scripts/assemble-artifact.py \
  arm64-apple-macosx /tmp/typst-stix-rust/aarch64-apple-darwin/debug/libswift_typst_bridge.a \
  --rust-target aarch64-apple-darwin --rust-version "$(rustc --version)" --profile debug
SWIFT_TYPST_TEST_NEWCM_MATH="$PWD/Rust/fonts/NewCMMath-Regular.otf" \
SWIFT_TYPST_TEST_CORPUS="$PWD/Spike/LicenseRelease/Corpus" \
  swift test --package-path /tmp/typst-stix-candidate
```

The copied suite removes the single production assertion specifically requiring
Book and adds candidate-specific tests. The NewCM font is supplied externally
only for the override test, so it must not be copied into the candidate. The
corpus directory is read for tests only. A separate byte/feature check requires
the source directory of Cargo's locked `typst-assets` 0.15.1:

```sh
python3 Spike/LicenseRelease/verify-gust-free.py \
  --candidate /tmp/typst-stix-candidate \
  --archive /tmp/typst-stix-rust/aarch64-apple-darwin/debug/libswift_typst_bridge.a \
  --assets-dir /path/to/typst-assets-0.15.1
```

This searches for exact source bytes, not transformed copies. Repeat it on each
actual target archive and inspect all artifacts and source-distribution paths.

## krilla source evidence and numeric alternative

`prepare-krilla-evidence.py` produces a deterministic **review-only** ZIP from
the unmodified crates.io archive, its pinned checksums and the captured upstream
notices. It neither publishes a source offer nor establishes what rights apply:

```sh
python3 Spike/LicenseRelease/prepare-krilla-evidence.py \
  --crate /tmp/krilla-0.8.2.crate --output /tmp/krilla-evidence.zip
```

`KurboProbe` compares the current quadratic-to-cubic numeric formula with
Kurbo's public `QuadBez::raise` on 100,000 deterministic examples. Kurbo is
already in the lockfile under MIT or Apache-2.0. The probe does not replace the
attributed method, assess complete PDF paths, or determine its licensing:

```sh
cargo run --locked --manifest-path Spike/LicenseRelease/KurboProbe/Cargo.toml --release
```

`prepare-krilla-kurbo.py` creates a second **review-only** copy of the candidate
and swaps the attributed method for an experiment calling Kurbo. It retains the
upstream NOTICE and license references. This is not clean-room work, does not
establish independent provenance, and must not be released. The updated
artifact-provenance scripts hash files under `Rust/vendor`, but hashes alone do
not provide corresponding source or resolve the other release questions.

```sh
python3 Spike/LicenseRelease/prepare-krilla-kurbo.py \
  --base "$PWD" --crate /tmp/krilla-0.8.2.crate \
  --output /tmp/typst-krilla-kurbo
cargo update --offline --manifest-path /tmp/typst-krilla-kurbo/Rust/Cargo.toml -p krilla
cargo build --offline --locked --manifest-path /tmp/typst-krilla-kurbo/Rust/Cargo.toml \
  --target aarch64-apple-darwin
```

The modified method emits a trace for its quadratic branch only when
`SWIFT_TYPST_TRACE_PATHS` is set. `CandidatePathTests.swift` supplies one SVG
fixture with quadratic/cubic paths, multiple subpaths and close operations.
Even a matching PDF for this fixture is not broad geometry or licensing proof.

## Linux VM smoke test

After building the candidate's `Tests/Consumer` executable with the verified
Swift 6.4.2 Static Linux SDK for `aarch64-swift-linux-musl`, run:

```sh
SWIFT_TYPST_TOOLCHAIN_BIN=/path/to/swift-6.4.2/usr/bin \
SWIFT_TYPST_LINUX_SYSROOT=/path/to/musl-1.2.5.sdk/aarch64 \
  sh Spike/LicenseRelease/run-linux-vm.sh /path/to/Consumer /path/to/alpine-virt-3.22.8-aarch64.iso
```

The script verifies the Alpine ISO checksum and boots a networkless temporary
VM. It removes debug symbols from a temporary executable copy so it fits the
512-MB guest, preserving the original executable. VM availability and
entitlements depend on the host environment.
