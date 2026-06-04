#!/usr/bin/env python3
"""Parse a GitHub Issue Form body into {field_id: value}.

The Issue Form YAML (.github/ISSUE_TEMPLATE/dataset-submission.yml) is the single source of truth:
GitHub renders each field as a `### <label>` section, so we read the form to map label -> id (and type)
rather than hardcoding it here. Keeps the page, the form, the parser, and the validator in lockstep.

Usage:
  python scripts/parse_submission.py [--form PATH] [--body-file PATH]   # body also taken from $ISSUE_BODY or stdin
  -> prints {field_id: value} as JSON.  Checkbox fields parse to a list of the checked option labels.
"""
import argparse
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FORM = os.path.join(REPO_ROOT, ".github", "ISSUE_TEMPLATE", "dataset-submission.yml")
VALUE_TYPES = ("input", "textarea", "dropdown", "checkboxes")
NO_RESPONSE = {"_No response_", "_No response_.", "*No response*"}


def load_fields(form_path):
    """Return [{id, label, type}] for the form's value-bearing elements, in order."""
    import yaml  # pyyaml; same dep the ingest tool already uses
    with open(form_path, encoding="utf-8") as fh:
        form = yaml.safe_load(fh)
    fields = []
    for el in form.get("body", []) or []:
        if el.get("type") not in VALUE_TYPES or not el.get("id"):
            continue
        label = (el.get("attributes", {}) or {}).get("label", "").strip()
        fields.append({"id": el["id"], "label": label, "type": el["type"]})
    labels = [f["label"] for f in fields]
    if not all(labels) or len(set(labels)) != len(labels):
        raise ValueError("Issue Form has empty or duplicate field labels; the parser locates sections by label.")
    return fields


def _interpret(value, ftype):
    value = value.strip()
    if value in NO_RESPONSE:
        return [] if ftype == "checkboxes" else ""
    if ftype == "checkboxes":
        checked = []
        for line in value.split("\n"):
            m = re.match(r"\s*[-*]\s*\[([ xX])\]\s*(.*)", line)
            if m and m.group(1).lower() == "x":
                checked.append(m.group(2).strip())
        return checked
    return value


def parse_body(body, fields):
    """Split a rendered Issue Form body into {field_id: value}.

    Fields are located in FORM ORDER, each search starting after the previous field's heading. So a
    stray '### <label>' line inside a free-text value (e.g. a markdown subheading or a pasted field
    name in Notes) is non-authoritative — it is not the next expected field, so it stays as literal
    text instead of overwriting another field or truncating the value it sits in.
    """
    body = (body or "").replace("\r\n", "\n").replace("\r", "\n")
    found = []  # (match, field), in form order
    cursor = 0
    for f in fields:
        m = re.compile(r"(?m)^###[ \t]+" + re.escape(f["label"]) + r"[ \t]*$").search(body, cursor)
        if m:
            found.append((m, f))
            cursor = m.end()
    result = {}
    for idx, (m, f) in enumerate(found):
        end = found[idx + 1][0].start() if idx + 1 < len(found) else len(body)
        result[f["id"]] = _interpret(body[m.end():end], f["type"])
    return result


def read_body(args):
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as fh:
            return fh.read()
    if os.environ.get("ISSUE_BODY"):
        return os.environ["ISSUE_BODY"]
    return sys.stdin.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", default=DEFAULT_FORM)
    ap.add_argument("--body-file")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    fields = load_fields(args.form)
    parsed = parse_body(read_body(args), fields)
    json.dump(parsed, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
