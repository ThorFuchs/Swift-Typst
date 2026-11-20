# ``SwiftTypst``

Compile Typst documents to PDF from Swift with an embedded, in-process engine.

## Overview

SwiftTypst wraps Typst 0.15.1 in a synchronous, value-oriented Swift API. Supply
a source string for a quick conversion or a ``TypstProject`` containing files,
assets, local packages, and fonts. The compiler returns PDF bytes, page counts,
and structured warnings; failures carry structured diagnostics.

```swift
import Foundation
import SwiftTypst

let result = try TypstCompiler().compilePDF("= Hello, Typst!")
try result.pdf.write(to: URL(fileURLWithPath: "hello.pdf"))
```

The published package includes a prebuilt bridge. It supports macOS, iOS, Linux,
and WASI on the variants listed in the repository README. WASI support does not
by itself establish support for browser hosts.

Compilation is synchronous and can be expensive. Schedule work away from the
main actor in interactive applications. Supply all resources explicitly: the
compiler does not discover system fonts or fetch packages over the network.

## Topics

### Essentials

- <doc:GettingStarted>
- ``TypstCompiler``
- ``TypstPDFResult``

### Documents and resources

- <doc:ProjectsAndResources>
- ``TypstProject``
- ``TypstFile``
- ``TypstPackage``

### Configuration

- ``TypstCompileOptions``
- ``TypstPDFOptions``
- ``TypstPDFStandard``
- ``TypstPageRange``
- ``TypstClock``
- ``TypstResourceLimits``

### Diagnostics

- <doc:DiagnosticsAndSafety>
- ``TypstError``
- ``TypstDiagnostic``
- ``TypstSourceRange``
