# Getting started

Add Swift-Typst to a package and compile a document to PDF.

## Add the package

In your Swift package manifest, add the dependency:

```swift
.package(url: "https://github.com/ThorFuchs/Swift-Typst.git", from: "1.0.0")
```

Add the `SwiftTypst` product to your target's dependencies. The binary bridge
is delivered by SwiftPM; supported consumers don't need Rust or custom linker
flags. The first download includes multiple platform variants.

```swift
.product(name: "SwiftTypst", package: "Swift-Typst")
```

## Compile and inspect a PDF

```swift
import Foundation
import SwiftTypst

let result = try TypstCompiler().compilePDF("= A small document\n\nHello, Typst!")
try result.pdf.write(to: URL(fileURLWithPath: "document.pdf"))
print("Exported \(result.pageCount) of \(result.documentPageCount) pages")
for warning in result.warnings {
    print(warning.message)
}
```

The call is synchronous. In an interactive application, perform compilation
away from the main actor. Separate calls can run concurrently; cancellation and
hard execution time limits are not provided by the wrapper.

For multi-file input, assets, and fonts, see <doc:ProjectsAndResources>. For
error reporting and resource limitations, see <doc:DiagnosticsAndSafety>.
