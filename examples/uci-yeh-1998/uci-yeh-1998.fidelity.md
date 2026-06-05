# Ingestion Fidelity Report — uci-yeh-1998

**Overall fidelity: 96.7 / 100 — A (high fidelity)**

- Rows produced: 14
- Source fields seen: 126
- Fields routed to triage sidecar: 0

| Dimension | Score | Weight | Detail |
|---|---:|---:|---|
| field_coverage | 100 | 0.30 | 126 of 126 mappable source fields mapped to Open3DCP columns (0 routed to triage sidecar). |
| value_fidelity | 89 | 0.30 | 126 values written; 125 exact, 1 required an assumption. |
| relational_integrity | 100 | 0.15 | 0 relational fields (reinforcement, geometry parametrization, devices, loading histories) had no flat home. |
| file_data_capture | 100 | 0.15 | 0 curve/table/image/raw-file references cannot be held by the flat schema (pre-v1.6). |
| vocabulary_match | 100 | 0.10 | 0 categorical values resolved, 0 unresolved against the crosswalk. |

### Not preserved — value_fidelity
_Assumed conversions (e.g. kg/m3<->mass-%, liquid->solids) need the missing density / solids fraction to become exact. Record mix_density_kg_m3 at source._

- superplasticizer (solids fraction unknown; recorded as-delivered mass-% (not solids))
