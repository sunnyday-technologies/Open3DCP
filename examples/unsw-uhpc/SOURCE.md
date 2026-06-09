# Source — UNSW Global UHPC Mix-Design Dataset

| | |
|---|---|
| **Dataset** | A global dataset of UHPC mix designs with SCMs, nano additives, and sustainable fillers (V2) |
| **Authors** | U. J. Malik, C. K. Lee, D. Mohotti, H. Mo — University of New South Wales (UNSW Canberra), Australia |
| **Host** | Mendeley Data |
| **DOI** | [10.17632/czb7ww5pkz.2](https://doi.org/10.17632/czb7ww5pkz.2) (data paper: [10.1016/j.dib.2025.112179](https://doi.org/10.1016/j.dib.2025.112179)) |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Storage medium** | single flat table (`.xlsx`, 3-row hierarchical header), one row per mix, constituents in **kg/m³** |
| **Size** | 2,188 UHPC mixes from 168 publications · 556 columns |
| **Retrieved** | 2026-06-09 |
| **Type** | **Ultra-high-performance concrete (UHPC)** — cast; silica-fume binder, steel-fibre reinforced |

## Why it is here

UHPC is the high end of the strength range — dense silica-fume matrices, very low w/b, steel fibres, and
28-day compressive strengths of ~130–281 MPa (with early-age points down to ~81 MPa). It exercises Open3DCP columns the normal-strength
benchmarks never touch: `silica_fume`, `metakaolin`, `mineral_powder` (quartz powder), `steel_fiber` with
its `fiber_length_mm` / `fiber_diameter_mm`, and the `flexural_strength_mpa`, `splitting_tensile_mpa`, and
`elastic_modulus_gpa` mechanical columns alongside multi-age compressive strength.

## What we committed

A curated **19-row excerpt** (`build/unsw-uhpc.csv`) of seven mixes chosen to span the UHPC design space:
a silica-fume + quartz-powder matrix with **no fibre** (F0, 199 MPa, with modulus + splitting tensile);
a **40 % fly-ash** replacement (F40, 153 MPa); **steel-fibre** mixes with fly ash and with metakaolin
(S10-F10 / S10-M10, with flexural MOR, 7 & 28 d); and **ultra-high-strength** fibre mixes with plain,
slag, and quaternary binders (B-S0 / B-S40 / G10F10, up to **281 MPa**). It is a **sample, not a re-host**
of the 2,188-mix source; download the full table from the DOI above.

## How it maps to Open3DCP

Every constituent is reported in kg/m³, so the wet-mix total closes and the kg/m³ → mass-% projection is
**exact**; the kg/m³ basis is preserved (`mix_density_kg_m3` / `total_binder_kg_m3` / `original_basis`),
and `w_b_ratio` is derived. Converted with:

```
open3dcp-ingest convert build/unsw-uhpc.csv --kind flat --out .
```

Fidelity **98.2 / 100 (A)**. It populates the **mix-design**, **hardened-mechanical** (compressive,
flexural, splitting-tensile, elastic-modulus), and **multi-age strength** groups; the only assumption is
the superplasticizer solids fraction. Fresh-rheology, 3DCP-process, interlayer-bond, durability,
environment, and raw-material-provenance columns stay **NULL** — see [`index.html`](index.html).

## Citation

Malik, U. J., Lee, C. K., Mohotti, D., & Mo, H. (2025). *A global dataset of UHPC mix designs with
supplementary cementitious materials, nano additives, and sustainable fillers* (Version 2) [Dataset].
Mendeley Data. DOI [10.17632/czb7ww5pkz.2](https://doi.org/10.17632/czb7ww5pkz.2). Licensed CC BY 4.0.
