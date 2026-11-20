# Diagnostics and resource boundaries

Inspect structured warnings and errors, and understand the wrapper's limits.

## Handle diagnostics

Successful compiles expose warnings through ``TypstPDFResult/warnings``.
Failures throw ``TypstError``, which includes a stable wrapper code and any
available Typst diagnostics:

```swift
import SwiftTypst

do {
    let result = try TypstCompiler().compilePDF("#let x = (")
    for warning in result.warnings { print(warning.message) }
} catch let error as TypstError {
    print(error.code.rawValue)
    for diagnostic in error.diagnostics {
        print(diagnostic.message)
        if let range = diagnostic.range {
            print("\(range.path): bytes \(range.start)..<\(range.end)")
        }
    }
}
```

A ``TypstSourceRange`` is zero-based and half-open, measured in UTF-8 bytes.
Diagnostic paths identify the virtual source; paths for packages include the
package identity. Hints and trace entries may have their own ranges.

## Bound input and output

``TypstResourceLimits`` can cap the aggregate supplied file and font bytes and
the returned PDF size. The output limit is checked after PDF export. These
limits don't bound peak memory, execution time, or internal compiler work.

The compiler runs in process and does not provide cancellation, a general
sandbox, or hard isolation. For untrusted documents requiring strict time or
memory guarantees, use an appropriately isolated host process and enforce those
limits outside SwiftTypst.
