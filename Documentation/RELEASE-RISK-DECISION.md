# Release owner's krilla risk decision

On 19 November 2026, the release owner explicitly chose to document and accept
the remaining krilla provenance risk for the proposed public release. This is a
business risk decision, not an independent legal opinion, a finding that every
right has been established, or a new license grant.

The decision addresses the pinned krilla 0.8.2 distribution: its crate metadata
declares `MIT OR Apache-2.0`, while the separately captured upstream NOTICE
attributes the complete `content_draw_path` method to resvg and references the
MPL. Relevant resvg contributors later granted MIT/Apache terms for their
contributions, but the full method's origins and the scope of those grants have
not been independently resolved. If the distribution terms are inadequate, a
rights holder could request correction or removal, and downstream distributors
could be affected. The owner accepts this residual uncertainty for the scope
below, with attribution, source and notices preserved.

## Scope and safeguards

- krilla 0.8.2 crate SHA-256:
  `27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33`.
- Upstream krilla NOTICE SHA-256:
  `7aa87a70e18c9c160b5a14e24b46a8e407858b21fed635920c701657b4bd7976`.
- Cargo.lock SHA-256:
  `281020646050f2e17aee92329a442c4425dcfbba0e1b37a7a553b9fac3f60bb1`.
- Exact nine-variant CI candidate ZIP SHA-256:
  `c27788475defb885943d978406ab787a87339314251b9a3305e5499207c1cf76`,
  built from commit `04a0f7fc770a438980217cc9d3ccc37aac994735`.
- Proposed SwiftPM release version `1.0.0` and binary location:
  `https://github.com/ThorFuchs/Swift-Typst/releases/download/bridge-v1.0.0/CTypstBridge.zip`.
  This address and its public consumer flow must be verified after publication.
- Deliver the unmodified krilla source archive and captured notices with the
  binary bundle; provide clear downstream instructions and retain access to the
  source and applicable licenses. Artifact tooling checks the bundled contents;
  final public download and downstream delivery remain to be tested.
- Keep the uncertainty visible in the third-party inventory and documentation.
  An independent review was not available at the time of this decision.

The public source history is intended to start from the separately prepared
clean candidate. The earlier private repository and its historical NewCM files
are outside this krilla risk decision and must not be published by importing
old refs or artifacts. Their prior private distribution remains a separate
question; removing the fonts from the public candidate does not decide it.

Changes to krilla, its attributed code or notices, the dependency lockfile,
included source, archive content, public-history scope, or applicable licensing
evidence require a new review and decision. A later release must not silently
inherit this decision. See [the distribution proposal](KRILLA-DISTRIBUTION-PROPOSAL.md)
and [license evidence](RELEASE-LICENSE-EVIDENCE.md).
