#!/usr/bin/env python3
"""Single-source-of-truth version guard for the Open3DCP schema release.

The current schema version is read from the top entry of CHANGELOG.md (`## [X.Y.Z]`).
Every other place that must state the *current* version is then verified to match.
This is the canonical list of version-bearing locations: bumping the schema means
editing these files, and running this script confirms none was missed (it would have
caught, e.g., a stale `.well-known/mcp-manifest.json`).

Historical references (changelog history, "added in vX.Y" notes, SQL section banners,
the examples' internal "(pre-vX.Y)" tool text) are deliberately NOT checked — they are
meant to name the version a feature first appeared in, not the current release.

Run:  python scripts/check_version.py        # exit 0 if consistent, 1 otherwise
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:  # Windows consoles default to cp1252; keep output (e.g. "→") from crashing the run
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def canonical_version():
    """Full (X.Y.Z) and minor (X.Y) version from the first CHANGELOG entry."""
    text = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
    m = re.search(r"^##\s*\[(\d+)\.(\d+)\.(\d+)\]", text, re.M)
    if not m:
        print("FAIL: could not read a `## [X.Y.Z]` entry from CHANGELOG.md")
        sys.exit(2)
    major, minor, patch = m.groups()
    return f"{major}.{minor}.{patch}", f"{major}.{minor}"


def checks(vv, v):
    """(relative_path -> list of substrings that MUST be present) for version vv (X.Y.Z) / v (X.Y)."""
    return {
        "Open3DCP_SCHEMA.md": [f"# Open3DCP v{v}", f"*Open3DCP v{v} -- Last updated:"],
        "crosswalk/open3dcp_to_relational.yaml": [f'open3dcp_version: "{v}"'],
        "tools/ingest/pyproject.toml": [f'version = "{vv}"'],
        "tools/ingest/open3dcp_ingest/__init__.py": [
            f'TARGET_SCHEMA_VERSION = "{v}"', f'__version__ = "{vv}"'],
        "tools/ingest/README.md": [f"schema v{v} → tool"],
        "index.html": [f'"version": "{v}"', f"// v{v}",
                       f'>v{v}<span class="spec-unit">'],
        "schema-reference/index.html": [f'"version": "{v}"', f"current public v{v} release"],
        "llms.txt": [f"Current public version: v{v}", f"Public schema version v{v}"],
        "README.md": [f"current schema v{v}", f"Open3DCP v{v} tracks"],
        "AGENTS.md": [f"v{v} defines the current public column vocabulary"],
        "intake/index.html": [f"schema v{v}"],
        ".well-known/mcp-manifest.json": [f"Current public schema version: v{v}"],
        ".zenodo.json": [f'"version": "{vv}"'],
        "examples/index.html": [f"schema v{v}"],
        "examples/uci-yeh-1998/index.html": [f"schema v{v}"],
        "examples/rilem-tc304-ils-mech/index.html": [f"schema v{v}"],
    }


# Maturity status (decoupled from the SemVer number): the schema is a working-group draft
# until ratified. Flip these markers (and the lines they sit in) from "Draft" to "Stable" at
# ratification. Kept here so the status, like the version, can't silently drift across surfaces.
STATUS = {
    "Open3DCP_SCHEMA.md": ["**Status: Draft**"],
    "index.html": ['"creativeWorkStatus": "Draft"', 'spec-unit">draft<'],
    "schema-reference/index.html": ['"creativeWorkStatus": "Draft"'],
    "llms.txt": ["Status: Draft"],
    ".well-known/mcp-manifest.json": ["Status: Draft"],
    ".zenodo.json": ["Status: Draft"],
    "README.md": ["Status: Draft"],
}


def main():
    vv, v = canonical_version()
    print(f"canonical version (from CHANGELOG.md): {vv}  (minor v{v})")
    missing = []
    for rel, needles in checks(vv, v).items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            missing.append(f"{rel}: file not found")
            continue
        text = open(path, encoding="utf-8").read()
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel}: missing version label {needle!r}")
    for rel, needles in STATUS.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            missing.append(f"{rel}: file not found")
            continue
        text = open(path, encoding="utf-8").read()
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel}: missing status marker {needle!r}")
    if missing:
        print(f"\nFAIL — {len(missing)} version/status label(s) out of sync:")
        for m in missing:
            print(f"  x {m}")
        return 1
    n_ver = sum(len(n) for n in checks(vv, v).values())
    n_stat = sum(len(n) for n in STATUS.values())
    print(f"OK — {n_ver} version labels across {len(checks(vv, v))} files consistent at v{vv}; "
          f"{n_stat} Draft-status markers across {len(STATUS)} files consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
