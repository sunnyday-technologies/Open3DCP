# Source — UF 3D-Printing-Concrete Mix-Design Open Dataset

| | |
|---|---|
| **Dataset** | 3D Printing Concrete Mix Design Open Dataset (v0.3) |
| **Authors** | Jianhao Gao, Zijie Wang, Chaofeng Wang (University of Florida), USA |
| **Host** | Zenodo |
| **DOI** | [10.5281/zenodo.6828947](https://doi.org/10.5281/zenodo.6828947) (concept; v0.3 = 8070144) |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Storage medium** | single flat table (`.xlsx`), one row per mix, constituents on a **ratio-to-binder** basis (binder = 1) |
| **Size** | extrusion-3DCP mixes standardized from many primary studies · 118 columns |
| **Retrieved** | 2026-06-09 |
| **Type** | **Real extrusion-based 3D-printed concrete** — printable Portland-cement mortars, with fresh rheology |

## Why it is here — and what it deliberately leaves NULL

This is the genuine **extrusion-3DCP mix slice**: printable Portland-cement mixes reported with the
fresh-state **rheology that governs printability** — static and dynamic yield stress and plastic viscosity
— plus water/binder and compressive strength. It fills `is_3d_printed`, `static_yield_stress_pa`,
`dynamic_yield_stress_pa`, and `plastic_viscosity_pa_s` — columns the cast benchmarks (UCI, Meta, UNSW)
leave empty.

It is also an honest illustration of a **basis mismatch**, which is the whole point of a connective
schema: the source reports constituents as **ratios to binder** (binder = 1), with **no absolute binder
content in kg/m³**, so the kg/m³ basis is **not recoverable** and a constituent mass-% of the total mix
cannot be formed without assuming a binder dosage. We therefore **do not fabricate** constituent mass-%;
the mix-design columns beyond `w_b_ratio` and the binder system stay NULL, recorded plainly in each row's
provenance note. *Missing data classes are not a defect — they are the gap the connective layer exists to
span.*

## What we committed

A hand-curated **10-row excerpt** (`uf-3dcp-mix.open3dcp.csv`) of printable Portland mixes drawn from
several primary studies, spanning static yield stress **~0.4–4.6 kPa**, w/b **0.30–0.45**, and 28-day
compressive strength **28–72 MPa**. It is a **sample, not a re-host**; download the full table from the DOI.

> Hand-curated via the source's ratio-to-binder structure; a turnkey `open3dcp-ingest` **ratio-to-binder
> reader (with a fidelity score) is a planned follow-up** — the score is deferred, exactly as for the
> RILEM excerpt.

## How it maps to Open3DCP

The relational/ratio fields are read and the rheology converted to SI (kPa → Pa). It populates the
**3DCP-process / printability** flag, **fresh-rheology** (yield stress, viscosity), partial **mix-design**
(`w_b_ratio`, binder system), and **hardened-compressive** groups; constituent mass-%, multi-age, interlayer
bond, durability, environment, and raw-material provenance stay **NULL**. Build:

```
python build/extract.py "3D concrete printing mix design dataset v0.3.xlsx"
```

## Citation

Gao, J., Wang, Z., & Wang, C. (2022). *3D Printing Concrete Mix Design Open Dataset* (v0.3) [Dataset].
Zenodo. DOI [10.5281/zenodo.6828947](https://doi.org/10.5281/zenodo.6828947). Licensed CC BY 4.0.
