# Ingestion Fidelity Report — meta-sustainableconcrete

**Overall fidelity: 100.0 / 100 — A (high fidelity)**

- Rows produced: 28
- Source fields seen: 516
- Fields routed to triage sidecar: 0
- Weakest applicable dimension: field_coverage (100)
- Scored over the **applicable** dimensions only (field_coverage, value_fidelity, vocabulary_match); weights renormalized.

| Dimension | Score | Eff. weight | Applicable | Detail |
|---|---:|---:|:--:|---|
| field_coverage | 100 | 0.43 | yes | 468 of 468 mappable source fields mapped to Open3DCP columns (0 routed to triage sidecar). Excluded from coverage (a flat row carries none as its own column): 48 consumed selector/metadata fields. Raw coverage over all 516 populated fields (no exclusions): 91%. |
| value_fidelity | 100 | 0.43 | yes | 459 substantive value cells: 459 stored without an assumption, 0 rest on one (a guessed conversion input such as a solids fraction or product density, or an incomplete-batch projection). 103 of these are recorded generically (classification or solids basis not stated by the source; the value is exact and the classification stays NULL). |
| relational_integrity | 100 | — | N/A | 0 relational fields (reinforcement, geometry parametrization, devices, loading histories) had no flat home. N/A: a flat source has no relational cardinality. |
| file_data_capture | 100 | — | N/A | 0 curve/table/image/raw-file references not captured; 0 routed to *_file columns. N/A: this source carries no file-referenced data. |
| vocabulary_match | 100 | 0.14 | yes | 56 categorical values resolved to canonical codes, 0 unresolved (enum/pivot miss, passed through). |
