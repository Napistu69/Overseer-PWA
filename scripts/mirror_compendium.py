#!/usr/bin/env python3
"""Mirror the authoritative Compendium into the site's content tree — dry run by default.

WHY. Three copies of the Compendium exist on this machine and only one is authoritative:

    C:\\TekTribe\\Overseer\\akashic_research\\Compendium   <- AUTHORITATIVE (corrected, indexed,
                                                              citation authority for AEFT)
    <repo>\\content\\                                <- the site mirror (what the site renders)
    C:\\TekTribe\\Chronicles\\Compendium            <- strata, superseded, NEVER a source
                                                       (still carries retired forms)

Hand-copying between them is what produced months of drift-back. This tool makes the
derivation a checked operation: it maps each site file to its corpus counterpart, diffs the
BODY (frontmatter is site-specific and never overwritten), and reports before it writes.

USAGE
    python scripts/mirror_compendium.py                    # dry run: report only
    python scripts/mirror_compendium.py --verbose          # + per-file first-difference detail
    python scripts/mirror_compendium.py --apply            # write the diffs (frontmatter kept)
    python scripts/mirror_compendium.py --corpus <path>    # override the authority root

RULES IT ENFORCES
  * Only the authority root is ever read. Chronicles/ is refused by name.
  * The site's frontmatter block is preserved verbatim; only the body is replaced.
  * A file with no corpus counterpart is reported, never guessed at.
  * Retired forms are counted on both sides, so a mirror cannot silently re-import them.
  * No writes without --apply; --apply prints every file it writes.
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CONTENT = SITE / "content"
DEFAULT_CORPUS = Path(r"C:\TekTribe\Overseer\akashic_research\Compendium")
REFUSED = ("chronicles",)

FM = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
RETIRED = {
    "Overseer Æ": re.compile(r"Overseer\s+Æ"),
    "Petrol Goliath": re.compile(r"Petrol\s+Goliath"),
}
# Corpus families whose files are the counterpart of a site part/ directory. Used only when
# title matching is ambiguous; the mapping still has to be by identity, not by position.
SKIP_CORPUS = re.compile(r"(--Index\.md$|Master_Index\.md$|Unified_Part_I_Index\.md$)")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def frontmatter(text: str) -> dict:
    m = FM.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(0).strip("-").strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def body(text: str) -> str:
    return FM.sub("", text, count=1).strip()


def corpus_index(root: Path):
    by_title, by_stem = {}, {}
    for p in sorted(root.rglob("*.md")):
        if SKIP_CORPUS.search(p.name):
            continue
        t = norm(frontmatter(p.read_text(encoding="utf-8", errors="replace")).get("title", ""))
        if t:
            by_title.setdefault(t, p)
        by_stem.setdefault(norm(p.stem.split("--")[-1]), p)
    return by_title, by_stem


def match(site_file: Path, by_title, by_stem):
    meta = frontmatter(site_file.read_text(encoding="utf-8", errors="replace"))
    t = norm(meta.get("title", ""))
    if t and t in by_title:
        return by_title[t], "title"
    stem = norm(site_file.stem.replace("_index", ""))
    if stem in by_stem:
        return by_stem[stem], "stem"
    for k, p in by_title.items():          # containment, longest match wins
        if t and len(t) > 12 and (t in k or k in t):
            return p, "title~"
    for k, p in by_stem.items():
        if stem and len(stem) > 8 and (stem in k or k in stem):
            return p, "stem~"
    return None, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    ap.add_argument("--apply", action="store_true", help="write body replacements (frontmatter kept)")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    root = Path(a.corpus)
    if any(x in str(root).lower() for x in REFUSED):
        print(f"REFUSED: {root} is strata, never a mirror source.")
        return 2
    if not root.exists():
        print(f"corpus root not found: {root}")
        return 2

    by_title, by_stem = corpus_index(root)
    site_files = sorted(p for p in CONTENT.rglob("*.md"))
    print(f"authority : {root}")
    print(f"site      : {CONTENT} ({len(site_files)} files)\n")

    identical, differ, unmapped = [], [], []
    retired_site = retired_corpus = 0
    rows = []
    for sf in site_files:
        cp, how = match(sf, by_title, by_stem)
        rel = sf.relative_to(CONTENT).as_posix()
        site_text = sf.read_text(encoding="utf-8", errors="replace")
        for rx in RETIRED.values():
            retired_site += len(rx.findall(site_text))
        if cp is None:
            unmapped.append(rel)
            continue
        ct = cp.read_text(encoding="utf-8", errors="replace")
        for rx in RETIRED.values():
            retired_corpus += len(rx.findall(ct))
        sb, cb = body(site_text), body(ct)
        if sb == cb:
            identical.append((rel, how))
            continue
        ratio = difflib.SequenceMatcher(None, sb, cb).ratio()
        d = list(difflib.unified_diff(sb.splitlines(), cb.splitlines(), lineterm="", n=0))
        changed = sum(1 for l in d if l.startswith(("+", "-")) and not l.startswith(("+++", "---")))
        differ.append((rel, cp.relative_to(root).as_posix(), how, len(sb), len(cb), ratio, changed))
        if a.verbose:
            first = next((l for l in d if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))), "")
            rows.append((rel, first[:150]))

    print(f"identical bodies : {len(identical)}")
    print(f"differing bodies : {len(differ)}")
    print(f"no counterpart   : {len(unmapped)}")
    print(f"retired forms    : site {retired_site} · corpus {retired_corpus}   "
          f"(a mirror must never raise the site's count)\n")

    if differ:
        print("DIFFERING (site body vs authority):")
        print(f"  {'site file':58s} {'chars':>13s}  {'sim':>5s} {'lines':>5s}")
        for rel, cp, how, ls, lc, ratio, changed in differ:
            print(f"  {rel:58s} {ls:6d}->{lc:<6d} {ratio:5.2f} {changed:5d}   [{how}] {cp}")
    if unmapped:
        print("\nNO COUNTERPART IN THE AUTHORITY (reported, never guessed):")
        for rel in unmapped:
            print(f"  {rel}")
    if rows:
        print("\nfirst difference per file:")
        for rel, first in rows:
            print(f"  {rel}: {first}")

    if not a.apply:
        print("\ndry run — nothing written. Re-run with --apply after reading the diff.")
        return 0

    written = 0
    for rel, cp, how, ls, lc, ratio, changed in differ:
        sf = CONTENT / rel
        site_text = sf.read_text(encoding="utf-8", errors="replace")
        m = FM.match(site_text)
        head = m.group(0) if m else ""
        new = head + body(cp.read_text(encoding="utf-8", errors="replace")) + "\n"
        sf.write_text(new, encoding="utf-8", newline="")
        written += 1
        print(f"  wrote {rel}")
    print(f"\napplied: {written} file(s). Run the build: bash build.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())