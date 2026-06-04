"""The ingestion engine: source records + crosswalk -> Open3DCP rows + fidelity trace + sidecar."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import Any, Optional

from . import transforms
from .crosswalk import Crosswalk


@dataclass
class Mapping:
    source: str                      # source field path (e.g. "material_batches.cement_content_kg_m3")
    target: Optional[str] = None     # Open3DCP column (None for pure pivots)
    transform: str = "identity"
    transform_kwargs: dict = field(default_factory=dict)
    declared_fidelity: str = transforms.EXACT
    pivot_on: Optional[str] = None   # categorical field selecting the target column
    pivot_map: dict = field(default_factory=dict)
    pivot_transform: str = "identity"
    refine_by: Optional[dict] = None  # {field, map} to switch target by a secondary field
    carry_to: Optional[str] = None    # copy this source value into another Open3DCP column (notes)
    note: str = ""


@dataclass
class CellTrace:
    row: int
    target: str
    source: str
    fidelity: str
    assumed: bool
    note: str


@dataclass
class Unmapped:
    row: int
    source: str
    value: Any
    fidelity: str
    reason: str


@dataclass
class IngestResult:
    rows: list[dict] = field(default_factory=list)
    trace: list[CellTrace] = field(default_factory=list)
    unmapped: list[Unmapped] = field(default_factory=list)
    source_kind: str = ""
    n_source_fields: int = 0
    n_mapped_fields: int = 0
    crosswalk_schema_version: str = ""


def build_relational_mappings(cw: Crosswalk) -> list[Mapping]:
    out: list[Mapping] = []
    for m in cw.mappings:
        if "pivot_on" in m:
            out.append(Mapping(
                source=m["src"], target=None, pivot_on=m["pivot_on"],
                pivot_map=m.get("pivot_map", {}), pivot_transform=m.get("transform_value", "identity"),
                declared_fidelity=m.get("fidelity", transforms.CATEGORICAL), note=m.get("notes", ""),
            ))
        else:
            kwargs = {}
            if "map" in m:
                kwargs["mapping"] = m["map"]
            out.append(Mapping(
                source=m["src"], target=m.get("open3dcp"), transform=m.get("transform", "identity"),
                transform_kwargs=kwargs, declared_fidelity=m.get("fidelity", transforms.EXACT),
                refine_by=m.get("refine_by"),
                carry_to=(m.get("carry") or {}).get("to"), note=m.get("notes", ""),
            ))
            # the "carry" source is consumed too
            if m.get("carry"):
                out[-1].transform_kwargs["_carry_source"] = m["carry"]["src"]
    return out


def build_uci_mappings(csv_path: str) -> tuple[list[Mapping], dict]:
    maps: list[Mapping] = []
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            src = row["uci_column"].split(" (")[0].strip()  # "Cement (component 1)" -> "Cement"
            tr = row["transform"]
            kwargs = {}
            if tr == "unit_convert":
                kwargs = {"from_unit": row.get("uci_unit"), "to_unit": "MPa"}
            maps.append(Mapping(source=src, target=row["open3dcp_column"], transform=tr,
                                transform_kwargs=kwargs,
                                declared_fidelity=row.get("fidelity", "lossy"),
                                note=row.get("notes", "")))
    return maps, {}


def _get(rec, path):
    return rec.get(path)


def ingest(records: list[dict], mappings: list[Mapping], quantity_map: dict,
           cw: Optional[Crosswalk], source_kind: str) -> IngestResult:
    res = IngestResult(source_kind=source_kind)
    for i, rec in enumerate(records):
        ctx = rec.get("_ctx", {})
        row: dict[str, Any] = {}
        handled: set[str] = {"_ctx"}
        mapped_here = 0

        for m in mappings:
            # --- pivot mapping (categorical field selects the target column) ---
            if m.pivot_on is not None:
                content = _get(rec, m.source)
                category = _get(rec, m.pivot_on)
                handled.add(m.source); handled.add(m.pivot_on)
                if content is None:
                    continue
                target = m.pivot_map.get(category)
                if target is None:
                    res.unmapped.append(Unmapped(i, m.source, content, transforms.CATEGORICAL,
                                                  f"category {category!r} not in pivot_map"))
                    continue
                tr = transforms.apply(m.pivot_transform, content, ctx=ctx)
                if tr.value is None and tr.fidelity in (transforms.LOSSY, transforms.NONE):
                    res.unmapped.append(Unmapped(i, m.source, content, tr.fidelity, tr.note))
                    continue
                row[target] = tr.value
                mapped_here += 1
                res.trace.append(CellTrace(i, target, m.source, tr.fidelity, tr.assumed, tr.note))
                continue

            # --- simple / enum / refine mapping ---
            if m.source not in rec:
                continue
            value = _get(rec, m.source)
            handled.add(m.source)
            carry_src = m.transform_kwargs.get("_carry_source")
            if carry_src:
                handled.add(carry_src)
            if value is None:
                continue
            target = m.target
            if m.refine_by:
                rb_field = m.refine_by.get("src")
                if rb_field:
                    handled.add(rb_field)
                    rb_val = _get(rec, rb_field)
                    rb_map = m.refine_by.get("map", {})
                    if rb_val in rb_map:
                        target = rb_map[rb_val]
            if target is None:
                continue
            kwargs = {k: v for k, v in m.transform_kwargs.items() if not k.startswith("_")}
            tr = transforms.apply(m.transform, value, ctx=ctx, **kwargs)
            if tr.value is None and tr.fidelity in (transforms.LOSSY, transforms.NONE):
                res.unmapped.append(Unmapped(i, m.source, value, tr.fidelity, tr.note))
                continue
            row[target] = tr.value
            mapped_here += 1
            res.trace.append(CellTrace(i, target, m.source, tr.fidelity, tr.assumed, tr.note))
            # carry a vocab type into a notes column
            if m.carry_to and carry_src and _get(rec, carry_src) is not None:
                prev = row.get(m.carry_to, "")
                row[m.carry_to] = (f"{prev}; " if prev else "") + f"{carry_src.split('.')[-1]}={_get(rec, carry_src)}"

        # --- quantity_map: pivot source `data` rows into property columns ---
        for q, spec in (quantity_map or {}).items():
            mean_path = f"data.{q}.mean"
            if mean_path in rec:
                handled.add(mean_path)
                units_path = f"data.{q}.units"; std_path = f"data.{q}.std"
                handled.add(units_path)
                val = _get(rec, mean_path)
                if val is not None:
                    src_unit = _get(rec, units_path)
                    tr = transforms.apply("unit_convert", val, ctx=ctx,
                                          from_unit=src_unit, to_unit=spec.get("to_unit"))
                    row[spec["open3dcp"]] = tr.value
                    mapped_here += 1
                    res.trace.append(CellTrace(i, spec["open3dcp"], mean_path, tr.fidelity, tr.assumed, tr.note))
                # v1.6: std-dev maps to the matching *_stddev_* column when defined
                if rec.get(std_path) is not None:
                    handled.add(std_path)
                    std_col = spec.get("stddev")
                    if std_col:
                        trs = transforms.apply("unit_convert", rec[std_path], ctx=ctx,
                                               from_unit=_get(rec, units_path), to_unit=spec.get("to_unit"))
                        row[std_col] = trs.value
                        mapped_here += 1
                        res.trace.append(CellTrace(i, std_col, std_path, trs.fidelity, trs.assumed, trs.note))
                    else:
                        res.unmapped.append(Unmapped(i, std_path, rec[std_path], transforms.NONE,
                                                     "per-measurement std-dev: no matching *_stddev column"))

        # --- everything left over -> triage sidecar (drop nothing) ---
        for src, value in rec.items():
            if src in handled or value is None:
                continue
            reason_entry = cw.unmapped_reason(src) if cw else None
            reason = (reason_entry or {}).get("reason", "no mapping in crosswalk")
            fidelity = (reason_entry or {}).get("fidelity", transforms.NONE)
            res.unmapped.append(Unmapped(i, src, value, fidelity, reason))

        # v1.6: make kg/m3 (primary basis) recoverable from the flat row (engine-populated)
        if ctx.get("total_wet_mass_kg_m3") is not None:
            row.setdefault("mix_density_kg_m3",
                           ctx.get("mix_density_kg_m3") or ctx.get("total_wet_mass_kg_m3"))
            row.setdefault("original_basis", "kg_m3")
        if ctx.get("total_binder_kg_m3") is not None:
            row.setdefault("total_binder_kg_m3", ctx.get("total_binder_kg_m3"))

        res.rows.append(row)
        res.n_source_fields += sum(1 for k, v in rec.items() if k != "_ctx" and v is not None)
        res.n_mapped_fields += mapped_here
    return res
