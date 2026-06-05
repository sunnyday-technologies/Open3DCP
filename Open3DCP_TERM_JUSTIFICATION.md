# Open3DCP — Term Justification (Appendix)

> **Auto-generated** by `tools/term_justification/generate.py` from the canonical column
> list in [`sql/create_tables.sql`](sql/create_tables.sql). Do not edit by hand — edit the
> schema/crosswalk and regenerate. This appendix justifies every Open3DCP term and unit
> for downstream interoperability and reuse.

## How terms were chosen

Each column uses the **most frequently used term** for its quantity, determined by
compiling the corpus of 3D-printable-cement literature and datasets; alternate spellings
normalize to that canonical term. Per term, the table gives its governing standard and —
where one exists — its relational-schema crosswalk. 3DCP-only terms are justified against
RILEM TC 276-DFC / TC 304-ADC.

**Coverage:** 241 canonical `mix_designs` terms, grouped into 25 sections.

---

## Identity & Versioning

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `mix_id` | varchar(50) | Unique human-readable identifier | — | Open3DCP-specific. |
| `name` | varchar(200) | Descriptive name | — | Open3DCP-specific. |
| `parent_mix_id` | varchar(50) | Links to parent formulation if this is a variant or iteration | — | Open3DCP-specific. |
| `version` | varchar(20) | Formulation version string | — | Open3DCP-specific. |
| `created_at` | timestamptz | Record creation timestamp | — | Open3DCP-specific. |

## Binder Materials

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `cement_type_1` | real | General purpose Portland cement | ASTM C150 Type I | Relational: `material_batches.cement_content_kg_m3` (by `material_batches.cement_type`=ASTM_C150_Type_I) |
| `cement_type_1_2` | real | General purpose / moderate sulfate resistance (most commonly sold cement in the US) | ASTM C150 Type I/II | Open3DCP-specific. |
| `cement_type_1l` | real | Portland-limestone cement (6-20% limestone) | ASTM C595 / EN 197-1 CEM II/A-L | Relational: `material_batches.cement_content_kg_m3` (by `material_batches.cement_type`=ASTM_C595_Type_IL) |
| `cement_type_2` | real | Moderate sulfate resistance, moderate heat of hydration | ASTM C150 Type II | Relational: `material_batches.cement_content_kg_m3` (by `material_batches.cement_type`=ASTM_C150_Type_II) |
| `cement_type_3` | real | High early strength / rapid hardening | ASTM C150 Type III | Relational: `material_batches.cement_content_kg_m3` (by `material_batches.cement_type`=ASTM_C150_Type_III) |
| `cement_type_4` | real | Low heat of hydration (rarely manufactured) | ASTM C150 Type IV | Relational: `material_batches.cement_content_kg_m3` (by `material_batches.cement_type`=ASTM_C150_Type_IV) |
| `cement_type_5` | real | High sulfate resistance (required in sulfate-rich soils, common in western US) | ASTM C150 Type V | Relational: `material_batches.cement_content_kg_m3` (by `material_batches.cement_type`=ASTM_C150_Type_V) |
| `cac` | real | Calcium aluminate cement (Ciment Fondu) | EN 14647 | Open3DCP-specific. |
| `csa_cement` | real | Calcium sulfoaluminate cement | — | Open3DCP-specific. |
| `fly_ash` | real | Fly ash (class not specified in source) | — | Relational: `material_batches.fly_ash_content_kg_m3` |
| `fly_ash_type_f` | real | Class F fly ash (SiO2+Al2O3+Fe2O3 ≥ 70%) | ASTM C618 | Relational: `material_batches.fly_ash_content_kg_m3` (+ `material_batches.fly_ash_class`) |
| `fly_ash_type_c` | real | Class C fly ash (SiO2+Al2O3+Fe2O3 ≥ 50%) | ASTM C618 | Relational: `material_batches.fly_ash_content_kg_m3` (+ `material_batches.fly_ash_class`) |
| `silica_fume` | real | Silica fume / microsilica | ASTM C1240 | Relational: `material_batches.silica_fume_content_kg_m3` |
| `nano_silica` | real | Nano-SiO2 (colloidal or fumed, <100 nm) | — | Open3DCP-specific. |
| `slag` | real | GGBS, grade not specified in source | ASTM C989 | Relational: `material_batches.slag_content_kg_m3` |
| `metakaolin` | real | Calcined kaolin clay, reactivity grade not specified in source | ASTM C618 Class N | Open3DCP-specific. |
| `limestone` | real | Limestone filler / calcium carbonate | EN 12620 | Open3DCP-specific. |
| `pumice` | real | Natural pozzolan (pumice), grade not specified in source | ASTM C618 Class N | Open3DCP-specific. |
| `bottom_ash` | real | Coal bottom ash | — | Open3DCP-specific. |
| `rice_husk_ash` | real | Rice husk ash (pozzolan) | — | Open3DCP-specific. |

