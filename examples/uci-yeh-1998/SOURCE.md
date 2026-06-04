# Source — UCI Concrete Compressive Strength (Yeh, 1998)

| | |
|---|---|
| **Dataset** | Concrete Compressive Strength |
| **Originator** | Prof. I-Cheng Yeh, Chung-Hua University, Taiwan |
| **Host** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength |
| **DOI** | [10.24432/C5PK67](https://doi.org/10.24432/C5PK67) |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Storage medium** | single flat table (`.xls` / `.csv`), one row per mix·age, constituents in **kg/m³ of a 1 m³ mixture** |
| **Size** | 1,030 rows · 8 inputs + 1 target |
| **Retrieved** | 2026-06-04 |
| **Type** | **Conventional cast concrete** — no 3D-printing process context |

## What we committed

A curated **14-row excerpt** (`build/uci-yeh-1998.csv`) chosen to span the dataset's variety — ages
1–365 d, plain OPC vs slag / fly-ash / ternary mixes, with and without superplasticizer, and the full
strength range (2.3–82.6 MPa). It is a **sample, not a re-host** of the 1,030-row source; download the
full dataset from the DOI above.

## How it maps to Open3DCP

Because every constituent (including water) is reported in kg/m³, the wet-mix total is complete, so the
kg/m³ → mass-% projection is **exact** and the kg/m³ basis is preserved via `mix_density_kg_m3` /
`total_binder_kg_m3` / `original_basis=kg_m3`. Converted with:

```
open3dcp-ingest convert build/uci-yeh-1998.csv --kind uci --out .
```

Fidelity **96.7 / 100 (A)**. It populates the **mix-design**, **hardened-compressive**, and
**multi-age strength** groups; every 3DCP-process, rheology, interlayer-bond, durability, environment,
and raw-material-provenance column stays **NULL** — see [`index.html`](index.html) for the full
structure → schema graphic.

## Citation

Yeh, I-C. (1998). *Concrete Compressive Strength* [Dataset]. UCI Machine Learning Repository.
DOI [10.24432/C5PK67](https://doi.org/10.24432/C5PK67). Licensed CC BY 4.0.

Underlying study (publisher-copyrighted; cited as courtesy, not redistributed):
Yeh, I-C. (1998). "Modeling of strength of high-performance concrete using artificial neural networks."
*Cement and Concrete Research*, 28(12), 1797–1808.
