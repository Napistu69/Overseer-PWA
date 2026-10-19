#!/usr/bin/env python3
"""Apply the Part V header case conversion to the SITE tree (content/part5).

Mapping source: the scribe's table `plans/part5_header_case_conversion.md` (rev 2), which is the
single mapping artifact — this script never invents a string. It reads the SITE column (= chosen
rule B minus the Roman-numeral prefix) and rewrites ONLY the matching '## ' header line of each
site file, leaving every other line byte-identical.

Matched on the text AFTER the numeral, because content/part5 lines carry none (the site's numerals
stay stripped). One row's site copy still carries the retired typo — that row is matched via an
explicit fallback and reported as such, never silently.

Dry-run by default. `--apply` writes. Exit 0 = every row matched; exit 2 = unmatched rows, nothing
written (an unmatched row means the base moved — re-read the table, do not improvise).
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

DEFAULT_TABLE = Path(r"C:/Users/Nefs/AppData/Local/hermes/profiles/compendium-scribe/plans/part5_header_case_conversion.md")
SITE = Path(__file__).resolve().parent.parent / "content" / "part5"

NUM = re.compile(r"^(?:[IVXLCDM]+)\.\s+")


def norm(s: str) -> str:
    """Case- and punctuation-insensitive identity key for a header's word sequence."""
    return re.sub(r"[^a-z0-9]", "", s.lower())

# The site's copy of this header still carries the pre-fix spelling; the table documents the
# substitution in its header block (line 8). Matched by token so the row is visible in the report.
TYPO_TOKENS = [("SoLidarity", "SOLEIDARITY")]


def load_rows(path: Path):
    rows, cur = [], None
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(.+?) :: line (\d+)$", ln)
        if m:
            cur = {"file": m.group(1), "corpus_line": int(m.group(2))}
            rows.append(cur)
            continue
        if cur is None:
            continue
        for k in ("OLD", "A", "B", "SITE"):
            if ln.startswith(f"  {k}"):
                cur[k] = ln[2 + len(k):].strip()
    missing = [r for r in rows if "SITE" not in r or "OLD" not in r]
    if missing:
        sys.exit(f"table rows missing a field: {len(missing)}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default=str(DEFAULT_TABLE))
    ap.add_argument("--site", default=str(SITE))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    table, site = Path(a.table), Path(a.site)
    if not table.exists():
        print(f"table not found: {table}")
        return 2
    rows = load_rows(table)
    print(f"table : {table}  ({len(rows)} rows)")
    print(f"site  : {site}\n")

    by_file = {}
    for r in rows:
        by_file.setdefault(r["file"], []).append(r)

    plan = []          # (file, old_line, new_line, mode)
    unmatched = []     # (file, corpus_line, wanted)
    dupes = []
    for fname, frows in by_file.items():
        p = site / fname
        if not p.exists():
            unmatched.append((fname, 0, "<file missing>"))
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        hdr_idx = [i for i, l in enumerate(lines) if l.startswith("## ") and not l.startswith("### ")]
        if len(hdr_idx) < len(frows):
            unmatched.append((fname, 0, f"file has {len(hdr_idx)} '## ' lines, table has {len(frows)} rows"))
            continue
        # Identity key is the row's WORD sequence, case- and punctuation-insensitive. Every
        # revision of this pass changes case only, so that key is stable across revisions: a
        # header already converted in a previous run (or converted and then re-cased by a later
        # promotion) is still found, and a SoL promotion cannot strand its own row.
        keys = {}
        for j in hdr_idx:
            keys.setdefault(norm(lines[j][3:].strip()), []).append(j)
        for i, r in enumerate(frows):
            want = NUM.sub("", r["OLD"]).strip()
            cands = [(want, "row key (case-insensitive)")]
            for a_, b_ in TYPO_TOKENS:
                if a_ in want:
                    cands.append((want.replace(a_, b_), f"retired-spelling fallback ({b_})"))
            if r.get("SITE"):
                cands.append((r["SITE"], "target text"))
            hit = None
            for cand, mode in cands:
                idxs = keys.get(norm(cand), [])
                if len(idxs) == 1:
                    hit = (idxs[0], cand, mode)
                    break
                if len(idxs) > 1:
                    dupes.append((fname, cand, len(idxs)))
            if hit is None:
                unmatched.append((fname, r["corpus_line"], want))
                continue
            idx, oldtxt, mode = hit
            plan.append((fname, idx + 1, lines[idx], "## " + r["SITE"], mode))

    print(f"matched   : {len(plan)} / {len(rows)}")
    print(f"unmatched : {len(unmatched)}")
    if dupes:
        print(f"AMBIGUOUS (same text twice in one file): {dupes}")
    for f, cl, want in unmatched:
        print(f"  UNMATCHED {f} (corpus line {cl}): wanted '{want}'")
    modes = {}
    for p_ in plan:
        modes[p_[4]] = modes.get(p_[4], 0) + 1
    print("match modes: " + " · ".join(f"{k} {v}" for k, v in sorted(modes.items())))
    for f, ln, old, new, mode in plan:
        if mode not in ("row key (case-insensitive)", "target text"):
            print(f"  {mode}  {f}:{ln}")

    changed = [p_ for p_ in plan if p_[2] != p_[3]]
    print(f"\nlines that would change: {len(changed)} of {len(plan)} (the rest already read as target)")
    for f, ln, old, new, _ in changed[:4]:
        print(f"  {f}:{ln}")
        print(f"      - {old}")
        print(f"      + {new}")

    if unmatched or dupes:
        print("\nREFUSING: unmatched or ambiguous rows — nothing written. The base moved; re-read the table.")
        return 2
    if not a.apply:
        print("\ndry run — nothing written. Re-run with --apply.")
        return 0

    written = 0
    per_file = {}
    for f, ln, old, new, _ in changed:
        per_file.setdefault(f, []).append((ln, old, new))
    for f, edits in per_file.items():
        p = site / f
        # newline="" on both sides: these files are CRLF, and a text-mode write would silently
        # normalise the whole file to LF and turn a 10-line edit into a full-file diff.
        with open(p, encoding="utf-8", newline="") as fh:
            raw = fh.read()
        lines = raw.splitlines(keepends=True)
        for ln, old, new in edits:
            body = lines[ln - 1].rstrip("\r\n")
            assert body.lstrip("\ufeff") == old, f"{f}:{ln} moved under us"
            ending = lines[ln - 1][len(body):]
            lines[ln - 1] = new + ending
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("".join(lines))
        written += 1
        print(f"  wrote {f} ({len(edits)} header(s))")

    # post-write proof: every table SITE string must now be present as a header line
    ok = 0
    for r in rows:
        p = site / r["file"]
        if p.exists() and ("## " + r["SITE"]) in p.read_text(encoding="utf-8"):
            ok += 1
    print(f"\napplied: {written} file(s). headers now matching the table SITE column: {ok}/{len(rows)}")
    print("next: bash build.sh")
    return 0 if ok == len(rows) else 3


if __name__ == "__main__":
    raise SystemExit(main())