## Alkali Activators

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `sodium_hydroxide` | real | NaOH (mass-%, purity-adjusted solids) | — | Open3DCP-specific. |
| `sodium_silicate` | real | Sodium silicate solution / waterglass (mass-%, as-delivered liquid) | — | Open3DCP-specific. |
| `potassium_hydroxide` | real | KOH (mass-%, purity-adjusted solids) | — | Open3DCP-specific. |
| `potassium_silicate` | real | Potassium silicate solution (mass-%, as-delivered liquid) | — | Open3DCP-specific. |
| `activator_ms_ratio` | real | SiO2/Na2O molar modulus of the activator solution | — | Open3DCP-specific. |
| `na2o_dosage_pct` | real | Na2O as % of binder mass (common AAM reporting convention) | — | Open3DCP-specific. |

## Additional Modifiers

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `nano_clay` | real | Nano clay / montmorillonite / nanoclay (rheology modifier for AAM and OPC 3DCP) | — | Open3DCP-specific. |
| `mineral_powder` | real | Generic mineral powder / filler (common in Chinese 3DCP literature) | — | Open3DCP-specific. |
| `mwcnt` | real | Multi-walled carbon nanotubes | — | Open3DCP-specific. |
| `graphene_oxide` | real | Graphene oxide / reduced graphene oxide (rGO) | — | Open3DCP-specific. |
| `recycled_sand` | real | Recycled concrete aggregate sand | — | Open3DCP-specific. |

## Pigments

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `iron_oxide_pigment` | real | Iron oxide pigment — red (Fe2O3), yellow (FeOOH), black (Fe3O4), or brown blends. Most common concrete pigment. | — | Open3DCP-specific. |
| `titanium_dioxide_pigment` | real | TiO2 white pigment. Also used for photocatalytic self-cleaning surfaces. | — | Open3DCP-specific. |
| `chromium_oxide_pigment` | real | Cr2O3 green pigment | — | Open3DCP-specific. |
| `carbon_black_pigment` | real | Carbon black pigment (distinct from coal bottom ash or fly ash) | — | Open3DCP-specific. |
| `pigment_other` | real | Other/unspecified pigment (record type in `provenance_notes`) | — | Open3DCP-specific. |

