# krilla replacement: independent review packet

Status: **not approved for release**. V1 currently uses the original pinned
krilla 0.8.2. The separate Kurbo-based experiment was written after inspecting
the attributed method, so it is not a clean-room implementation and its
existence does not establish rights to redistribute the derivative. This packet
identifies exactly what a reviewer would need to decide; no message has been
sent to a third party.

## Inputs and provenance

- The exact original crate is [krilla 0.8.2](https://static.crates.io/crates/krilla/krilla-0.8.2.crate),
  SHA-256 `27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33`.
- Its separately captured [upstream NOTICE](../Notices/Upstream/krilla/NOTICE.md)
  attributes the entire `content_draw_path` method to resvg under MPL. It must
  not be removed merely because Cargo metadata states MIT OR Apache-2.0.
- [Kurbo 0.13.1](https://docs.rs/kurbo/0.13.1/kurbo/struct.QuadBez.html#method.raise)
  is already a locked transitive dependency and declares Apache-2.0 OR MIT. Its
  public degree-elevation operation supplies cubic control points from a
  quadratic Bézier; it does not by itself provide an independent implementation
  or license of the complete krilla method.
- The reproducible experimental transformation is in
  [prepare-krilla-kurbo.py](../Spike/LicenseRelease/prepare-krilla-kurbo.py).
  It verifies the original crate and `content.rs` checksums, copies the upstream
  notice/license evidence, changes the one method, and uses a local Cargo patch.
  Read the original and generated versions and assess their actual provenance;
  this is not a claim that the replacement is untainted.

## Behavioral contract to verify

For each path segment, emit the corresponding PDF drawing operation. Quadratic
segments require degree elevation to a cubic using the current point, control
point and endpoint; cubic segments preserve their two controls and endpoint.
Exercise move, line, quadratic, cubic, close, multiple subpaths, repeated
closes, degenerate and extreme coordinates, transformations, fill and stroke.
Test specifically what current point is used for a quadratic after a close:
the experimental replacement deliberately preserves the previous method's
state behavior and must not silently be assumed to fix or reproduce PDF path
semantics in every case.

The local experiment passed 22 candidate macOS tests. One SVG fixture contained
lines, quadratic and cubic curves, close operations, transformations and
fractional coordinates. Tracing observed eight quadratic operations; the two
PDFs happened to be byte-identical for that fixture. A separate deterministic
100,000-input numeric probe saw rounding differences in 16,188 of 200,000
control coordinates. Neither result establishes equivalence for arbitrary
paths, physical platforms, malformed input or rendering engines.

## Reproduce the candidate for review

```sh
python3 Spike/LicenseRelease/prepare-krilla-kurbo.py \
  --base "$PWD" --crate /path/to/krilla-0.8.2.crate \
  --output /tmp/swift-typst-krilla-review
cargo update --offline --manifest-path /tmp/swift-typst-krilla-review/Rust/Cargo.toml -p krilla
```

Then compare `Rust/vendor/krilla/src/content.rs` with the verified original
crate, inspect the generated Cargo.lock and bundled notices, build with the
pinned Rust toolchain, and execute the path, Swift API, PDF and platform tests.
Use `SWIFT_TYPST_TRACE_PATHS=1` only for the experimental quadratic-branch
trace. The trace is diagnostic and must not become production behavior.

## Decisions before adoption

1. Determine whether the documented original resvg grants and krilla terms
   cover the exact original method, or whether a conservatively compliant MPL
   distribution is available. If so, record exact corresponding source, notices
   and downstream delivery obligations.
2. If those rights cannot be established or are unsuitable, obtain an actually
   independent implementation and review. Establish its rights and history;
   do not infer independence from a textual diff or from the Kurbo dependency.
3. For any approved local patch, commit the complete audited source and lockfile,
   regenerate the license inventory, hash all build inputs, provide any required
   source and notices to downstream recipients, and run the release matrix. The
   inventory now rejects local Cargo dependencies outside `Rust/vendor` and
   records vendored crates; artifact assembly hashes that directory and rejects
   symlinks. Other external/path inputs still require explicit review.
4. The release owner must review the evidence and decide whether the exact
   distribution is cleared. Until then retain the unresolved krilla gate.
