#!/usr/bin/env python3
"""Generate Open3DCP_TERM_JUSTIFICATION.md from the authoritative column list.

Reads the canonical columns from sql/create_tables.sql (the source of truth), enriches
them with descriptions/standards from Open3DCP_SCHEMA.md and a relational-schema crosswalk
note from crosswalk/open3dcp_to_relational.yaml, and writes one justified entry per
term. Doubles as the COVERAGE GATE: exits non-zero if any SQL column lacks an entry.

Usage:
    python tools/term_justification/generate.py            # write the appendix
    python tools/term_justification/generate.py --check    # verify coverage only (CI)
"""
from __future__ import annotations

import argparse
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SQL = os.path.join(REPO, "sql", "create_tables.sql")
SCHEMA = os.path.join(REPO, "Open3DCP_SCHEMA.md")
CROSSWALK = os.path.join(REPO, "crosswalk", "open3dcp_to_relational.yaml")
OUT = os.path.join(REPO, "Open3DCP_TERM_JUSTIFICATION.md")

STD_RE = re.compile(r"\b(ASTM\s*[A-Z]?\d[\w/.\-]*|EN\s*\d[\w\-]*|EN\s*\d{3}-\d|ACI\s*[\w.]+|"
                    r"RILEM[\w \-]*|NT\s*BUILD\s*\d+|ASTM\s*D\d+|ICC\s*\d+)", re.I)
# NOTE: a trailing \b fails after "VARCHAR(20)" because ")"->"," is not a word boundary,
# which would silently drop every varchar/text column. Use a lookahead for space/comma instead.
TYPE_RE = re.compile(r"^\s*([a-z][a-z0-9_]+)\s+(SERIAL|REAL|INTEGER|BOOLEAN|TIMESTAMPTZ|"
                     r"VARCHAR\(\d+\)|TEXT|NUMERIC|DATE)(?=[\s,]|$)(.*)$", re.I)
SECTION_RE = re.compile(r"^\s*--\s*(?:-+\s*)?(.+?)\s*-*$")

# 3DCP-native sections (no conventional-dataset equivalent)
THREEDCP_SECTIONS = {"3DCP PROCESS PARAMETERS", "Pumping System", "3DCP INTERLAYER PROPERTIES"}
THREEDCP_COLS = {"static_yield_stress_pa", "dynamic_yield_stress_pa", "thixotropy_pa_per_s",
                 "structuration_rate_pa_per_s", "open_time_min", "green_strength_kpa",
                 "test_orientation", "test_orientation_code"}


def parse_sql_columns(path):
    """Return ordered [(column, type, inline_desc, section)] for the mix_designs table."""
    cols = []
    in_table = False
    section = "Identity & Versioning"
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if "CREATE TABLE IF NOT EXISTS mix_designs" in line:
                in_table = True
                continue
            if in_table and re.match(r"^\s*\);", line):
                break
            if not in_table:
                continue
            # section banner: a comment line that is not a column and not a stray note
            if line.strip().startswith("--"):
                m = SECTION_RE.match(line)
                if m:
                    label = m.group(1).strip()
                    # only treat as a section if it looks like a heading (UPPER or Title (mass-%))
                    if label and (label.isupper() or "(mass-%)" in label or label.istitle()):
                        # strip "COMPOSITION — " prefix
                        label = label.split("—")[-1].strip()
                        label = re.sub(r"\s*\(mass-%\)\s*$", "", label)
                        if 2 < len(label) < 60 and not label.startswith("NOTE"):
                            section = label
                continue
            m = TYPE_RE.match(line)
            if m:
                col, typ, rest = m.group(1), m.group(2), m.group(3)
                desc = ""
                if "--" in rest:
                    desc = rest.split("--", 1)[1].strip()
                if col.lower() in ("id",):
                    continue
                cols.append((col, typ, desc, section))
    return cols


def parse_schema_md(path):
    """Map column -> (description, standard) from the markdown tables."""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            col = cells[0].strip("`")
            desc = cells[2] if len(cells) > 2 else ""
            std = ""
            # a trailing cell often holds the standard
            for c in cells[3:]:
                if STD_RE.search(c):
                    std = c
                    break
            if not std:
                m = STD_RE.search(" ".join(cells))
                std = m.group(0) if m else ""
            out[col] = (desc, std)
    return out


