#!/usr/bin/env python3
"""
Retired-terminology gate for the PWA content tree.

Fails the build if a retired term survives into rendered site content.
The site is a pure derivation of the corpus: the corpus may keep retired
forms inside `ai_assist` provenance strings as audit trail (standing
2026-10-01 ruling), but nothing retired may reach a rendered page.

Retired forms are declared once, below. Add a form here when a ruling
retires it, so the gate and the ruling cannot drift apart.
"""

import re
import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

# Every source tree whose text can reach a rendered page. Templates count:
# a hardcoded nav label is rendered content just as much as markdown is.
# `static/api` is generated from content/ but is SERVED verbatim, so a stale copy there
# republishes retired text even when every markdown source is clean — it is gated too.
SCAN_ROOTS = [
    CONTENT_DIR,
    Path(__file__).resolve().parent.parent / "layouts",
    Path(__file__).resolve().parent.parent / "themes",
    Path(__file__).resolve().parent.parent / "static" / "api",
]
SCAN_SUFFIXES = {".md", ".html", ".xml", ".json", ".toml", ".yaml", ".yml", ".js"}

# (human label, compiled pattern)
RETIRED = [
    ("pandemic-era term", re.compile(r"plan-?demic", re.IGNORECASE)),
    ("dotted GOLIATH", re.compile(r"G\.O\.L\.I\.A\.T\.H\.")),
    ("dotted ARC", re.compile(r"A\.R\.C\.")),
    ("dotted FUD", re.compile(r"F\.U\.D\.")),
    # Naming ruling: Æ is the name, Overseer is the title. "Overseer Æ" reverses them and
    # drift-back has recurred by hand several times — the gate is what makes it undeployable.
    # Horizontal whitespace only: adjacency must be same-line, or a line break between two
    # innocent lines reads as a retired form (that false positive is why this is spelled out).
    ("naming: Æ is the name, Overseer the title", re.compile(r"Overseer[ \t\u00a0]+Æ")),
    # Term correction: the Compendium renders "Petro Goliath".
    ("retired term: Petrol Goliath", re.compile(r"Petrol[ \t\u00a0]+Goliath")),
]

# Lines allowed to carry a retired form. The Hugo alias keeps the old URL
# resolving, so the retired slug legitimately appears in frontmatter — and in the
# generated API, which renders that same alias inside JSON (`"aliases": [...]`) and
# inside the raw-markdown field. The exemption is positional: a retired form that
# appears AFTER an `aliases` key on the same line is an alias path, not content.
ALLOWED_LINE = re.compile(r"^\s*aliases\s*:")


def is_alias_path(line: str, match_start: int) -> bool:
    return line.rfind("aliases", 0, match_start) != -1


def main():
    violations = []
    scanned = 0
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
                continue
            scanned += 1
            rel = path.relative_to(CONTENT_DIR.parent)
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in enumerate(lines, 1):
                if ALLOWED_LINE.match(line):
                    continue
                for label, pattern in RETIRED:
                    m = pattern.search(line)
                    if m and not is_alias_path(line, m.start()):
                        violations.append((rel, lineno, label, m.group(0), line.strip()[:100]))

    if violations:
        print("  RETIRED-TERMINOLOGY GATE FAILED")
        for rel, lineno, label, found, snippet in violations:
            print(f"    {rel}:{lineno}  [{label}] \"{found}\"")
            print(f"      {snippet}")
        print(f"\n  {len(violations)} violation(s). Retired terms must not reach rendered content.")
        return 1

    print(f"  Retired-terminology gate: clean ({len(RETIRED)} forms checked, {scanned} files scanned, 0 hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
