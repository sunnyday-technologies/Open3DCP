# Ingestion Fidelity Report — meta-sustainableconcrete

**Overall fidelity: 79.0 / 100 — C (partial; triage recommended) — capped by the weakest dimension**

- Rows produced: 28
- Source fields seen: 1020
- Fields routed to triage sidecar: 476
- Weakest applicable dimension: field_coverage (51)
- Scored over the **applicable** dimensions only (field_coverage, value_fidelity, vocabulary_match); weights renormalized.

| Dimension | Score | Eff. weight | Applicable | Detail |
|---|---:|---:|:--:|---|
| field_coverage | 51 | 0.43 | yes | 496 of 972 mappable source fields mapped to Open3DCP columns (476 routed to triage sidecar). Excluded from coverage (a flat row carries none as its own column): 48 consumed selector/metadata fields. Raw coverage over all 1020 populated fields (no exclusions): 49%. |
| value_fidelity | 100 | 0.43 | yes | 487 substantive value cells: 487 stored without an assumption, 0 rest on one (a guessed conversion input such as a solids fraction or product density, or an incomplete-batch projection). 103 of these are recorded generically (classification or solids basis not stated by the source; the value is exact and the classification stays NULL). |
| relational_integrity | 100 | — | N/A | 0 relational fields (reinforcement, geometry parametrization, devices, loading histories) had no flat home. N/A: a flat source has no relational cardinality. |
| file_data_capture | 100 | — | N/A | 0 curve/table/image/raw-file references not captured; 0 routed to *_file columns. N/A: this source carries no file-referenced data. |
| vocabulary_match | 100 | 0.14 | yes | 56 categorical values resolved to canonical codes, 0 unresolved (enum/pivot miss, passed through). |

### Not preserved — field_coverage
_Sidecar fields are preserved in <dataset>.unmapped.jsonl; review for schema extension._

- source.age_days
- source.cement_kg_m3
- source.coarse_agg_kg_m3
- source.compressive_strength_mpa
- source.compressive_strength_std_mpa
- source.curing_temp_c
- source.embodied_carbon_kg_co2_m3
- source.fine_agg_kg_m3
- source.fly_ash_kg_m3
- source.material_class
- source.n_specimens
- source.slag_kg_m3
- source.slump_mm
- source.specimen_geometry
- source.superplasticizer_kg_m3
- source.test_method
- source.water_kg_m3
