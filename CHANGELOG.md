# Changelog

All notable changes to the Open3DCP schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Schema versioning follows these rules:
- **Major** (1.0 -> 2.0): Breaking changes -- columns renamed, removed, or redefined in a way that existing datasets would need migration.
- **Minor** (1.0 -> 1.1): New columns added. Existing datasets remain compatible without changes.
- **Patch** (1.0.0 -> 1.0.1): Documentation corrections, description clarifications, or typo fixes. No schema changes.

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
