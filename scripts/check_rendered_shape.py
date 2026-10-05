#!/usr/bin/env python3
"""
Rendered-output shape check — runs AFTER the Hugo build, against public/.

This is the sign-off surface for the entry-title bleed. Source-shape rules
cannot see the defect (a bold title run into prose on one line is
indistinguishable from an ordinary bold lead-in — 266 false positives when
trialled), so the count that matters is taken from the built HTML.

Defect definition: a block whose first child is <strong>Title</strong> followed
immediately by prose, with NO `— ` separator. The `— ` form is the sanctioned
canonical entry shape (Overseer ruling 2026-10-05, Part I's single-line form),
so a remainder that opens with an em-dash is correct and is not counted.

Not enforced yet: the corpus shape fix is outstanding. Set ENFORCE = True once
the corpus lands, the site mirrors are re-derived, and this reports 0.
"""

import re
import sys
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent.parent / "public"
ENFORCE = True

# The entry-list surfaces only. Thread pages legitimately use bold lead-ins
# throughout (232 of them tree-wide), so scanning every index.html would bury
# the signal — the ruling's target is these six mirrors.
IN_SCOPE = ["preamble", "part1", "part2", "part3", "part4", "part5"]

# <p><strong>Title</strong> prose...  — but NOT if the prose opens with an em-dash.
BLEED = re.compile(r"<p><strong>([^<]{2,140})</strong>(?!\s*—)\s*([^<]{20,})")


def main():
    if not PUBLIC.exists():
        print("  Rendered-shape check: skipped (no public/ — run after Hugo)")
        return 0

    total = 0
    rows = []
    for name in IN_SCOPE:
        page = PUBLIC / name / "index.html"
        if not page.exists():
            continue
        n = len(BLEED.findall(page.read_text(encoding="utf-8", errors="replace")))
        if n:
            rows.append((page.relative_to(PUBLIC).as_posix(), n))
            total += n

    if not rows:
        print("  Rendered-shape check: clean (0 bold titles run into prose)")
        return 0

    state = "FAILED" if ENFORCE else "not yet enforced"
    print(f"  Rendered-shape check [{state}] — bold title run into prose, no `— ` separator: {total}")
    for rel, n in rows:
        print(f"    /{rel}: {n}")
    if ENFORCE:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())