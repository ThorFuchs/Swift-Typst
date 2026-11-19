# Swift-Typst: API and Swift 6.4 design review

Status: **design proposals**, 18 November 2026. These are not implemented
interfaces. Version 1's output format is **PDF only**. The roadmap and platform
gates are in [IMPLEMENTATION-ROADMAP.md](IMPLEMENTATION-ROADMAP.md).

## Design priorities

1. The smallest use case is one synchronous call and returns PDF bytes.
2. Keep warnings, precise failures, and reproducibility accessible without
   requiring a session, an async context, or a platform-specific API.
3. Use the same upstream compiler semantics across supported backends; don't
   present a convenience projection as a guarantee the backend does not make.
4. Give ordinary Swift clients safe owned values. Offer lower-level ownership
   or concurrent facilities only after measurements justify their complexity.
5. Keep editor state, live preview, GUI, and non-PDF exporters out of v1.

## Proposed core

```swift
let result = try TypstCompiler().compilePDF("= Invoice\nHello!")
let bytes = result.pdf
let warnings = result.warnings
```

The same compiler accepts a project:

```swift
let project = TypstProject(
    main: "main.typ",
    files: [
        "main.typ": .text("""
            #import "body.typ": greeting
            = #sys.inputs.customer
            #greeting
            """),
        "body.typ": .text("#let greeting = [Hello!]")
    ],
    fonts: [.bundled]
)
let result = try TypstCompiler().compilePDF(
    project,
    options: .init(inputs: ["customer": "Rhoe"])
)
```

`TypstCompiler`, `TypstProject`, compile options, result, and diagnostics
should be Swift-owned value types with checked `Sendable` where possible.
Initially each call owns a separate backend request/result. Reuse of internal
immutable libraries or font caches is permitted only behind audited
synchronization and after cross-platform tests; it must not create a public
session contract by accident.

### Results and failures

- A successful `TypstPDFResult` contains owned `Data` and warnings. The
  proposed `pageCount` means pages in the exported PDF; a separate
  `documentPageCount` means pages before selection. Verify the exporter can
  report both accurately for every accepted page-selection case.
- A compilation failure throws a `TypstError` with an extensible code and
  all available diagnostics, including warnings produced before failure.
  Separate invalid input/options, unavailable resources, compiler/exporter
  errors, and bridge/runtime failures. Do not treat an error string or a PDF
  magic header as a complete validation contract.
- A diagnostic includes severity, message, hints, source path and optional
  range, plus trace information when upstream provides it. Detached or
  unavailable spans remain optional. Canonical source offsets are zero-based
  half-open UTF-8 byte ranges; explicitly named helpers can project line/column
  or UTF-16 positions using the matching original source.
- Start with normal `throws`. Typed throws could be ergonomic, but decide it
  only after every backend, cancellation boundary, and unexpected error can
  be represented without hiding useful information. Document source
  compatibility before promising a closed error set.
- Engine version and provenance are read-only properties. An optional
  capability report is useful only if it describes **verified** features of
  the selected artifact, not a broad promise inferred from compilation.

### Source, assets, and templates

- `TypstProject` is an in-memory snapshot, with a virtual entrypoint and
  explicit text/binary files. Additional in-memory package contents use a
  distinct namespace and versioned package identity; don't confuse package
  paths with ordinary project paths.
- Virtual path normalization, duplicate handling, case sensitivity, path
  encoding, imports, package precedence, and lookup failures are documented
  and tested. A native directory adapter is useful but must be explicit about
  root, traversal, symlinks, file-change snapshots, and errors.
- `sys.inputs` is `[String: String]` for CLI-compatible behavior. A JSON
  convenience that encodes `Encodable` values to a string could be a small
  optional helper, but it must preserve encoding errors, specify determinism,
  and make clear the Typst template must parse the value. It is not a generic
  mapping to native Typst values.
- Encourage callers to pass variable data through inputs or files instead of
  constructing executable Typst source with interpolation. A general Typst
  source builder, string escaping system, template language, or remote package
  manager should not be rushed into the core.
- Default to bundled, pinned fonts. Explicit font bytes, deterministic order,
  missing-font diagnostics, and licenses are first-class. System discovery is
  opt-in and not assumed on iOS or Wasm.

## PDF functionality worth exposing

These are candidates for typed options on the existing PDF compile operation,
not new output formats:

| Facility | Proposal | Important contract |
| --- | --- | --- |
| Standards | Select supported PDF versions and compatible PDF/A or PDF/UA targets. | Let Typst validate combinations; return its errors and hints. |
| Accessibility | Preserve Typst's tagged-PDF default. | Tagged output is a baseline, not a guarantee of PDF/UA compliance or accessible content. |
| Pages | A typed set of one-based pages and ranges. | Define duplicates, open ranges, ordering and out-of-bounds behavior; verify against upstream. |
| Creation metadata | Typed creation timestamp and optional creator/identifier overrides. | Distinguish PDF metadata from document `datetime.today()`; upstream document settings can take precedence. |
| Attachments | Let Typst source use `pdf.attach` with files provided in the project. | Expose no duplicate Swift attachment builder until a real use case and conformance behavior are verified. |
| PDF bytes on disk | An explicit native convenience may write the result to a URL. | Specify overwrite/atomicity and I/O errors; keep the pure bytes API available on WASI. |

