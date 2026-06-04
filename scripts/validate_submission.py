#!/usr/bin/env python3
"""Validate a parsed Open3DCP dataset submission and emit a markdown readiness checklist.

Honest, structure-only validation — it never invents a fidelity score. The authoritative 0-100
fidelity score is computed during human curation by `open3dcp-ingest`.

Usage:
  python scripts/validate_submission.py [--form PATH] [--body-file PATH] [--index PATH] [--out checklist.md]
  body also taken from $ISSUE_BODY or stdin.
  Writes the checklist to --out (and stdout). Exit 0 if all hard checks pass, 1 otherwise.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_submission import DEFAULT_FORM, load_fields, parse_body, read_body  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INDEX = os.path.join(REPO_ROOT, "submissions", "index.json")
MARKER = "<!-- open3dcp-validation -->"

REQUIRED = ["dataset_title", "dataset_doi", "archive_url", "source_citation", "lab_name", "license", "schema_version"]
LICENSE_ALLOW = {"CC BY 4.0", "CC0 1.0", "Other open license"}
CURRENT_SCHEMA = "1.6"
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
URL_RE = re.compile(r"^https?://\S+$", re.I)
ORCID_RE = re.compile(r"^(\d{4}-){3}\d{3}[\dX]$")
# The four advertised archives (Zenodo / DesignSafe / MDF-NIST / Dataverse) + DOI resolvers, so a
# doi.org link doesn't trip the "unrecognized archive" warning. Keep in sync with the user-facing copy.
KNOWN_ARCHIVES = ("zenodo.org", "designsafe-ci.org", "materialsdatafacility", "mdf",
                  "dataverse", "doi.org", "datacite.org")


def normalize_doi(doi):
    doi = doi.strip()
    for pre in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if doi.lower().startswith(pre):
            doi = doi[len(pre):]
    return doi.strip()


def orcid_valid(orcid):
    """ORCID format + ISO 7064 MOD 11-2 checksum."""
    if not ORCID_RE.match(orcid):
        return False
    digits = orcid.replace("-", "")
    total = 0
    for ch in digits[:-1]:
        total = (total + int(ch)) * 2
    result = (12 - total % 11) % 11
    check = "X" if result == 10 else str(result)
    return check == digits[-1].upper()


def load_index(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def validate(parsed, index):
    """Return (checks, warnings). checks = [(name, ok, detail)]; a False ok is a hard failure."""
    checks, warnings = [], []
    g = lambda k: (parsed.get(k) or "").strip() if isinstance(parsed.get(k), str) else parsed.get(k)

    missing = [k for k in REQUIRED if not g(k)]
    checks.append(("Required fields present", not missing,
                   "all present" if not missing else "missing: " + ", ".join(missing)))

    doi = normalize_doi(g("dataset_doi") or "")
    checks.append(("Dataset DOI format", bool(doi) and bool(DOI_RE.match(doi)),
                   doi or "—"))

    url = g("archive_url") or ""
    url_ok = bool(URL_RE.match(url))
    checks.append(("Archive URL", url_ok, url or "—"))
    if url_ok and not any(h in url.lower() for h in KNOWN_ARCHIVES):
        warnings.append("Archive URL host is not a recognized archive (Zenodo / DesignSafe / MDF-NIST / "
                        "Dataverse). A curator will confirm it resolves to the dataset.")

    orcid = g("declared_orcid") or ""
    checks.append(("ORCID iD", orcid == "" or orcid_valid(orcid),
                   "not provided" if orcid == "" else (orcid if orcid_valid(orcid) else f"invalid: {orcid}")))

    lic = g("license") or ""
    checks.append(("License redistributable", lic in LICENSE_ALLOW, lic or "—"))

    sv = g("schema_version") or ""
    checks.append(("Schema version present", bool(sv), sv or "—"))
    if sv and sv != CURRENT_SCHEMA:
        warnings.append(f"Schema version is `{sv}`; the current Open3DCP schema is `{CURRENT_SCHEMA}`. "
                        "A curator will confirm the mapping.")

    redist = parsed.get("redistribution_confirmed") or []
    checks.append(("Redistribution confirmed", len(redist) >= 1, "checked" if redist else "not checked"))

    arch_ack = parsed.get("archive_ack") or []
    checks.append(("Archive-resolves declaration", len(arch_ack) >= 1, "checked" if arch_ack else "not checked"))

    dup = doi and any(normalize_doi(str(row.get("dataset_doi", ""))) == doi for row in index)
    checks.append(("Not a duplicate DOI", not dup,
                   "already in catalog" if dup else "new"))

    return checks, warnings


def _cell(s):
    """Keep user-controlled text from breaking the markdown table (display-only; never eval'd)."""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def render(checks, warnings):
    passed = all(ok for _, ok, _ in checks)
    out = [MARKER, "", f"**Open3DCP submission check** — {'PASS ✅' if passed else 'NEEDS FIXES ❌'}", "",
           "| Check | Result | Detail |", "|---|:---:|---|"]
    for name, ok, detail in checks:
        out.append(f"| {name} | {'✅' if ok else '❌'} | {_cell(detail)} |")
    if warnings:
        out += ["", "**Notes**"]
        out += [f"- ⚠️ {w}" for w in warnings]
    if not passed:
        out += ["", "Edit the issue to fix the ❌ items above — this check re-runs automatically."]
    out += ["", f"_The authoritative 0–100 fidelity score is computed during curation by `open3dcp-ingest`; "
                f"this automated check validates structure only._"]
    return "\n".join(out) + "\n", passed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", default=DEFAULT_FORM)
    ap.add_argument("--body-file")
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--out")
    args = ap.parse_args()

    try:  # markdown checklist contains ✅/❌; ensure stdout can carry them on any platform
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    fields = load_fields(args.form)
    parsed = parse_body(read_body(args), fields)
    checks, warnings = validate(parsed, load_index(args.index))
    md, passed = render(checks, warnings)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md)
    sys.stdout.write(md)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
