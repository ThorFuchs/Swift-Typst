# Swift-Typst

Swift 6.4.2 interface to the embedded Typst 0.15.1 compiler. Version 1 focuses
on compiling in-memory projects to PDF; editor/IDE APIs and other exports are
outside its current scope. Calls are synchronous and do not invoke a subprocess.

> **Development status:** the initial API and bridge are implemented, but this
> repository is not yet a published, production-ready binary distribution.
> A clean checkout must first build the local Rust artifact. The release checklist
> and platform limitations are described below and in
> [Artifacts/README.md](Artifacts/README.md).

## Compile a document

```swift
import Foundation
import SwiftTypst

let result = try TypstCompiler().compilePDF("= Hello, Typst!")
try result.pdf.write(to: URL(fileURLWithPath: "hello.pdf"))
print("\(result.pageCount) pages; \(result.warnings.count) warnings")
```

Projects may include files, assets and explicit packages without touching the
filesystem or network:

```swift
let project = TypstProject(main: "main.typ", files: [
    "main.typ": .text("#import \"chapter.typ\": title\n= #title"),
    "chapter.typ": .text("#let title = [Hello from Swift]"),
])
let options = TypstCompileOptions(inputs: ["customer": "Rhoe"])
let result = try TypstCompiler().compilePDF(project, options: options)
```

Additional fonts, in-memory Typst packages, fixed/unavailable clocks, PDF
standards, page ranges and byte limits are available through the public value
types. `TypstError` contains a stable wrapper error code and structured Typst
diagnostics. Source ranges are zero-based, half-open UTF-8 byte offsets;
package paths include their package identity. Warnings accompany successful
PDFs. Page selection in Typst 0.15.1 requires `tagged: false`.

The compiler runs synchronously. In interactive apps schedule it away from the
main actor; independent calls can be made concurrently. The byte limits cover
the sum of supplied file/font bytes and the returned PDF respectively. The
output limit is checked *after* export, and neither limit bounds peak memory or
execution time. Cancellation, hard resource isolation, network fetching, system
font discovery and a general-purpose sandbox are not provided. Supply all
needed files, packages and fonts explicitly. The pinned bundled set contains
Libertinus Serif, STIX Two text and math, and DejaVu Sans Mono; its license
notices are included in the generated artifact. STIX Two Math is the default
for equations when bundled fonts are enabled. A document's explicit math font
rule takes precedence. New Computer Modern is not bundled: selecting it may
produce a missing-font warning unless the caller supplies the required faces via
`TypstProject.fonts`. Font selection affects layout, Unicode coverage and PDF
text extraction; see [the font investigation](Documentation/FONT-INVESTIGATION.md).
The krilla/resvg provenance and historical font distribution questions remain
documented in [Notices/README.md](Notices/README.md). The release owner's
scoped decision on the remaining krilla risk is recorded in
[RELEASE-RISK-DECISION.md](Documentation/RELEASE-RISK-DECISION.md).

## Local build

Install Swift 6.4.2, Rust 1.94.1 and the desired Rust target. For example, on
Apple Silicon macOS:

```sh
rustup target add aarch64-apple-darwin
sh Scripts/build-artifact.sh aarch64-apple-darwin
swift test
swift run --package-path Tests/Consumer Consumer
```

This builds a local SwiftPM static-library artifact. Consumers of this local
artifact need neither Rust nor manual linker flags. The Swift package currently
points at that ignored local artifact: a clean checkout is not yet a zero-setup
remote dependency. See [Artifacts/README.md](Artifacts/README.md) for target
mappings, provenance, ZIP packaging and release prerequisites.

## Verification and next steps

The implementation's local evidence, including precise scope and remaining
release gates, is in [Documentation/PRODUCTION-STATUS.md](Documentation/PRODUCTION-STATUS.md).
The historical design and decisions are recorded in
[Documentation/IMPLEMENTATION-ROADMAP.md](Documentation/IMPLEMENTATION-ROADMAP.md)
and [Documentation/API-DESIGN.md](Documentation/API-DESIGN.md). The font and
license research is retained under [Spike/LicenseRelease](Spike/LicenseRelease/README.md).

The Swift-Typst source is licensed under [Apache-2.0](LICENSE). Bundled and
transitive components have their own licenses and notices.
