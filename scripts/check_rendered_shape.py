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

SCOPE. Two lists, and the distinction is the whole point:

  IN_SCOPE   must read 0. The Index mirrors, where the canonical `— ` entry
             form applies.

  EXEMPT     pages carrying a *deliberate* run-in, pinned to an exact expected
             count. The ruling (user, 2026-10-05) leaves the Architecture
             Synthesis's 11 Layer lines as run-in titles — a design choice, not
             a defect. But it is NOT invisible here: the count is pinned so the
             page stays walled. A 12th bleed is a regression and fails; fixing
             the 11 also fails, so the exemption cannot rot into a stale
             allowance.

             Why it is recorded as an exemption rather than described as clean:
             the Layer lines do bleed. The `(Thread N)` parenthetical does not
             split them — the four `**DIMENSION N: …**` lines split because a
             bullet list follows them, and that list is the actual mechanism.

The reported number is "index bleed N / exempt 11" — never a bare zero, so it
cannot be quoted later as an absolute.
"""

import re
import sys
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent.parent / "public"
ENFORCE = True

# 3. RUNTIME DEPENDENCIES. A page may not depend on an artifact the build does not
#    produce. This is the check that would have caught `/akashic-index.json`: the file
#    existed only on one machine (gitignored, and its generator is not in build.sh), so a
#    deploy either served an HTML fallback for it or `/compendium-index.json` silently
#    became the whole search surface. Nothing about the page's source looks wrong in that
#    state — only the built output does. Dynamic targets (template interpolation) and
#    off-site URLs are skipped; every static same-origin target must resolve.
FETCH_RX = [
    re.compile(r"""fetch\(\s*["'](/[^"']+)["']"""),
    re.compile(r"""serviceWorker\.register\(\s*["'](/[^"']+)["']"""),
    re.compile(r"""register\(\s*["'](/[^"']+)["']"""),
]
TAG_RX = re.compile(r"<script[^>]*>|<link[^>]*>")
ATTR_RX = re.compile(r"""(?:src|href)=["']?(/[^"'\s>]+)""")
DYNAMIC = ("${", "{{", "%s")

# Must read 0 — the Index mirrors, where the `— ` entry form applies.
IN_SCOPE = ["preamble", "part1", "part2", "part3", "part4", "part5"]

# Deliberate run-in pages, pinned to an exact expected count.
EXEMPT = {
    "part4/the_complete_architecture_synthesis_and_transition": 11,
}

# <p><strong>Title</strong> prose...  — but NOT if the prose opens with an em-dash.
BLEED = re.compile(r"<p><strong>([^<]{2,140})</strong>(?!\s*—)\s*([^<]{20,})")


def count(page):
    return len(BLEED.findall(page.read_text(encoding="utf-8", errors="replace")))


def runtime_targets(page_text: str):
    """Static same-origin paths this page loads at runtime."""
    found = set()
    for rx in FETCH_RX:
        found |= set(rx.findall(page_text))
    for tag in TAG_RX.findall(page_text):
        if "<link" in tag and "manifest" not in tag and "icon" not in tag and "stylesheet" not in tag:
            continue
        for m in ATTR_RX.findall(tag):
            found.add(m)
    return {p for p in found if not any(d in p for d in DYNAMIC) and not p.startswith("//")}


def resolve(target: str):
    if target.endswith("/"):
        return PUBLIC / target.strip("/") / "index.html"
    return PUBLIC / target.lstrip("/")


# 4. The SERVED SEARCH INDEXES are content too. They are generated from the corpus/content
#    trees at step 1, so the source-side gates cannot see them, and a page's rendered output
#    does not contain them either — but every search result a reader sees comes from here.
#    A retired form surviving in an index is published text, so it fails the build.
INDEX_FILES = ["compendium-index.json", "akashic-index.json"]
# HORIZONTAL whitespace only. `\s` crosses line boundaries, so `... the Overseer\nÆ (...)`
# matched and this gate reported a retired form the source never contained — the same
# invented-adjacency class as the fusion it was catching. Adjacency must be same-line.
INDEX_RETIRED = [
    ("naming: Æ is the name, Overseer the title", re.compile(r"Overseer[ \t\u00a0]+Æ")),
    ("retired term: Petrol Goliath", re.compile(r"Petrol[ \t\u00a0]+Goliath")),
]


def main():
    if not PUBLIC.exists():
        print("  Rendered-shape check: skipped (no public/ — run after Hugo)")
        return 0

    state = "FAILED" if ENFORCE else "not yet enforced"
    failures = []

    # 1. Must be zero.
    total = 0
    rows = []
    for name in IN_SCOPE:
        page = PUBLIC / name / "index.html"
        if not page.exists():
            continue
        n = count(page)
        if n:
            rows.append((page.relative_to(PUBLIC).as_posix(), n))
            total += n

    print(f"  Rendered-shape check: index bleed {total} (must be 0)")
    for rel, n in rows:
        print(f"    /{rel}: {n}")
    if total:
        failures.append(f"index bleed is {total}, expected 0")

    # 2. Pinned exemptions: exact, both directions.
    for name, expected in sorted(EXEMPT.items()):
        page = PUBLIC / name / "index.html"
        if not page.exists():
            print(f"    exempt /{name}: page missing — check the exemption list")
            failures.append(f"exempt page /{name} not found")
            continue
        n = count(page)
        if n == expected:
            print(f"    exempt /{name}: {n} (recorded, intentional)")
        else:
            print(f"    exempt /{name}: {n} — expected {expected}")
            if n > expected:
                failures.append(f"exempt /{name}: {n} > {expected}, new bleed on an exempt page")
            else:
                failures.append(
                    f"exempt /{name}: {n} < {expected}, the run-in was fixed — retire the exemption"
                )

    # 3. Runtime dependencies must resolve in the built output.
    checked, missing = 0, {}
    for page in sorted(PUBLIC.rglob("*.html")):
        rel = page.relative_to(PUBLIC).as_posix()
        for t in sorted(runtime_targets(page.read_text(encoding="utf-8", errors="replace"))):
            checked += 1
            if not resolve(t).exists():
                missing.setdefault(t, []).append(rel)
    for js in sorted(PUBLIC.rglob("*.js")):
        text = js.read_text(encoding="utf-8", errors="replace")
        for rx in FETCH_RX[1:]:  # registration forms live in JS, not in the page
            for t in rx.findall(text):
                if any(d in t for d in DYNAMIC) or not t.startswith("/"):
                    continue
                checked += 1
                if not resolve(t).exists():
                    missing.setdefault(t, []).append(js.relative_to(PUBLIC).as_posix())

    print(f"  Rendered-shape check: runtime dependencies {checked} checked, {len(missing)} missing")
    for t, pages in sorted(missing.items()):
        print(f"    MISSING {t} — referenced by {len(pages)}: {pages[:3]}")
        failures.append(f"runtime dependency {t} is not in the build output")

    # 4. Retired forms in the served indexes.
    idx_hits = []
    for name in INDEX_FILES:
        f = PUBLIC / name
        if not f.exists():
            continue
        blob = f.read_text(encoding="utf-8", errors="replace")
        for label, rx in INDEX_RETIRED:
            n = len(rx.findall(blob))
            if n:
                idx_hits.append((name, label, n))
    print(f"  Rendered-shape check: served indexes {len(INDEX_FILES)} checked, {len(idx_hits)} carrying retired forms")
    for name, label, n in idx_hits:
        print(f"    {name}: {n}× [{label}] — fix the source file, then rebuild")
        failures.append(f"{name} publishes {n} retired form(s) [{label}]")

    if failures:
        print(f"  Rendered-shape check [{state}]")
        for f in failures:
            print(f"    {f}")
        return 1 if ENFORCE else 0

    print("  Rendered-shape check: pass (index 0, exemptions at their recorded counts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())