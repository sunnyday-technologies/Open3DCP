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

EN_LIMESTONE = (
    r"(?:EN\s*197-1(?:\s+CEM\s*II/(?:A|B)-(?:L|LL))?"
    r"|CEM\s*II/(?:A|B)-(?:L|LL))"
)
CURRENT_TYPE_IL_ASSERTION = re.compile(
    r"\bIn\s+v1\.8\b[^.!?]{0,80}\bcement_type_1l\b"
    r"[^.!?]{0,80}\bASTM\s*C595\s+Type\s+IL\s+only\b",
    re.IGNORECASE,
)

# Known concrete forms of the former ASTM/EN mapping in prose, table cells,
# and worked examples. Keep this narrow rather than guessing at arbitrary prose.
STALE_CEMENT_PATTERNS = (
    re.compile(
        rf"\bASTM\s*C595\s*/\s*{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bASTM\s*C595\s+CEM\s*II/(?:A|B)-(?:L|LL)\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bcement_type_1l\b\s*(?:=|:)\s*[^.!?]{{0,120}}\b{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bcement_type_1l\b\s+(?:means|represents?|maps?\s+to|cross-ref(?:erence)?s?)"
        rf"\s+[^.!?]{{0,80}}\b{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bcement_type_1l\b\s+(?:(?:is|should\s+be)\s+)?"
        rf"(?:used|recorded|stored)\s+(?:for|as)\s+[^.!?]{{0,80}}\b{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"(?<!not\s)(?<!never\s)\b(?:use|record|store)\s+"
        rf"(?:the\s+)?cement_type_1l\b\s+"
        rf"(?:for|as)\s+[^.!?]{{0,80}}\b{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bcement_type_1l\b\s+is\b[^.!?]{{0,120}}\b(?:per|under)\s+"
        rf"[^.!?]{{0,60}}\b{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\bcement_type_1l\b\s+is\s+(?:an?\s+)?{EN_LIMESTONE}\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b{EN_LIMESTONE}\b\s+(?:maps?\s+to|(?:is\s+)?(?:recorded|stored)\s+as)"
        r"\s+\bcement_type_1l\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b{EN_LIMESTONE}\b\s+(?:should\s+be\s+)?(?:mapped|assigned)\s+to\s+"
        r"(?:the\s+)?\bcement_type_1l\b",
        re.IGNORECASE,
    ),
)
STALE_BASIS_PHRASES = (
    "where you store densities and compute mass-percent on the fly",
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


def mentions_field(text, field):
    return re.search(rf"\b{re.escape(field)}\b", text) is not None


def consistency_errors(text):
    errors = []

    if not CURRENT_TYPE_IL_ASSERTION.search(text):
        errors.append(
            "public reference must state that in v1.8 cement_type_1l is "
            "ASTM C595 Type IL only"
        )

    if any(pattern.search(text) for pattern in STALE_CEMENT_PATTERNS):
        errors.append(
            "stale cement_type_1l ASTM/EN conflation appears in the public reference"
        )

    lower_text = text.lower()
    for phrase in STALE_BASIS_PHRASES:
        if phrase in lower_text:
            errors.append(
                "stale density-based mass-percent conversion instruction appears in "
                "the public reference"
            )
            break

    for field in REQUIRED_EN_FIELDS:
        if not mentions_field(text, field):
            errors.append(f"public reference is missing EN limestone field: {field}")

    for field in REQUIRED_BASIS_FIELDS:
        if not mentions_field(text, field):
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