## Aggregate Materials

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `mason_sand` | real | Very fine sand, high fines content | — | Open3DCP-specific. |
| `fine_sand` | real | Fine concrete sand | — | Open3DCP-specific. |
| `concrete_sand` | real | Standard concrete sand (most common in US 3DCP) | — | Relational: `material_batches.fine_aggregate_content_kg_m3` |
| `coarse_sand` | real | Coarse washed sand | — | Open3DCP-specific. |
| `agg_size_89` | real | Very fine gravel (3/8" - #16 sieve, 9.5-1.18 mm) | ASTM C33 Size #89 | Open3DCP-specific. |
| `agg_size_8` | real | Fine pea gravel (3/8" - #8 sieve, 9.5-2.36 mm) | ASTM C33 Size #8 | Open3DCP-specific. |
| `agg_size_7` | real | 1/2" - #4 (12.5-4.75 mm) | ASTM C33 Size #7 | Open3DCP-specific. |
| `agg_size_67` | real | 3/4" - #4 (19-4.75 mm) | ASTM C33 Size #67 | Open3DCP-specific. |
| `agg_size_6` | real | 3/4" - 3/8" (19-9.5 mm) | ASTM C33 Size #6 | Open3DCP-specific. |
| `agg_size_57` | real | 1" - #4 (25-4.75 mm) | ASTM C33 Size #57 | Relational: `material_batches.coarse_aggregate_content_kg_m3` |
| `agg_size_5` | real | 1" - 1/2" (25-12.5 mm) | ASTM C33 Size #5 | Open3DCP-specific. |
| `agg_size_467` | real | 1.5" - #4 (37.5-4.75 mm) | ASTM C33 Size #467 | Open3DCP-specific. |
| `agg_size_4` | real | 1.5" - 3/4" (37.5-19 mm) | ASTM C33 Size #4 | Open3DCP-specific. |
| `agg_size_357` | real | 2" - #4 (50-4.75 mm) | ASTM C33 Size #357 | Open3DCP-specific. |
| `agg_size_3` | real | 2" - 1" (50-25 mm) | ASTM C33 Size #3 | Open3DCP-specific. |
| `agg_size_2` | real | 2.5" - 1.5" (63-37.5 mm) | ASTM C33 Size #2 | Open3DCP-specific. |
| `agg_size_1` | real | 3.5" - 1.5" (90-37.5 mm) | ASTM C33 Size #1 | Open3DCP-specific. |

## Fiber Reinforcement

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `steel_fiber` | real | Steel fiber (hooked, crimped, or micro) | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=steel_hooked) |
| `pp_fiber` | real | Polypropylene fiber | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=polypropylene_macro) |
| `glass_fiber` | real | Alkali-resistant glass fiber | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=glass) |
| `carbon_fiber` | real | Carbon fiber | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=carbon) |
| `pva_fiber` | real | Polyvinyl alcohol fiber | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=polyvinyl_alcohol) |
| `basalt_fiber` | real | Basalt fiber | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=basalt) |
| `nylon_fiber` | real | Nylon fiber | — | Open3DCP-specific. |
| `aramid_fiber` | real | Aramid fiber (Kevlar) | — | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=aramid) |
| `cellulose_fiber` | real | Natural cellulose fiber per ASTM D7357 | ASTM D7357 | Relational: `material_batches.fiber_volume_fraction` (by `material_batches.fiber_type`=natural) |
| `fiber_length_mm` | real | Fiber length (mm). Industry example: Dramix 3D 65/35 = 35 mm | — | Relational: `material_batches.fiber_length_mm` |
| `fiber_diameter_mm` | real | Fiber diameter (mm). Required to calculate aspect ratio | — | Relational: `material_batches.fiber_diameter_mm` |
| `fiber_aspect_ratio` | real | Length-to-diameter ratio (L/d). Common fiber bridging and ordering parameter. Example: Dramix 65/35 has L/d = 65 | — | Open3DCP-specific. |
| `fiber_tensile_strength_mpa` | real | Fiber tensile strength as specified by supplier | — | Open3DCP-specific. |
| `superplasticizer` | real | High-range water reducer (PCE, SNF, SMF) -- ASTM C494 Type F/G. Record as solids content. | ASTM C494 | Relational: `material_batches.superplasticizer_content_kg_m3` |
| `water_reducer` | real | Mid/normal-range water reducer -- ASTM C494 Type A | ASTM C494 | Relational: `material_batches.water_reducer_content_ml_m3` |
| `accelerator` | real | Set/strength accelerator -- ASTM C494 Type C/E | ASTM C494 | Relational: `material_batches.hydration_accelerator_content_ml_m3` |
| `calcium_formate` | real | Organic salt accelerator (Ca(HCOO)2), promotes early C3S hydration. Used as set accelerator; not formally classified under ASTM C494 | ASTM C494 | Open3DCP-specific. |
| `retarder` | real | Set retarder -- ASTM C494 Type B/D | ASTM C494 | Open3DCP-specific. |
| `air_entrainer` | real | Air-entraining admixture -- ASTM C260 | ASTM C260 | Relational: `material_batches.air_entrainment_content_ml_m3` |
| `vma` | real | Viscosity-modifying admixture (generic) | — | Relational: `material_batches.rheology_modifier_content_kg_m3` |
| `shrinkage_reducer` | real | Shrinkage-reducing admixture | — | Open3DCP-specific. |
| `corrosion_inhibitor` | real | Corrosion-inhibiting admixture | — | Open3DCP-specific. |

