#!/usr/bin/env python3
"""Inspect PDFs from CorpusProbe; PDF geometry and extraction are not correctness proofs."""
import argparse
import difflib
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("run", type=Path, help="CorpusProbe output directory")
args = parser.parse_args()
records = json.loads((args.run / "results.json").read_text())
if any(record.get("error") is not None for record in records):
    raise SystemExit("Corpus contains compilation failures")
fixtures = sorted({r["fixture"] for r in records})
if len(records) != 2 * len(fixtures):
    raise SystemExit("Expected one result per fixture and font mode")
summary = []
for fixture in fixtures:
    stem = Path(fixture).stem
    pdfs = {mode: args.run / mode / (stem + ".pdf") for mode in ("newcm", "stix")}
    text = {mode: subprocess.check_output(["pdftotext", "-raw", str(pdf), "-"], text=True) for mode, pdf in pdfs.items()}
    fonts = {mode: subprocess.check_output(["pdffonts", str(pdf)], text=True).splitlines()[2:] for mode, pdf in pdfs.items()}
    diff = "".join(difflib.unified_diff(text["newcm"].splitlines(keepends=True), text["stix"].splitlines(keepends=True), fromfile="newcm", tofile="stix"))
    (args.run / (stem + ".text.diff")).write_text(diff)
    info = {r["mode"]: r for r in records if r["fixture"] == fixture}
    if set(info) != {"newcm", "stix"}:
        raise SystemExit(f"Missing or duplicate mode for {fixture}")
    if any(info[mode]["warnings"] for mode in info):
        raise SystemExit(f"Unexpected compiler warning for {fixture}")
    if "NewCMMath" not in "\n".join(fonts["newcm"]) or "STIXTwoMath" not in "\n".join(fonts["stix"]):
        raise SystemExit(f"Expected math fonts are not embedded for {fixture}")
    if fixture == "05-glyphs.typ":
        arrows = "⇫⇬⇭⇮⇯⇰⇱⇲⇳"
        if any(arrows not in text[mode] for mode in info) or "DejaVuSansMono" not in "\n".join(fonts["stix"]):
            raise SystemExit("The rare-arrow fixture did not exercise the expected fallback")
    summary.append({"fixture": fixture, "rawTextEqual": text["newcm"] == text["stix"],
                    "newcmPages": info["newcm"]["pages"], "stixPages": info["stix"]["pages"],
                    "newcmWarnings": info["newcm"]["warnings"], "stixWarnings": info["stix"]["warnings"],
                    "newcmFonts": fonts["newcm"], "stixFonts": fonts["stix"]})
    print(f"{fixture}: pages {info['newcm']['pages']}/{info['stix']['pages']}, raw text {'equal' if text['newcm'] == text['stix'] else 'different'}")
(args.run / "comparison.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
