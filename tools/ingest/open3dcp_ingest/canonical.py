"""Read an already-canonical CSV without treating wet mass-% as kg/m3.

Conversion fidelity is not scientific validation or database admission.
Unknown fields stay in the existing unmapped sidecar. Record order and repeats
are retained; source identifiers are never generated from composition hashes.
"""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from .ingest import CellTrace, IngestResult, Unmapped
from .transforms import EXACT, NONE


def schema_columns():
    return json.loads(Path(__file__).with_name("canonical_schema.json").read_text(encoding="utf-8"))["columns"]


def _value(raw, sql_type, column, row):
    if raw == "":
        return None
    if sql_type == "BOOLEAN":
        values = {"true": True, "false": False, "1": True, "0": False}
        if raw.lower() not in values:
            raise ValueError(f"Invalid boolean at row {row}, column {column}")
        return values[raw.lower()]
    if sql_type in ("REAL", "DOUBLE PRECISION", "INTEGER", "BIGINT", "SMALLINT", "SERIAL") or sql_type.startswith("NUMERIC"):
        try:
            value = Decimal(raw)
        except InvalidOperation:
            raise ValueError(f"Invalid number at row {row}, column {column}") from None
        if not value.is_finite():
            raise ValueError(f"Nonfinite number at row {row}, column {column}")
        if sql_type in ("INTEGER", "BIGINT", "SMALLINT", "SERIAL"):
            if value != value.to_integral_value():
                raise ValueError(f"Noninteger value at row {row}, column {column}")
            return int(value)
        return value
    return raw


def read_canonical_csv(path):
    columns = schema_columns()
    result = IngestResult(source_kind="canonical")
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if not headers or len(headers) != len(set(headers)) or any(not h or h != h.strip() for h in headers):
            raise ValueError("Canonical CSV requires unique, nonempty, exact column names")
        for i, source in enumerate(reader):
            if None in source or any(v is None for v in source.values()):
                raise ValueError(f"CSV width mismatch at row {i + 2}")
            row = {}
            for column, raw in source.items():
                result.n_source_fields += 1
                if column in columns or column.startswith("x_"):
                    row[column] = _value(raw, columns.get(column, "TEXT"), column, i + 2)
                    result.trace.append(CellTrace(i, column, column, EXACT, False,
                                                   "Canonical values and declared units preserved; no scientific admission"))
                    result.n_mapped_fields += 1
                else:
                    result.unmapped.append(Unmapped(i, column, raw, NONE,
                                                     "Outside public schema; retained without inventing a mapping"))
            result.rows.append(row)
    return result