def build_relational_crosswalk_map(path):
    """column -> short relational-schema reference string."""
    import yaml
    with open(path, encoding="utf-8") as fh:
        cw = yaml.safe_load(fh)
    m = {}
    for entry in cw.get("mappings", []):
        if "pivot_on" in entry:
            for cat, col in entry.get("pivot_map", {}).items():
                m.setdefault(col, f"`{entry['src']}` (by `{entry['pivot_on']}`={cat})")
            continue
        if entry.get("open3dcp"):
            m[entry["open3dcp"]] = f"`{entry['src']}`"
        rb = entry.get("refine_by") or {}
        for _, col in (rb.get("map") or {}).items():
            m.setdefault(col, f"`{entry['src']}` (+ `{rb.get('src')}`)")
    for q, spec in cw.get("quantity_map", {}).items():
        m[spec["open3dcp"]] = f"`data` where `quantity_reported={q}`"
    return m


def standard_for(col, sql_desc, schema_std):
    s = schema_std or ""
    if not s:
        mm = STD_RE.search(sql_desc)
        s = mm.group(0) if mm else ""
    return s.strip()


def rationale(col, section, std, rel_ref):
    # Efficiency: the term-frequency methodology is stated once in the header. Each row
    # carries only what is term-specific -- the 3DCP marker and the purposeful crosswalk link.
    is_3dcp = section in THREEDCP_SECTIONS or col in THREEDCP_COLS
    parts = []
    if is_3dcp:
        parts.append("3DCP-native (RILEM TC 276-DFC / 304-ADC).")
    if rel_ref:
        parts.append(f"Relational: {rel_ref}")
    elif not is_3dcp:
        parts.append("Open3DCP-specific.")
    return " ".join(parts) if parts else "—"


def generate():
    cols = parse_sql_columns(SQL)
    schema = parse_schema_md(SCHEMA)
    rel = build_relational_crosswalk_map(CROSSWALK)

    # group by section preserving order
    sections = []
    by_section = {}
    for col, typ, sqldesc, section in cols:
        if section not in by_section:
            by_section[section] = []
            sections.append(section)
        by_section[section].append((col, typ, sqldesc))

    missing_desc = []
    lines = [
        "# Open3DCP — Term Justification (Appendix)",
        "",
        "> **Auto-generated** by `tools/term_justification/generate.py` from the canonical column",
        "> list in [`sql/create_tables.sql`](sql/create_tables.sql). Do not edit by hand — edit the",
        "> schema/crosswalk and regenerate. This appendix justifies every Open3DCP term and unit",
        "> for downstream interoperability and reuse.",
        "",
        "## How terms were chosen",
        "",
        "Each column uses the **most frequently used term** for its quantity, determined by",
        "compiling the corpus of 3D-printable-cement literature and datasets; alternate spellings",
        "normalize to that canonical term. Per term, the table gives its governing standard and —",
        "where one exists — its relational-schema crosswalk. 3DCP-only terms are justified against",
        "RILEM TC 276-DFC / TC 304-ADC.",
        "",
        f"**Coverage:** {len(cols)} canonical `mix_designs` terms, grouped into {len(sections)} sections.",
        "",
        "---",
        "",
    ]
    for section in sections:
        lines.append(f"## {section}")
        lines.append("")
        lines.append("| Term | Type | Definition | Standard | Justification & crosswalk |")
        lines.append("|---|---|---|---|---|")
        for col, typ, sqldesc in by_section[section]:
            md_desc, md_std = schema.get(col, ("", ""))
            desc = md_desc or sqldesc or "—"
            if not (md_desc or sqldesc):
                missing_desc.append(col)
            std = standard_for(col, sqldesc, md_std) or "—"
            rel_ref = rel.get(col, "")
            just = rationale(col, section, std if std != "—" else "", rel_ref)
            desc = desc.replace("|", "/")
            just = just.replace("|", "/")
            lines.append(f"| `{col}` | {typ.lower()} | {desc} | {std} | {just} |")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by Sunnyday Technologies. "
                 "Regenerate with `python tools/term_justification/generate.py`.*")
    return "\n".join(lines) + "\n", cols, missing_desc


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="verify coverage only; do not write")
    args = p.parse_args(argv)
    content, cols, missing_desc = generate()
    print(f"canonical terms: {len(cols)}")
    if missing_desc:
        print(f"WARNING: {len(missing_desc)} terms lack a description: {missing_desc}", file=sys.stderr)
    if args.check:
        # coverage gate: every SQL column must be representable; fail on missing descriptions
        if missing_desc:
            return 1
        print("coverage OK: every canonical term has a justification entry.")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
