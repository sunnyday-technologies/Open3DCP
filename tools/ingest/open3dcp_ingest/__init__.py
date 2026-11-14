"""open3dcp_ingest -- translate external concrete datasets into the Open3DCP flat schema.

Public API:
    convert(path, kind=None, crosswalk_path=None, uci_crosswalk=None)
        -> (IngestResult, FidelityReport)
"""
from __future__ import annotations

import os
from typing import Optional

from . import readers, fidelity as _fidelity
from .crosswalk import Crosswalk, default_crosswalk_dir
from .ingest import (IngestResult, Mapping, build_relational_mappings, build_uci_mappings, ingest)

# Versioning policy: the tool's MAJOR.MINOR tracks the Open3DCP schema version it targets.
# Bumping the schema (e.g. 1.6 -> 1.7) requires updating the crosswalk + this constant + tests.
TARGET_SCHEMA_VERSION = "1.8"
__version__ = "1.8.1"
__all__ = ["convert", "IngestResult", "Crosswalk", "TARGET_SCHEMA_VERSION", "__version__"]


def convert(path: str, kind: Optional[str] = None, crosswalk_path: Optional[str] = None,
            uci_crosswalk: Optional[str] = None):
    """Read a dataset, map it to Open3DCP, and score the ingestion fidelity."""
    if kind == "canonical":
        from .canonical import read_canonical_csv
        result = read_canonical_csv(path)
        result.crosswalk_schema_version = TARGET_SCHEMA_VERSION
        return result, _fidelity.score(result)
    kind, records = readers.detect_and_read(path, kind)
    if kind == "uci":
        uci_csv = uci_crosswalk or os.path.join(default_crosswalk_dir(), "open3dcp_to_uci.csv")
        mappings, qmap = build_uci_mappings(uci_csv)
        cw = None
    else:
        cw = Crosswalk.load(crosswalk_path)
        mappings = build_relational_mappings(cw)
        qmap = cw.quantity_map
        if kind == "flat":
            # Keep source identities as supplied; never generate a measurement
            # ID from a composition hash or infer a database FK namespace.
            mappings += [Mapping(source=f"source.{field}", target=field)
                         for field in ("mix_id", "doi", "source_citation", "raw_data_doi")]
    result = ingest(records, mappings, qmap, cw, source_kind=kind)
    result.crosswalk_schema_version = (cw.meta.get("open3dcp_version", "") if cw else TARGET_SCHEMA_VERSION)
    report = _fidelity.score(result)
    return result, report
