"""Readers that turn external dataset files into normalized *source records*.

A source record is a dict mapping a fully-qualified source field path
(e.g. "material_batches.cement_content_kg_m3", "tests.age_days",
"data.<quantity>.mean") to a value, plus a "_ctx" entry with conversion context
(total wet mass, units, etc.). The ingest engine maps these onto Open3DCP columns.
"""
from __future__ import annotations

import csv
import os
from typing import Any


# ---------------------------------------------------------------------------
# UCI "Concrete Compressive Strength" (Yeh 1998) -- flat CSV, kg/m3
# ---------------------------------------------------------------------------
_UCI_ALIASES = {
    "cement": "Cement", "blast furnace slag": "Blast Furnace Slag", "slag": "Blast Furnace Slag",
    "fly ash": "Fly Ash", "water": "Water", "superplasticizer": "Superplasticizer",
    "coarse aggregate": "Coarse Aggregate", "fine aggregate": "Fine Aggregate",
    "age": "Age", "concrete compressive strength": "Concrete compressive strength",
    "csmpa": "Concrete compressive strength",
}
# UCI components that sum to the full wet-mix mass (all kg/m3, incl. water).
_UCI_MASS_COMPONENTS = ["Cement", "Blast Furnace Slag", "Fly Ash", "Water",
                        "Superplasticizer", "Coarse Aggregate", "Fine Aggregate"]


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _canon_uci(header: str) -> str | None:
    h = header.strip().lower()
    # strip the "(component N)(unit)" decorations Yeh's CSV carries
    for key, canon in _UCI_ALIASES.items():
        if h.startswith(key):
            return canon
    return None


def read_uci_csv(path: str) -> list[dict[str, Any]]:
    records = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        canon = [_canon_uci(h) for h in header]
        for raw in reader:
            if not any(c.strip() for c in raw):
                continue
            rec: dict[str, Any] = {}
            for col, val in zip(canon, raw):
                if col is None:
                    continue
                rec[col] = _num(val)
            total = sum(rec.get(c) or 0.0 for c in _UCI_MASS_COMPONENTS)
            binder = sum(rec.get(c) or 0.0 for c in ("Cement", "Blast Furnace Slag", "Fly Ash"))
            rec["_ctx"] = {
                "total_wet_mass_kg_m3": total if total > 0 else None,
                "total_wet_mass_is_complete": True,  # UCI reports every constituent incl. water
                "total_binder_kg_m3": binder if binder > 0 else None,
                "mix_density_kg_m3": total if total > 0 else None,
                "source": "uci_yeh_1998",
            }
            records.append(rec)
    return records


# ---------------------------------------------------------------------------
# relational concrete database .xlsx template -- kg/m3
# ---------------------------------------------------------------------------
def _load_xlsx_tabs(path: str) -> dict[str, list[dict[str, Any]]]:
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    tabs: dict[str, list[dict[str, Any]]] = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            tabs[ws.title] = []
            continue
        # the template uses a single header row for entity tabs; some tabs carry a
        # banner row above the header (reinforcement_components, data) -- detect the
        # header row as the first row whose first cell ends with "_id".
        header_idx = 0
        for i, r in enumerate(rows[:3]):
            first = (r[0] or "") if r else ""
            if isinstance(first, str) and first.strip().endswith("_id"):
                header_idx = i
                break
        header = [str(c).strip() if c is not None else "" for c in rows[header_idx]]
        body = []
        for r in rows[header_idx + 1:]:
            if not any(c is not None and str(c).strip() for c in r):
                continue
            body.append({h: v for h, v in zip(header, r) if h})
        tabs[ws.title] = body
    wb.close()
    return tabs


_BINDER_KG = ["cement_content_kg_m3", "silica_fume_content_kg_m3",
              "fly_ash_content_kg_m3", "slag_content_kg_m3"]


