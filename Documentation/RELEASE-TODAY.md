# Swift-Typst: backward plan for a public V1 release

Planning snapshot: 19 November 2026. The desired outcome is a public SwiftPM
package with a synchronous PDF API and prebuilt binaries for the documented
targets. Dates, version numbers, URLs, and durations below are planning inputs,
not evidence of a release or a promise that all dependencies can be cleared
today.

## Release decision, working backwards

### 6. Publish and verify

After all preceding checks pass and the release owner approves the exact
distribution, publish an immutable binary asset and a semantic-versioned source
tag. Verify from genuinely fresh consumers that the public URL and checksum work
without Rust, custom linker flags, local artifacts, credentials, or caches.
Check every supported platform or accurately narrow the published support claim.
Announce V1 only after those checks. A preview is also a distribution and does
not waive third-party license obligations.

### 5. Freeze and test the distribution

Prepare a complete candidate including source, nine intended archive variants,
license notices, corresponding source and downstream instructions as determined
by the review. Check versions, hashes, font bytes and a reproducible asset ZIP.
Run the complete CI matrix on the final source snapshot and the explicit license
gate. Compare binary input provenance against that snapshot. Validate actual
downloaded artifacts with independent consumers on each claimed target.

The current `Package.swift` points to an ignored local artifact, and the CI
scripts assume that local declaration. A production remote target needs both a
URL and SHA-256, while the ZIP itself must first be built and uploaded. Implement
and test the transition rather than merely editing the manifest: for example,
build the binary from a frozen source commit, upload it under a separate asset
tag, then make a distribution commit with the immutable URL and checksum. Record
and verify that the distribution commit has identical bridge inputs, adapt CI's
local-artifact tests, and run fresh remote-consumer tests against the final tag.
An asset tag and package version tag have different roles; do not overwrite an
asset after publication. The exact release hosting and visibility sequence must
allow an unauthenticated public download to be tested.

The current evidence covers local STIX debug builds on macOS ARM64, iOS ARM64
simulator, Linux ARM64/musl and WASI; a macOS ARM64 optimized Rust build also
passed. The nine-variant CI that passed earlier used the Book font and does not
validate the current tree. After an earlier billing rejection and budget update,
two clean STIX candidate CI runs passed all eight platform jobs and combined
nine variants; their scope and checksums are recorded in
[PRODUCTION-STATUS.md](PRODUCTION-STATUS.md). The optional license release gate
was not requested in either run.
One physical iPhone PDF/font/diagnostic test has passed; broader physical iOS,
browser-hosted WASI, stress/memory, malformed input and independent build
reproduction remain unverified; decide claims and acceptance criteria
explicitly rather than treating simulator, WASI runner, and deterministic ZIP
as evidence for those scenarios.

### 4. Choose a public repository with an acceptable history

The development repository, `ThorFuchs/Swift-Typst-Internal`, is private. Its
initial `main` contains only a README, but its draft PR and branch include
historical NewCM font commits. A separate empty `ThorFuchs/Swift-Typst` has
been created as the intended public destination; GitHub reported it as private
when checked on 19 November 2026. Making the repository public exposes more than the tip of `main`:
review branches, tags, PR-associated commits/diffs, Actions history and logs,
and candidate assets. A squash onto `main` alone is not proof that earlier
commits and PR-associated data become inaccessible.

The least ambiguous containment option is a **new, clean public repository**
created from the reviewed current snapshot, without importing old refs,
PRs, Actions artifacts or Git objects; retain this repository privately for
history and evidence. Choose its name and canonical package URL deliberately.
Alternatively, keep the existing URL only after a qualified reviewer accepts
the historical distribution or all exposure paths have been assessed and
addressed. Renaming, replacing, deleting, or rewriting the existing repository
is a separate action and must not be done implicitly. Historical private
distribution obligations still require review even if the public release uses a
clean repository.

An earlier isolated working-tree snapshot contained 341 Git-visible files and
no exact byte match for the eight investigated NewCM faces. That historical
scan is not a complete license audit or validation of a later candidate. Recheck
the exact final snapshot; an exact-byte scan does not detect transformed font data.

On 19 November, a further scan of the prepared clean candidate examined all
six then-reachable commits, their 313 distinct Git blobs and the 78 file entries
inside the included krilla source archive. The exact bytes of the seven pinned
`typst-assets` NewCM references and historical `NewCM10-Book` were absent.
The references were checksum-verified first. This is a point-in-time scan of
those exact byte sequences, not a check for transformed data or other archives,
nor a determination of obligations from the older private distribution. Scan
the final public refs and distributed archives again before publication.

