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
    n_consumed_fields: int = 0   # selector/plumbing fields consumed by a mapping (pivot key,
                                 # refine key, carry source, data_type, curve descriptor) that
                                 # write no column of their own -> excluded from coverage denom
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


def _is_key(source: str) -> bool:
    """A foreign key / identifier leaf (`*_id`, `id`) -- plumbing, not data a flat row holds.
    Mirrors fidelity._is_relational_key (kept local to avoid an import cycle)."""
    leaf = source.rsplit(".", 1)[-1].lower()
    return leaf == "id" or leaf.endswith("_id")


# Tokens (in data_type or the quantity name) that select the file-reference column a
# non-scalar `data` record routes to. An "intelligent" ingestor reads the descriptor
# rather than dropping curves/images to the triage sidecar.
_SCALAR_TYPES = {"scalar", "value", "mean", "point", "number"}


def _file_target_for(data_type, quantity) -> str:
    s = f"{data_type or ''} {quantity or ''}".lower()
    if any(t in s for t in ("rheo", "flow", "viscos", "yield")):
        return "rheology_curve_file"
    if any(t in s for t in ("image", "sem", " ct", "ct_", "micrograph", "xrd", "tomograph")):
        return "microstructure_image"
    if any(t in s for t in ("stress", "strain", "load", "displac", "force")):
        return "stress_strain_file"
    return "raw_data_file"


def _data_quantities(rec) -> set:
    """The set of <q> appearing as data.<q>.<attr> keys (q may contain underscores)."""
    qs = set()
    for k in rec:
        if k.startswith("data.") and k.count(".") >= 2:
            qs.add(".".join(k.split(".")[1:-1]))
    return qs


def _route_data_records(rec, row, handled, res, i, quantity_map, ctx) -> int:
    """Map each source `data` record onto the flat row by its kind.

    - scalar quantity in the quantity_map  -> its property column (+ matching *_stddev);
    - any record with a file reference      -> the *_file column chosen by data_type;
    - a non-scalar record's axis units      -> provenance_notes (the curve descriptor that
                                               explains the linked file -- not silent loss).
    data_type itself is consumed as a routing selector (handled), like a pivot key.
    """
    n = 0
    notes: list[str] = []
    qmap = quantity_map or {}
    for q in sorted(_data_quantities(rec)):
        mean_k, std_k = f"data.{q}.mean", f"data.{q}.std"
        units_k, dtype_k, file_k = f"data.{q}.units", f"data.{q}.data_type", f"data.{q}.file_name"
        for k in (mean_k, std_k, units_k, dtype_k, file_k):
            if k in rec:
                handled.add(k)
        mean, units = _get(rec, mean_k), _get(rec, units_k)
        dtype, fname = _get(rec, dtype_k), _get(rec, file_k)
        spec = qmap.get(q)
        is_scalar = (dtype is None) or (str(dtype).lower() in _SCALAR_TYPES)

        # scalar measured property -> property column (unit-converted), with std-dev companion
        if spec and mean is not None:
            tr = transforms.apply("unit_convert", mean, ctx=ctx, from_unit=units, to_unit=spec.get("to_unit"))
            row[spec["open3dcp"]] = tr.value
            n += 1
            res.trace.append(CellTrace(i, spec["open3dcp"], mean_k, tr.fidelity, tr.assumed, tr.note))
            std = _get(rec, std_k)
            if std is not None:
                std_col = spec.get("stddev")
                if std_col:
                    trs = transforms.apply("unit_convert", std, ctx=ctx, from_unit=units, to_unit=spec.get("to_unit"))
                    row[std_col] = trs.value
                    n += 1
                    res.trace.append(CellTrace(i, std_col, std_k, trs.fidelity, trs.assumed, trs.note))
                else:
                    res.unmapped.append(Unmapped(i, std_k, std, transforms.NONE,
                                                 "per-measurement std-dev: no matching *_stddev column"))
        elif spec is None and mean is not None:
            # a scalar quantity with no flat column -> sidecar (named, not dropped)
            res.unmapped.append(Unmapped(i, mean_k, mean, transforms.NONE,
                                         f"quantity {q!r} not in quantity_map"))

        # non-scalar payload -> route the file reference by data_type; keep the axis descriptor
        if not is_scalar or fname is not None:
            if fname is not None:
                target = _file_target_for(dtype, q)
                if target not in row:
                    row[target] = fname
                    n += 1
                    res.trace.append(CellTrace(i, target, file_k, transforms.FILE_REF, False,
                                               f"data_type={dtype}; routed {q} -> {target}"))
            if units is not None and not (spec and mean is not None):
                notes.append(f"curve {q}.units={units}")

    if notes:
        prev = row.get("provenance_notes", "")
        row["provenance_notes"] = (f"{prev}; " if prev else "") + "; ".join(notes)
    return n


