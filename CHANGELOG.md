# Changelog

All notable changes to the Open3DCP schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Schema versioning follows these rules:
- **Major** (1.0 -> 2.0): Breaking changes -- columns renamed, removed, or redefined in a way that existing datasets would need migration.
- **Minor** (1.0 -> 1.1): New columns added. Existing datasets remain compatible without changes.
- **Patch** (1.0.0 -> 1.0.1): Documentation corrections, description clarifications, or typo fixes. No schema changes.

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