## Clay / VMA Rheology Modifiers

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `hpmc` | real | Hydroxypropyl methylcellulose (cellulose ether VMA) | — | Open3DCP-specific. |
| `sepiolite_clay` | real | Sepiolite clay (fiber-network thixotropy) | — | Open3DCP-specific. |
| `attapulgite` | real | Attapulgite / palygorskite (fiber-network, US domestic) | — | Open3DCP-specific. |
| `calcium_bentonite` | real | Calcium bentonite (low-moderate swell) | — | Open3DCP-specific. |

## Water

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `water` | real | Free (added) mix water, aggregates at SSD basis (mass-% of total wet mix). See *Aggregate Conditioning* to recover effective water when batched off SSD. | — | Open3DCP-specific. |

## KEY RATIOS

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `w_c_ratio` | real | Water-to-cement ratio (water / cement only) | — | Open3DCP-specific. |
| `w_b_ratio` | real | Water-to-binder ratio (water / all cementitious materials) | — | Relational: `material_batches.water_binder_ratio` |
| `a_b_ratio` | real | Aggregate-to-binder ratio | — | Open3DCP-specific. |
| `water_premix_pct` | real | % of water added during pre-mix phase | — | Open3DCP-specific. |
| `water_temperature_c` | real | Water temperature at mixing (C) | — | Open3DCP-specific. |

## AGGREGATE CONDITIONING

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `aggregate_moisture_state` | varchar(20) | As-batched condition: `oven_dry` / `air_dry` / `SSD` / `wet` | — | Open3DCP-specific. |
| `aggregate_absorption_pct` | real | 24-h aggregate absorption, % of oven-dry mass | ASTM C127 / C128 | Open3DCP-specific. |
| `aggregate_moisture_content_pct` | real | Total as-batched aggregate moisture, % of oven-dry mass (free moisture = this − absorption) | ASTM C566 | Open3DCP-specific. |
| `original_basis` | varchar(20) | Basis the source reported: `kg_m3` (primary), `mass_pct`, `volume`, or `lb_yd3` | — | Open3DCP-specific. |
| `mix_density_kg_m3` | real | Total fresh wet-mix density (sum of kg/m³ constituents); enables exact mass-% ↔ kg/m³ conversion | — | Open3DCP-specific. |
| `total_binder_kg_m3` | real | Total cementitious content (kg/m³); supports w/b and absolute back-conversion | — | Open3DCP-specific. |

## TEST CONDITIONS

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `test_age_days` | integer | Age at testing (default: 28) | — | Relational: `tests.age_days` |
| `specimen_prep` | varchar(50) | Specimen preparation method | — | Open3DCP-specific. |
| `specimen_geometry` | varchar(50) | Specimen shape (see standard geometries below) | — | Open3DCP-specific. |
| `specimen_length_mm` | real | Specimen dimension L | — | Open3DCP-specific. |
| `specimen_width_mm` | real | Specimen dimension W | — | Open3DCP-specific. |
| `specimen_height_mm` | real | Specimen dimension H | — | Open3DCP-specific. |
| `test_orientation` | varchar(20) | Loading direction relative to print layers | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `test_orientation_code` | varchar(10) | Coded orientation (X, Y, Z, XY_45, CAST) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `test_method_code` | varchar(50) | Test standard reference (e.g., ASTM C39, EN 12390-3) | ASTM C39 | Relational: `tests.test_type` |
| `n_specimens` | integer | Number of specimens averaged | — | Relational: `data.number_of_specimens` |
| `curing_regime` | varchar(100) | Curing description (moist, sealed, ambient, steam) | — | Open3DCP-specific. |
| `curing_regime_code` | varchar(50) | Coded curing regime | — | Relational: `tests.curing_condition` |
| `curing_temperature_c` | real | Curing temperature (C) | — | Relational: `tests.initial_env_temperature_C` |
| `curing_humidity_pct` | real | Curing relative humidity (%) | — | Relational: `tests.initial_env_relative_humidity_percent` |
| `curing_duration_days` | real | Curing duration in days | — | Open3DCP-specific. |

