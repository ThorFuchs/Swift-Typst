# Third-party license evidence

`Rust/inventory.json` is a conservative Cargo metadata superset for the pinned
`Rust/Cargo.lock`: all 298 registry packages, including target-conditional and
build-time packages. It records the declared expression, authors, repository,
Cargo VCS commit where provided, and SHA-256 references into `Rust/texts/`.
Those files contain every recursively discovered LICENSE, LICENCE, COPYING and
NOTICE file from the crates, plus the pinned upstream files below. Inclusion in
this inventory does not establish that a package is present in every binary.

`Upstream/manifest.json` maps supplemental files to exact repository commits.
Cargo's published archives omit several workspace-root notices; the captured
Typst and krilla NOTICE files are particularly important. Glidesort declares
`MIT OR Apache-2.0` in its published Cargo manifest and pinned upstream commit,
but neither archive contains a license file. The README independently declares
the same dual license. The inventory records the Apache-2.0 option, includes
the exact author metadata and the standard Apache license text, and does not
invent a copyright statement.

`typst-assets-0.15.1-NOTICE.txt` is the unmodified upstream notice; it is
deliberately overinclusive for our current font selection. The five bundled
STIX Two faces are covered by [STIX-Two-OFL.txt](STIX-Two-OFL.txt), from the
[v2.13 b171 release](https://github.com/stipub/stixfonts/tree/v2.13b171)
(SHA-256 `0c8825913b60d858aacdb33c4ca6660a7d64b0d6464702efbb19313f5765861a`).
`NewComputerModern-8.1.1-License.txt` is the historical font package's
[license file](https://mirrors.ctan.org/fonts/newcomputermodern/License.txt)
(SHA-256 `8641346ee391ff97eb66c70f3d5d695792cf9c5b3c5d748c6158d49cf79646e3`).
The GUST font license references the LaTeX Project Public License;
`LPPL-1.3c.txt` preserves the [official LPPL 1.3c text](https://www.latex-project.org/lppl/lppl-1-3c.txt)
(SHA-256 `c1ae6e179a6d28bbd5c483fbacc744acc75e922d598281dc3390aab26126e163`).
`RustToolchain-1.94.1/` reproduces the Rust distribution's standard-library
copyright inventory and license texts for the compiler used to build the bridge.
The Swift and OS SDKs used by downstream apps have their own licensing and SBOMs;
this directory does not purport to establish all obligations of a consuming app.

`Source/krilla/` contains the exact unmodified crates.io source archive matching
the pinned Cargo.lock checksum, together with recipient instructions. Bridge
assembly includes this directory and the upstream krilla notices in every
artifact; packaging checks the archive against the lockfile and checks that the
bundle's notice files match the recorded source. This provides a self-contained
candidate source-delivery path for krilla, not a legal determination or a
source offer for every dependency. Applicability, scope and downstream obligations
remain open as explained below.

## Release-blocking questions

The exact krilla upstream NOTICE states that `content_draw_path` was adapted from
resvg and refers to an MPL license. The function and its attribution comment
are present in the pinned `krilla` crate, although krilla's Cargo metadata says
`MIT OR Apache-2.0` and the separately resolved `resvg` version declares
`Apache-2.0 OR MIT`. The NOTICE does not identify the original resvg version,
its exact MPL terms, or any relicensing grant. `Upstream/krilla/` contains the
pinned krilla notice and an MPL-2.0 reference text; it does **not** establish
which license applies to the copied code. The source provenance and applicable
redistribution obligations need to be resolved before distributing a release.
A license-list metadata scan alone cannot resolve this conflict.

The same method and attribution are present in krilla's
[September 2024 source](https://github.com/LaurenzV/krilla/blob/021114146242/src/content.rs),
before the resvg relicense. The resvg project records the later change to dual
licensing in its [relicensing issue](https://github.com/linebender/resvg/issues/838)
and [0.45.0 changelog](https://github.com/linebender/resvg/blob/main/CHANGELOG.md).
Those facts do not by themselves establish the rights to the specific copied
implementation; its original authors and the relevant grant must be checked.

The current `Rust/fonts/manifest.json` contains Libertinus, STIX Two and DejaVu
faces, with no NewCM font. The upstream `typst-assets/fonts` feature is
disabled. The archive verifier checks known upstream NewCM font bytes; an
additional exact-byte check for the historical NewCM10-Book face can be enabled
with `--excluded-book` or `SWIFT_TYPST_EXCLUDED_BOOK_FONT`. An exact-byte search
is supporting evidence, not proof that no transformed font material exists.

Earlier commits and candidate binaries included NewCM. The full upstream notice
remains unmodified and mentions NewCM10-Regular (GPL-3-or-later with Font and
Distribution Exceptions) and other GUST/LPPL faces. Before publishing source,
Git history or prior artifacts, review their actual content and distribution
obligations, including the GUST/LPPL Work and source questions documented in
[RELEASE-LICENSE-EVIDENCE.md](../Documentation/RELEASE-LICENSE-EVIDENCE.md).
Removing a file from the current tree does not remove it from earlier commits.

Regenerate/check the Rust inventory using the documented command in
`Scripts/collect-license-evidence.py`. Changes to Cargo.lock, upstream evidence,
or collected texts must be reviewed and included in each shipped bundle.
