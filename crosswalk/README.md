# Open3DCP Crosswalks

Versioned, machine-readable mappings between Open3DCP and external concrete dataset
schemas. These files are the **single source of truth** consumed by the public ingestion
tool ([`tools/ingest/`](../tools/ingest/)), the ingestion **fidelity scorer**, and the
data-intake portal validator. Keep them in sync with both schemas; bump the version in
each file's `meta` when either schema changes.

| File | Maps | Notes |
|---|---|---|
| [`open3dcp_to_relational.yaml`](open3dcp_to_relational.yaml) | Open3DCP ⇄ a relational concrete database (kg/m³) | Primary. Handles relational→flat collapse, kg/m³↔mass-% conversion, vocab pivots, and triage of fields with no flat home. |
| [`open3dcp_to_uci.csv`](open3dcp_to_uci.csv) | Open3DCP ⇄ UCI "Concrete Compressive Strength" (Yeh 1998) | The canonical flat ML baseline (9 columns, kg/m³). |

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
