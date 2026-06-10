# Ingestion Fidelity Report — meta-sustainableconcrete

**Overall fidelity: 90.4 / 100 — B (good; review flagged items) — capped by the weakest dimension**

- Rows produced: 28
- Source fields seen: 544
- Fields routed to triage sidecar: 0
- Weakest applicable dimension: value_fidelity (78)
- Scored over the **applicable** dimensions only (field_coverage, value_fidelity, vocabulary_match); weights renormalized.

| Dimension | Score | Eff. weight | Applicable | Detail |
|---|---:|---:|:--:|---|
| field_coverage | 100 | 0.43 | yes | 468 of 468 mappable source fields mapped to Open3DCP columns (0 routed to triage sidecar). Excluded from coverage (a flat row carries none as its own column): 76 consumed selector/metadata fields. Raw coverage over all 544 populated fields (no exclusions): 86%. |
| value_fidelity | 78 | 0.43 | yes | 459 substantive value cells: 356 stored without an assumption, 103 rest on one (liquid->solids admixture, FM/size aggregate bucket, defaulted cement type, or an incomplete-batch projection). |
| relational_integrity | 100 | — | N/A | 0 relational fields (reinforcement, geometry parametrization, devices, loading histories) had no flat home. N/A: a flat source has no relational cardinality. |
| file_data_capture | 100 | — | N/A | 0 curve/table/image/raw-file references not captured; 0 routed to *_file columns. N/A: this source carries no file-referenced data. |
| vocabulary_match | 100 | 0.14 | yes | 84 categorical values resolved to canonical codes, 0 unresolved (enum/pivot miss, passed through). |

### Not preserved — value_fidelity
_Assumed cells need the missing source detail (solids fraction, fineness modulus, aggregate size, cement type) to become exact; the value is recorded, the attribute is inferred._

- agg_size_57 (full batch known)
- cement_type_1 (full batch known; assumed (defaulted selector))
- concrete_sand (full batch known)
- superplasticizer (solids fraction unknown; recorded as-delivered mass-% (not solids))
