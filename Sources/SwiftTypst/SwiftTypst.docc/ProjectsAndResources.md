# Projects and resources

Supply an in-memory document, its supporting files, and optional packages.

## Build a project

A ``TypstProject`` maps relative virtual paths to ``TypstFile`` values. The
`main` path identifies the entry point; imports and assets resolve against
this in-memory project.

```swift
import SwiftTypst

let project = TypstProject(main: "main.typ", files: [
    "main.typ": .text("#import \"chapter.typ\": title\n= #title"),
    "chapter.typ": .text("#let title = [Hello from Swift]"),
])
let options = TypstCompileOptions(inputs: ["customer": "Rhoe"])
let result = try TypstCompiler().compilePDF(project, options: options)
```

Use `.bytes` for binary assets. Options supplied through `inputs` are visible to
Typst as `sys.inputs`. The compiler doesn't read arbitrary host files or fetch
remote packages: provide all needed resources in the project.

## Include fonts and packages

Set ``TypstProject/fonts`` to the bytes of additional OpenType or TrueType
fonts. These are searched before the bundled fonts. Set
``TypstProject/useBundledFonts`` to `false` to use only supplied fonts.
The bundled selection includes Libertinus Serif, STIX Two Text and Math, and
DejaVu Sans Mono. Font choices affect layout, glyph coverage, and PDF text
extraction.

Use a ``TypstPackage`` with its complete identity and files to provide an
explicit local package. Package discovery and network fetching are not
provided. See the repository's example gallery for complete document sources.

## Configure PDF output

``TypstPDFOptions`` selects PDF standards, tagging, creation metadata, and
optional page ranges. Page numbers are one-based. With Typst 0.15.1, page
selection requires `tagged: false`:

```swift
let options = TypstCompileOptions(
    pdf: .init(tagged: false, pages: [.page(2)])
)
```

``TypstPDFResult/pageCount`` counts exported pages;
``TypstPDFResult/documentPageCount`` counts the full document before selection.
