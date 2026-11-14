# open3dcp-ingest

A public ingestion / conversion tool that translates external concrete datasets into
the **Open3DCP flat schema** — with an **honest fidelity score** and a **drop-nothing
triage sidecar**. Bridges relational concrete databases and the Open3DCP flat schema.

> Part of [Open3DCP](https://open3dcp.org). Apache-2.0. The crosswalks it consumes live
> in [`../../crosswalk/`](../../crosswalk/).

## Versioning — the tool tracks the schema

The ingestion tool and crosswalk are **versioned together with the Open3DCP schema** and must be
updated every time the schema changes:

- The package version's **MAJOR.MINOR tracks the schema version** it targets (schema v1.8 → tool
  `1.8.x`). Check with `open3dcp-ingest --version`.
- `TARGET_SCHEMA_VERSION` in [`open3dcp_ingest/__init__.py`](open3dcp_ingest/__init__.py) is the
  authoritative target; the crosswalk declares `meta.open3dcp_version`.
- On every run, the tool **warns if the crosswalk's schema version ≠ the tool's target**, so a
  stale crosswalk can't silently produce wrong output.

**When the schema is bumped (e.g. 1.6 → 1.7):** update `TARGET_SCHEMA_VERSION`, the package
`version`, `meta.open3dcp_version` in each crosswalk, add/adjust mappings for new columns, and
re-run the tests.

## Why

Bringing prior research into a common schema repeatedly loses data — different unit
bases (kg/m³ vs mass-%), relational-vs-flat shapes, controlled-vocabulary mismatches,
and raw curve/image files that flat tables can't hold. This tool makes those losses
**explicit and measurable** instead of silent:

- Every source field is **mapped or written to `<dataset>.unmapped.jsonl`** — never dropped.
- Every converted value carries a **fidelity class** (`exact`, `lossy`, `categorical`, …).
- A 0–100 **Ingestion Fidelity Score** decomposes into five dimensions and tells a
  researcher whether the flat projection is sufficient or the data should stay in its
  original / relational form (the **triage** decision).

## Install

```bash
cd tools/ingest
pip install -e .
```

Dependencies: `pyyaml`, `openpyxl` (Python ≥ 3.9).

## Use

```bash
# relational concrete database template (.xlsx)  ->  Open3DCP flat
open3dcp-ingest convert path/to/source.xlsx --kind relational --out ./out

# UCI "Concrete Compressive Strength" (Yeh 1998) CSV
open3dcp-ingest convert concrete_data.csv --kind uci --out ./out
```

Outputs (per dataset):

| File | Contents |
|---|---|
| `<name>.open3dcp.csv` | Flat Open3DCP rows |
| `<name>.unmapped.jsonl` | Triage sidecar — every field with no flat home, with reason + fidelity class |
| `<name>.fidelity.json` | Machine-readable score |
| `<name>.fidelity.md` | Human-readable report (what was/wasn't preserved + triage advice) |

Python API:

```python
from open3dcp_ingest import convert
result, report = convert("source.xlsx", kind="relational")
print(report.overall, report.grade)        # e.g. 75.8 "B (good; review flagged items)"
for u in result.unmapped:                    # nothing is dropped silently
    print(u.source, u.reason, u.fidelity)
```

## Fidelity dimensions

| Dimension | Weight | Measures |
|---|---:|---|
| `field_coverage` | 0.30 | fraction of populated source fields mapped vs. sidecarred |
| `value_fidelity` | 0.30 | fraction of written values that were exact (no assumed density / solids fraction) |
| `relational_integrity` | 0.15 | cardinality collapse (reinforcement, geometry, devices, loading) |
| `file_data_capture` | 0.15 | curve/table/image/raw files the flat schema can't hold (pre-v1.6) |
| `vocabulary_match` | 0.10 | categorical terms resolved against the crosswalk |

## Adding a source format

1. Add a reader in [`open3dcp_ingest/readers.py`](open3dcp_ingest/readers.py) that emits
   normalized source records (`{source_field_path: value, "_ctx": {...}}`).
2. Add/extend a crosswalk in [`../../crosswalk/`](../../crosswalk/).
3. Wire it into `detect_and_read` and `convert`.

## Tests

```bash
pip install -e ".[test]"
pytest -q          # unit tests (+ integration if OPEN3DCP_RELATIONAL_TEMPLATE is set)
```


## Canonical import and export (tool 1.8.1, schema 1.8)

The UCI reader is limited to the original Yeh format with one unclassified fly-ash component. It rejects class-qualified fly-ash headers and duplicate component columns instead of dropping a class or overwriting a mass. For source quantities use `--kind flat` with `fly_ash_kg_m3` and `fly_ash_class` (`C` or `F`); an omitted class remains generic. For independently specified C/F quantities, use `--kind canonical` with separate `fly_ash_type_c`, `fly_ash_type_f`, and generic `fly_ash` columns already expressed as whole-mix wet mass-%. Unsupported typed kg/m3 header names stay in the unmapped sidecar and prevent an exact mass-balance claim.

Use `--kind flat` for curated **kg/m3 source quantities**. Use `--kind canonical`
for an already canonical CSV whose constituent columns contain **mass-% of the
whole wet batch**. These are different input contracts; do not feed canonical
exports to the kg/m3 reader or rely on CSV auto-detection (which defaults to UCI).

```bash
open3dcp-ingest convert source_kg_m3.csv --kind flat --out converted
open3dcp-ingest convert converted/source_kg_m3.open3dcp.csv --kind canonical --out roundtrip
```

Canonical import preserves row order, repeated mix labels, NULL versus zero,
booleans, decimal precision and source identifiers. It does not normalize again,
infer material classes, deduplicate specimens, or authorize database admission.
Public columns come from the bundled schema registry; update that registry with
schema changes. Site extensions use `x_` and require deposit documentation.
Unrecognized columns stay in the unmapped sidecar. Private fields and sidecars
need a separate publication review; conversion does not make them public-safe.

The CLI also writes `<dataset>.trace.jsonl`, carrying each mapped value's source
and fidelity. Flat source CSVs retain the original lexical record in the sidecar,
including unknown ingredients and invalid values. Keep the source file, trace,
sidecar, dataset version/hash, citation and source specimen/measurement identifiers
together. A DOI alone, a 100% sum, or a high fidelity score is not validation.

Different specimens, ages, orientations and batches remain separate observations.
A reported mean with n=3 remains one mean with its reported count, not three
invented specimen values. Failed/held study outcomes should also be retained so
unchanged sources are not repeatedly re-extracted. Validation must distinguish
measured, inferred and synthetic values, cast and printed preparation, source
rights and complete ingredient inventories before admitting data to calculations.
