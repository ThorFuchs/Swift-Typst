# Swift-Typst: Version 1 implementation roadmap

Status: **proposed design**, informed by the architecture spike on
18 November 2026. Public names and signatures below are design sketches, not
implemented APIs. The current implementation and platform evidence are described in
[PRODUCTION-STATUS.md](PRODUCTION-STATUS.md).

## Product goal and boundaries

Ship a Swift 6.4 library that compiles Typst documents to PDF through the
upstream Typst engine, with a convenient one-shot Swift API. The initial
backend is embedded on macOS, iOS, Linux, and WASI; an external process is not
required. A caller may run the library from a command-line tool, server, app,
or compatible Wasm host.

**Version 1 scope**

- Compile a source string or a multi-file, in-memory project to PDF.
- Provide source files, images, fonts, and already-available package files
  explicitly. Support string-valued `sys.inputs`.
- Return PDF bytes, page count, and compiler warnings; report compilation
  failures with structured diagnostics.
- Offer explicit PDF configuration and reproducible inputs, time, and fonts.
- Support the platform and distribution matrix below with real consumer tests.
- Pin the Typst engine to 0.15.1 for the first implementation, and report its
  version and provenance. Update deliberately; do not track upstream HEAD.

PDF is the **only** export format in version 1, as confirmed by the maintainer.
PNG and SVG are follow-ups. HTML and bundle export are experimental upstream
and are outside the stable v1 scope.
There is no promise of complete CLI option or command parity.

Editor sessions, live preview, source-to-preview navigation, completion,
tooltips, document indexing, package management UI, automatic registry
downloads, and SwiftUI components are outside v1. The design leaves room for
them without exposing speculative session or revision APIs now. A separate
CLI executable or subprocess backend is a later product decision; neither is
required for the v1 cross-platform library.

## Upstream behavior to preserve

Typst 0.15.1 separates a compiler from its environment: the host implements
`World` to provide sources, files, fonts, and the current date. Compilation
returns a paged document and warnings, or source diagnostics. The PDF exporter
then turns the paged document into PDF bytes and can itself report errors.

- The CLI's `--input key=value` supplies strings through `sys.inputs`.
  Do not silently convert arbitrary Swift values into Typst values and call
  the result CLI-compatible. Typed inputs can be considered separately.
- Typst supports PDF, PNG, SVG, HTML, and bundle export, with HTML and bundle
  behind upstream in-development feature flags. PNG and SVG are page-oriented;
  do not force all output formats into a single-data-blob API.
- PDF settings include page ranges, PDF standards, tagged output, creation
  metadata, and other export choices. Expose only options actually implemented
  and validated; unsupported combinations must fail explicitly.
- Document time and PDF creation metadata are distinct concerns. Typst's
  `datetime.today(offset:)` accepts offsets as hours or durations, so the
  world needs a defined instant and local-offset policy, including fractional
  hours. Reproducibility requires explicit fonts, inputs, time, and resources.
- Diagnostics can include warnings, errors, source spans, and hints. The
  wrapper must preserve them rather than flattening them to a single string.

