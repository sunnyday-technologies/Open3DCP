# Ingestion Fidelity Report — uci-yeh-1998

**Overall fidelity: 79.9 / 100 — C (partial; triage recommended) — capped by the weakest dimension**

- Rows produced: 14
- Source fields seen: 126
- Fields routed to triage sidecar: 0
- Weakest applicable dimension: value_fidelity (60)
- Scored over the **applicable** dimensions only (field_coverage, value_fidelity); weights renormalized.

| Dimension | Score | Eff. weight | Applicable | Detail |
|---|---:|---:|:--:|---|
| field_coverage | 100 | 0.50 | yes | 126 of 126 mappable source fields mapped to Open3DCP columns (0 routed to triage sidecar). |
| value_fidelity | 60 | 0.50 | yes | 117 substantive value cells: 70 stored without an assumption, 47 rest on one (liquid->solids admixture, FM/size aggregate bucket, defaulted cement type, or an incomplete-batch projection). |
| relational_integrity | 100 | — | N/A | 0 relational fields (reinforcement, geometry parametrization, devices, loading histories) had no flat home. N/A: a flat source has no relational cardinality. |
| file_data_capture | 100 | — | N/A | 0 curve/table/image/raw-file references not captured; 0 routed to *_file columns. N/A: this source carries no file-referenced data. |
| vocabulary_match | 100 | — | N/A | 0 categorical values resolved to canonical codes, 0 unresolved (enum/pivot miss, passed through). N/A: this source has no categorical vocabulary to resolve. |

### Not preserved — value_fidelity
_Assumed cells need the missing source detail (solids fraction, fineness modulus, aggregate size, cement type) to become exact; the value is recorded, the attribute is inferred._

- agg_size_57 (full batch known)
- cement_type_1 (full batch known)
- concrete_sand (full batch known)
- superplasticizer (solids fraction unknown; recorded as-delivered mass-% (not solids))
