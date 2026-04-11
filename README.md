<p align="center">
  <img src="assets/logo.svg" alt="Open3DCP" width="200"/>
</p>

<h1 align="center">Open3DCP</h1>
<p align="center"><strong>Open Data Standard for 3D Concrete Printing</strong></p>
<p align="center">
  <a href="https://open3dcp.org">open3dcp.org</a> ·
  <a href="Open3DCP_SCHEMA.md">Schema Reference</a> ·
  <a href="sql/create_tables.sql">SQL Implementation</a>
</p>

An open database schema for 3D-printable concrete (3DCP) mix design data, developed by [Sunnyday Technologies](https://sunn3d.com).

Open3DCP defines a standard way to store the full digital twin of a 3DCP formulation: what goes into the mix, how it was printed, how it was cured, and what came out in testing. Every column has a name, a unit, and a purpose. No JSON parsing, no nested structures, no guesswork.

This repository provides the **schema definition only** -- column names, types, units, and engineering context. We encourage researchers and industry to adopt this schema as a common format so that 3DCP datasets from different labs and research groups can be combined without painful reformatting.

---

## Why This Exists

There is no standard way to store 3D-printable concrete data.

Research papers describe mixes as free-text tables with inconsistent naming. One paper calls it "GGBFS," another says "slag," a third writes "ground granulated blast-furnace slag." The aggregate is "sand" in one study and "siliceous fine aggregate (0-2 mm)" in another. Print parameters are buried in methodology sections. Test results are scattered across figures, tables, and supplementary files.

This makes it nearly impossible to combine datasets from different research groups into a single training corpus for machine learning. Open3DCP solves this by defining a canonical flat schema where every material, process parameter, and test result has exactly one column name, one unit, and one meaning.

The schema follows **FAIR data principles** (Findable, Accessible, Interoperable, Reusable) and the **Processing-Structure-Property-Performance** pattern, consistent with the NASA GRC ICME Schema philosophy for materials data management (Hearley & Arnold, 2023). Column organization aligns with NIST Materials Data Repository guidelines, RILEM TC 304-ADC recommendations, and Citrine GEMD conventions.

---

## Design Principles

1. **Flat schema** -- Every feature is a named column. No JSON nesting for ML-relevant data.

2. **Mass-percent basis** -- All material quantities are stored as mass-% of the total wet mix (water included, 0-100 scale). This eliminates the need for density assumptions during inference and is consistent across datasets.

3. **Standards-aligned** -- Column naming follows established test standards: ASTM C150 for cement types, ASTM C618 for fly ash, ASTM C989 for slag, ASTM C1240 for silica fume, ASTM C33 for aggregate grading by fineness modulus.

4. **3DCP-native** -- First-class columns for print process parameters (nozzle geometry, layer timing, print speed, pump pressure), fresh-state rheology (yield stress, thixotropy, open time), and interlayer bond properties. These do not exist in conventional concrete schemas.

5. **Multi-age** -- A companion `strength_measurements` table stores test results at multiple ages (1 hour through 365 days), supporting strength gain curve analysis.

---

## What Goes Into Concrete

Concrete is fundamentally simple: mix a powder (binder) with water, add rocks (aggregate) for bulk, and stir until uniform. The water triggers a chemical reaction (hydration) that hardens the paste around the aggregate particles. Everything else is refinement.

3D-printable concrete is more demanding. The mix must flow through a pump and nozzle, hold its shape immediately after deposition (no formwork to contain it), bond to the previous layer, and develop strength quickly enough to support the next layer. This requires careful control of rheology and setting behavior, which is where admixtures, fibers, and process parameters become critical.

### Binders -- The Glue

Binders are the reactive powders that harden when mixed with water. Portland cement is the baseline, but modern 3DCP mixes often replace 20-50% of the cement with supplementary cementitious materials (SCMs) to reduce cost, lower embodied carbon, or modify setting behavior.

| Column | What It Is | Why It Matters for 3DCP |
|--------|------------|------------------------|
| `cement_type_1` | General purpose Portland cement, ASTM C150 Type I. | Primary source of early strength. Most 3DCP mixes use 20-40% by total mass. |
| `cement_type_1_2` | General purpose / moderate sulfate resistance, ASTM C150 Type I/II. | The most commonly sold cement in the US. Many suppliers don't stock pure Type I. |
| `cement_type_1l` | Portland-limestone cement, ASTM C595 / EN 197-1 CEM II/A-L. Contains 6-20% limestone. | Lower carbon than OPC. Distinct product, not just "cement with limestone filler." |
| `cement_type_2` | Moderate sulfate resistance / moderate heat, ASTM C150 Type II. | Used in environments with moderate sulfate exposure. |
| `cement_type_3` | High early strength / rapid hardening, ASTM C150 Type III. Finer grind, faster hydration. | Useful when early strength gain is critical for layer-on-layer buildability. |
| `cement_type_5` | High sulfate resistance, ASTM C150 Type V. | Required in sulfate-rich soils, common in western US. |
| `fly_ash` | Coal combustion byproduct. When class is known, use `fly_ash_type_f` (SiO2+Al2O3+Fe2O3 ≥ 70% per ASTM C618) or `fly_ash_type_c` (≥ 50%). | Improves long-term strength and reduces heat of hydration. Slows early strength, which can be problematic for 3DCP layer timing. |
| `silica_fume` | Ultra-fine amorphous silica from silicon/ferrosilicon production. Particle size ~0.1 um. ASTM C1240. | Fills micro-voids between cement grains (packing effect), dramatically increases strength. Typical dosage 5-10%. Increases water demand. |
| `slag` | Ground granulated blast-furnace slag (GGBFS). Steel industry byproduct. ASTM C989. | Improves durability, reduces permeability, contributes to long-term strength. Common at 30-50% replacement in 3DCP. |
| `metakaolin` | Calcined kaolin clay. High reactivity pozzolan. ASTM C618 Class N. | Popular in 3DCP for early strength development and thixotropy enhancement. Typical 5-15%. |
| `limestone` | Ground limestone powder/filler. EN 12620. | Provides nucleation sites that accelerate cement hydration. Improves particle packing. Common in European 3DCP mixes at 5-20%. |

Additional binder columns in the full schema include `pumice` (natural volcanic pozzolan), `cement_type_4` (low heat, rarely manufactured), `cac` (calcium aluminate cement for rapid set), `csa_cement` (calcium sulfoaluminate), `nano_silica`, `bottom_ash`, and classified fly ash variants (`fly_ash_type_f`, `fly_ash_type_c`).

### Aggregates -- The Skeleton

Aggregates provide bulk, dimensional stability, and reduce cost. In conventional concrete, coarse aggregates (10-20 mm) dominate. In 3DCP, aggregates must pass through a pump and nozzle, so maximum particle size is typically limited to 2-4 mm for standard equipment. This makes sand the primary aggregate, though large-nozzle systems (military, infrastructure) can accommodate coarser material.

**Fine aggregates** are classified using US industry ordering terms. FM ranges are adapted from ASTM C33 grading principles; note that ASTM C33 defines fine aggregate as FM 2.3-3.1 without further subdivision:

| Column | FM Range | US Order Name | Role in 3DCP |
|--------|----------|---------------|--------------|
| `mason_sand` | 1.0-1.8 | Mason sand / plaster sand | Very fine, high fines content. Surface finish. |
| `fine_sand` | 1.6-2.2 | Fine sand | Filler, improves pumpability |
| `concrete_sand` | 2.3-3.0 | Concrete sand / C33 sand | Primary aggregate in most 3DCP mixes |
| `coarse_sand` | 3.1-3.7 | Coarse sand / torpedo sand | Improves dimensional stability, harder to pump |

**Coarse aggregates** use ASTM C33 size numbers. Most 3DCP uses Size #8 or smaller; larger sizes are included for large-nozzle systems and conventional concrete compatibility:

| Column | ASTM C33 Size | Nominal Range | US Common Name |
|--------|--------------|---------------|----------------|
| `agg_size_89` | #89 | 3/8" - #16 sieve | Fine gravel |
| `agg_size_8` | #8 | 3/8" - #8 sieve | Pea gravel (3DCP limit for most systems) |
| `agg_size_7` | #7 | 1/2" - #4 | — |
| `agg_size_67` | #67 | 3/4" - #4 | Common structural |
| `agg_size_6` | #6 | 3/4" - 3/8" | — |
| `agg_size_57` | #57 | 1" - #4 | Most common US concrete aggregate |
| `agg_size_5` | #5 | 1" - 1/2" | — |
| `agg_size_467` | #467 | 1.5" - #4 | Common ready-mix |
| `agg_size_4` | #4 | 1.5" - 3/4" | — |
| `agg_size_357` | #357 | 2" - #4 | Crusher run |
| `agg_size_3` | #3 | 2" - 1" | — |
| `agg_size_2` | #2 | 2.5" - 1.5" | — |
| `agg_size_1` | #1 | 3.5" - 1.5" | Large stone |

A typical 3DCP mix is 55-65% sand by total mass with little or no coarse aggregate.

### Fibers -- The Reinforcement

Without formwork, printed concrete has no external confinement. Fibers provide ductility, crack control, and post-crack load carrying capacity. Open3DCP tracks eight fiber types by material, plus industry-standard fiber characterization:

| Column | Material | Typical Use in 3DCP |
|--------|----------|---------------------|
| `steel_fiber` | Hooked, crimped, or micro steel wire | High mechanical performance, but can clog nozzles. Typical 0.5-2% by volume. |
| `pp_fiber` | Polypropylene (monofilament or fibrillated) | Most common in 3DCP. Cheap, chemically inert, easy to pump. Typical 0.1-0.5%. |
| `pva_fiber` | Polyvinyl alcohol | High bond with cement matrix. Used in Engineered Cementitious Composites (ECC). |
| `glass_fiber` | Alkali-resistant glass | Good balance of strength and cost. Must be AR-coated to resist alkaline cement paste. |
| `basalt_fiber` | Basalt rock | Sustainable, good thermal resistance. Growing 3DCP interest. |
| `carbon_fiber` | Carbon | Highest tensile strength, highest cost. Rare in 3DCP. |

In addition to mass-%, three characterization columns capture how fiber is actually specified and ordered commercially: `fiber_length_mm`, `fiber_diameter_mm`, and `fiber_aspect_ratio` (L/d — the key performance parameter; e.g., Dramix 3D 65/35 means L/d=65, length=35 mm). `fiber_tensile_strength_mpa` records the supplier-specified fiber tensile strength.

### Admixtures -- The Tuning Knobs

Admixtures are chemicals added in small quantities (typically 0.1-2% by mass) to modify fresh-state behavior. In 3DCP, they control the narrow window between pumpability and shape retention.

**Important:** All admixture values in Open3DCP represent **solids content** by mass-%. Most commercial admixtures are sold as liquid solutions (typically 20-40% solids by weight). Convert using the manufacturer's technical data sheet — e.g., a PCE dosed at 1.0% liquid with 30% solids = 0.3% in this schema.

| Column | Function | Why It Matters |
|--------|----------|----------------|
| `superplasticizer` | High-range water reducer (HRWR). PCE-based polymers that disperse cement particles. ASTM C494 Type F/G. Record as solids content. | Allows the mix to flow through the pump at low water content. The most important admixture in 3DCP. |
| `water_reducer` | Mid-range water reducer. ASTM C494 Type A. | Less powerful than superplasticizer. These are chemically distinct products and should not be combined into a single column. |
| `accelerator` | Speeds up setting and early strength gain. ASTM C494 Type C/E. | Critical for 3DCP: each layer must support the next within minutes. Often sprayed at the nozzle tip. |
| `retarder` | Slows setting. ASTM C494 Type B/D. | Extends the open time (workable window) for long print jobs. |
| `air_entrainer` | Introduces stabilized microscopic air bubbles. ASTM C260. | Improves freeze-thaw resistance but reduces strength. Rarely used in structural 3DCP. |

Additional admixture columns include `vma` (viscosity-modifying admixture), `shrinkage_reducer`, `corrosion_inhibitor`, and specialized clay-based rheology modifiers (`hpmc`, `sepiolite_clay`, `attapulgite`, `calcium_bentonite`).

### Water

A single column: `water`, stored as mass-% of total wet mix. Despite its simplicity, water content is the single most influential variable in concrete performance, because it controls the water-to-binder ratio.

---

## Key Ratios

Three derived ratios capture the essential character of a mix more than any individual material percentage:

| Column | Formula | Why It Matters |
|--------|---------|----------------|
| `w_c_ratio` | water / cement only | The classic predictor from Abrams' law (1918): lower w/c = higher strength. Does not account for SCMs. |
| `w_b_ratio` | water / total binder | **The single most important predictor of compressive strength.** Accounts for all cementitious materials, not just Portland cement. A typical 3DCP mix has w/b between 0.30 and 0.45. |
| `a_b_ratio` | aggregate / total binder | Indicates paste volume. Lower a/b means more paste (binder + water), which generally improves pumpability but increases cost and shrinkage. |

---

## What We Measure

### Hardened Mechanical Properties

| Column | What It Is | Typical 3DCP Range | Standard |
|--------|------------|-------------------|----------|
| `compressive_strength_mpa` | The load at failure divided by the cross-sectional area, under uniaxial compression. | 20-120 MPa | ASTM C39 / EN 12390-3 |
| `tensile_strength_mpa` | Direct or splitting tensile strength. Roughly 8-12% of compressive. | 2-10 MPa | ASTM C496 |
| `flexural_strength_mpa` | Bending strength (modulus of rupture). Important for structural elements. | 3-15 MPa | ASTM C78 |
| `elastic_modulus_gpa` | Stiffness. How much the material deforms under load. | 15-45 GPa | ASTM C469 |
| `test_age_days` | Age at testing. 28 days is the industry standard per ACI 318. | 1-365 days | -- |

### Fresh-State Properties

3DCP demands more from fresh concrete than conventional construction. The mix must be simultaneously pumpable (fluid enough to flow) and buildable (stiff enough to hold shape). Open3DCP captures both:

- **Rheology:** `yield_stress_pa`, `plastic_viscosity_pa_s`, `thixotropy_pa_per_s` (structural buildup rate)
- **Workability:** `slump_mm`, `spread_mm`, `open_time_min`
- **Setting:** `setting_time_initial_min`, `setting_time_final_min`
- **Buildability:** `green_strength_kpa` (fresh concrete compressive strength)

### Durability Properties

Long-term performance under environmental exposure: chloride penetration, carbonation, freeze-thaw resistance, shrinkage, creep, sulfate attack, alkali-silica reaction, and more. See `Open3DCP_SCHEMA.md` for the full column reference.

---

## 3D Printing Process Parameters

What makes Open3DCP different from conventional concrete databases is first-class support for print process data. These columns are null for cast specimens and populated for printed specimens.

### Extrusion Geometry

| Column | Description | Why It Matters |
|--------|-------------|----------------|
| `nozzle_diameter_mm` | Exit diameter of the print nozzle | Constrains maximum aggregate size. Typical 10-40 mm. |
| `nozzle_shape` | Cross-section: circular, rectangular, or custom | Rectangular nozzles produce flatter layers with better interlayer contact. |
| `nozzle_area_mm2` | Calculated exit area | Used to derive volumetric flow rate from print speed. |
| `layer_height_mm` | Height of each deposited layer | Typical 5-15 mm. Thinner layers = better surface finish, more layers needed. |
| `layer_time_gap_s` | Seconds between successive layers at the same location | The cold joint indicator. Longer gaps allow surface drying, which weakens interlayer bond. |
| `print_speed_mm_s` | Nozzle travel speed | Affects layer geometry, surface quality, and production rate. |

### Why Direction Matters

Printed concrete is anisotropic: its properties depend on the direction of loading relative to the layer orientation.

- **`print_direction`** -- The path the nozzle follows (X, Y, or Z axis)
- **`test_orientation`** -- How the specimen was loaded in the testing machine:
  - `perpendicular` -- Load applied across layers (weakest direction, tests interlayer bond)
  - `parallel` -- Load applied along layers (strongest direction)
  - `diagonal` -- Load at 45 degrees to layers
  - `cast` -- Moulded specimen, no layer orientation

A printed concrete specimen tested perpendicular to its layers can be 20-40% weaker than the same material tested parallel. This is why `test_orientation` is a critical schema field, not just metadata.

---

## Provenance

Every record in Open3DCP should carry provenance metadata that traces it back to its source:

| Column | Purpose |
|--------|---------|
| `doi` | Digital Object Identifier for the source publication |
| `source_citation` | Full citation string for sources without a DOI (theses, conference papers, internal reports) |
| `measurement_confidence` | How the value was obtained: `measured`, `calculated`, `estimated`, or `reported` |
| `lab_name` | Laboratory that performed the tests (enables inter-laboratory comparison) |

Provenance matters because data quality directly determines model accuracy. A single miscoded material percentage (e.g., recording cement as 45% when the paper says 24%) can shift a model's predictions for every similar mix.

---

## Companion Tables

The main mix design table is supported by several reference tables. Implementers should adapt these to their needs:

| Table | Purpose |
|-------|---------|
| `sources` | Publication metadata: title, authors, DOI, year, license |
| `test_methods` | Controlled vocabulary of test standards (ASTM C39, EN 12390-3, RILEM 3DCP, etc.) |
| `curing_regimes` | Standard curing conditions (water 20C, moist room, steam, autoclave, etc.) |
| `standard_test_ages` | Reference ages from 1 hour (0.042 days) through 91 days |
| `strength_measurements` | Multi-age test data beyond the primary value in the main table |

---

## Getting Started

Open3DCP is designed to be database-agnostic. The canonical column definitions target PostgreSQL, but the flat structure works in any relational database, CSV export, or dataframe.

If you maintain a 3DCP mix design database, you can adopt the Open3DCP schema by creating tables matching the column definitions in `Open3DCP_SCHEMA.md`. Start with the columns relevant to your data -- you do not need to populate every column. The schema is designed so that null columns are simply ignored during analysis.

---

## References & Acknowledgments

Open3DCP is an agglomeration of the most applicable schema patterns for 3DCP mix design data, drawn from established standards bodies and open-access research:

### Schema Design Philosophy
- **NASA GRC ICME Schema** -- Hearley, B.L. and Arnold, S.M. (2023). "NASA GRC ICME Schema for Materials Data Management: An Executive Summary." NASA/TM-20230018337. Open3DCP follows the same FAIR data principles and Processing-Structure-Property-Performance pattern described in this work.
- **NIST** -- Materials Data Repository schema patterns and Materials Genome Initiative (MGI) guidelines
- **RILEM TC 304-ADC** -- Assessment of Additively Manufactured Concrete Materials and Structures (interlaboratory test protocols, orientation nomenclature)
- **ACI 318** -- Building Code Requirements for Structural Concrete (design age conventions, strength classifications)
- **Citrine Informatics** -- GEMD (Graphical Expression of Materials Data) data model concepts

### ASTM Test Standards Referenced in Column Definitions
- **ASTM C150** -- Portland Cement
- **ASTM C618** -- Fly Ash and Natural Pozzolans
- **ASTM C989** -- Slag Cement (GGBFS)
- **ASTM C1240** -- Silica Fume
- **ASTM C33** -- Concrete Aggregates (fineness modulus grading)
- **ASTM C494** -- Chemical Admixtures (Types A-G)
- **ASTM C260** -- Air-Entraining Admixtures
- **ASTM C39** -- Compressive Strength of Cylindrical Specimens
- **ASTM C496** -- Splitting Tensile Strength
- **ASTM C78** -- Flexural Strength (Third-Point Loading)
- **ASTM C469** -- Static Modulus of Elasticity
- **ASTM C191** -- Time of Setting (Vicat Needle)
- **ASTM C1611** -- Slump Flow of Self-Consolidating Concrete

### EN Standards
- **EN 197-1** -- Cement Composition and Classification
- **EN 12390-3/5/6** -- Hardened Concrete Testing (Compressive, Flexural, Tensile)
- **EN 206** -- Exposure Classifications

### Open-Access Data Sources
Schema design was informed by the structure and content of these CC BY-licensed datasets:
- Bos, F.P. et al. (2023). RILEM TC 304-ADC ILS-mech interlaboratory study dataset. CC BY 4.0.
- TU Eindhoven IBS 3DCP Dataset v1.1.0. 4TU.ResearchData. CC BY 4.0.
- Zenodo 3DCP Dataset v0.3. CC BY 4.0.
- UCI Machine Learning Repository -- Concrete Compressive Strength Dataset. CC BY 4.0.

### Technical Reference
- **Open3DCP_SCHEMA.md** -- Full column-by-column technical reference with types, units, and test method citations

---

## Disclaimers

This document references published standards from ASTM International, CEN (EN), ACI, RILEM, and other organizations for identification and context only. **Open3DCP is not a substitute for any referenced standard.** Users must obtain and comply with the full text of applicable standards through authorized channels. Standard designations are trademarks of their respective organizations; their use here does not imply endorsement or affiliation.

Open3DCP defines a data format, not a dataset, and makes no warranties regarding the accuracy or fitness for purpose of any data stored in this format. **This schema is not intended for structural design, construction specifications, or regulatory compliance.** Mix designs must be independently validated through laboratory testing by qualified professionals before use in construction. Nothing in this document constitutes engineering advice.

See `Open3DCP_SCHEMA.md` for full disclaimer language.

---

## License

Open3DCP is released under the **Apache License, Version 2.0** ([Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)).

You are free to use, adapt, and redistribute this schema for any purpose, including commercial use, provided you give appropriate credit to Sunnyday Technologies. The Apache 2.0 license includes an express grant of patent rights from contributors to users.

---

## Citation

If you use Open3DCP in your research, please cite:

```
Sunnyday Technologies (2026). Open3DCP: Open Data Standard for
3D Concrete Printing. https://github.com/sunnyday-technologies/Open3DCP
```

---

## Contributing

We welcome contributions from the 3DCP research community. If you have suggestions for schema improvements, new columns for emerging test methods, or corrections to existing descriptions, please open an issue or pull request.

Developed and maintained by [Sunnyday Technologies](https://sunn3d.com) | Wisconsin, USA
