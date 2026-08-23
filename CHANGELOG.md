# Changelog

All notable changes to the Open3DCP schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Schema versioning follows these rules:
- **Major** (1.0 -> 2.0): Breaking changes -- columns renamed, removed, or redefined in a way that existing datasets would need migration.
- **Minor** (1.0 -> 1.1): New columns added. Existing datasets remain compatible without changes.
- **Patch** (1.0.0 -> 1.0.1): Documentation corrections, description clarifications, or typo fixes. No schema changes.

---

## [1.8.0] - 2026-08-23 — record the market, not just the lab

Additive, backward-compatible. Proposed in large part by David Scheidt (Chair of Concrete
Structures, TU Munich) and Daniel Auer ([#1](https://github.com/sunnyday-technologies/Open3DCP/issues/1)),
whose report first flagged the missing reproducibility fields. Two of the three gaps stem from the
schema being shaped around US practice, one from its being shaped around research mixes batched from
individual constituents. All three cut against v1.7.5's own principle: the schema offered no way to
record what the user actually knows. Column count: 248 → **295**.

### Added — Commercial Product Identity (premixed materials)
A proprietary premix's composition is *unknowable*, not unreported: the manufacturer does not
disclose it. What fully determines reproducibility — the product, the supplier lot, and the water
added — now records first-class, so a reproducible premix print is a complete row, not a nearly
empty one. Constituent columns stay NULL (unknown), never 0.
- `is_premixed`, `supplier`, `product_name`, `supplier_batch_number` (distinct from `batch_label`,
  which remains the user's own repeat-batch sub-identifier), `production_date`, `bulk_density_kg_m3`
- `premix_composition_disclosed` — whether the constituent breakdown is published at all
- `premix_water_addition_pct` — water per 100 kg dry premix, the manufacturer/TDS dosing basis
  (not derivable from `water` once anything else is batched alongside the premix)

### Added — EN 197-1 / EN 197-5 cements and hydraulic-cement completeness
Ends the forced choice between silently equating CEM I with ASTM Type I and losing the real
designation to `provenance_notes`. The goal is that *any* hydraulic cement records losslessly:
typed mass columns for the main-line notations, plus exact-designation carriers for everything.
- EN 197-1: `cem_i`, `cem_ii_a_s`, `cem_ii_b_s`, `cem_ii_a_v`, `cem_ii_b_v`, `cem_ii_a_l`,
  `cem_ii_b_l`, `cem_ii_a_ll`, `cem_ii_b_ll`, `cem_ii_a_m`, `cem_ii_b_m`, `cem_iii_a`, `cem_iii_b`,
  `cem_iii_c`, `cem_iv_a`, `cem_iv_b`, `cem_v_a`, `cem_v_b`
- EN 197-5 low-clinker: `cem_ii_c_m`, `cem_vi`
- ASTM C595 completion: `cement_type_1s` (IS), `cement_type_1p` (IP), `cement_type_1t` (IT);
  `cement_type_1l` is now documented as ASTM C595 IL only (pre-v1.8 rows may carry CEM II/A-L there
  via the former dual mapping)
- ASTM C1157 performance-spec hydraulic cement: `cement_c1157` (class in `cement_designation`)
- CSA-ternary support: `calcium_sulfate` (gypsum / hemihydrate / anhydrite for ettringite control)
- Lime binders: `natural_hydraulic_lime` (EN 459-1 NHL), `hydrated_lime` (ASTM C207 / EN 459-1 CL)
- `cement_other` — a *stated* type with no dedicated column (GB 175, rare EN notations, natural
  cement): mass exact, designation preserved. Distinct from `cement_unspecified` (type unknown).
- `cement_designation` (exact string as printed), `cement_standard` (designation system),
  `cement_strength_class_mpa` (32.5 | 42.5 | 52.5, numeric for ML), `cement_early_strength_class`
  (L | N | R — 42.5 R vs 42.5 N changes open time and structuration outright)

### Added — EN 12620 d/D grading fallback beneath fineness modulus
FM stays the primary analysable index (white paper §5.6); d/D preserves the weaker statement
exactly where that is all the source made — European suppliers designate sand by size fraction and
FM cannot be derived from d/D alone.
- `fine_agg_fineness_modulus` — the measured FM value itself (the FM bins are its classification
  projection; previously only the bins existed)
- `agg_fraction_d_lower_mm`, `agg_fraction_d_upper_mm`, `agg_grading_designation` (designation
  verbatim, incl. DIN 1045-2 grading regions)
- `sieve_analysis_file` — full grading-curve file reference (ASTM C136 / EN 933-1)

### Added — raw-data integrity
- `raw_data_sha256`, `raw_data_version` — integrity pin and deposit version for referenced raw
  data (the model crosswalks already carried these as forward-compat keys)

### Changed
- The `x_` column prefix is officially reserved for site-specific extension columns: no canonical
  column will ever use it, so migrating an extension to an official column is a rename.
- Ingestion crosswalk: EN 197-1/-5 vocabulary members now map to their own `cem_*` columns instead
  of approximating to ASTM columns or dropping to the sidecar; ASTM C1157 members map to
  `cement_c1157` (previously approximated to `cement_type_1`); C595 IS/IP/IT and GB 175 members
  now have homes (`cement_type_1s/1p/1t`, `cement_other`).

---

## [1.7.5] - 2026-06-10 — preserve, don't presume

Additive, backward-compatible. Driven directly by the re-architected ingestion-fidelity metric: when it
began counting assumptions honestly, nearly every penalty on clean public datasets traced to the SAME
failure mode — the schema forcing a classification or basis decision the source never made (a cement
type defaulted, an aggregate gradation bucket guessed, an admixture solids fraction assumed). v1.7.5
removes the need to guess: record exactly what the source stated; leave what it did not state NULL.
Column count: 244 → **248**.

### Added — unspecified-constituent columns (the generic-`fly_ash` pattern, completed)
- `cement_unspecified` — cement whose ASTM/EN type the source does not state. The mass is stored
  exactly; the type stays NULL. Refine to `cement_type_*` only when the source states the type.
- `fine_agg_unspecified` — fine aggregate with no stated fineness modulus / grading (the FM bucket
  columns are used only when the source states FM).
- `coarse_agg_unspecified` — coarse aggregate with no stated maximum size / ASTM C33 size number.
- `admixture_basis` (`solids` | `as_delivered`) — records the basis of the admixture columns for the
  row. Sources rarely state a solids fraction; storing the as-delivered mass WITH this flag preserves
  the source exactly, and solids remain derivable when the fraction is known.

### Changed — ingestion tool (no more schema-induced assumptions)
- The flat/UCI readers no longer default an unstated cement type to ASTM C150 Type I; unclassified
  constituents map to the `*_unspecified` columns with fidelity **exact** (nothing assumed).
- `as_delivered_to_solids_pct` records the as-delivered mass exactly and sets `admixture_basis`
  instead of flagging an assumed solids fraction (conversion happens only when a fraction is stated).
- The fidelity report adds an informational "recorded generically" section listing constituents stored
  without a classification — visible NULLs instead of fabricated certainty.
- Crosswalks updated accordingly; the genuine-assumption paths (volume doses, unknown batch mass,
  unstated units, enum misses) are still penalized exactly as before.



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
  relational ingestion example: 83.1 (B) → **97.4 (A)** after the above; UCI **98.8 (A)** (corrected tool).

### Added — aggregate conditioning (water accounting)
- `aggregate_moisture_state` -- as-batched aggregate condition: `oven_dry` | `air_dry` | `SSD` | `wet`.
- `aggregate_absorption_pct` -- 24-h aggregate absorption, % of oven-dry mass (ASTM C127/C128).
- `aggregate_moisture_content_pct` -- total as-batched aggregate moisture, % of oven-dry mass (ASTM C566).
  Free moisture = `aggregate_moisture_content_pct` − `aggregate_absorption_pct`, so the effective
  (free) mix water is recoverable when aggregates are batched off the SSD reference. The SSD-basis
  `water` column plus these three make water accounting unambiguous without duplicating w/c, w/b.
- `aggregate_prewetted` -- process flag for pre-wetting aggregate to a damp condition before
  batching (a common 3DCP practice).

### Added — interoperability: basis, uncertainty, raw-data references
- **Dual basis with kg/m³ first-class** (industry/field standard): the constituent columns store mass-%
  of total wet mix (the self-normalizing projection); the source's kg/m³ is preserved exactly via the
  bridge columns below. No existing column was renamed or redefined.
- Mix basis (lossless conversion): `original_basis` (`kg_m3` | `mass_pct` | `volume` | `lb_yd3`),
  `total_batched_mass_kg_m3` (sum of as-batched constituent masses per m³ — the mass-% ↔ kg/m³ bridge denominator, not a measured density), `total_binder_kg_m3` (total cementitious kg/m³).
- Per-measurement uncertainty (mean + std-dev + N): `compressive_strength_stddev_mpa`,
  `flexural_strength_stddev_mpa`, `tensile_strength_stddev_mpa`, `elastic_modulus_stddev_gpa`,
  `interlayer_bond_stddev_mpa`.
- Raw-data references (FAIR; payloads stay external): `raw_data_doi`, `stress_strain_file`,
  `rheology_curve_file`, `microstructure_image`, `raw_data_file`.

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

## [1.6.5] - 2026-06-05 — SCM taxonomy consolidation

Consolidation of the v1.6.0 per-grade SCM split, folded into the 1.7.0 release (**no separate git
tag**). The fine-grained per-grade/per-form columns added in 1.6.0 fragmented a sparse vocabulary
without analytical benefit and were reverted to the generic binder columns; grade/purity is now
recorded in `provenance_notes` instead.

### Removed
- `slag_grade_80`, `slag_grade_100`, `slag_grade_120` — reverted to generic `slag` (ASTM C989 grade in notes).
- `metakaolin_high_purity`, `metakaolin_standard` — reverted to generic `metakaolin`.
- `pumice_coarse`, `pumice_powder`, `pumice_sand` — reverted to generic `pumice`.

### Notes
- Net count returned to the v1.5 level (224) before the 1.7.0 additions. This episode is why the
  git-tag snapshots read **v1.5 = 224 → v1.6 = 232 → v1.7 = 244** with no intermediate tag — the 232
  reflects the grade split, which was consolidated away before the 1.7.0 feature columns landed.
- **Semver note:** removing columns would normally imply a major bump (see the versioning rules at the
  top of this file). This consolidation is treated as an in-train correction rather than a breaking
  change because the reverted columns shipped only in the interim `V1.6.0` tag, were never part of a
  stable public release, and were superseded within the same release train before `1.7.0`. No dataset
  built against the v1.5 or v1.7 public schema is affected.

---

## [1.6.0] - 2026-05-05 — SCM per-grade taxonomy split (experimental, superseded)

An experimental refinement that split three supplementary cementitious materials into per-grade /
per-form columns (+8). Tagged V1.6.0; **superseded and removed in the consolidation above (1.6.5)**
before the 1.7.0 feature work. Recorded here so the version history matches the git tags rather than
papering over the episode.

### Added
- `slag_grade_80`, `slag_grade_100`, `slag_grade_120` — GGBFS by ASTM C989 activity grade.
- `metakaolin_high_purity`, `metakaolin_standard` — metakaolin by reactivity/purity.
- `pumice_coarse`, `pumice_powder`, `pumice_sand` — pumice by particle form.

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

Open3DCP added columns for alkali-activated systems and additional materials commonly used in 3DCP research. **Scope note (see whitepaper §2 and `examples/README.md`):** the project's *curation* scope is hydraulic cementitious systems, including high-calcium alkali-activated slag (AAS, whose C-(A-)S-H gel is continuous with Portland hydrates); low-calcium fly-ash **geopolymers** (N-A-S-H gel) are a distinct binder chemistry and are out of scope. These activator columns exist to record the in-scope high-Ca AAS systems, not to characterize geopolymers.

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
