#!/usr/bin/env python3
"""Render the sample PDFs with Swift-Typst and rasterize them with Poppler."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = ROOT / "Examples" / "Documents"
IMAGES = ROOT / "Examples" / "Images"
NAMES = ["01-editorial", "02-mathematics", "03-report", "04-invoice", "05-resume", "06-letter"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compile and rasterize without changing committed images")
    args = parser.parse_args()
    if shutil.which("swift") is None or shutil.which("pdftoppm") is None:
        parser.error("Swift and Poppler's pdftoppm must both be on PATH")
    with tempfile.TemporaryDirectory(prefix="swift-typst-gallery-") as temporary:
        work = Path(temporary)
        subprocess.run(["swift", "run", "--package-path", str(ROOT / "Examples/Gallery"),
                        "Gallery", str(DOCUMENTS), str(work)], check=True, cwd=ROOT)
        for name in NAMES:
            subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-singlefile", "-png",
                            "-scale-to-x", "900", "-scale-to-y", "-1",
                            str(work / (name + ".pdf")), str(work / name)], check=True)
            image = work / (name + ".png")
            if not image.is_file() or image.stat().st_size == 0:
                raise RuntimeError("Rasterization produced no image: " + name)
            if not args.check:
                IMAGES.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, IMAGES / image.name)
            print(("Checked " if args.check else "Rendered ") + name, flush=True)


if __name__ == "__main__":
    main()
