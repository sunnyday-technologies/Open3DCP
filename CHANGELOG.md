# Changelog

All notable changes to the Open3DCP schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Schema versioning follows these rules:
- **Major** (1.0 -> 2.0): Breaking changes -- columns renamed, removed, or redefined in a way that existing datasets would need migration.
- **Minor** (1.0 -> 1.1): New columns added. Existing datasets remain compatible without changes.
- **Patch** (1.0.0 -> 1.0.1): Documentation corrections, description clarifications, or typo fixes. No schema changes.

---

## [1.6.0] - 2026-05-05

### SCM Per-Grade Taxonomy Split

Slag, metakaolin, and pumice are now captured by grade (or particle size, in pumice's case) so the schema records the actual SCM behavior the test specimen used. Generic `slag`, `metakaolin`, and `pumice` columns are preserved for backward compatibility — use them when the source paper does not state a grade.

### Added

**Slag grades (ASTM C989):**
- `slag_grade_80` — Grade 80 GGBS (Strength Index ≥ 75% at 28d). Lower reactivity, lower water demand.
- `slag_grade_100` — Grade 100 GGBS (Strength Index ≥ 95% at 28d). Most common commercial grade.
- `slag_grade_120` — Grade 120 GGBS (Strength Index ≥ 115% at 28d). Higher early strength, higher heat of hydration.

**Metakaolin reactivity grades (ASTM C618 Class N):**
- `metakaolin_high_purity` — High-Reactivity Metakaolin (HRM). Kaolinite >95%, Blaine ~15,000 m²/kg.
- `metakaolin_standard` — Standard Metakaolin (MRM). Kaolinite 75-90%, Blaine ~10,000 m²/kg.

**Pumice by particle size:**
- `pumice_powder` — SCM-grade pumice <75 μm (binder-section column).
- `pumice_sand` — Lightweight fine-aggregate pumice 75-600 μm (aggregate-section column).
- `pumice_coarse` — Lightweight coarse-aggregate pumice 600 μm - 9.5 mm.

### Notes

- Generic `slag`, `metakaolin`, `pumice` columns remain valid for legacy data and for sources that do not state a grade.
- Total schema size: 247 columns across 10 domains.

---

## [1.5.0] - 2026-04-16

### Pigment Columns

Pigments are ultra-fine particles (~1 um) used at 1-5% in architectural 3DCP with significant impact on particle packing, water demand, and microstructure. At typical dosages they interact strongly with silica fume and metakaolin due to comparable surface area/energy effects.

### Added
- `iron_oxide_pigment` -- Fe2O3 (red), FeOOH (yellow), Fe3O4 (black). Most common concrete pigment.
- `titanium_dioxide_pigment` -- TiO2 white pigment. Also used for photocatalytic self-cleaning surfaces.
- `chromium_oxide_pigment` -- Cr2O3 green pigment.
- `carbon_black_pigment` -- Carbon black (distinct from coal bottom ash or fly ash).
- `pigment_other` -- Other/unspecified pigment type.

### Notes
- Total schema size: 239 columns across 10 domains.
- Future CEMFORGE algorithm update needed to model pigment surface area interactions with SCMs (silica fume, metakaolin) — tracked separately.

---

## [1.4.0] - 2026-04-16

### Alkali-Activated Materials (AAM) + Additional 3DCP Modifiers

Open3DCP now supports alkali-activated systems (geopolymer, AAS) and additional materials commonly used in 3DCP research.

### Added
- `sodium_hydroxide` -- NaOH activator (mass-%, purity-adjusted solids).
- `sodium_silicate` -- Na2SiO3 waterglass (mass-%, as-delivered liquid).
- `potassium_hydroxide` -- KOH activator.
- `potassium_silicate` -- K2SiO3 activator.
- `activator_ms_ratio` -- SiO2/Na2O molar modulus of activator solution.
- `na2o_dosage_pct` -- Na2O as % of binder (standard AAM reporting convention).
- `nano_clay` -- Nanoclay / montmorillonite (rheology modifier for AAM and OPC 3DCP).
- `mineral_powder` -- Generic mineral powder / filler (common in Chinese 3DCP literature).
- `mwcnt` -- Multi-walled carbon nanotubes.
- `graphene_oxide` -- Graphene oxide / reduced graphene oxide.
- `rice_husk_ash` -- Rice husk ash pozzolan.
- `recycled_sand` -- Recycled concrete aggregate sand.

### Notes
- AAM rows stored with `is_training_ready = false` until specimen count supports ML prediction (100+ minimum).
- Total schema size: 234 columns across 10 domains.

---

## [1.3.0] - 2026-04-16

### Added
- `cellulose_fiber` -- Natural cellulose fiber mass-% per ASTM D7357.
- `sorptivity_secondary_mm_sqrt_s` -- ASTM C1585 secondary sorptivity rate (day 1-7). Same test specimen and setup as initial rate — zero additional lab cost. Useful for characterizing interlayer zone moisture transport in 3DCP.

### Removed (proposed in earlier draft, not shipped)
- `interbead_shear_strength_mpa` -- Redundant with `interlayer_shear_mpa` + `test_orientation_code`. Bead-to-bead shear is simply a transverse test direction, already representable in the schema.
- `flame_spread_index`, `smoke_developed_index` -- ASTM E84 / UL 723 apply to surface finishes and coatings, not to concrete itself. Concrete is non-combustible; these columns would be NULL or trivially zero for every 3DCP record.

### Changed
- `sql/create_tables.sql` updated from v1.0 to v1.3 (was 2 versions behind the docs).

### Notes
- Total schema size: 222 columns across 10 domains.

---

## [1.2.0] - 2026-04-15

### Durability & Transport

### Added
- 11 durability/transport columns: `water_absorption_pct`, `rcpt_coulombs`, `bulk_resistivity_kohm_cm`, `freeze_thaw_cycles`, `durability_factor_pct`, `drying_shrinkage_microstrain`, `autogenous_shrinkage_microstrain`, `carbonation_depth_mm`, `air_content_fresh_pct`, `interlayer_bond_strength_mpa`, `durability_test_age_days`.

---

## [1.1.0] - 2026-04-15

### Cement Type Expansion & Fiber/Admixture Coverage

### Added
- `cement_type_2`, `cement_type_3`, `cement_type_4` -- ASTM C150 Types II, III, IV.
- `pe_fiber` -- Polyethylene (UHMWPE) fiber, distinct from PP fiber.
- `hpmc` -- Hydroxypropyl methylcellulose (cellulose ether VMA).
- `vma` -- Generic viscosity-modifying admixture.
- `shrinkage_reducer` -- Shrinkage-reducing admixture (SRA).
- 150+ material aliases seeded for fiber types, admixtures, and sand grades.

---

## [1.0.0] - 2026-03-23

### Initial Release

**10 schema domains, 175+ columns across the following collections:**

- **Composition** (40 columns) -- Binders, aggregates, fibers, admixtures, rheology modifiers, water
- **Process** (32 columns) -- 3DCP extrusion, pumping, mixing, print geometry
- **Mechanical** (16 columns) -- Compressive, tensile, flexural, elastic modulus, bond, fracture, impact, fatigue
- **Fresh State** (20 columns) -- Rheology, workability, setting time, buildability
- **Durability** (28 columns) -- Chloride, carbonation, shrinkage, creep, freeze-thaw, sulfate, ASR, permeability
- **Environment** (14 columns) -- Thermal properties, embodied carbon, exposure classification
- **Specimen** (5 columns) -- Geometry, dimensions, extraction method
- **Interlayer** (7 columns) -- Bond, shear, void fraction, surface condition
- **Microstructure** (3 columns) -- Hydration degree, Ca(OH)2, pore size
- **Provenance** (8 columns) -- DOI, citation, confidence, quality flags

**Standards alignment:** ASTM C150, C618, C989, C1240, C33, C494, C260, C39, C78, C496, C469, C191, C1611; EN 197-1, EN 12390, EN 206; RILEM TC 304-ADC; NIST MGI.

**Design principles:** Flat schema, mass-percent basis, 3DCP-native process columns, multi-age strength support.

**Companion tables:** `strength_measurements`, `sources`, `test_methods`, `curing_regimes`.

**Reference SQL implementation:** `sql/create_tables.sql` (PostgreSQL).
