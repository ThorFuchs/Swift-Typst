# Swift-Typst example gallery

Six independent, single-page Typst documents demonstrate editorial layout,
mathematics, tables, a résumé and a letter. Each preview is rasterized from a
PDF produced by the `TypstCompiler` API and the package's bundled fonts. The
names, organizations, addresses and figures are fictional.

| Example | Typst source | Preview |
| --- | --- | --- |
| Editorial | [Source](Documents/01-editorial.typ) | [PNG](Images/01-editorial.png) |
| Mathematics | [Source](Documents/02-mathematics.typ) | [PNG](Images/02-mathematics.png) |
| Research report | [Source](Documents/03-report.typ) | [PNG](Images/03-report.png) |
| Invoice | [Source](Documents/04-invoice.typ) | [PNG](Images/04-invoice.png) |
| Résumé | [Source](Documents/05-resume.typ) | [PNG](Images/05-resume.png) |
| Letter | [Source](Documents/06-letter.typ) | [PNG](Images/06-letter.png) |

## Render the gallery

From the repository root, with Swift 6.4.2 and Poppler's `pdftoppm` installed:

```sh
python3 Scripts/render-gallery.py
```

The gallery executable uses `TypstCompiler.compilePDF` with the published bridge,
bundled fonts, a fixed clock and a fixed PDF creation date. It requires every
example to compile to exactly one page with no warnings. The script rasterizes
those PDFs to 900-pixel-wide PNGs in `Examples/Images/`. The PDFs are temporary;
to retain them, run the executable directly:

```sh
mkdir -p /tmp/swift-typst-gallery-pdf
swift run --package-path Examples/Gallery Gallery Examples/Documents /tmp/swift-typst-gallery-pdf
```

Run `python3 Scripts/render-gallery.py --check` to compile and rasterize all
examples without changing the committed images. Rasterization and PNG encoding
can vary across Poppler versions, so the check does not compare image bytes;
review regenerated previews visually when changing examples or rendering tools.
The examples require no external assets, Typst packages or system fonts.