The upstream PDF exporter also has pretty output and identifier options.
Expose individual options when their defaults, compatibility, and tests are
specified rather than publishing a general stringly typed option dictionary.
Avoid implying streaming support: upstream PDF export returns a complete
buffer. A write convenience does not remove peak memory costs.

Upstream references: [PDF export](https://typst.app/docs/reference/pdf/),
[PDF attachments](https://typst.app/docs/reference/pdf/attach/),
[SourceDiagnostic](https://docs.rs/typst/0.15.1/typst/diag/struct.SourceDiagnostic.html).

## Concurrency blueprint

- The primary API is synchronous. It runs on the caller's execution context;
  do not promise automatic background execution. Calling it directly from the
  main actor blocks the UI.
- Independent requests can be submitted by clients to an appropriate bounded
  background executor. A long synchronous native call can occupy a
  cooperative executor thread; `Task.detached` alone is not a dedicated
  thread, capacity limit, or cancellation mechanism. Browser execution needs a
  separately tested worker/host arrangement.
- Prove reentrancy with independent concurrent compilations, multiple compiler
  values, repeated invalid input, and thread sanitizer where available. If
  shared Rust/Typst state requires a lock, document its scope and test it;
  avoid blocking the cooperative pool on future Swift tasks.
- Offer no `async` convenience until its executor, bounded scheduling,
  cancellation before/during/after native work, and WASI behavior are
  specified. Native Typst does not thereby become interruptible. Hard timeout
  or forced cancellation needs a separately designed isolation boundary.
- Compile in Swift 6 language mode under strict concurrency and test from a
  main-actor client and from independent tasks. Avoid accidental main-actor
  default isolation in public library declarations.

## Memory and ownership blueprint

- **Baseline:** borrow input bytes only during a synchronous FFI call, copy
  output into independently owned Swift `Data`, then free the opaque Rust
  result exactly once using its Rust destructor. Never reconstruct an
  allocation from length while guessing its original capacity.
- Avoid needless transient conversions such as an unconditional `Array` of
  an entire source when a safe contiguous UTF-8 borrow is available. The
  borrow may not escape the call; embedded NUL, empty input, invalid UTF-8
  from byte APIs, and length conversion require explicit handling.
- `Span`/`RawSpan`, `borrowing`, `consuming`, and noncopyable types can
  make an internal hot path safer or cheaper when they fit the lifetime.
  They are not automatically zero-copy across FFI. Verify Swift 6.4.2 support
  and availability on each target before adding them to a public signature.
- An adopted Rust-backed `Data` buffer is an **optional optimization**, not
  the starting design. It is valid only if one owner keeps the result alive,
  a matching Rust destructor runs exactly once after the last Swift owner,
  thread and mutation rules are proven, and Foundation/WASI behavior is
  tested. Never hand Rust memory to Swift's default `free`.
- Do not expose Rust pointers or non-escaping views tied to a hidden result.
  Measure compile time, allocations, PDF transfer, peak resident memory,
  concurrent jobs, and Wasm memory on representative small and large fixtures.
  Include output bytes and embedded fonts in size accounting.

[Swift Span](https://docs.swift.org/latest/documentation/swift/span/) is a
non-owning, non-escaping view; [Swift concurrency](https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/dataracesafety/)
describes isolation and executor behavior.

## API candidates deferred pending evidence

- **Batch compilation:** define bounded parallelism, ordering, individual
  failures, and cancellation before introducing a batch facade. Ordinary
  one-shot calls can be composed by clients.
- **Prepared templates or caches:** consider only after profiling repeated
  compiles; distinguish immutable resources from mutable world/session state
  and specify invalidation and memory ceilings.
- **Document metadata, page geometry, dependency lists, evaluation:** Typst
  may expose useful data internally, but each projection needs a stable
  meaning, privacy/resource policy, and cross-platform tests. A PDF byte
  count, page count, and diagnostics do not imply editor or query support.
- **Expression evaluation and document query:** Typst 0.15.1's CLI has an
  `eval` operation, optionally in a document context; the older CLI
  `query` command is deprecated in favor of it. This can serve data extraction
  use cases without an editor, but exposing it requires a separate design for
  supported values, serialization, errors, security, and whether work is
  repeated. Do not build a new public API around the deprecated CLI shape.
- **Font inventory:** Typst's CLI exposes discovered font families and
  variants. A read-only inventory of the exact configured font set may be
  useful for reproducibility, but must not implicitly scan system fonts.
- **Automatic package download, persistent font management, async
  compilation, live preview, and editor assistance:** separately scoped work;
  none is silently enabled by the v1 compile API.

## Decisions for review

PDF-only v1 and the synchronous one-shot entry point are agreed. Before API
freeze, verify the proposed result/page-count semantics; decide bundled fonts and size
budget; whether filesystem conveniences ship in v1; specific PDF settings;
and the typed-throws and helper policy. Compile the final declarations and
examples in a real consumer before declaring source stability.

See the pinned upstream
[CLI argument definitions](https://github.com/typst/typst/blob/v0.15.1/crates/typst-cli/src/args.rs)
for the `eval`, deprecated `query`, and font-discovery commands.
