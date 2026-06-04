#!/usr/bin/env python3
"""Regression tests for the submission parser/validator. Run: python scripts/test_submission.py

No pytest needed — plain asserts. Covers the boundary cases that motivated form-order parsing:
a recognized field name typed inside Notes must NOT overwrite the real field, and an unrecognized
markdown subheading inside Notes must NOT truncate the Notes value.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_submission import DEFAULT_FORM, load_fields, parse_body  # noqa: E402
from validate_submission import render, validate  # noqa: E402

FIELDS = load_fields(DEFAULT_FORM)
ORDER = [
    "Dataset title", "Dataset DOI", "Archive URL", "Source citation", "Lead author / lab",
    "ORCID iD (optional)", "Data license", "Open3DCP schema version targeted", "Notes (optional)",
    "Redistribution", "Archive",
]
BASE = {
    "Dataset title": "A mix",
    "Dataset DOI": "10.5281/zenodo.1",
    "Archive URL": "https://doi.org/10.5281/zenodo.1",
    "Source citation": "Real citation",
    "Lead author / lab": "Lab",
    "ORCID iD (optional)": "_No response_",
    "Data license": "CC BY 4.0",
    "Open3DCP schema version targeted": "1.6",
    "Notes (optional)": "_No response_",
    "Redistribution": "- [X] I confirm the data is legally redistributable.",
    "Archive": "- [X] The dataset is deposited in a public archive.",
}


def body(**over):
    vals = dict(BASE, **over)
    return "\n\n".join(f"### {k}\n\n{vals[k]}" for k in ORDER)


def test_basic_parse():
    p = parse_body(body(), FIELDS)
    assert p["source_citation"] == "Real citation", p["source_citation"]
    assert p["notes"] == "", repr(p["notes"])           # _No response_ -> ""
    assert p["declared_orcid"] == ""


def test_injected_field_name_does_not_overwrite():
    p = parse_body(body(**{"Notes (optional)": "see also\n### Source citation\nFAKE citation"}), FIELDS)
    assert p["source_citation"] == "Real citation", "injection overwrote source_citation!"
    assert "FAKE citation" in p["notes"] and "### Source citation" in p["notes"], "injected text lost from notes"


def test_unrecognized_subheading_kept():
    p = parse_body(body(**{"Notes (optional)": "Mix:\n### Mix design\n50% slag"}), FIELDS)
    assert "### Mix design" in p["notes"] and "50% slag" in p["notes"], "unrecognized subheading truncated notes"


def test_checkboxes():
    assert parse_body(body(), FIELDS)["redistribution_confirmed"], "checked box not detected"
    assert not parse_body(body(**{"Redistribution": "- [ ] nope"}), FIELDS)["redistribution_confirmed"]


def test_validate_pass_and_fail():
    _, ok = render(*validate(parse_body(body(), FIELDS), []))
    assert ok, "clean submission should pass"
    _, ok_bad = render(*validate(parse_body(body(**{"Dataset DOI": "not-a-doi"}), FIELDS), []))
    assert not ok_bad, "bad DOI should fail"


def test_crlf_body():
    p = parse_body(body().replace("\n", "\r\n"), FIELDS)
    assert p["dataset_title"] == "A mix", "CRLF body broke parsing"


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
            n += 1
    print(f"\n{n} tests passed")
