# Changelog

All notable changes to the Open3DCP schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Schema versioning follows these rules:
- **Major** (1.0 -> 2.0): Breaking changes -- columns renamed, removed, or redefined in a way that existing datasets would need migration.
- **Minor** (1.0 -> 1.1): New columns added. Existing datasets remain compatible without changes.
- **Patch** (1.0.0 -> 1.0.1): Documentation corrections, description clarifications, or typo fixes. No schema changes.

---

## [1.7.0] - 2026-06-04

Additive, backward-compatible changes. Existing v1.6 datasets remain valid unchanged.

### Added — classification & batch timeline
- `material_class` -- mix/binder system classification (`OPC` | `blended_OPC` | `AAM` | `CAC` |
  `CSA` | `UHPC` | `mortar` | `paste` | `concrete`). A primary classification, not free metadata;
  it also lets the ingestor route by chemistry (e.g. an AAM row expects activators, water ≈ 0).
- `batch_label` -- physical batch sub-identifier within a mix design (provenance; distinguishes
  repeat batches of one formulation). Not a foreign key.
- `date_of_casting` -- casting/pour date = t=0 of the curing clock; with the test date the
  ingestor can derive `test_age_days`. Distinct from `created_at` (record creation).

### Changed — intelligent ingestion (relational sources)
- The ingestor now maps `material_class` / `date_of_casting` / `batch_label` (was: triage
  sidecar) and routes `data` records by their `data_type`: scalar → property column, curve/image
  → the matching `*_file` column, and a curve's axis-unit descriptor (e.g. `data.strain.units`)
  → `provenance_notes`. The wet-mass denominator now includes admixtures/SCMs (was: binder +
  water + aggregate only, which biased mass-% and over-reported "exact"). Consumed
  selector/metadata fields (pivot keys, `data_type`, carried descriptors) are excluded from the
  fidelity coverage denominator, like foreign keys.
- A committed, reproducible relational fixture (`tools/ingest/tests/fixtures/`) now anchors the
  relational ingestion example: 83.1 (B) → **97.4 (A)** after the above; UCI stays 96.7 (A).

### Added — aggregate conditioning (water accounting)
- `aggregate_moisture_state` -- as-batched aggregate condition: `oven_dry` | `air_dry` | `SSD` | `wet`.
- `aggregate_absorption_pct` -- 24-h aggregate absorption, % of oven-dry mass (ASTM C127/C128).
- `aggregate_moisture_content_pct` -- total as-batched aggregate moisture, % of oven-dry mass (ASTM C566).
  Free moisture = `aggregate_moisture_content_pct` − `aggregate_absorption_pct`, so the effective
  (free) mix water is recoverable when aggregates are batched off the SSD reference. The SSD-basis
  `water` column plus these three make water accounting unambiguous without duplicating w/c, w/b.
- `aggregate_prewetted` -- process flag for pre-wetting aggregate to a damp condition before
  batching (a common 3DCP practice).

### Fixed — ingestion fidelity & crosswalk
- Fidelity `field_coverage` no longer penalizes relational foreign keys / identifiers (a flat row
  carries none); they are excluded from the coverage denominator and still preserved in the
  triage sidecar. As of this release, consumed selector/metadata fields are likewise excluded.
- Crosswalk test-method map completed (e.g. `four_point_bending` -> `ASTM_C78`), so standard test
  methods canonicalize instead of passing through unmapped.
- Fixed a crosswalk enum bug: unquoted YAML `yes`/`no` keys were parsed as booleans, so
  `is_3d_printed` mapping never matched the source string `"yes"`; keys are now quoted. Curing
  codes adopted verbatim are recorded as an exact identity copy (no longer flagged as an
  assumption), so `value_fidelity` reflects only genuine conversions.

### Fixed — unit converter (ingestion tool)
- Added imperial-tonnage factors: `lb_yd3` (US batch-ticket concentration unit), US `short_ton`,
  UK `long_ton`, plus explicit `metric_ton`/`tonne`; a bare "ton"/"t" is now rejected as
  ambiguous (short vs long ton differ by ~12%).

### Notes
- Ingestion-tool MAJOR.MINOR bumped to 1.7 to track the schema (`TARGET_SCHEMA_VERSION`).
- Canonical column list remains `Open3DCP_SCHEMA.md` / `sql/create_tables.sql`.

## [1.6.0] - 2026-06-03

### Interoperability — basis, uncertainty, raw-data references

Additive, backward-compatible changes that align Open3DCP with relational concrete databases
and raise ingestion fidelity. Existing v1.5 datasets remain valid unchanged.

### Changed
- **kg/m³ is now the primary reporting basis** (industry/field standard). mass-% of total wet
  mix is retained as a derived secondary representation. No existing column was renamed or
  redefined; the change is one of stated convention plus the new basis columns below.

### Added — mix basis (lossless conversion)
- `original_basis` -- basis the source reported: `kg_m3` (primary) | `mass_pct` | `volume` | `lb_yd3`.
- `mix_density_kg_m3` -- total fresh wet-mix density; enables exact mass-% ↔ kg/m³ conversion.
- `total_binder_kg_m3` -- total cementitious content (kg/m³).

### Added — per-measurement uncertainty (mirrors mean + std-dev + N)
- `compressive_strength_stddev_mpa`, `flexural_strength_stddev_mpa`,
  `tensile_strength_stddev_mpa`, `elastic_modulus_stddev_gpa`, `interlayer_bond_stddev_mpa`.

### Added — raw-data references (FAIR; payloads stay external)
- `raw_data_doi`, `stress_strain_file`, `rheology_curve_file`, `microstructure_image`, `raw_data_file`.

### Notes
- Canonical column list remains `Open3DCP_SCHEMA.md` / `sql/create_tables.sql`.
- Crosswalk updated so the source `data` std-dev and file references map to columns instead of
  the ingestion triage sidecar; `original_basis`/`mix_density_kg_m3`/`total_binder_kg_m3` are
  populated by the ingestion tool from the source batch.

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
- Canonical column list is maintained in `Open3DCP_SCHEMA.md`.
- Modeling pigment/SCM (silica fume, metakaolin) surface-area interactions is out of scope for the schema and is tracked separately.

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
- Canonical column list is maintained in `Open3DCP_SCHEMA.md`.

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
- Canonical column list is maintained in `Open3DCP_SCHEMA.md`.

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
- Expanded fiber synonym and characterization coverage.
- `hpmc` -- Hydroxypropyl methylcellulose (cellulose ether VMA).
- `vma` -- Generic viscosity-modifying admixture.
- `shrinkage_reducer` -- Shrinkage-reducing admixture (SRA).
- Expanded recognized material synonyms for fiber types, admixtures, and sand grades.

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
