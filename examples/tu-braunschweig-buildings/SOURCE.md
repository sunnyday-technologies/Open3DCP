# Source — TU-Braunschweig Database of 3D Concrete Printed Buildings

| | |
|---|---|
| **Dataset** | Database of 3D Concrete Printed Buildings |
| **Authors** | Gerrit Placzek, Maike Dahlberg — TU Braunschweig (Inst. für Bauwirtschaft und Baubetrieb), Germany |
| **Host** | Zenodo |
| **DOI** | [10.5281/zenodo.14214812](https://doi.org/10.5281/zenodo.14214812) (paper: [10.3390/buildings14113410](https://doi.org/10.3390/buildings14113410)) |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Storage medium** | single flat table (`.xlsx`), one row per built project, 22 project/process categories |
| **Size** | ~175 extrusion-printed building projects (2013–2023) |
| **Retrieved** | 2026-06-09 |
| **Type** | **Real extrusion-3DCP buildings** — project/process catalogue (who printed what, where, with which system) |

## Why it is here — a *different* slice, on purpose

Not every open 3DCP dataset is a materials dataset. This one is a **project / process layer** catalogue:
consortium, country, printer/system, fabrication and printing strategy, storeys, floor area, purpose. It
carries **no mix composition, no rheology, no strength** — and that is exactly the point. *A data class
being absent is not a defect; it is the frontier the connective layer has to reach next.* The current
Open3DCP flat schema is **mix-centric**, so most of these building-project fields have **no flat materials
home** today; they are curated here as named **project-layer columns** plus provenance, with **no
mix-fidelity score**, to make the boundary explicit.

The union is the argument: UCI/Meta/UNSW supply mix design and strength, UF and RILEM supply
printability and printed-specimen mechanics, and this source supplies the **as-built project record** that
a full digital twin must eventually link to its mixes and prints.

## What we committed

A curated **10-record excerpt** (`tu-braunschweig-buildings.open3dcp.csv`) of landmark printed buildings
(2016–2020) spanning eight countries and the major systems — WinSun *Office of the Future* (UAE), Apis Cor
(Russia, Dubai), COBOD *The BOD* (Denmark) and the Malawi school (14trees/PERI/Holcim), SQ4D (USA), ICON
(Mexico community, US *Community First!*), Kamp C (Belgium), and Twente's *Fibonacci House* (Canada) — and
the off-site vs in-situ strategies. It is a **sample, not a re-host**; download the full catalogue from the
DOI.

## How it maps to Open3DCP

`is_3d_printed` is set; the rest are **project/process-layer** fields recorded as named columns + a
provenance note. There is **no fidelity score** — this is a layer beyond the current flat mix schema, not a
lossy mix conversion. A future Open3DCP project/process table would give these fields a typed home and link
them to the mixes and prints used.

## Citation

Placzek, G., & Dahlberg, M. (2024). *Database of 3D Concrete Printed Buildings* [Dataset]. Zenodo. DOI
[10.5281/zenodo.14214812](https://doi.org/10.5281/zenodo.14214812). Licensed CC BY 4.0.
