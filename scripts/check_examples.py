#!/usr/bin/env python3
"""Validate the examples/ directory. Run: python scripts/check_examples.py

For every examples/<dir>/ with a record.json:
  - record.json has the required keys and a redistributable license (allowlist);
  - a NOTICE file is present;
  - if the build_cmd uses open3dcp-ingest, re-run it and confirm the committed *.open3dcp.csv is
    reproducible (exact structure/text; eight-ULP allowance in REAL columns only).
Optionally scans examples/ against a LOCAL blocklist (scripts/examples_blocklist.txt, gitignored) —
the public script never enumerates sensitive/commercial terms itself. Absent the file (e.g. in CI),
the scan is skipped; the maintainer runs it locally before publishing.

Exit 0 if everything passes, 1 otherwise.
"""
import glob
import csv
import json
import math
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
with open(os.path.join(ROOT, "sql", "create_tables.sql"), encoding="utf-8") as _schema:
    REAL_COLUMNS = set(re.findall(r"^\s+(\w+)\s+REAL\b", _schema.read(), re.M))

try:  # Windows consoles default to cp1252; keep the "·"/"✓" status glyphs from crashing
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
REQUIRED = ["id", "dataset", "license", "license_url", "attribution", "classification"]
ALLOWED_LICENSES = {
    "cc by 4.0", "cc0 1.0", "cc0", "us public domain", "nist open license",
    "nist open license (us public domain)", "godl-india", "mit",
}
# Optional local blocklist (gitignored): one regex per line, '#' comments. The public script does
# not enumerate sensitive/commercial terms; the maintainer keeps them out-of-tree.
BLOCKLIST = os.path.join(ROOT, "scripts", "examples_blocklist.txt")
TEXT_EXT = {".md", ".html", ".css", ".csv", ".json", ".py", ".yml", ".yaml", ".txt", ""}

errors, notes = [], []


def equivalent_csv(left, right):
    """Exact structure/text; permit at most eight float ULPs of serialization noise.

    Python's summation implementations can differ in their last few binary digits.
    This is a machine-precision allowance, not a scientific/measurement tolerance.
    Empty cells, row/column order and nonnumeric provenance must remain identical.
    """
    with open(left, encoding="utf-8", newline="") as f:
        a = list(csv.reader(f))
    with open(right, encoding="utf-8", newline="") as f:
        b = list(csv.reader(f))
    if not a or not b or a[0] != b[0] or len(a) != len(b):
        return False
    for x, y in zip(a[1:], b[1:]):
        if len(x) != len(a[0]) or len(y) != len(a[0]):
            return False
        for column, old, new in zip(a[0], x, y):
            if old == new:
                continue
            if column not in REAL_COLUMNS:
                return False
            try:
                u, v = float(old), float(new)
            except ValueError:
                return False
            if not (math.isfinite(u) and math.isfinite(v)):
                return False
            if abs(u - v) > 8 * max(math.ulp(u), math.ulp(v)):
                return False
    return True


def check_record(d, rec):
    rel = os.path.relpath(d, ROOT)
    for k in REQUIRED:
        if not rec.get(k):
            errors.append(f"{rel}: record.json missing '{k}'")
    if not (rec.get("source_url") or rec.get("doi")):
        errors.append(f"{rel}: record.json needs source_url or doi")
    lic = str(rec.get("license", "")).strip().lower()
    if lic not in ALLOWED_LICENSES:
        errors.append(f"{rel}: license '{rec.get('license')}' not in the redistributable allowlist "
                      f"(CC BY 4.0 / CC0 / US public domain / GODL-India / MIT)")
    if not os.path.exists(os.path.join(d, "NOTICE")):
        errors.append(f"{rel}: missing NOTICE (attribution is mandatory for stored data)")


def reproduce(d, rec):
    """If build_cmd is an open3dcp-ingest convert, re-run it and diff the committed output."""
    rel = os.path.relpath(d, ROOT)
    cmd = str(rec.get("build_cmd", ""))
    if not cmd.startswith("open3dcp-ingest"):
        notes.append(f"{rel}: reproduce-and-diff skipped (hand-curated build: {cmd[:48]}…)")
        return
    toks = cmd.split()
    src = toks[toks.index("convert") + 1]
    kind = toks[toks.index("--kind") + 1] if "--kind" in toks else None
    src_path = os.path.join(d, src)
    if not os.path.exists(src_path):
        errors.append(f"{rel}: build input not found: {src}")
        return
    base = os.path.splitext(os.path.basename(src))[0]
    committed = os.path.join(d, f"{base}.open3dcp.csv")
    if not os.path.exists(committed):
        errors.append(f"{rel}: committed {base}.open3dcp.csv not found")
        return
    with tempfile.TemporaryDirectory() as tmp:
        run = [sys.executable, "-m", "open3dcp_ingest.cli", "convert", src_path, "--out", tmp]
        if kind:
            run += ["--kind", kind]
        r = subprocess.run(run, capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"{rel}: open3dcp-ingest failed: {r.stderr.strip()[:160]}")
            return
        produced = os.path.join(tmp, f"{base}.open3dcp.csv")
        if not equivalent_csv(committed, produced):
            errors.append(f"{rel}: committed {base}.open3dcp.csv does NOT match a fresh conversion (drift)")
        else:
            notes.append(f"{rel}: reproduce-and-diff OK ✓")


def token_guard():
    if not os.path.exists(BLOCKLIST):
        notes.append("blocklist scan skipped (no scripts/examples_blocklist.txt — local-only confidentiality list)")
        return
    pats = []
    for ln in open(BLOCKLIST, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            pats.append(re.compile(ln, re.I))
    for dirpath, _, files in os.walk(EX):
        for f in files:
            if os.path.splitext(f)[1].lower() not in TEXT_EXT:
                continue
            p = os.path.join(dirpath, f)
            try:
                txt = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for pat in pats:
                m = pat.search(txt)
                if m:
                    errors.append(f"{os.path.relpath(p, ROOT)}: blocklisted token '{m.group(0)}'")


def main():
    if not os.path.isdir(EX):
        print("no examples/ directory"); return 0
    dirs = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(EX, "*", "record.json")))
    if not dirs:
        errors.append("examples/ has no dataset folders with record.json")
    for d in dirs:
        try:
            rec = json.load(open(os.path.join(d, "record.json"), encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"{os.path.relpath(d, ROOT)}: bad record.json: {e}")
            continue
        check_record(d, rec)
        reproduce(d, rec)
    token_guard()

    for n in notes:
        print("  ·", n)
    if errors:
        print("\nFAIL — examples/ checks:")
        for e in errors:
            print("  ✗", e)
        return 1
    print(f"\nOK — {len(dirs)} example(s) valid; licenses allowlisted; NOTICE present; no banned tokens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
