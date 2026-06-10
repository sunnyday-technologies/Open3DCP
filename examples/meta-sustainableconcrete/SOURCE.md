# Source — Meta SustainableConcrete (BOxCrete dataset)

| | |
|---|---|
| **Dataset** | SustainableConcrete — `data/boxcrete_data.csv` (the BOxCrete dataset) |
| **Producers** | Meta Platforms / FAIR · University of Illinois Urbana-Champaign · Amrize |
| **Host** | GitHub — `facebookresearch/SustainableConcrete` |
| **URL** | https://github.com/facebookresearch/SustainableConcrete |
| **License** | MIT License (© Meta Platforms, Inc. and affiliates) |
| **Storage medium** | single flat table (`.csv`), one row per **mix · curing age**, constituents in **kg/m³ of a 1 m³ batch** |
| **Size** | 149 mixes · 727 rows (multi-age) · 19 columns |
| **Retrieved** | 2026-06-09 |
| **Type** | **Conventional cast concrete & mortar** (Portland + fly ash + slag); no 3D-printing process context |

## Why it is here

This is the rare **corporate-sponsored, openly-licensed** concrete dataset: Meta released it (with UIUC
and Amrize) to support carbon-aware mix optimization for data-centre construction. It is the same shape as
the UCI benchmark — every constituent in kg/m³ — but adds two things UCI lacks: a **per-mix GWP / embodied-
carbon** figure and **per-measurement mean / standard-deviation / n**. It exercises the Open3DCP
**environment** (embodied carbon) and **measurement-uncertainty** groups that the UCI row leaves null.

We ingest only the **measured** table here. The same repository also ships a trained Gaussian-process
model and a model-explored design space of optimization-derived candidate mixes (a "synthetic" arm);
ingesting those as *model-generated* records — kept distinct from measured data by the
`measurement_confidence` flag — is a planned follow-up, not done here.

## What we committed

A curated **28-row excerpt** (`build/meta-sustainableconcrete.csv`) of six mixes chosen to span the
dataset's variety — plain OPC, fly-ash, slag, and ternary binders; mortar and concrete; the carbon range
(GWP **204–521 kg CO₂/m³**) and the strength range (**26–110 MPa**), each across its 1–28 d age series. It
is a **sample, not a re-host** of the 727-row source; download the full table from the repo above.

The carbon contrast is the worked-demonstration point: plain-OPC concrete (Mix_84) sits at **GWP 521** for
~65 MPa, while a low-clinker ternary (Mix_88) reaches **~110 MPa at GWP 204** — *higher strength, ~60 % less
embodied carbon* — exactly the trade-off a connective schema is meant to make legible across sources.

## How it maps to Open3DCP

Every constituent (including water) is reported in kg/m³, so the wet-mix total closes and the kg/m³ →
mass-% projection is **exact**; the kg/m³ basis is preserved via `total_batched_mass_kg_m3` / `total_binder_kg_m3`
/ `original_basis=kg_m3`, and `w_b_ratio` is derived. Converted with:

```
open3dcp-ingest convert build/meta-sustainableconcrete.csv --kind flat --out .
```

Fidelity **90.4 / 100 (B)**. It populates the **mix-design**, **hardened-compressive**, **multi-age
strength**, **embodied-carbon (environment)**, and **measurement-uncertainty** groups. Specimen geometry
and test method are **not reported by the source** and are recorded as `NULL` (not inferred); the
superplasticizer (HRWR) is recorded as-delivered (solids fraction unknown). Every 3DCP-process, rheology,
interlayer-bond, durability, and raw-material-provenance column stays **NULL** — see [`index.html`](index.html).

## Citation

Baten, B., Iqbal, M. A., Ament, S., Kusuma, J., & Garg, N. (2026). *SustainableConcrete / BOxCrete*
[Dataset & code]. Meta Platforms, Inc. / University of Illinois Urbana-Champaign / Amrize.
https://github.com/facebookresearch/SustainableConcrete. Licensed MIT.
