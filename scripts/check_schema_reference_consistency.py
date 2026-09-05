#!/usr/bin/env python3
"""Guard v1.8 cement and composition-basis wording in the public reference."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "schema-reference" / "index.html"

REQUIRED_EN_FIELDS = (
    "cem_ii_a_l",
    "cem_ii_a_ll",
    "cem_ii_b_l",
    "cem_ii_b_ll",
)
REQUIRED_BASIS_FIELDS = (
    "original_basis",
    "total_batched_mass_kg_m3",
    "total_binder_kg_m3",
)

# These cover the stale prose, table, and worked-example forms without rejecting
# the correct two-sentence explanation that distinguishes ASTM from EN fields.
STALE_CEMENT_PATTERNS = (
    re.compile(
        r"\bcement_type_1l\b[^.!?]{0,240}\b(?:EN\s*197-1|CEM\s*II(?:\s*/\s*[A-Z-]+)?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bASTM\s*C595\s*(?:/|and|or)\s*(?:EN\s*197-1|CEM\s*II)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bType\s+IL\b[^.!?]{0,180}\bCEM\s*II(?:\s*/\s*[A-Z-]+)?",
        re.IGNORECASE,
    ),
)


class TextExtractor(HTMLParser):
    """Collect text rendered by the reference page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignored_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template"}:
            self.ignored_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template"} and self.ignored_depth:
            self.ignored_depth -= 1

    def handle_data(self, data):
        if not self.ignored_depth:
            self.parts.append(data)


def visible_text(source):
    parser = TextExtractor()
    parser.feed(source)
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def consistency_errors(text):
    errors = []

    if any(pattern.search(text) for pattern in STALE_CEMENT_PATTERNS):
        errors.append(
            "stale cement_type_1l ASTM/EN conflation appears in the public reference"
        )

    for field in REQUIRED_EN_FIELDS:
        if field not in text:
            errors.append(f"public reference is missing EN limestone field: {field}")

    for field in REQUIRED_BASIS_FIELDS:
        if field not in text:
            errors.append(f"public reference is missing dual-basis field: {field}")

    return errors


def main():
    try:
        source = REFERENCE.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL: could not read {REFERENCE}: {exc}")
        return 2

    errors = consistency_errors(visible_text(source))
    if errors:
        print(f"FAIL: {len(errors)} schema-reference consistency error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "OK: schema reference keeps ASTM Type IL separate from EN limestone "
        "cements and documents the dual-basis provenance fields."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