## 3DCP PROCESS PARAMETERS

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `is_3d_printed` | boolean | True if specimen was 3D printed (false = cast/moulded) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). Relational: `material_batches.printable` |
| `print_speed_mm_s` | real | Nozzle travel speed | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `layer_height_mm` | real | Deposited layer height | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `layer_time_gap_s` | real | Time interval between successive layers | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `nozzle_diameter_mm` | real | Nozzle exit diameter | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `nozzle_shape` | varchar(20) | Nozzle cross-section (circular, rectangular, custom) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `nozzle_area_mm2` | real | Nozzle exit area | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `filament_width_mm` | real | Deposited filament width | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `layer_width_mm` | real | Layer width after deposition | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `extrusion_rate_l_min` | real | Volumetric extrusion rate | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `num_layers` | integer | Total number of printed layers | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `path_length_mm` | real | Total toolpath length per layer | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `infill_pattern` | varchar(50) | Internal fill pattern (solid, zigzag, contour) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `contour_count` | integer | Number of perimeter contours | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `print_direction` | varchar(20) | Primary print path direction | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |

## Pumping System

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `pump_type` | varchar(50) | Pump mechanism (piston, progressive cavity, peristaltic) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `pump_pressure_bar` | real | Pump outlet pressure | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `pump_rotational_speed_rpm` | real | Pump motor speed | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `pump_distance_m` | real | Hose length from pump to nozzle | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `pipe_diameter_mm` | real | Delivery hose internal diameter | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `pumping_duration_s` | real | Total pumping time | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |

## Mixing Process

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `mixing_time_s` | real | Total mixing duration | — | Open3DCP-specific. |
| `mixing_speed_rpm` | real | Mixer blade speed | — | Open3DCP-specific. |
| `mixer_type` | varchar(50) | Mixer type (pan, planetary, twin-shaft, continuous) | — | Open3DCP-specific. |
| `shear_rate_per_s` | real | Applied shear rate during mixing | — | Open3DCP-specific. |
| `admixture_addition_point` | varchar(50) | When admixtures were added (dry, wet, delayed) | — | Open3DCP-specific. |
| `aggregate_prewetted` | boolean | Aggregate pre-wetted / pre-soaked before batching (common 3DCP practice; pairs with *Aggregate Conditioning*) | — | Open3DCP-specific. |

## ENVIRONMENTAL CONDITIONS

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `mix_temperature_c` | real | Concrete temperature at mixing | — | Open3DCP-specific. |
| `ambient_temperature_c` | real | Ambient air temperature during printing | — | Open3DCP-specific. |
| `ambient_humidity_pct` | real | Ambient relative humidity during printing | — | Open3DCP-specific. |
| `wind_speed_m_s` | real | Wind speed during outdoor printing | — | Open3DCP-specific. |

