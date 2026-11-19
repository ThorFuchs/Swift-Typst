#!/usr/bin/env python3
"""Prepare a disposable STIX-font bridge experiment, never a release artifact."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--stix-dir", required=True, type=Path, help="extracted official STIX static_otf directory")
parser.add_argument("--ofl", required=True, type=Path, help="OFL.txt from the exact STIX release")
parser.add_argument("--output", required=True, type=Path, help="new directory outside this repository")
args = parser.parse_args()
out = args.output.resolve()
if out == root or out.is_relative_to(root) or out.exists():
    raise SystemExit("Output must be a nonexistent directory outside the repository")
baseline = json.loads((root / "Rust/fonts/manifest.json").read_text())
if not any(entry["file"].startswith("NewCM") for entry in baseline["fonts"]):
    raise SystemExit("V1 already uses STIX; this historical experiment requires a Book-era checkout")
expected = {
    "STIXTwoMath-Regular.otf": "3a5f3f26f40d5698b3c62dd085d48d6663696a3f80825aab8b553d5097518e8c",
    "STIXTwoText-Regular.otf": "c4864ca6ec071c2d31d0d8309001faa1ee3517fffb53a31a405a697b71f52ca1",
    "STIXTwoText-Italic.otf": "cd64481fd10b69469074a3a8172fb5a22cb4116941d8aceafb8c77756b563df8",
    "STIXTwoText-Bold.otf": "7ef76c666a6704f76ed3fa27bcdda55b36e558b5c2c93b49b03d854db96bdeb5",
    "STIXTwoText-BoldItalic.otf": "90e88f2ac79d6c00a5ce2d8446bfdf9457aed6afc1159cde33262979d82c8586",
}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
for name, sha in expected.items():
    if digest(args.stix_dir / name) != sha:
        raise SystemExit(f"Wrong STIX font: {name}")
if digest(args.ofl) != "0c8825913b60d858aacdb33c4ca6660a7d64b0d6464702efbb19313f5765861a":
    raise SystemExit("Wrong STIX OFL text")
out.mkdir(parents=True)
for folder in ("Rust", "Sources", "Tests", "Scripts", "Notices"):
    shutil.copytree(root / folder, out / folder, ignore=shutil.ignore_patterns("__pycache__"))
for name in ("LICENSE", "Package.swift"):
    shutil.copy2(root / name, out / name)
shutil.copy2(args.ofl, out / "Notices" / "STIX-Two-OFL.txt")
font_dir = out / "Rust" / "fonts"
manifest = json.loads((font_dir / "manifest.json").read_text())
removed = [f for f in manifest["fonts"] if f["file"].startswith("NewCM")]
if len(removed) != 7:
    raise SystemExit("Unexpected upstream font set")
for entry in removed:
    (font_dir / entry["file"]).unlink()
for name in expected:
    shutil.copy2(args.stix_dir / name, font_dir / name)
source = "https://github.com/stipub/stixfonts/blob/v2.13b171/zipfiles/static_otf.zip"
new_entries = [{"file": name, "sha256": sha, "source": source, "license": "OFL-1.1"} for name, sha in expected.items()]
old_entries = [f for f in manifest["fonts"] if not f["file"].startswith("NewCM")]
insert = next(i for i, f in enumerate(old_entries) if f["file"].startswith("DejaVu"))
manifest["fonts"] = old_entries[:insert] + new_entries + old_entries[insert:]
manifest["experiment"] = "STIX replacement; local development only, not a release"
(font_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
world = out / "Rust" / "src" / "world.rs"
text = world.read_text()
text, count = re.subn(r'^\s*include_bytes!\("\.\./fonts/NewCM[^\n]+\n', '', text, flags=re.MULTILINE)
if count != 7:
    raise SystemExit(f"Expected seven NewCM references, found {count}")
anchor = '                include_bytes!("../fonts/DejaVuSansMono-Bold.ttf") as &\'static [u8],'
if text.count(anchor) != 1:
    raise SystemExit("Could not find font insertion point")
text = text.replace(anchor, ''.join(f'                include_bytes!("../fonts/{n}") as &\'static [u8],\n' for n in expected) + anchor)
text = text.replace('    text::{Font, FontBook},', '    text::{Font, FontBook, FontFamily, FontList, TextElem},\n    math::EquationElem,\n    foundations::{NativeElement, Recipe, Selector, Styles, Transformation},\n    syntax::Span,')
old = '        Ok(Self {\n            library: LazyHash::new(Library::builder().with_inputs(inputs).build()),'
new = '''        let mut library = Library::builder().with_inputs(inputs).build();
        if request.bundled_fonts {
            let mut math = Styles::new();
            math.set(TextElem::font, FontList(vec![FontFamily::new("STIX Two Math")]));
            library.styles.push(Recipe::new(
                Some(Selector::Elem(EquationElem::ELEM, None)),
                Transformation::Style(math),
                Span::detached(),
            ));
        }
        Ok(Self {
            library: LazyHash::new(library),'''
if text.count(old) != 1:
    raise SystemExit("Could not find library initialization")
text = text.replace(old, new)
world.write_text(text)
# The production test for the Book face cannot apply to this deliberately
# different candidate. Keep all other tests and add candidate-specific checks.
tests = out / "Tests" / "SwiftTypstTests" / "CompilationTests.swift"
test_text = tests.read_text()
start_marker = "@Test func usesBookForExplicitNewComputerModern()"
end_marker = "@Test func reportsImportedSourceLocation()"
if test_text.count(start_marker) != 1 or test_text.count(end_marker) != 1:
    raise SystemExit("Could not find the production Book-font test")
start, end = test_text.index(start_marker), test_text.index(end_marker)
if end <= start:
    raise SystemExit("Unexpected font test order")
tests.write_text(test_text[:start] + test_text[end:])
shutil.copy2(root / "Spike" / "LicenseRelease" / "CandidateFontTests.swift",
             out / "Tests" / "SwiftTypstTests" / "CandidateFontTests.swift")
shutil.copy2(root / "Spike" / "LicenseRelease" / "CandidatePathTests.swift",
             out / "Tests" / "SwiftTypstTests" / "CandidatePathTests.swift")
consumer = out / "Tests" / "Consumer" / "Sources" / "Consumer" / "main.swift"
consumer_text = consumer.read_text()
if consumer_text.count('New Computer Modern') != 2 or consumer_text.count('NewCM10-Book') != 1:
    raise SystemExit("Unexpected production consumer font check")
consumer_text = consumer_text.replace('New Computer Modern', 'STIX Two Text')
consumer_text = consumer_text.replace('NewCM10-Book', 'STIXTwoText')
pages_marker = 'let pages = try compiler.compilePDF('
if consumer_text.count(pages_marker) != 1:
    raise SystemExit("Unexpected consumer page-selection test")
math_check = '''let mathResult = try compiler.compilePDF("Formula: $ x^2 + y^2 $")
guard mathResult.warnings.isEmpty, mathResult.pdf.range(of: Data("STIXTwoMath".utf8)) != nil else {
    fatalError("Unexpected default math font")
}
'''
consumer_text = consumer_text.replace(pages_marker, math_check + pages_marker)
consumer.write_text(consumer_text)
ios_test = out / "Tests" / "iOS" / "Tests" / "PDFTests.swift"
ios_text = ios_test.read_text()
old_font = '"#set text(font: \\"New Computer Modern\\")\\nRegular text"'
if ios_text.count(old_font) != 1 or ios_text.count('NewCM10-Book') != 1:
    raise SystemExit("Unexpected production iOS font check")
ios_test.write_text(ios_text.replace(old_font, '"$ x^2 + y^2 $"').replace('NewCM10-Book', 'STIXTwoMath'))
print(f"Prepared experimental source at {out}; NewCM removed from Rust/fonts; release remains blocked.")