def _batch_total_wet_mass(batch: dict):
    """Estimate total wet-mix mass (kg/m3) for a source batch.

    binder = cement + scms ; water = w/b * binder ; total = binder + water + aggregates.
    Returns (total, is_complete, binder). Complete only if binder, w/b and aggregates present.
    """
    binder = sum(_num(batch.get(k)) or 0.0 for k in _BINDER_KG)
    wb = _num(batch.get("water_binder_ratio"))
    fine = _num(batch.get("fine_aggregate_content_kg_m3")) or 0.0
    coarse = _num(batch.get("coarse_aggregate_content_kg_m3")) or 0.0
    binder_out = binder if binder > 0 else None
    if binder <= 0 or wb is None:
        return (None, False, binder_out)
    water = wb * binder
    total = binder + water + fine + coarse
    complete = binder > 0 and wb is not None and (fine + coarse) > 0
    return (total, complete, binder_out)


def read_relational_xlsx(path: str) -> list[dict[str, Any]]:
    """Denormalize the relational template into per-(batch x test) source records.

    Joins material_batches -> specimens -> tests -> data and pivots each `data` row
    (one quantity) under "data.<quantity>.{mean,std,units}". Fields that don't fit the
    flat grain are still attached (prefixed by tab) so the engine can route them to the
    triage sidecar -- nothing is dropped at read time.
    """
    tabs = _load_xlsx_tabs(path)
    batches = {b.get("batch_id"): b for b in tabs.get("material_batches", [])}
    specimens = tabs.get("specimens", [])
    tests_by_specimen: dict[Any, list] = {}
    for t in tabs.get("tests", []):
        tests_by_specimen.setdefault(t.get("specimen_id"), []).append(t)
    data_by_test: dict[Any, list] = {}
    for d in tabs.get("data", []):
        data_by_test.setdefault(d.get("test_id"), []).append(d)

    records: list[dict[str, Any]] = []
    # specimens drive the grain; if a specimen has no test, still emit the batch row.
    seen_specimens = set()
    for spec in specimens:
        seen_specimens.add(spec.get("specimen_id"))
        batch = batches.get(spec.get("batch_id"), {})
        total, complete, binder = _batch_total_wet_mass(batch)
        spec_tests = tests_by_specimen.get(spec.get("specimen_id"), [None])
        for test in spec_tests:
            rec: dict[str, Any] = {}
            for k, v in batch.items():
                rec[f"material_batches.{k}"] = v
            for k, v in spec.items():
                rec[f"specimens.{k}"] = v
            if test:
                for k, v in test.items():
                    rec[f"tests.{k}"] = v
                for d in data_by_test.get(test.get("test_id"), []):
                    q = d.get("quantity_reported")
                    if q:
                        rec[f"data.{q}.mean"] = d.get("quantity_reported_mean")
                        rec[f"data.{q}.std"] = d.get("quantity_reported_standard_deviation")
                        rec[f"data.{q}.units"] = d.get("units")
                    for k in ("number_of_specimens", "extraction_methods", "data_type",
                              "file_name", "curator_first_name", "curator_last_name"):
                        if d.get(k) is not None:
                            rec[f"data.{k}"] = d.get(k)
            rec["_ctx"] = {
                "total_wet_mass_kg_m3": total,
                "total_wet_mass_is_complete": complete,
                "total_binder_kg_m3": binder,
                "mix_density_kg_m3": total,
                "source": "relational",
                "source_id": batch.get("source_id") or spec.get("source_id"),
            }
            records.append(rec)
    # batches with no specimen at all -> still emit so nothing is lost
    referenced = {s.get("batch_id") for s in specimens}
    for bid, batch in batches.items():
        if bid in referenced:
            continue
        total, complete, binder = _batch_total_wet_mass(batch)
        rec = {f"material_batches.{k}": v for k, v in batch.items()}
        rec["_ctx"] = {"total_wet_mass_kg_m3": total, "total_wet_mass_is_complete": complete,
                       "total_binder_kg_m3": binder, "mix_density_kg_m3": total,
                       "source": "relational", "source_id": batch.get("source_id")}
        records.append(rec)
    return records


def detect_and_read(path: str, kind: str | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Dispatch on file type / explicit kind. Returns (kind, records)."""
    ext = os.path.splitext(path)[1].lower()
    if kind is None:
        kind = "relational" if ext in (".xlsx", ".xlsm") else "uci"
    if kind == "relational":
        return kind, read_relational_xlsx(path)
    if kind == "uci":
        return kind, read_uci_csv(path)
    raise ValueError(f"unknown source kind {kind!r}")
