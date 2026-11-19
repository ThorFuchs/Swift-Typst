# krilla: proposed conservative distribution route

Working proposal, 19 November 2026. This is preparation for review and does not
approve a release, establish ownership, grant rights, or assert that MPL 2.0
actually applies to every part of the pinned krilla code. The license gate stays
blocked until the exact distribution and outstanding rights are decided.

## Candidate and evidence

- Keep the upstream krilla 0.8.2 implementation unchanged. Its published Cargo
  package declares `MIT OR Apache-2.0`; the separately captured upstream NOTICE
  attributes the whole `content_draw_path` method and an SVG test suite to
  resvg and refers to the MPL. These statements need reconciliation.
- The pinned [crates.io archive](https://static.crates.io/crates/krilla/krilla-0.8.2.crate)
  has SHA-256 `27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33`.
  Its `src/content.rs` has SHA-256
  `9e59b2c77b73b36caedacfe80894d1cce7fd6fe6f7438ea24fda2019391a980c`,
  and Cargo VCS metadata identifies commit `3ffdf0588cf98050aad6edba51ca70162e1fb5b5`.
- A local inspection of that exact crate found 78 regular files, no
  `assets/svgs` or `src/tests` entries and no archive links. Its manifest
  excludes `src/tests`. This says nothing about other crates or external test
  data and does not remove the attributed implementation from the library.
- The 2024 [resvg relicensing issue](https://github.com/linebender/resvg/issues/838)
  records dual-license grants from relevant contributors. The whole attributed
  method's original contributors and applicable terms are not yet established;
  see [RELEASE-LICENSE-EVIDENCE.md](RELEASE-LICENSE-EVIDENCE.md).

A locally regenerated review bundle had SHA-256
`c4694ed3c7718465eaa57f42d9d976f3ffc4204b839116df4c924cf114954374`.
It contains the unmodified crate plus the captured upstream NOTICE and license
texts. Recreate it from the verified crate using
`Spike/LicenseRelease/prepare-krilla-evidence.py`. It is review material, not
an accessible source offer or a legal determination.

## If the conservative MPL route is established

Subject to confirming the actual upstream grant, affected files and applicable
license version, a concrete candidate distribution would:

1. Preserve applicable krilla and resvg copyright and license notices, include
   the correct license text, identify the exact covered files and keep a record
   of any modifications. Do not describe the entire bridge as Apache-only.
2. Make the exact covered source in its required form durably available to every
   recipient of each prebuilt archive, including later SwiftPM consumers. A
   separately hosted source asset plus the corresponding source and instructions
   within the binary's notices is one possible implementation; verify the actual
   mechanism and required scope before using it. Preserve source identity with
   hashes and link it to the exact archive and release.
3. Explain the relevant conditions to downstream redistributors, while licensing
   Swift-Typst's own original code under Apache-2.0. Mozilla's
   [MPL 2.0 FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/) explains its
   file-level model and discusses static linking; it is not itself the license.
4. Exercise the source and notice delivery from a fresh consumer of the exact
   public asset. Include all other applicable dependency and font notices and
   maintain source availability as required.

The candidate implementation now bundles the exact unmodified krilla crate and
instructions under `notices/Source/krilla/`, alongside the captured notices, in
each bridge artifact. Assembly checks its checksum against the hardcoded pinned
version and Cargo.lock; packaging verifies the bundle's notice tree against
source provenance. Tests exercise source presence and rejection of missing or
modified evidence. This self-contained source-delivery candidate must still be
tested with the actual public assets and reviewed for completeness and ongoing
availability. Do not clear the license gate merely because these files exist.

## Decision still required

A qualified independent reviewer or the appropriate release decision process
must establish which rights cover the complete attributed method and what must
be distributed, including whether the proposed conservative MPL route is valid.
Record the evidence, residual uncertainty, distribution scope and decision.
If it cannot be established or is unsuitable, pursue an independently sourced
replacement and review it and its platform behavior before shipping. Risk
acceptance by itself does not create a missing copyright license.

Separately, verify the historical NewCM distribution, the remaining dependency
and font notices, and the new public repository's exact contents and references.
