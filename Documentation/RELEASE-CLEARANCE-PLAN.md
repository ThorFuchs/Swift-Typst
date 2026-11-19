# Release clearance plan

This is an engineering and evidence plan, not a legal determination. The release
owner must approve the exact intended distribution and, where interpretation or
rights remain uncertain, obtain appropriate legal review. No release is
approved by this document or by removing an inventory entry.

Update, 19 November: V1 now adopts the STIX route described below. References
to the former Book-based tree and prospective fallback are retained as the
historical reasoning. The GUST/LPPL questions still apply to earlier Git
history and artifacts; krilla remains unresolved.

The examined commits, CTAN archive, font hashes and expanded corpus results are
recorded in [RELEASE-LICENSE-EVIDENCE.md](RELEASE-LICENSE-EVIDENCE.md).

## Decision and scope

V1 now uses the STIX font set. Review historical NewCM distribution and pursue
either a documented rights/compliance path or an independently reviewed
replacement for the krilla/resvg code. Favor evidence and an upstream fix over
a permanent fork. No outside messages have been sent as part of this plan.

The object of review is the exact source commit, Cargo.lock and patches, bundled
fonts, SwiftPM source package, each static archive and combined release ZIP,
notices and source offers, and downstream redistribution on Apple platforms,
Linux and WASI. A private candidate or runtime font option is not evidence
that published source or binaries exclude a component. Record how source
archives, Git refs and historical commits, CI artifacts, tags and release
assets are exposed; removing a file from the current tree does not remove it
from existing history. Do not rewrite history without a separate decision.

## 1. krilla/resvg

