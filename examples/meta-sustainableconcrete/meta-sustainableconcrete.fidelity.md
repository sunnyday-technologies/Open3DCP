# Ingestion Fidelity Report — meta-sustainableconcrete

**Overall fidelity: 98.9 / 100 — A (high fidelity)**

- Rows produced: 28
- Source fields seen: 600
- Fields routed to triage sidecar: 0

| Dimension | Score | Weight | Detail |
|---|---:|---:|---|
| field_coverage | 100 | 0.30 | 524 of 524 mappable source fields mapped to Open3DCP columns (0 routed to triage sidecar). Excluded from coverage (a flat row carries none as its own column): 76 consumed selector/metadata fields. Raw coverage over all 600 populated fields (no exclusions): 87%. |
| value_fidelity | 96 | 0.30 | 524 values written; 505 exact, 19 required an assumption. |
| relational_integrity | 100 | 0.15 | 0 relational fields (reinforcement, geometry parametrization, devices, loading histories) had no flat home. |
| file_data_capture | 100 | 0.15 | 0 curve/table/image/raw-file references cannot be held by the flat schema (pre-v1.6). |
| vocabulary_match | 100 | 0.10 | 84 categorical values resolved, 0 unresolved against the crosswalk. |

### Not preserved — value_fidelity
_Assumed conversions (e.g. kg/m3<->mass-%, liquid->solids) need the missing density / solids fraction to become exact. Record mix_density_kg_m3 at source._

- superplasticizer (solids fraction unknown; recorded as-delivered mass-% (not solids))
