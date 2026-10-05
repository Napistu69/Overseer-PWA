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

PENDING_RULES_ENFORCED = False

LINE_LEADING_MARKER = re.compile(r"^\s*(?:-\s*)?=>\s")
# A line that is nothing but a bold title, with a non-blank, non-block line
# immediately after it: markdown soft-wraps the two into one paragraph.
BOLD_TITLE_ONLY = re.compile(r"^\s*(?:[-*]\s+)?\*\*[^*]+\*\*\s*$")
BLOCK_START = ("#", "|", "-", "*", ">", "=")


def scan():
    markers, bleeds = [], []
    for path in sorted(CONTENT_DIR.rglob("*.md")):
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

    if bleeds:
        state = "FAILED" if PENDING_RULES_ENFORCED else "not yet enforced"
        print(f"  Content-shape gate [{state}] — bold title line followed by unseparated body: {len(bleeds)}")
        by_file = {}
        for rel, _, _, _ in bleeds:
            by_file[rel] = by_file.get(rel, 0) + 1
        for rel, n in sorted(by_file.items()):
            print(f"    {rel}: {n}")
        if PENDING_RULES_ENFORCED:
            return 1
    else:
        print("  Content-shape gate: 0 bleeding bold title lines")

    return 0


if __name__ == "__main__":
    sys.exit(main())
