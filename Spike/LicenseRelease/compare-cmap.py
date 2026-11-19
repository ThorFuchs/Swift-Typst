#!/usr/bin/env python3
"""Compare two OpenType fonts' Unicode cmap sets (requires fonttools)."""
import argparse
import unicodedata
from fontTools.ttLib import TTFont

parser = argparse.ArgumentParser()
parser.add_argument("baseline", help="baseline OpenType font")
parser.add_argument("candidate", help="candidate OpenType font")
args = parser.parse_args()


def inspect(path):
    with TTFont(path) as font:
        cmap = font.getBestCmap()
        if cmap is None:
            raise SystemExit(f"No Unicode cmap: {path}")
        print(f"{path}: {len(cmap)} codepoints, MATH table: {'MATH' in font}")
        return set(cmap)


def report(label, codepoints):
    private = sum(unicodedata.category(chr(cp)) == "Co" for cp in codepoints)
    print(f"{label}: {len(codepoints)} ({private} private-use)")

baseline = inspect(args.baseline)
candidate = inspect(args.candidate)
report("baseline only", baseline - candidate)
report("candidate only", candidate - baseline)
