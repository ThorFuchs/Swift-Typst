# krilla 0.8.2 source and notices

The adjacent `krilla-0.8.2.crate` is the unmodified source archive used by
the Cargo lockfile to build the bundled bridge. A `.crate` file is a gzip
compressed tar archive; unpack it with `tar -xzf krilla-0.8.2.crate`.

- Archive SHA-256: `27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33`
- Upstream archive: <https://static.crates.io/crates/krilla/krilla-0.8.2.crate>
- Cargo VCS revision: `3ffdf0588cf98050aad6edba51ca70162e1fb5b5`
- The archive's `src/content.rs` SHA-256:
  `9e59b2c77b73b36caedacfe80894d1cce7fd6fe6f7438ea24fda2019391a980c`

The published crate declares `MIT OR Apache-2.0`. Its separately distributed
upstream [NOTICE](../../Upstream/krilla/NOTICE.md) attributes the
`content_draw_path` method to resvg and refers to the MPL. The original
krilla [MIT](../../Upstream/krilla/LICENSE_MIT) and
[Apache-2.0](../../Upstream/krilla/LICENSE_APACHE) texts and an
[MPL-2.0 reference text](../../Upstream/krilla/MPL-2.0-reference.txt) are
included. The precise rights and license terms applicable to the attributed
method remain under review; the reference text is provided for transparency,
not as a declaration that it applies to the entire crate.

This directory and those notices are included in each bridge artifact under
`CTypstBridge.artifactbundle/notices/`. Distributors of the bridge or apps
containing it should retain the applicable notices and provide recipients access
to the applicable source and license terms. The archive covers krilla itself;
it is not an inventory or source offer for every transitive component. See
the enclosing [third-party evidence](../../README.md) and its inventory.