## FRESH-STATE PROPERTIES

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `slump_mm` | real | Slump height | ASTM C143 | Relational: `data` where `quantity_reported=slump` |
| `spread_mm` | real | Slump flow spread diameter | ASTM C1611 | Open3DCP-specific. |
| `yield_stress_pa` | real | Static yield stress | — | Relational: `data` where `quantity_reported=yield_stress` |
| `plastic_viscosity_pa_s` | real | Plastic viscosity | — | Relational: `data` where `quantity_reported=viscosity` |
| `static_yield_stress_pa` | real | Static yield stress (at rest) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `dynamic_yield_stress_pa` | real | Dynamic yield stress (during flow) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `thixotropy_pa_per_s` | real | Structural buildup rate (Athix) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `structuration_rate_pa_per_s` | real | Structuration rate | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `open_time_min` | real | Workable window before set | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `green_strength_kpa` | real | Strength of fresh concrete (buildability) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `air_content_fresh_pct` | real | Fresh-state air content | ASTM C231 | Relational: `material_batches.air_content_percent_volume_concrete` |
| `unit_weight_fresh_kg_m3` | real | Fresh unit weight | ASTM C138 | Open3DCP-specific. |
| `setting_time_initial_min` | real | Initial set (Vicat needle) | ASTM C191 | Open3DCP-specific. |
| `setting_time_final_min` | real | Final set (Vicat needle) | ASTM C191 | Open3DCP-specific. |
| `bleeding_pct` | real | Bleeding water (% of mix water) | ASTM C232 | Open3DCP-specific. |
| `temperature_fresh_c` | real | Concrete temperature at discharge | — | Open3DCP-specific. |
| `j_ring_mm` | real | J-Ring passing ability | ASTM C1621 | Open3DCP-specific. |
| `v_funnel_s` | real | V-Funnel flow time | EN 12350-9 | Open3DCP-specific. |
| `l_box_ratio` | real | L-Box passing ratio (H2/H1) | EN 12350-10 | Open3DCP-specific. |
| `segregation_resistance_pct` | real | Sieve segregation | EN 12350-11 | Open3DCP-specific. |

