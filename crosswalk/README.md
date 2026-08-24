# Open3DCP Crosswalks

Versioned, machine-readable mappings between Open3DCP and external schemas, datasets,
and data models. The two **ingestion crosswalks** (`open3dcp_to_relational.yaml`,
`open3dcp_to_uci.csv`) are the single source of truth consumed by the public ingestion
tool ([`tools/ingest/`](../tools/ingest/)), the ingestion **fidelity scorer**, and the
data-intake portal validator — keep them in sync with both schemas and bump the version
in the YAML `meta` when either schema changes. The three **model-level crosswalks**
(`open3dcp_to_{amcdm,gemd,cpto}.csv`) are generated artifacts; see
*Structural mapping classes* below for their regeneration and pinning rules.

| File | Maps | Notes |
|---|---|---|
| [`open3dcp_to_relational.yaml`](open3dcp_to_relational.yaml) | Open3DCP ⇄ a relational concrete database (kg/m³) | Primary. Handles relational→flat collapse, kg/m³↔mass-% conversion, vocab pivots, and triage of fields with no flat home. |
| [`open3dcp_to_uci.csv`](open3dcp_to_uci.csv) | Open3DCP ⇄ UCI "Concrete Compressive Strength" (Yeh 1998) | The canonical flat ML baseline (9 columns, kg/m³). |
| [`open3dcp_to_amcdm.csv`](open3dcp_to_amcdm.csv) | Open3DCP → AM-CDM (Additive Manufacturing Common Data Model) | Model-level. Target pinned: [`AM-CDM/AM-CDM`](https://github.com/AM-CDM/AM-CDM)@`141030b` (2026-07-28; the model has no release tags); Kuan et al. 2024, [doi:10.1007/s40192-024-00341-x](https://doi.org/10.1007/s40192-024-00341-x). |
| [`open3dcp_to_gemd.csv`](open3dcp_to_gemd.csv) | Open3DCP → GEMD (Graphical Expression of Materials Data) | Model-level. Target: GEMD format v0.1, [docs](https://citrineinformatics.github.io/gemd-docs/). |
| [`open3dcp_to_cpto.csv`](open3dcp_to_cpto.csv) | Open3DCP → CPTO (Concrete Production and Testing Ontology) | Model-level. Target: CPTO v1.0.1 ([w3id.org/cpto](https://w3id.org/cpto), built on PMDco 2.0 + PROV-O); Meng et al. 2023, [doi:10.1002/cepa.2955](https://doi.org/10.1002/cepa.2955). |
| [`units.csv`](units.csv) | Open3DCP → units, quantity kinds, and SI(mm) conversion factors | Generated (v1.8). One row per `mix_designs` column; `si_mm_factor` converts a value into the **SI(mm) consistent system** (mm / N / tonne / s ⇒ MPa, tonne/mm³, mJ) used by FE codes such as Abaqus. `fe_relevant` flags the columns a structural or thermal model consumes. |

## Units manifest (`units.csv`, v1.8)

Open3DCP embeds units in column names (`compressive_strength_mpa`) so a value can never be
entered or read under the wrong unit — a deliberate ergonomic choice for humans. `units.csv` is
its machine-readable counterpart: a consumer never has to parse a column name to learn what a
number means, and never has to hard-code a conversion factor.

```
value_si_mm = value_open3dcp * si_mm_factor
```

Generated from `sql/create_tables.sql` by
[`scripts/build_units_manifest.py`](../scripts/build_units_manifest.py) and verified in CI with
`--check`, so it cannot drift from the schema. A blank `si_mm_factor` means the column is not a
physical quantity (identifier, category, flag, date, file reference) or has no FE analogue — note
in particular that `cement_strength_class_mpa` is an EN 197-1 *classification label*, not a mix
stress, and is deliberately not convertible.

Much of the schema is already SI(mm)-native: every strength and stress column is MPa (= N/mm²) and
every geometry column is mm, both factor 1. The conversions that matter are densities
(kg/m³ → tonne/mm³, ×10⁻¹²) and the thermal block. Requested by David Scheidt
([ORCID 0009-0003-1996-4918](https://orcid.org/0009-0003-1996-4918)) for a conversion-free
structural export.

## Fidelity classes

Every mapping declares a fidelity class so the scorer can quantify what is preserved:

- `exact` — reversible, no information lost.
- `derived` — computed from other reported fields; exact only if inputs are present.
- `lossy` — needs an assumption (density / solids fraction) to convert.
- `categorical` — vocab/value pivot; information-equivalent, structure differs.
- `collapse` — relational one-to-many flattened into the wide row (cardinality lost).
- `file_ref` — source is an external file the flat schema cannot hold (until v1.6).
- `none` — no flat Open3DCP home → routed to the triage sidecar (never dropped).

The **drop-nothing** rule (see [`AGENTS.md`](../AGENTS.md)): any source field that does not
map is written to `<dataset>.unmapped.jsonl`, not discarded.

## Structural mapping classes (model/ontology crosswalks)

The three **model-level** files (`open3dcp_to_amcdm.csv`, `open3dcp_to_gemd.csv`,
`open3dcp_to_cpto.csv`) describe how a flat Open3DCP record *lifts into* an external
data model or ontology — a structural mapping, not a value conversion — so they use a
distinct class set:

- `exact` — the same quantity exists in the target; unit conversion at most.
- `normalized` — same information, restructured (column → class instance/attribute).
- `derived` — computable from other mapped fields.
- `partial` — the target holds only a subset or a coarser form of the information.
- `sidecar` — needs a linked non-flat record (**reserved**: assigned once the planned
  context/measurement sidecar records exist; currently unused).
- `no_map` — no target entity exists. For the 3DCP process, printing-state rheology,
  and interlayer blocks this is the substantive finding: the extrusion vocabulary is
  Open3DCP's additive contribution, offered as a candidate domain profile.

Two reading rules keep the classes honest. **GEMD is a structural format with no domain
vocabulary**, so `no_map` is definitionally unreachable there — its `normalized` rows
mean "holdable in a generic container via project-defined attribute templates" (each
such row says so in its note), not "a named target concept exists." And **AM-CDM
target entities are concept paths** whose identifiers resolve in the pinned commit's
SADL modules (module prefix before the colon).

These files are **generated** from `sql/create_tables.sql` (the schema's source of
truth) by [`scripts/build_precedent_crosswalks.py`](https://github.com/sunnyday-technologies/Open3DCP/blob/main/scripts/build_precedent_crosswalks.py);
regenerate them whenever the schema changes (`--check` verifies freshness and runs in
CI), and bump the pinned target versions in the table above when a target releases.
