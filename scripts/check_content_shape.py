#!/usr/bin/env python3
"""
Content-shape gate for the PWA content tree.

Enforces source shapes that render badly if violated. Scope is deliberately
site `content/` only (Overseer ruling 2026-10-05): the marker can never
legitimately appear in rendered site content, whereas the corpus and its
backups legitimately hold both markers and pre-edit baselines. A gate that
fires on its own backups is a gate everyone learns to bypass.

Two rules:

  FATAL  line-leading `=> ` entry marker. A lumo-era workaround for `>`
         escaping into plain text; retired because it is never stripped by a
         template and leaks to the reader as literal text. Inline flow arrows
         (`asylum => jail`) are legitimate and are NOT flagged — only a
         line-leading marker is.

  PENDING a bold title line immediately followed by unseparated body text.

         NOTE: the sibling shape — a bold title run into prose on one line, as
         in the Part V index entries — is deliberately NOT rule-enforced. It
         was trialled and produced 266 matches across the tree (97 even when
         narrowed to list items), i.e. it cannot distinguish an entry title
         from an ordinary bold lead-in. It is fixed by the shape ruling, not
         by regex; spot-check it by hand instead of trusting a rule here.
         This is a real rendering defect (title and description collapse into
         one paragraph) but it is still present in Parts II-V at the time of
         writing, pending the corpus shape fix. It is counted and reported
         here, not enforced, so the gate does not block deploys on a known
         outstanding fix. Flip PENDING_RULES_ENFORCED to True once the corpus
         pass lands and the site mirrors are re-derived.
"""

import re
import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

PENDING_RULES_ENFORCED = True

LINE_LEADING_MARKER = re.compile(r"^\s*(?:-\s*)?=>\s")
# A line that is nothing but a bold title, with a non-blank, non-block line
# immediately after it: markdown soft-wraps the two into one paragraph.
BOLD_TITLE_ONLY = re.compile(r"^\s*(?:[-*]\s+)?\*\*[^*]+\*\*\s*$")
BLOCK_START = ("#", "|", "-", "*", ">", "=")


def scan():
    markers, bleeds = [], []
    # Scoped to *_index.md: the entry-list shape only exists in Index files.
    # Thread pages (e.g. the Architecture Synthesis) are a different construct
    # and were ruled out of scope, so they must not be counted here.
    for path in sorted(CONTENT_DIR.rglob("_index.md")):
        rel = path.relative_to(CONTENT_DIR.parent)
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            if LINE_LEADING_MARKER.match(line):
                markers.append((rel, i, line.strip()[:90]))
            if BOLD_TITLE_ONLY.match(line) and i < len(lines):
                nxt = lines[i]
                if nxt.strip() and not nxt.startswith(BLOCK_START):
                    bleeds.append((rel, i, line.strip()[:60], nxt.strip()[:60]))
    return markers, bleeds


def main():
    markers, bleeds = scan()

    if markers:
        print("  CONTENT-SHAPE GATE FAILED — line-leading `=> ` marker")
        for rel, lineno, snippet in markers:
            print(f"    {rel}:{lineno}  {snippet}")
        print(f"\n  {len(markers)} marker(s). Strip the marker; keep any `— ` separator.")
        return 1

    print(f"  Content-shape gate: clean (0 line-leading `=> ` markers)")

    state = "FAILED" if PENDING_RULES_ENFORCED else "not yet enforced"

    if bleeds:
        print(f"  [{state}] bold title line followed by unseparated body: {len(bleeds)}")
        for rel, n in sorted(_by_file(bleeds).items()):
            print(f"    {rel}: {n}")
    else:
        print("  0 bold title lines followed by unseparated body")

    if PENDING_RULES_ENFORCED and bleeds:
        return 1
    return 0


def _by_file(rows):
    out = {}
    for row in rows:
        out[row[0]] = out.get(row[0], 0) + 1
    return out


if __name__ == "__main__":
    sys.exit(main())
