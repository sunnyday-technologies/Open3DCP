# Source — RILEM TC 304-ADC interlaboratory study (ILS-mech)

| | |
|---|---|
| **Dataset** | Database of the RILEM TC 304-ADC interlaboratory study on **mechanical properties of 3D-printed concrete** |
| **Producer** | RILEM Technical Committee 304-ADC (30 laboratories; DE/BAM, NL, IT, IN/IIT Madras, …) |
| **Host** | Zenodo |
| **DOI** | [10.5281/zenodo.12200570](https://doi.org/10.5281/zenodo.12200570) |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Storage medium** | **relational** openBIS-exported **SQLite** (`2024-06-21_openbis.db`, 23.3 MB; 31 tables/views), **one row per tested specimen** |
| **Size** | ~5,000 mechanical data points (compressive, 3-/4-pt flexural, splitting & uniaxial tensile, E-modulus) |
| **Retrieved** | 2026-06-04 |
| **Type** | **Real 3D-printed concrete** — printed objects, sawn specimens, load-vs-print orientation |

## What we committed

A **hand-curated 9-row excerpt** ([`rilem-tc304-ils-mech.open3dcp.csv`](rilem-tc304-ils-mech.open3dcp.csv)) for
three participating labs (mixes 01, 13, 19). Each Open3DCP row aggregates the per-specimen flexural results for
one **(mix × orientation)** group at ~28 d into **mean + std-dev + n** — directly populating the v1.6 measurement-
uncertainty columns. The source SQLite is **not re-hosted**; download it from the DOI and reproduce with
[`build/extract.py`](build/extract.py) (see [`build/README.md`](build/README.md)).

> v1 is hand-curated via the relational structure; a turnkey `open3dcp-ingest` **SQLite reader is a planned
> follow-up**, after which this example will join the reproduce-and-diff CI guard like the UCI one.

## How it maps to Open3DCP

The relational chain (material → print → per-specimen test) is **denormalized and aggregated** into flat rows. The
RILEM **U/V/W** orientation (U = print path, V = transverse, W = build axis) maps onto Open3DCP `test_orientation_code`
**X/Y/Z/CAST** — the original RILEM code is retained in `provenance_notes`. The headline result is **print
anisotropy**: the same mix is markedly weaker loaded *parallel to the layers* (X) than cast or *perpendicular* (Z):

| lab | cast (MPa) | printed ∥ layers / X | printed ⟂ or transverse |
|---|---|---|---|
| 01 | 6.84 ±1.09 (n=19) | 4.09 ±1.58 (n=34) | 6.07 ±0.74 (Z, n=19) |
| 13 | 9.97 ±0.84 (n=22) | 6.80 ±0.97 (n=40) | 9.93 ±0.96 (Y, n=20) |
| 19 | 14.76 ±5.90 (n=12) | 6.72 ±2.47 (n=17) | 14.48 ±2.52 (Y, n=12) |

It populates the **3DCP-process**, **fresh-rheology** (static yield stress), **hardened-mechanical**,
**print-anisotropy** (orientation), and **measurement-uncertainty** groups — the columns UCI leaves null. The
participating mortars are **commercial premixes**, so the per-constituent **mix-design** columns stay null (composition
not disclosed); the print travel-velocity field is unit-inconsistent in the source and is deliberately omitted.

## Citation

RILEM TC 304-ADC (2024). *Database of the RILEM TC 304-ADC interlaboratory study on mechanical properties of 3D
printed concrete* [Dataset]. Zenodo. DOI [10.5281/zenodo.12200570](https://doi.org/10.5281/zenodo.12200570).
Licensed CC BY 4.0.
