# Font selection investigation — 18 November 2026

This document records the historical Book-font investigation. As of 19
November the V1 source has moved to a STIX Two font set; the Book-based build
and fixture results below do not describe the current default. See
[RELEASE-LICENSE-EVIDENCE.md](RELEASE-LICENSE-EVIDENCE.md) for the STIX
comparison, remaining provenance questions and experimental validation.

`typst-assets` 0.15.1's `fonts` feature embeds 17 fonts, including
`NewCM10-Regular.otf`. Its notice identifies that particular face as
GPL-3-or-later with Font and Distribution Exceptions. Those bytes occur
contiguously in the original macOS ARM64 spike's Rust static archive. Setting
`useBundledFonts: false` does not remove compiled-in asset bytes and therefore is
not a distribution-level exclusion.

## Local macOS debug spike

An isolated copy of the Rust bridge disabled the `typst-assets/fonts` feature
and embedded the other 16 fonts from the exact 0.15.1 assets crate directly.
The original `NewCM10-Regular.otf` byte sequence was absent from that spike's
static archive. This exact-byte test is evidence for the tested build, not a
formal license scan or proof about every release target.

The temporary preparation script used for this early experiment is retained in
the private development archive; the public candidate omits that old spike,
which enables Typst's entire font bundle. The Book-font comparison below used
the existing caller-supplied-font API separately.

We compiled two fixed-clock, fixed-creation-date PDF fixtures using the original
bridge and the spike:

- A default text and math document produced byte-identical PDFs on both builds
  (SHA-256 `dd6a679fff16bd201207876c9461786fea07bd09ded856c66cf49af85d7ac928`).
  The PDF used Libertinus Serif and New Computer Modern Math.
- A document explicitly selecting `New Computer Modern` no longer had a regular
  face. Typst selected the retained **Bold** face for regular body text without a
  warning. Simply omitting Regular would thus silently change some documents.

The same spike was tested with `NewCM10-Book.otf` supplied explicitly using
`TypstProject.fonts`, not embedded in the spike binary. This face was downloaded
from [CTAN's NewComputerModern 8.1.1 distribution](https://www.ctan.org/tex-archive/fonts/newcomputermodern/otf),
SHA-256 `005f9b4e13b2a133df36d4ebfbb8f5fe402854bcb5882deb500b9c0f72b1bb49`.
Its embedded metadata states GUST Font License, and upstream's asset notice
assigns NewCM fonts other than `NewCM10-Regular` to that license. With Book
supplied, the default PDF was still byte-identical, and the explicit NewCM
fixture embedded **NewCM10-Book** for body text and NewCM10-Bold for its heading.
The explicit-font PDF differed from the original, as expected for a different
face. FontTools compared their best Unicode cmaps: Regular has 4,025 mapped
codepoints and Book 3,986; 45 Regular codepoints are absent from Book and 6
are present only in Book. Metrics, shaping, fallback, math and language
coverage have not been comprehensively assessed.

In a separate local test with the prepared production bridge, explicitly
supplying the original Regular font through `TypstProject.fonts` restored the
original explicit-NewCM fixture byte-for-byte
(`14cde28747221b6df7385458b77dc9fb71181dabdd16ddcb203ab41b0663aefd`).
That is evidence for this fixture only. Supplying or redistributing a font
remains subject to that font's own terms.

## Production preparation

A selectively bundled, pinned font set with Book as a substitute is a plausible
future implementation, but it changes output for explicit NewCM users and is
not a drop-in replacement. The existing API can accept a caller-supplied font.
Following the decision to prepare Book as a replacement, the draft bridge now
embeds the 16 selected Typst-assets faces plus NewCM10-Book. The files and their
hashes are recorded in `Rust/fonts/manifest.json` and build provenance. The
upstream `fonts` feature is disabled, and the build checks each static archive
for the original Regular bytes and for the Book bytes. Explicit NewCM output
can change, including fallback for the 45 codepoints absent from Book.
The prepared production bridge reproduced the original default fixture's PDF
byte-for-byte and used Book for the explicit-NewCM fixture. The 16-test Swift
suite passed locally on macOS and WASI, iOS simulator XCTest passed, and a
separate consumer including the Book check ran on ARM64 Linux/musl.

This remains a draft until the new production build is tested on the intended
platforms, including representative multilingual documents, and the exact
license/attribution treatment is reviewed for distribution. The separate
krilla/resvg provenance issue remains open.