References: [Typst 0.15.1 compiler](https://docs.rs/typst/0.15.1/typst/fn.compile.html),
[World](https://docs.rs/typst/0.15.1/typst/trait.World.html),
[CLI arguments at v0.15.1](https://github.com/typst/typst/blob/v0.15.1/crates/typst-cli/src/args.rs),
[`sys.inputs`](https://typst.app/docs/reference/foundations/sys/),
[`datetime.today`](https://typst.app/docs/reference/foundations/datetime/),
[HTML export status](https://typst.app/docs/reference/html/).

## Proposed Swift experience

The common case has no session setup and keeps warnings available:

```swift
import SwiftTypst

let compiler = TypstCompiler()
let result = try compiler.compilePDF("""
    = Hello, Typst

    Compiled from Swift.
    """)

let pdf = result.pdf                 // Data
let pageCount = result.pageCount   // pages in the exported PDF
for warning in result.warnings {
    print(warning.message)
}
```

An explicit project uses the same operation:

```swift
let project = TypstProject(
    main: "main.typ",
    files: [
        "main.typ": .text("""
            #import "chapter.typ": body
            = Report for #sys.inputs.customer
            #body
            """),
        "chapter.typ": .text("#let body = [Hello from a second file.]"),
        "assets/logo.svg": .bytes(logoBytes),
    ],
    fonts: [.bundled]
)

let result = try TypstCompiler().compilePDF(
    project,
    options: .init(inputs: ["customer": "Rhoe"])
)
```

Here `logoBytes` is caller-provided `Data`. Exact initializers, Foundation
usage, and naming remain subject to a compile-tested API review.

The intended minimal public shape is:

```swift
public struct TypstCompiler: Sendable {
    public init()
    public func compilePDF(
        _ source: String,
        options: TypstCompileOptions = .init()
    ) throws -> TypstPDFResult
    public func compilePDF(
        _ project: TypstProject,
        options: TypstCompileOptions = .init()
    ) throws -> TypstPDFResult
}

public struct TypstPDFResult: Sendable {
    public let pdf: Data
    /// Number of pages in the exported PDF, after page selection.
    public let pageCount: Int
    /// Number of pages in the laid-out source document, before selection.
    public let documentPageCount: Int
    public let warnings: [TypstDiagnostic]
}
```

This is a proposed surface, not a promise that the implementation is already
thread-safe or that these declarations have been compiled.
For a deeper review of API ergonomics, PDF capabilities, ownership, and
Swift concurrency, see [API-DESIGN.md](API-DESIGN.md).

### Contract

1. **One-shot and synchronous.** `TypstCompiler` is a value-like facade and
   `compilePDF` returns a Swift-owned `TypstPDFResult`. A synchronous call
   can be expensive: UI clients must schedule it off the main thread, and
   browser clients may need a worker. Do not imply `async` makes CPU work
   nonblocking or makes an active Typst compile cancellable.
2. **Explicit project resources.** A project owns an entry-point path and a
   mapping of virtual paths to text or bytes; all references resolve within
   that project or explicitly provided package resources. Reject duplicate,
   invalid, escaping, and ambiguous paths. Define Unicode and case handling.
   File and package lookup semantics must not vary silently by host platform.
3. **Predictable fonts.** The default is a documented, version-pinned bundled
   font set. Additional caller-provided bytes and their ordering are explicit.
   System font discovery and directory-based projects are separate opt-in
   adapters, subject to platform capabilities and their own tests. Never
   silently substitute a system-dependent configuration.
4. **Warnings on success; diagnostics on failure.** Successful results contain
   PDF bytes, page count, and all compilation/export warnings. Failures throw
   a Swift-owned, checked-`Sendable` `TypstError` that carries errors and
   warnings, including missing-file and exporter diagnostics. Bridge failures,
   invalid configuration, and Typst document errors remain distinguishable.
   Missing, detached, or unavailable source locations are represented honestly.
5. **Stable diagnostic coordinates.** Canonical ranges are zero-based,
   half-open UTF-8 byte offsets in the named virtual file; optionally provide
   clearly defined line/column conversion helpers. Test Unicode, CRLF,
   non-BMP characters, missing spans, and imported files. Do not confuse UTF-8
   bytes with Swift character indices or UTF-16 editor offsets.
6. **No network or host-file access by default.** The host supplies sources,
   assets, and packages. Optional native filesystem access must have an
   explicit root and policy; resolve symlinks safely and test traversal.
   Package fetch and persistent caches are later features unless explicitly
   designed and tested for a specific backend.
7. **Concurrency and cancellation are evidence-based.** Public values should
   be checked `Sendable`; no raw Rust pointers escape. Prove simultaneous
   independent calls are safe or serialize them internally and document the
   scope. Cancellation can be checked before and after native calls, but v1
   must not promise to interrupt an in-flight Typst compile without upstream
   support. Never use `@unchecked Sendable` without an audited invariant.
8. **Limits are honest.** Input and output size checks may reject requests but
   do not bound Typst's peak memory, execution time, native panics, or Wasm
   traps. Process isolation and hard kill/time limits are a separate optional
   native-host architecture, not a property of the embedded backend.

The public error type should follow Swift-GFM's extensible error-code approach
where appropriate. Fix v1 source/binary compatibility policy before declaring
the API stable. Expose `TypstCompiler.engineVersion` and an auditable
upstream revision or release identifier.

## Internal architecture

```text
SwiftTypst: source/project + PDF options -> result / diagnostics
    -> private C ABI: opaque owned results, explicit byte lengths
        -> Rust compile core: immutable request + in-memory World
            -> pinned Typst compiler -> paged document -> PDF exporter
```

- Keep the compile core independent of editor state and host services. Provide
  only an internal seam for future sessions and optional host adapters.
- Use an opaque result handle and one matching Rust-owned destructor. Document
  lifetimes, null/empty buffers, UTF-8 and binary lengths, thread ownership,
  ABI version, and what happens on errors. No allocator crosses ownership
  boundaries. Audit the old kit's vector-capacity issue before borrowing code.
- Convert ordinary Rust errors to stable bridge statuses. Catch unwinding
  panics at the ABI boundary where supported; aborts, OOM, and Wasm traps may
  still terminate the host. Never unwind across C.
- Define a versioned bridge representation for diagnostics and options.
  JSON is acceptable for small structured metadata if measured; move PDF bytes
  as bytes and avoid JSON/base64 for binary output. Benchmark before optimizing.
- Split Rust modules by world/resources, compilation, diagnostics, PDF, and
  FFI; avoid carrying the old macOS-oriented package and IDE subsystem wholesale.
- Select exact Rust and Swift toolchains for builds and CI. SwiftPM expresses
  tools version `6.4`; the Swift 6.4.2 patch is pinned in CI/toolchain
  configuration, not misrepresented as a distinct Swift language mode.

## Distribution is the first implementation gate

The spike passes a manually supplied archive through linker flags. This is
**not** yet an installable SwiftPM dependency.

Swift Evolution
[SE-0482](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0482-swiftpm-static-library-binary-target-non-apple-platforms.md)
is implemented since Swift 6.2 and adds `staticLibrary` artifact bundles
with headers and module maps. The
separate consumer experiment exercised a
Rust-built Typst archive with separate consumers on macOS arm64, iOS simulator,
WASI, and Linux arm64/musl, without manual linker flags. A local bundle with
macOS and iOS variants was also exercised. This establishes a viable candidate,
not universal compatibility: remote artifact distribution, device slices,
Linux glibc and x86_64, full multi-variant packaging, and browser execution
remain open. Apple XCFrameworks remain an alternative if needed.

Before building out the API:

1. Produce candidate, versioned bridge artifacts and a manifest with target
   triples, Rust/Typst versions, checksums, licenses, and exact build inputs.
2. Build a separate clean SwiftPM consumer with ordinary package dependency
   declarations and **no manual linker flags**. Exercise SwiftPM and Xcode
   where applicable, including iOS device and simulator slices.
3. Prove Linux dynamic/glibc and static/musl dependency/link compatibility,
   and the actual WASI triple with the full Swift 6.4.2 SDK. Examine Rust's
   native system-library requirements and duplicate-symbol behavior.
4. If SE-0482 artifacts do not satisfy the matrix, document the concrete
   failure and choose a validated alternative. Do not publish a nominal
   platform badge or require users to discover undocumented flags.
5. Do not commit huge opaque archives by default. Decide release assets,
   checksums, rebuild and update workflow, and supply-chain audit together
   with actual artifact sizes and consumer behavior.

## Platform acceptance matrix

| Platform | Minimum acceptance for 1.0 | Evidence still needed |
| --- | --- | --- |
| macOS arm64 and x86_64 | Consumer build and runtime tests; documented deployment minimum. | Clean artifact integration, Intel execution, and final deployment targets. |
| iOS arm64 | Device and simulator builds; simulator runtime test through a consumer app. | Device slice and clean consumer integration; physical-device runtime where available. |
| Linux x86_64 and arm64 | Consumer builds and runtime tests on specified glibc targets; separately validate any promised musl target. | Linux x86_64, glibc matrix, normal dependency installation, and Docker execution. The current ARM64 musl VM smoke test is not this whole matrix. |
| WASI wasm32 | Matching Swift 6.4.2 SDK; link and execute consumer smoke and failure tests. | Artifact-based integration, fixture coverage, runtime limits and optimized size. |
| Browser | Only claim browser support after an actual browser-hosted Wasm test with documented host/worker requirements. | The WASI runtime test does not establish browser compatibility. |

Deployment minimums, exact Linux distributions, and the final support table
are release decisions backed by CI, not inferred from compilation.

## Implementation milestones and gates

### 0. Freeze the contract

Resolve and record API names, PDF-only v1 scope, default fonts, time and
resource policies, diagnostic offsets, platform targets, artifact policy, and
the minimum supported operating-system versions. Compile small Swift API
examples as part of the review. Decide whether a thin CLI deserves its own
later milestone; it must not add platform-specific behavior to the core.

**Gate:** reviewed, unambiguous v1 API and capability matrix.

### 1. Prove dependency distribution

Implement the artifact experiment above, with clean consumer projects for all
four target families. Include a real CI runtime per promised platform.

**Gate:** a user can add the package and run a PDF smoke test without custom
linker flags or Rust installation, or the remaining requirement is explicitly
agreed and documented before proceeding.

### 2. Harden a minimal compile core and bridge

Replace the spike's one-file world with the audited Rust/C boundary and typed
Swift values. Add in-memory sources, assets, supplied fonts, stable ownership,
warnings, errors, source offsets, and one-shot PDF export. Keep upstream Typst
and dependencies pinned through Cargo.lock and a reproducible build.

**Gate:** successful and failed documents, warnings, Unicode locations, missing
imports, multiple pages, binary assets, memory ownership, and concurrent calls
tested end-to-end on the matrix.

### 3. Complete the PDF and environment contract

Add explicit inputs, package resources already available to the host, PDF
options, deterministic clock/metadata and controlled fonts. Define
capabilities and errors for native-only filesystem/font adapters. Validate
PDF standards and incompatible settings against the pinned backend.

**Gate:** fixtures cover multi-file documents, images, fonts, local packages,
`sys.inputs`, time zones, warnings and PDF options; all documented defaults
are consistent across supported targets or differences are explicit.

### 4. Prove fidelity, resilience, and consumption

Compare representative fixtures with an independently built Typst 0.15.1 CLI
under the same fonts, inputs, time, and resource policies. Compare diagnostics,
page counts, text/layout and rendered output as appropriate; require identical
PDF bytes only when reproducibility has been demonstrated. Test malformed
inputs, resource policy, no implicit network, FFI ownership, thread safety,
Wasm runtime, optimized artifact size, and clean package consumers. Use
sanitizers/fuzzing where supported, with explicit limits on what they prove.

**Gate:** CI matrix green, no unexplained fidelity regressions, and known
security and performance boundaries documented. Do not label Docker, browser,
or physical-device runtime as tested until actually exercised.

### 5. Release readiness

Write DocC and README examples, platform matrix, security and resource model,
upstream update guide, attribution, font licenses, notices, artifact provenance,
and changelog. Review source compatibility, distribution size, supported
targets, and versioning policy. Add CI release reproducibility checks and
test an external consumer from release artifacts.

**Gate:** maintainer review of a complete release candidate; publishing is a
separate explicit action.

## Open design decisions

- PDF-only for 1.0 is decided. For any later SVG/PNG APIs, specify per-page
  return values, ordering, options, and equivalent validation.
- Choose the actual SwiftPM artifact layout after the distribution gate,
  including any differences between Apple, Linux, and WASI.
- Choose whether v1 requires a filesystem project adapter or only in-memory
  projects; the core and common API must work on WASI either way.
- Define exact default bundled fonts, their ordering and licenses, the size
  budget, and whether a smaller explicit-font build can be offered.
- Decide PDF options exposed at launch and whether browser hosting is a 1.0
  requirement or a separately qualified target.
- Define the cross-platform reproducible clock and PDF metadata policy before
  locking `TypstCompileOptions`.
- Decide whether a native CLI executable and process backend are later
  products. If introduced, verify diagnostic, feature, version, resource, and
  cancellation differences explicitly rather than assuming backend parity.