## MECHANICAL PROPERTIES (HARDENED)

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `design_strength_mpa` | real | Specified/target compressive strength (f'c) the mix is designed to achieve. This is the number on a concrete order ticket. | — | Open3DCP-specific. |
| `compressive_strength_mpa` | real | Compressive strength | ASTM C39 / EN 12390-3 | Relational: `data` where `quantity_reported=compressive_strength` |
| `tensile_strength_mpa` | real | Direct tensile strength | ASTM C496 | Relational: `data` where `quantity_reported=tensile_strength` |
| `splitting_tensile_mpa` | real | Splitting tensile (Brazilian) | ASTM C496 | Open3DCP-specific. |
| `flexural_strength_mpa` | real | Flexural (modulus of rupture) | ASTM C78 | Open3DCP-specific. |
| `elastic_modulus_gpa` | real | Static elastic modulus | ASTM C469 | Relational: `data` where `quantity_reported=elastic_modulus` |
| `bond_strength_mpa` | real | Bond / pull-off strength | ASTM C1583 | Open3DCP-specific. |
| `fracture_energy_n_m` | real | Fracture energy (GF) | RILEM FMC-50 | Open3DCP-specific. |
| `toughness_index` | real | Toughness index (I5, I10, I20) | ASTM C1018 | Open3DCP-specific. |
| `impact_resistance_j` | real | Impact energy | ACI 544.2R | Open3DCP-specific. |
| `fatigue_life_cycles` | real | Fatigue life (cycles to failure) | — | Open3DCP-specific. |
| `density_hardened_kg_m3` | real | Hardened density | ASTM C642 | Relational: `data` where `quantity_reported=density` |
| `poissons_ratio` | real | Poisson's ratio | ASTM C469 | Open3DCP-specific. |

## 3DCP INTERLAYER PROPERTIES

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `interlayer_bond_mpa` | real | Tensile bond between printed layers (pull-off) | ASTM C1583 | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `interlayer_shear_mpa` | real | Shear strength at layer interface | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `air_content_deposited_pct` | real | Air content in deposited filament | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `void_area_fraction_pct` | real | Void fraction at interlayer zone | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `surface_roughness_avg` | real | Surface roughness of printed layer | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `surface_moisture_state` | varchar(20) | Surface condition at interface (dry, SSD, wet) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |
| `surface_treatment` | varchar(50) | Interface treatment (none, scratch, bonding agent) | — | 3DCP-native (RILEM TC 276-DFC / 304-ADC). |

## DURABILITY PROPERTIES

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `chloride_rcpt_coulombs` | real | Rapid chloride permeability (total charge) | ASTM C1202 | Open3DCP-specific. |
| `chloride_migration_coeff` | real | Non-steady-state chloride migration | NT BUILD 492 | Open3DCP-specific. |
| `chloride_diffusion_coeff` | real | Apparent chloride diffusion | ASTM C1556 | Open3DCP-specific. |
| `carbonation_depth_1yr_mm` | real | Carbonation front depth at 1 year | EN 12390-12 | Open3DCP-specific. |
| `carbonation_rate_coeff` | real | Carbonation rate coefficient (KAC) | EN 12390-12 | Open3DCP-specific. |
| `drying_shrinkage_28d_ue` | real | 28-day drying shrinkage | ASTM C157 | Open3DCP-specific. |
| `autogenous_shrinkage_ue` | real | Autogenous shrinkage | ASTM C1698 | Open3DCP-specific. |
| `creep_coefficient` | real | Creep coefficient (phi) | ASTM C512 | Open3DCP-specific. |
| `freeze_thaw_cycles` | real | Cycles to 60% relative dynamic modulus | ASTM C666 | Open3DCP-specific. |
| `freeze_thaw_durability_factor` | real | Durability factor | ASTM C666 | Open3DCP-specific. |
| `freeze_thaw_mass_loss_pct` | real | Mass loss after freeze-thaw | — | Open3DCP-specific. |
| `sulfate_expansion_6mo_pct` | real | 6-month sulfate expansion | ASTM C1012 | Open3DCP-specific. |
| `sulfate_expansion_12mo_pct` | real | 12-month sulfate expansion | ASTM C1012 | Open3DCP-specific. |
| `asr_expansion_14d_pct` | real | 14-day ASR mortar bar expansion | ASTM C1260 | Relational: `data` where `quantity_reported=expansion` |
| `asr_expansion_1yr_pct` | real | 1-year ASR concrete prism expansion | ASTM C1293 | Open3DCP-specific. |
| `abrasion_depth_mm` | real | Abrasion depth | ASTM C779 | Open3DCP-specific. |
| `water_penetration_depth_mm` | real | Water penetration under pressure | EN 12390-8 | Open3DCP-specific. |
| `electrical_resistivity_kohm_cm` | real | Surface resistivity | ASTM C1876 | Open3DCP-specific. |
| `porosity_pct` | real | Total porosity (MIP or vacuum saturation) | ASTM C642 | Relational: `data` where `quantity_reported=porosity` |
| `water_absorption_pct` | real | Water absorption by immersion | ASTM C642 | Open3DCP-specific. |
| `sorptivity_mm_sqrt_s` | real | Sorptivity — initial rate (first 6 hours) | ASTM C1585 | Relational: `data` where `quantity_reported=sorptivity` |
| `sorptivity_secondary_mm_sqrt_s` | real | Sorptivity — secondary rate (day 1–7). Critical for 3DCP interlayer moisture transport. | ASTM C1585 | Open3DCP-specific. |
| `oxygen_permeability_m2` | real | Oxygen permeability coefficient | — | Open3DCP-specific. |
| `scaling_resistance_kg_m2` | real | De-icing salt scaling mass loss | ASTM C672 | Open3DCP-specific. |
| `corrosion_rate_ua_cm2` | real | Corrosion current density (Icorr) | ASTM C876 | Open3DCP-specific. |
| `half_cell_potential_mv` | real | Half-cell corrosion potential | ASTM C876 | Open3DCP-specific. |
| `heat_of_hydration_kj_kg` | real | Heat of hydration | ASTM C186 | Open3DCP-specific. |

## THERMAL & ENVIRONMENTAL

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `thermal_conductivity_w_mk` | real | Thermal conductivity | — | Open3DCP-specific. |
| `specific_heat_j_kg_k` | real | Specific heat capacity | — | Open3DCP-specific. |
| `coeff_thermal_expansion_ue_c` | real | Coefficient of thermal expansion | — | Open3DCP-specific. |
| `fire_resistance_min` | real | Fire resistance duration (ASTM E119) | ASTM E119 | Open3DCP-specific. |
| `embodied_carbon_kg_co2_m3` | real | Embodied CO2 (cradle-to-gate) | — | Open3DCP-specific. |
| `embodied_energy_mj_m3` | real | Embodied energy | — | Open3DCP-specific. |

## MICROSTRUCTURE

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `degree_of_hydration` | real | Degree of hydration (0-1) | — | Open3DCP-specific. |
| `calcium_hydroxide_pct` | real | Ca(OH)2 content (TGA/XRD) | — | Open3DCP-specific. |
| `pore_size_distribution_nm` | real | Critical pore diameter (MIP) | — | Open3DCP-specific. |
| `compressive_strength_stddev_mpa` | real | Std-dev of compressive strength across specimens | — | Open3DCP-specific. |
| `flexural_strength_stddev_mpa` | real | Std-dev of flexural strength | — | Open3DCP-specific. |
| `tensile_strength_stddev_mpa` | real | Std-dev of tensile / splitting strength | — | Open3DCP-specific. |
| `elastic_modulus_stddev_gpa` | real | Std-dev of elastic modulus | — | Open3DCP-specific. |
| `interlayer_bond_stddev_mpa` | real | Std-dev of interlayer bond strength | — | Open3DCP-specific. |
| `raw_data_doi` | varchar(255) | DOI of a deposited raw-data record | — | Open3DCP-specific. |
| `stress_strain_file` | varchar(255) | Load-displacement / stress-strain curve file | — | Open3DCP-specific. |
| `rheology_curve_file` | varchar(255) | Flow / structuration curve file | — | Open3DCP-specific. |
| `microstructure_image` | varchar(255) | SEM / CT / crack-pattern image file | — | Open3DCP-specific. |
| `raw_data_file` | varchar(255) | Generic table / HDF5 raw-data reference | — | Relational: `data.file_name` |

## DATA PROVENANCE

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `doi` | varchar(255) | Digital Object Identifier of source publication | — | Open3DCP-specific. |
| `source_citation` | varchar(500) | Full citation string (for sources without DOI: theses, conference papers, internal reports) | — | Open3DCP-specific. |
| `measurement_confidence` | varchar(20) | Data reliability: `measured` (direct lab measurement), `calculated` (derived from other properties), `estimated` (approximated or inferred), `reported` (taken from literature without independent verification) | — | Relational: `data.extraction_methods` |
| `lab_name` | varchar(100) | Laboratory that performed the tests (enables inter-laboratory comparison) | — | Open3DCP-specific. |
| `provenance_notes` | text | Free-text notes on data origin or quality concerns | — | Open3DCP-specific. |

## DATA QUALITY FLAGS

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `is_training_ready` | boolean | Record passes quality gates and is eligible for ML training | — | Open3DCP-specific. |
| `is_synthetic` | boolean | True if generated by ML/optimization, not from real lab measurements | — | Open3DCP-specific. |
| `outlier_flag` | boolean | Statistical outlier detected during quality audit | — | Open3DCP-specific. |

## EXPOSURE CLASSIFICATION (EN 206 / ACI 318)

| Term | Type | Definition | Standard | Justification & crosswalk |
|---|---|---|---|---|
| `exposure_class_freeze` | varchar(10) | Freeze-thaw exposure (e.g., XF1-XF4) | — | Open3DCP-specific. |
| `exposure_class_sulfate` | varchar(10) | Sulfate exposure (e.g., S0-S3) | — | Open3DCP-specific. |
| `exposure_class_chloride` | varchar(10) | Chloride exposure (e.g., XD1-XD3, XS1-XS3) | — | Open3DCP-specific. |
| `exposure_class_water` | varchar(10) | Waterproofing requirement | — | Open3DCP-specific. |
| `exposure_class_asr` | varchar(10) | ASR risk classification | — | Open3DCP-specific. |

---

*Generated by Sunnyday Technologies. Regenerate with `python tools/term_justification/generate.py`.*
