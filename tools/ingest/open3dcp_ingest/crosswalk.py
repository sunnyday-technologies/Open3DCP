"""Load and represent a crosswalk spec (the YAML in the repo `crosswalk/` dir)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml


def default_crosswalk_dir() -> str:
    """Locate the repo-level crosswalk/ directory relative to this package."""
    here = os.path.dirname(os.path.abspath(__file__))
    # tools/ingest/open3dcp_ingest/ -> repo root is three levels up
    repo = os.path.abspath(os.path.join(here, "..", "..", ".."))
    return os.path.join(repo, "crosswalk")


@dataclass
class Crosswalk:
    meta: dict = field(default_factory=dict)
    transforms: dict = field(default_factory=dict)
    mappings: list = field(default_factory=list)
    quantity_map: dict = field(default_factory=dict)
    src_unmapped: list = field(default_factory=list)
    cardinality: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | None = None) -> "Crosswalk":
        if path is None:
            path = os.path.join(default_crosswalk_dir(), "open3dcp_to_relational.yaml")
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return cls(
            meta=data.get("meta", {}),
            transforms=data.get("transforms", {}),
            mappings=data.get("mappings", []),
            quantity_map=data.get("quantity_map", {}),
            src_unmapped=data.get("src_unmapped", []),
            cardinality=data.get("cardinality", {}),
            raw=data,
        )

    def unmapped_reason(self, source_path: str) -> dict[str, Any] | None:
        """Return the declared triage reason for a source field with no flat home, if any."""
        for entry in self.src_unmapped:
            pat = entry.get("src", "")
            # match on the leading "tab.field" token of the pattern
            head = pat.split()[0].split("/")[0].strip()
            if source_path == head or source_path.startswith(head.rstrip(".*")):
                return entry
        return None