def ingest(records: list[dict], mappings: list[Mapping], quantity_map: dict,
           cw: Optional[Crosswalk], source_kind: str) -> IngestResult:
    res = IngestResult(source_kind=source_kind)
    for i, rec in enumerate(records):
        ctx = rec.get("_ctx", {})
        row: dict[str, Any] = {}
        handled: set[str] = {"_ctx", "_assumed_fields"}
        assumed_fields = rec.get("_assumed_fields") or set()
        mapped_here = 0
        trace_start, unmapped_start = len(res.trace), len(res.unmapped)

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
                realized = transforms.worst(m.declared_fidelity, tr.fidelity)
                assumed = (tr.assumed or transforms.is_assumption(realized)
                           or m.source in assumed_fields or m.pivot_on in assumed_fields)
                note = tr.note + ("; assumed (defaulted selector)" if m.pivot_on in assumed_fields else "")
                res.trace.append(CellTrace(i, target, m.source, realized, assumed, note))
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
                    rb_val = _get(rec, rb_field)
                    rb_map = m.refine_by.get("map", {})
                    rb_key = None
                    if rb_val is not None:
                        cands = [str(rb_val)]
                        if isinstance(rb_val, float) and rb_val.is_integer():
                            cands.append(str(int(rb_val)))
                        rb_key = next((c for c in cands if c in rb_map), None)
                    if rb_key is not None:
                        target = rb_map[rb_key]
                        handled.add(rb_field)  # consumed as a selector; keep the exact value as a note
                        _n = f"{rb_field.rsplit('.', 1)[-1]}={rb_val}"
                        row["provenance_notes"] = ((row.get("provenance_notes", "") + "; ")
                                                   if row.get("provenance_notes") else "") + _n
                    # else: rb_field stays UNHANDLED -> falls through to the sidecar (drop nothing,
                    # rather than silently consuming an unmapped refinement value)
            if target is None:
                continue
            kwargs = {k: v for k, v in m.transform_kwargs.items() if not k.startswith("_")}
            tr = transforms.apply(m.transform, value, ctx=ctx, **kwargs)
            if tr.value is None and tr.fidelity in (transforms.LOSSY, transforms.NONE):
                res.unmapped.append(Unmapped(i, m.source, value, tr.fidelity, tr.note))
                continue
            row[target] = tr.value
            mapped_here += 1
            realized = transforms.worst(m.declared_fidelity, tr.fidelity)
            assumed = tr.assumed or transforms.is_assumption(realized) or m.source in assumed_fields
            note = tr.note + ("; assumed (engine default, not source-stated)"
                              if (m.source in assumed_fields and "default" not in tr.note) else "")
            res.trace.append(CellTrace(i, target, m.source, realized, assumed, note))
            # carry a vocab type into a notes column
            if m.carry_to and carry_src and _get(rec, carry_src) is not None:
                prev = row.get(m.carry_to, "")
                row[m.carry_to] = (f"{prev}; " if prev else "") + f"{carry_src.split('.')[-1]}={_get(rec, carry_src)}"

        # --- data records: scalars -> property columns; curves/images -> *_file columns ---
        # data_type is consumed as routing metadata (not dropped); a curve's axis-unit
        # descriptor (e.g. data.strain.units) is folded into provenance_notes.
        mapped_here += _route_data_records(rec, row, handled, res, i, quantity_map, ctx)

        # --- derive test age from the casting date when an explicit age is absent ---
        # date_of_pouring is t=0 of the curing clock; with a test date it yields the age.
        if "test_age_days" not in row:
            pour = _get(rec, "material_batches.date_of_pouring")
            test_date = _get(rec, "tests.date_of_testing") or _get(rec, "tests.test_date")
            handled.add("tests.date_of_testing"); handled.add("tests.test_date")
            if pour is not None and test_date is not None:
                try:
                    age = (test_date - pour).days
                    row["test_age_days"] = age
                    mapped_here += 1
                    res.trace.append(CellTrace(i, "test_age_days", "tests.date_of_testing",
                                               transforms.DERIVED, True,
                                               "age = test date - date_of_pouring"))
                except (TypeError, AttributeError):
                    pass

        # --- everything left over -> triage sidecar (drop nothing) ---
        for src, value in rec.items():
            if src in handled or value is None:
                continue
            reason_entry = cw.unmapped_reason(src) if cw else None
            reason = (reason_entry or {}).get("reason", "no mapping in crosswalk")
            fidelity = (reason_entry or {}).get("fidelity", transforms.NONE)
            res.unmapped.append(Unmapped(i, src, value, fidelity, reason))

        # v1.7: make kg/m3 (primary basis) recoverable from the flat row (engine-populated).
        # total_batched_mass_kg_m3 is the honest denominator for the mass-% <-> kg/m3 bridge -- the sum
        # of the as-batched constituent masses -- NOT a fresh density. The reader's absolute-volume yield
        # check (when the batch does not close to ~1 m3) is carried in provenance_notes.
        if ctx.get("total_wet_mass_kg_m3") is not None:
            row.setdefault("total_batched_mass_kg_m3",
                           ctx.get("total_batched_mass_kg_m3") or ctx.get("total_wet_mass_kg_m3"))
            row.setdefault("original_basis", "kg_m3")
            if ctx.get("provenance_notes"):
                prev = row.get("provenance_notes", "")
                row["provenance_notes"] = (f"{prev}; " if prev else "") + ctx["provenance_notes"]
        if ctx.get("total_binder_kg_m3") is not None:
            row.setdefault("total_binder_kg_m3", ctx.get("total_binder_kg_m3"))

        # Selector/plumbing fields consumed by a mapping (pivot key, refine key, carry source,
        # data_type, folded curve descriptor) are `handled` yet write no column of their own and
        # are not sidecar'd -- like foreign keys, they are not coverage failures, so exclude them
        # from the coverage denominator (see fidelity.field_coverage).
        non_null = {k for k, v in rec.items() if k not in ("_ctx", "_assumed_fields") and v is not None}
        mapped_src = {t.source for t in res.trace[trace_start:]}
        sidecar_src = {u.source for u in res.unmapped[unmapped_start:]}
        consumed = {s for s in non_null
                    if s in handled and s not in mapped_src and s not in sidecar_src
                    and not _is_key(s)}

        res.rows.append(row)
        res.n_source_fields += len(non_null)
        res.n_mapped_fields += mapped_here
        res.n_consumed_fields += len(consumed)
    return res
