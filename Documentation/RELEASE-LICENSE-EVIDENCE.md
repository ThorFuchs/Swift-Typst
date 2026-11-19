# Release license and math-font evidence

Research snapshot, 18 November 2026. This records engineering evidence and
outstanding interpretation questions; it is not a legal opinion or approval.
The release gate remains blocked for krilla/resvg and historical NewCM
distribution. V1 adopted the STIX font set on 19 November; passages below
describing the Book-era source tree refer to the earlier snapshot.

## krilla/resvg provenance

- `Rust/Cargo.lock` pins `krilla` 0.8.2 with registry archive SHA-256
  `27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33`.
  The downloaded [crates.io archive](https://static.crates.io/crates/krilla/krilla-0.8.2.crate)
  matched that hash. Its `src/content.rs` SHA-256 is
  `9e59b2c77b73b36caedacfe80894d1cce7fd6fe6f7438ea24fda2019391a980c`,
  byte-identical to `crates/krilla/src/content.rs` at the Cargo VCS commit
  [`3ffdf058`](https://github.com/LaurenzV/krilla/tree/3ffdf0588cf98050aad6edba51ca70162e1fb5b5).
- The current 42-line `content_draw_path` matches the body in
  [`021114146`](https://github.com/LaurenzV/krilla/commit/02111414624240a2bc3e55de8bc642e32ae814fd),
  dated 1 September 2024, which moved it from `src/stream.rs` to
  `src/content.rs`. Git blame alone calls this move the origin; it is not the
  original creation. The previous body was already in `src/stream.rs` at
  [`d1ed0a27`](https://github.com/LaurenzV/krilla/commit/d1ed0a27b58c7c6188765d4c5fa2ce6d4c6e9f08),
  30 July 2024, and that commit copied it from the older `src/canvas.rs`.
- The `draw_path` implementation was added to `krilla-core/src/canvas.rs` in
  [`6379b4cd`](https://github.com/LaurenzV/krilla/commit/6379b4cd4b77fd5032c5e1bfa64e14143a3c9041),
  authored by Laurenz Stampfl on 13 July 2024. It already included the comment
  attributing code to resvg. Its direct parent does not contain that function
  in the same file. These observations trace the krilla history and refactors;
  they do not establish independent authorship of every attributed line.
- A matching quadratic-to-cubic helper appears in
  [`resvg` commit `95a469e5`](https://github.com/linebender/resvg/commit/95a469e5a4c90c2401f34fd8f06e8e49e7ea1fea),
  authored by Yevhenii Reizner on 25 May 2023, at
  `crates/usvg-parser/src/marker.rs`. That commit's `LICENSE.txt` is MPL-2.0.
  The pre-krilla [resvg v0.42.0 marker source](https://github.com/linebender/resvg/blob/v0.42.0/crates/usvg/src/parser/marker.rs)
  has the same five path-segment cases and the matching helper, although the
  operations are adapted and the implementations are not identical. Git blame
  for the compared loop and helper attributes 41 lines to the same 2023 commit;
  the commit replaces an earlier segment-collection mechanism, so this alone
  does not rule out earlier origins or resolve rights to the whole method.
  The [later relicensing issue](https://github.com/linebender/resvg/issues/838)
  records `RazrFalcon` and `LaurenzV` granting MIT/Apache-2.0 for their past
  and future resvg contributions. The method's full copied provenance, the
  scope of those grants and the current krilla NOTICE still require a review:
  the matching helper does not prove the origin of every remaining line.

**Release decision still needed:** review the full method, its actual grants
and whether an MPL-2.0 route applies to the derivative. For an MPL route,
identify the exact covered source and changes, retain applicable notices, and
provide a durable source-access mechanism and downstream instructions as
required. Do not treat the reference MPL text or an attribution alone as proof
that every right to distribute the derived code has been established. If this
cannot be resolved, evaluate an upstream change or independently reviewed
replacement as set out in [the plan](RELEASE-CLEARANCE-PLAN.md).

## New Computer Modern 8.1.1

The [CTAN package](https://ctan.org/tex-archive/fonts/newcomputermodern) obtained
for this investigation identifies itself as version 8.1.1. Its ZIP SHA-256 was
`9cc2e55835ab9adac227ccf1b8ed68bc0f73845489ea3533b88a1f56bd05d79a`;
its embedded `sfd.txz` SHA-256 was
`73f140c8fa850b1dc460518227332c71bb69ed0a60ede072860d60d85be49b68`.
CTAN mirror URLs can change contents, so these hashes identify the files
actually examined; they are not an immutable source-access mechanism.

- All seven NewCM OTF files in the Book-era `Rust/fonts/manifest.json` matched the
  corresponding CTAN ZIP files byte-for-byte. The `sfd.txz` contains a
  corresponding FontForge `.sfd` file for each of the seven; their headers
  name version 8.1.1 and the GUST Font License. This establishes
  correspondence of filenames and metadata, not a bit-reproducible build from
  those sources.
- The ZIP had 82 entries and the SFD archive had 42 entries. No entry in either
  archive contained `manifest` in its filename. The README describes the
  package and how to generate OTF files from SFD files, but the absence of a
  named manifest does not in itself establish that each font file is a separate
  LPPL Work or that the whole package is one Work.
- The author's `License.txt` separates NewCM10-Regular and other specifically
  named fonts under GPL-3-or-later with Font and Distribution Exceptions from
  the remaining GUST-licensed fonts. The seven selected faces are in the latter
  group. The GUST notice refers to LPPL 1.3c or later, and its font-renaming
  request is explicitly nonbinding. LPPL 1.3c distinguishes whole Works from
  partial distribution and discusses compiled forms; see the
  [license text](https://www.latex-project.org/lppl/lppl-1-3c.txt).

**Release decision still needed:** determine the Work's boundary and the
obligations for a subset embedded in a static archive, including source access,
notices and downstream distribution. A per-font SFD copyright line saying
"this work" is evidence to review, not a conclusive definition of Work.
The complete CTAN package includes the separately GPL-licensed faces, so
bundling the entire original package as a source-compliance measure has its own
scope and licensing implications. Do not publish it as a presumed fix without
review. If a reliable compliance decision cannot be reached, use the GUST-free
fallback plan, with its explicit output-compatibility costs.

## Controlled STIX Two Math comparison

The publisher's [STIX Two v2.13 b171](https://github.com/stipub/stixfonts/releases/tag/v2.13b171)
static OTF ZIP had SHA-256
`b5ec34636e117ec97e71e6b89ad2718618184329bbb3d3be5d1e3b0f8ed52789`.
Its `STIXTwoMath-Regular.otf` had SHA-256
`3a5f3f26f40d5698b3c62dd085d48d6663696a3f80825aab8b553d5097518e8c`
and matched the machine's STIX copy byte-for-byte. STIX is supplied under
[OFL 1.1](https://github.com/stipub/stixfonts/blob/v2.13b171/OFL.txt).
At the time of this comparison STIX had not yet been added; the current V1
working tree now includes the five selected STIX faces and their OFL notice.

The [reproducible corpus](../Spike/LicenseRelease/README.md) used the then-current
macOS ARM64 debug bridge, Swift 6.4.2, Poppler 26.04.0, a fixed clock, common
Libertinus/DejaVu faces and
separately supplied NewCMMath-Regular or STIXTwoMath-Regular. Both sides
explicitly select their math font and disable bundled-font use at runtime.
This is a controlled comparison of two single math faces; the Book-era binary
still contained GUST fonts and the comparison does not represent every NewCM
weight or an end-to-end GUST-free implementation.

| Fixture | NewCM pages | STIX pages | Warnings each | Raw PDF text |
| --- | ---: | ---: | ---: | --- |
| Calculus and scripts | 1 | 1 | 0 | differs |
| Matrices and accents | 1 | 1 | 0 | differs |
| Multilingual | 1 | 1 | 0 | equal |
| Text flow | 1 | 1 | 0 | equal |
| Rare arrows and fallback | 1 | 1 | 0 | equal |
| Long form | 4 | 4 | 0 | differs |

`pdffonts` verified the respective math faces. In the arrow fixture,
`pdftohtml -xml` identified NewCM Math for the tested arrows in the baseline
and DejaVu Sans Mono for the same text and math arrows in the STIX run; their
shapes and spacing visibly differ. Extracted-text differences in the sample
include line placement of a radical, delimiters/accents, and a superscript.
They are observations, not a verdict on PDF accessibility or correctness.
Visual inspection of the calculus, structures and arrow pages showed legible
samples and differences in glyph design and spacing. Additional real-world
math, language, missing-glyph, accessibility and all-target testing remains
necessary before releasing the selected replacement.

## Questions prepared for review

These are drafts for the release owner or an appropriately qualified reviewer.
No questions have been sent upstream.

For krilla/resvg:

1. For the exact 0.8.2 `content_draw_path` method and its resvg attribution,
   which original revision(s) and contributors are relevant to the complete
   method, including the five path-segment branches?
2. Do the documented resvg relicensing grants and krilla's own stated license
   cover the complete adapted method under Apache-2.0 or MIT? If not, which
   exact MPL grant, covered source files and redistribution steps apply?
3. For an unchanged statically linked build distributed through SwiftPM, what
   notices and durable source-access information must reach downstream users?

For New Computer Modern 8.1.1:

1. For the seven identified unmodified GUST-licensed OTF faces and corresponding
   SFD files, what is the boundary of each LPPL Work? Does the absence of an
   explicit manifest in the examined archive affect that determination?
2. Does selecting those faces and embedding their bytes in a static library
   constitute distribution of a complete Work, a Compiled Work, or a Derived
   Work under the relevant terms? Which notices, original/source access and
   change records are necessary for the exact binary and SwiftPM distribution?
3. Can those steps be met without redistributing separately GPL-licensed font
   files in our release artifacts, and what must downstream app distributors
   retain or make available?

## Experimental alternate bridge — 19 November 2026

A disposable copy generated by `Spike/LicenseRelease/prepare-gust-free.py`
replaces the seven selected NewCM files with five checksum-verified STIX Two
faces. It configures an equation show-set recipe in Typst's `Library.styles`
rather than prepending text to source documents. At that time the repository's
production bridge had not been changed. The candidate's old upstream license inventory
and notices are intentionally overinclusive and it is not a publishable build.

- macOS ARM64 debug: 22 Swift tests passed. The candidate suite removes the
  production Book-specific assertion, keeps the other production tests and
  adds seven candidate checks. These verify, among other things, no-warning STIX
  default math, a user-supplied NewCM math font selected by an explicit show
  rule, disabling bundled fonts, missing NewCM text diagnostics, STIX text and
  the six-document corpus without extra per-document rules.
- WASI debug: 19 Swift Testing tests passed with Swift 6.4.2. Three tests needing
  host font/corpus files were skipped; this is not browser-host testing. On
  this Mac the Swift.org 6.4.2 toolchain and `--disable-xctest
  --enable-swift-testing --build-system native` were needed to use the WASI
  Swift Testing runner.
- iOS 27.2 ARM64 simulator debug: the adapted PDF/math-font/diagnostic XCTest
  passed (1 test, 0 failures). No physical device was tested.
- Linux ARM64/musl debug: an independent SwiftPM consumer built with the
  checksum-verified Swift 6.4.2 Static Linux SDK and ran successfully in a
  networkless Alpine 3.22.8 VM. The VM used a temporary copy with debug symbols
  removed; its consumer checked default STIX math, imports, SVG, packages,
  options and diagnostics. This does not cover Linux glibc or x86_64.
- The macOS, iOS simulator, Linux musl and WASI archives were checked for the
  exact bytes of the seven selected NewCM faces and the upstream GPL-exception
  Regular face; none were
  found. All five selected STIX face byte sequences were found, and the Cargo
  feature tree did not enable `typst-assets/fonts`. These checks do not prove
  that transformed font data or other GUST material is absent from every
  distribution path.
- A local ZIP containing the macOS and WASI variants was consumed by separate SwiftPM
  packages on macOS and WASI without Cargo or manual linker flags. It was a
  local debug ZIP, not a downloaded release.
- A second local debug ZIP combined macOS ARM64, iOS ARM64 simulator, Linux
  ARM64/musl and WASI (SHA-256
  `e807e9dc5954b7c871eb0cbc76e6746901b0341ea439466f30dcde9e182ecbb5`).
  It is a local diagnostic artifact, not an approved or published release.
- The macOS debug test and ZIP consumer links reported an oversized `__eh_frame`
  warning from the linker. Assess the optimized release archive and any impact
  before claiming a warning-free release build. A subsequent macOS ARM64
  optimized Rust archive passed the current 21-test Swift suite without that
  linker warning; this does not cover the other release variants.
- Explicitly asking for `New Computer Modern` without supplying it now yields a
  missing-font warning. The replacement changes text/font availability and math
  typography, so it needs a deliberate compatibility decision, further font
  corpus and accessibility tests, all intended target builds, a fresh exact
  license inventory and release packaging before it can be released as V1.

After adopting STIX in the V1 working tree, an additional local scan compared
the exact bytes of all eight historical NewCM faces against 340 nonempty
Git-visible tracked or untracked files that existed at scan time. It found no
matches and skipped no symlinks. This was not a scan of ignored files, Git
objects, previously uploaded artifacts or transformed data. In particular,
commit `96ef6af` still contains NewCM font files, so the scope of any public
repository or historical distribution remains a separate release question.

## krilla alternatives and evidence packaging — 19 November 2026

The [current krilla source](https://github.com/LaurenzV/krilla/tree/cc194f14613ab5535bcb7919378f9fe524235cd0)
still has both the method attribution and the NOTICE's MPL reference; simply
updating to this upstream revision does not eliminate the question.
`prepare-krilla-evidence.py` checked the Cargo.lock crate checksum, exact source
revision and the captured upstream notice/license hashes, then produced two
byte-identical local review bundles. The unmodified source crate lacks the
workspace-root krilla NOTICE, so the bundle includes that separately. It is not
an accessible source offer and does not determine applicable rights.

The existing lockfile also contains `kurbo` 0.13.1, whose public
[`QuadBez::raise`](https://docs.rs/kurbo/0.13.1/kurbo/struct.QuadBez.html#method.raise)
performs quadratic-to-cubic degree elevation and whose declared license is
Apache-2.0 OR MIT. In a deterministic probe over 100,000 input triples with
coordinates from -10,000 to 10,000, 16,188 of 200,000 resulting control
coordinates differed bitwise from krilla's current f32 formula; the largest
observed absolute difference was 0.000976562. This supports feasibility but
not numerical identity or full path equivalence. A separate disposable candidate
replaces the method with a Kurbo-based experiment and retains the upstream
NOTICE. It was developed with access to the original method; it is not a
clean-room implementation and cannot establish independent provenance or clear
the rights question. The production bridge continues to use upstream krilla. The local
replacement passed all 22 macOS candidate tests. One traced SVG fixture
exercised its quadratic branch eight times and produced a PDF byte-identical to
the original-krilla candidate for that input, including tested close, cubic and
multi-subpath operations (both SHA-256
`ead51d6a7bde9da0d8e3cdaf9d5c6412c17fbace95cfeda33696585380ac6dee`
in this run). This does not establish equivalence for arbitrary paths. Broader
precision, close-path, PDF-rendering and cross-platform tests plus
provenance review remain required before adopting any patch. The artifact
scripts now hash files under `Rust/vendor` and reject symlinks there; tests
confirm a modified vendored file prevents packaging and symlinks block both
assembly and packaging. The local patched candidate recorded 82 vendored file
hashes. The license inventory includes local crates under `Rust/vendor` and
rejects other local Cargo dependencies instead of silently omitting them; the
experimental krilla fork was checked with eight license-evidence entries. Other
local inputs outside this directory are not covered by that artifact safeguard.
This does not supply corresponding source to recipients or make the patched
candidate releasable.