### 3. Clear third-party rights and obligations

**Critical path: krilla.** The exact krilla 0.8.2 NOTICE attributes
`content_draw_path` to resvg under MPL, while crate metadata states MIT OR
Apache-2.0. The documented upstream grants are useful evidence, not a complete
independent review of the whole method. The fastest plausible route is a
qualified reviewer deciding whether the original upstream code can be shipped
with a documented rights and compliance path, including exact source and notices
as applicable. The separately developed Kurbo experiment is not independent and
is not approved for distribution. An actually independent replacement requires
its own provenance and behavioral review and a fresh matrix.

Review packet: [KRILLA-INDEPENDENT-REVIEW.md](KRILLA-INDEPENDENT-REVIEW.md).
Record reviewer, decision, exact source and archive hashes, obligations, and how
each obligation reaches downstream users. Review the remaining curated fonts,
dependencies, SDK and toolchain notices for the exact distribution as well.
Only resolve entries in the license gate after the corresponding evidence and
required materials exist. On 19 November the owner indicated an independent
reviewer is **not available today**. This blocks the requested independently
reviewed clearance; there is no evidence-based time estimate for resolving it.

**Historical NewCM.** Current STIX sources and four local artifacts passed
exact-byte checks for the eight investigated NewCM files. Old Git commits and
previous candidate artifacts still contain them. A clean public repository
reduces the future release scope; it does not establish that earlier
distribution was compliant or cure obligations for prior recipients.

### 2. Freeze the functional V1 scope

V1 offers PDF compilation through the current synchronous Swift API and embeds
the curated STIX font set. It does not promise editor features, SVG/PNG export,
or NewCM-identical typography. The tested WASI runtime is not a browser test;
the separate physical-device test covers one iPhone. Publish platform support only
for the precise variants and environments verified in the final matrix. The
release owner decides whether additional promised physical-device, browser,
stress or accessibility validation is needed before a stable version.

### 1. Start now: parallel work and decisions

1. Prepare the exact reviewer packet and source/notice delivery proposal; route
   it to an independent reviewer when one is available. No external request has
   been sent. This is on the critical path and has no reliable same-day ETA.
2. Agree the canonical public repository/URL and V1 target claims. Prepare a
   clean snapshot and review its full contents before creating or changing a
   public destination. Keep the existing private history untouched.
3. Prepare the remote-binary manifest and CI transition in an isolated candidate;
   do not publish an asset before its licensing and contents are cleared.
4. Run a current nine-variant release-profile matrix as soon as a reviewable
   snapshot and usable CI are available. Expect queue/build time and possible
   iteration; verify billing rather than assuming the previous increase fixed
   it. Build candidates are not release approval.
5. Resolve physical-device, browser, stress and license-review acceptance items
   against the scope actually promised. Freeze source and notice hashes, run the
   explicit gate, then proceed to publication only if every required item passes.

If no independent reviewer can participate today, use today to finish the
candidate and all other checks; do not silently reclassify the open question,
clear the gate, or publish a preview containing the unresolved material.

## Time boxes, conditional on no failures

These are rough planning estimates, not measured guarantees. Work on the
review packet, clean snapshot and CI preparation can overlap.

| Workstream | Planning estimate | Dependency |
| --- | --- | --- |
| Clean snapshot, CI and remote-distribution preparation | 1–3 hours | Repository/URL and scope decisions; implementation and review. |
| Nine-variant release matrix | 1–3 hours after dispatch | CI allocation and runner availability; failures add time. |
| Final asset publication, manifest and clean consumer checks | 1–2 hours | Exact reviewed candidate, working hosting and all relevant gates. |
| Independent krilla and distribution review | Unknown | Reviewer availability and findings; not available today. |

The workstreams overlap but the final publication cannot precede review or
validated release artifacts. A later review, runner outage, failed build, or
required code change moves the finish and may require a new matrix.

## References

- [Production status and tested targets](PRODUCTION-STATUS.md)
- [Detailed license and font evidence](RELEASE-LICENSE-EVIDENCE.md)
- [Detailed clearance plan](RELEASE-CLEARANCE-PLAN.md)
- [GitHub visibility consequences](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [GitHub on history and pull-request references](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [SwiftPM binary target URL and checksum](https://docs.swift.org/latest/documentation/packagedescription/target/)
- [Mozilla MPL 2.0 FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)