**Preferred: establish rights and retain upstream code.** The pinned krilla
NOTICE explicitly attributes the whole `content_draw_path` method to resvg
under MPL, while krilla's crate metadata says `MIT OR Apache-2.0`. The upstream
[resvg relicensing discussion](https://github.com/linebender/resvg/issues/838)
contains a grant covering past contributions by the author of a matching
helper and by krilla's author. That is useful evidence, not by itself proof for
every part of this method or permission to discard the existing NOTICE.

1. Map the complete method, not only the matching mathematical helper, to its
   sources and revisions; record contributors, changes, applicable licenses,
   grants and corresponding exact source hashes. Check both the pinned krilla
   crate and the release-specific resvg revisions. Include the other copied
   sources and test assets in the NOTICE when determining what is distributed.
2. Ask the release reviewer to decide whether the evidence establishes a
   permissive grant for the full distributed method. If an upstream
   clarification or correction would be helpful, prepare a precise request with
   the evidence; send it only when explicitly authorized.
3. If rights permit redistribution under MPL-2.0, the next practical route is
   to comply with that license instead of rewriting the method: identify the
   covered source form and modifications, retain notices and license terms,
   and provide recipients the required access to exact corresponding source
   and information on their rights. The [MPL 2.0 FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)
   describes executable distribution and file-level scope. Confirm that the
   grant really applies to this derivative and review the complete obligations;
   the MPL reference text alone does not establish permission. Define how
   downstream SwiftPM consumers receive the notices and source information.
4. If the provenance/grant remains insufficient or these distribution terms are
   unacceptable, investigate an upstream correction or a pinned local Cargo
   patch. A replacement must be independently implementable from the SVG/PDF
   behavior, reviewed for provenance and license, and must eliminate all
   affected copied material from the resulting distributed source and builds.
   A superficial rewrite or deleting the attribution is not clearance. Test
   quadratic/cubic paths, close-path behavior, SVGs, PDFs, diagnostics and all
   supported targets. Record fork maintenance and an upstream-removal plan.

**Acceptance:** a reviewable provenance/rights decision, exact corresponding
source and notices where required, a documented downstream distribution path,
and tests against the exact shipped build. Update the gate only after that
specific finding has been resolved and the evidence archived.

## 2. GUST/LPPL fonts

**Historical distribution review.** Identify the relevant Work and manifest for
the previously bundled New Computer Modern 8.1.1 files, the
role of source files and any required change notices or source availability for
our curated font selection and static embedding. Compare the author's package
terms and font metadata with the [LPPL 1.3c](https://www.latex-project.org/lppl/lppl-1-3c.txt),
particularly its rules on complete and partial Works and compiled forms. Have
the release reviewer determine the resulting obligations for our distribution.
The current source no longer bundles these faces, but previous commits and
artifacts do. This question applies to the historical NewCM text faces
**and** all three historical NewCM math faces, not only Book.

**V1 font set.** Retain the separately reviewed Libertinus
and DejaVu faces, replace all seven NewCM faces (three math and four text) with
appropriately licensed alternatives, or omit a family with an explicit
compatibility policy. [STIX Two Math](https://github.com/stipub/stixfonts) is
used under OFL 1.1; pin a release from its publisher, verify hashes and
include its actual license/copyright and any other applicable notices. Do not
use a system-installed font as a distribution source without verifying its
origin and terms. Review each retained font independently.

A local macOS debug probe using Libertinus Serif Regular and the machine's
STIX Two Math 2.13 b171, supplied via `TypstProject.fonts`, produced two
single-page PDFs. With bundled fonts disabled at runtime, Typst used STIX in
both; `pdffonts` confirmed it. An implicit equation emitted `current font is
not designed for math`, while an explicit show-set rule emitted no warning.
The probe is in [Spike/LicenseRelease](../Spike/LicenseRelease/README.md).
This is not a GUST-free build: the current archive still contains embedded
GUST fonts. It tests one formula and does not establish general compatibility.
For these two local font files, FontTools' best Unicode cmap reports 4,887
codepoints in NewCMMath-Regular and 4,605 in STIX Two Math: 1,141 only in
NewCM (246 private-use) and 859 only in STIX (37 private-use). These counts are
not a measure of typographic or practical math support; they demonstrate why
coverage and real-document tests are necessary.

Typst 0.15.1's [equation implementation](https://github.com/typst/typst/blob/v0.15.1/crates/typst-library/src/math/equation.rs)
sets `New Computer Modern Math` in its built-in show-set rule. Investigate a
proper configuration/default-rule mechanism that selects the new face without
requiring every caller to edit source; verify precedence with explicit user
rules, imported files, source locations and diagnostics. If that cannot be
made reliable without a substantial engine patch, make the compatibility tradeoff
explicit rather than silently rewriting document source or suppressing warnings.

Compare the new set against the pinned baseline: ordinary text, explicitly
selected NewCM, bold/italic, equations, symbols, accents, stretching,
fractions, multilingual coverage, missing glyphs, fallback, page geometry,
PDF text extraction and accessibility. Record intentional differences; do not
claim byte-for-byte compatibility. Confirm behavior with caller-provided fonts.
After a decision, remove affected fonts from every intended distribution,
disable upstream feature inclusion, and check dependency features, vendored
files and release artifacts on every target. Exact-byte checks are supporting
evidence, not proof against all transformed or compressed copies.

**Acceptance:** either a recorded, approved GUST/LPPL compliance route with its
actual obligations implemented, or a verified replacement distribution with
new license evidence and documented output differences. Update the finding
only when the corresponding route is complete.

## 3. Final validation and release decision

1. Implement the chosen obligations, archive evidence and update the inventory;
   make the release gate reject missing evidence as well as open findings.
2. Rebuild release-profile variants from the exact final commit; check artifact
   provenance, notices, checksums, archive contents and the combined bundle.
   Rerun the full CI matrix and test a fresh SwiftPM consumer using the actual
   immutable release URL without local linker flags or Rust.
3. Complete the remaining product checks documented in
   [PRODUCTION-STATUS.md](PRODUCTION-STATUS.md): physical iOS, intended browser
   host, stress/memory/malformed-input coverage, SDK obligations and independent
   rebuild comparisons. Restore GitHub billing or the spending limit before
   rerunning the final CI; the successful older CI run does not validate the
   latest commit's changed notices.
4. The release owner reviews the exact distribution, compatibility changes,
   license evidence and test results. Only then clear the gate and publish.
