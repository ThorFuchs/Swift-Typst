#!/usr/bin/env python3
"""Prepare a disposable path-conversion experiment; NOT a rights clearance."""
import argparse
import hashlib
import io
import shutil
import tarfile
from pathlib import Path, PurePosixPath

repo = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--base", required=True, type=Path, help="prepared STIX candidate source")
parser.add_argument("--crate", required=True, type=Path, help="original krilla 0.8.2 crate")
parser.add_argument("--output", required=True, type=Path, help="nonexistent directory outside repository")
args = parser.parse_args()
out = args.output.resolve()
base = args.base.resolve()
if out == repo or out.is_relative_to(repo) or out == base or out.is_relative_to(base) or out.exists():
    raise SystemExit("Output must be a nonexistent directory outside the repository and base")
blob = args.crate.read_bytes()
if hashlib.sha256(blob).hexdigest() != "27da593198b20eeba65caeb73c2bbeec3e53ab08fa549898312ce81c4fce5e33":
    raise SystemExit("krilla archive does not match Cargo.lock")
out.mkdir(parents=True)
for folder in ("Rust", "Sources", "Tests", "Scripts", "Notices"):
    shutil.copytree(base / folder, out / folder, ignore=shutil.ignore_patterns("__pycache__"))
for name in ("LICENSE", "Package.swift"):
    shutil.copy2(base / name, out / name)
vendor = out / "Rust/vendor/krilla"
vendor.mkdir(parents=True)
with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
    for item in archive:
        parts = PurePosixPath(item.name).parts
        if not parts or parts[0] != "krilla-0.8.2" or any(part in ("..", ".") for part in parts):
            raise SystemExit("Unexpected path in crate")
        dest = vendor.joinpath(*parts[1:])
        if item.isdir():
            dest.mkdir(parents=True, exist_ok=True)
        elif item.isfile():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(item) as src, dest.open("wb") as dst:
                shutil.copyfileobj(src, dst)
        else:
            raise SystemExit("Unexpected non-file entry in crate")
for name in ("NOTICE.md", "LICENSE_APACHE", "LICENSE_MIT", "MPL-2.0-reference.txt"):
    shutil.copy2(repo / "Notices/Upstream/krilla" / name, vendor / name)
source = vendor / "src/content.rs"
text = source.read_text()
if hashlib.sha256(source.read_bytes()).hexdigest() != "9e59b2c77b73b36caedacfe80894d1cce7fd6fe6f7438ea24fda2019391a980c":
    raise SystemExit("Unexpected original content.rs")
start = text.index("    fn content_draw_path(")
end = text.index("\n    }\n}", start) + len("\n    }")
replacement = '''    // Experimental replacement for behavior comparison only. Original upstream
    // attribution and notices are preserved; rights review remains unresolved.
    fn content_draw_path(&mut self, path_data: impl Iterator<Item = PathSegment>) {
        let mut current = None;
        for segment in path_data {
            match segment {
                PathSegment::MoveTo(point) => {
                    self.content.move_to(point.x, point.y);
                    current = Some(point);
                }
                PathSegment::LineTo(point) => {
                    self.content.line_to(point.x, point.y);
                    current = Some(point);
                }
                PathSegment::QuadTo(control, end) => {
                    if std::env::var_os("SWIFT_TYPST_TRACE_PATHS").is_some() {
                        eprintln!("SWIFT_TYPST_EXPERIMENTAL_QUADRATIC_PATH");
                    }
                    let start = current.expect("quadratic segment without current point");
                    let curve = kurbo::QuadBez::new(
                        (f64::from(start.x), f64::from(start.y)),
                        (f64::from(control.x), f64::from(control.y)),
                        (f64::from(end.x), f64::from(end.y)),
                    ).raise();
                    self.content.cubic_to(
                        curve.p1.x as f32, curve.p1.y as f32,
                        curve.p2.x as f32, curve.p2.y as f32,
                        end.x, end.y,
                    );
                    current = Some(end);
                }
                PathSegment::CubicTo(first, second, end) => {
                    self.content.cubic_to(first.x, first.y, second.x, second.y, end.x, end.y);
                    current = Some(end);
                }
                PathSegment::Close => { self.content.close_path(); }
            }
        }
    }'''
source.write_text(text[:start] + replacement + text[end:])
with (vendor / "Cargo.toml").open("a") as file:
    file.write('\n[dependencies.kurbo]\nversion = "=0.13.1"\n')
with (out / "Rust/Cargo.toml").open("a") as file:
    file.write('\n[patch.crates-io]\nkrilla = { path = "vendor/krilla" }\n')
print(f"Prepared REVIEW-ONLY krilla/Kurbo candidate: {out}")
print("Run cargo update -p krilla --offline in the candidate before building.")
print("No release clearance, independent provenance, or behavior equivalence is implied.")
