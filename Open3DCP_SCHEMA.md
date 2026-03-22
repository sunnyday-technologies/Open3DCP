# Open3DCP v1.0

**Open Data Standard for 3D Concrete Printing**

A flat database schema for 3D-printable concrete (3DCP) mix design data. Open3DCP captures materials, process parameters, fresh-state rheology, hardened mechanical properties, durability performance, and environmental impact in a single table designed for direct ML training.

---

## Design Principles

1. **Flat schema** -- Every feature is a named column, no JSON parsing required for ML.
2. **Mass-percent basis** -- All material quantities stored as mass-% of total wet mix (water included). Consistent across datasets, eliminates density assumptions.
3. **ASTM/RILEM-aligned** -- Column naming follows established standards: ASTM C150 (cement types), ASTM C618 (fly ash), ASTM C989 (slag), ASTM C1240 (silica fume), ASTM C33 (aggregate grading by fineness modulus).
4. **3DCP-native** -- First-class columns for print process parameters (nozzle, layer, speed, pump), rheology (yield stress, thixotropy, open time), and interlayer properties that don't exist in conventional concrete schemas.
5. **Multi-age** -- Companion `strength_measurements` table stores multi-age data (1, 3, 7, 14, 28, 56, 90, 365 days).

---

## Main Table: `mix_designs`

### Identity & Versioning

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Auto-increment primary key |
| `mix_id` | varchar | Unique human-readable identifier |
| `name` | varchar | Descriptive name |
| `parent_mix_id` | varchar | Links to parent formulation if this is a variant or iteration |
| `version` | varchar | Formulation version string |
| `created_at` | timestamptz | Record creation timestamp |

### Binder Materials (mass-% of total wet mix)

Cements are classified by ASTM C150 / EN 197-1 type. SCMs follow their respective ASTM standards.

| Column | Type | Description | Standard |
|--------|------|-------------|----------|
| `cement_type_1` | real | OPC / CEM I 42.5 N (general purpose Portland) | ASTM C150 Type I |
| `cement_type_1l` | real | CEM II/A-L (Portland-limestone, 6-20% limestone) | EN 197-1 |
| `cement_type_3` | real | CEM I 52.5 R (rapid hardening / high early strength) | ASTM C150 Type III |
| `cement_type_4` | real | Low-heat Portland cement | ASTM C150 Type IV |
| `cac` | real | Calcium aluminate cement (Ciment Fondu) | EN 14647 |
| `csa_cement` | real | Calcium sulfoaluminate cement | -- |
| `fly_ash` | real | Fly ash (unclassified) | ASTM C618 |
| `fly_ash_type_f` | real | Class F fly ash (low calcium, <7% CaO) | ASTM C618 |
| `fly_ash_type_c` | real | Class C fly ash (high calcium, >20% CaO) | ASTM C618 |
| `silica_fume` | real | Silica fume / microsilica | ASTM C1240 |
| `nano_silica` | real | Nano-SiO2 (colloidal or fumed, <100 nm) | -- |
| `slag` | real | Ground granulated blast furnace slag (GGBS) | ASTM C989 |
| `metakaolin` | real | Calcined kaolin clay | ASTM C618 Class N |
| `limestone` | real | Limestone filler / calcium carbonate | EN 12620 |
| `pumice` | real | Natural pozzolan (pumice) | ASTM C618 Class N |
| `bottom_ash` | real | Coal bottom ash | -- |

### Aggregate Materials (mass-% of total wet mix)

Sand columns use ASTM C33 fineness modulus (FM) grading. Coarse aggregates by nominal max size.

| Column | Type | Description | FM / Size |
|--------|------|-------------|-----------|
| `fine_sand` | real | Fine sand | FM 1.6-2.2 |
| `medium_sand` | real | Medium sand | FM 2.3-3.0 |
| `coarse_sand` | real | Coarse sand | FM 3.1-3.7 |
| `agg_4mm` | real | Fine aggregate, nominal max 4 mm | 4.75 mm sieve |
| `agg_6mm` | real | Coarse aggregate, 4-6 mm | -- |
| `agg_10mm` | real | Coarse aggregate, 6-10 mm | -- |
| `agg_14mm` | real | Coarse aggregate, 10-14 mm | -- |
| `agg_20mm` | real | Coarse aggregate, 14-20 mm | -- |

### Fiber Reinforcement (mass-% of total wet mix)

| Column | Type | Description |
|--------|------|-------------|
| `steel_fiber` | real | Steel fiber (hooked, crimped, or micro) |
| `pp_fiber` | real | Polypropylene fiber |
| `glass_fiber` | real | Alkali-resistant glass fiber |
| `carbon_fiber` | real | Carbon fiber |
| `pva_fiber` | real | Polyvinyl alcohol fiber |
| `basalt_fiber` | real | Basalt fiber |
| `nylon_fiber` | real | Nylon fiber |
| `aramid_fiber` | real | Aramid fiber (Kevlar) |
| `fiber_length_mm` | real | Dominant fiber length in mm |

### Chemical Admixtures (mass-% of total wet mix)

| Column | Type | Description |
|--------|------|-------------|
| `superplasticizer` | real | High-range water reducer (PCE, SNF, SMF) -- ASTM C494 Type F/G |
| `water_reducer` | real | Mid/normal-range water reducer -- ASTM C494 Type A |
| `accelerator` | real | Set/strength accelerator -- ASTM C494 Type C/E |
| `calcium_formate` | real | Organic accelerator (Ca(HCOO)2), promotes early C3S hydration -- ASTM C494 Type C |
| `retarder` | real | Set retarder -- ASTM C494 Type B/D |
| `air_entrainer` | real | Air-entraining admixture -- ASTM C260 |
| `vma` | real | Viscosity-modifying admixture (generic) |
| `shrinkage_reducer` | real | Shrinkage-reducing admixture |
| `corrosion_inhibitor` | real | Corrosion-inhibiting admixture |

### Clay / VMA Additives (mass-% of total wet mix)

Specialized rheology modifiers for 3DCP thixotropy and shape retention.

| Column | Type | Description | Mineral Class |
|--------|------|-------------|---------------|
| `hpmc` | real | Hydroxypropyl methylcellulose (cellulose ether VMA) | Organic polymer |
| `sepiolite_clay` | real | Sepiolite clay (fiber-network thixotropy) | Chain silicate |
| `attapulgite` | real | Attapulgite / palygorskite (fiber-network, US domestic) | Chain silicate |
| `calcium_bentonite` | real | Calcium bentonite (low-moderate swell) | Smectite |

### Water & Ratios

| Column | Type | Description |
|--------|------|-------------|
| `water` | real | Total mix water (mass-% of total wet mix) |
| `w_c_ratio` | real | Water-to-cement ratio (water / cement only) |
| `w_b_ratio` | real | Water-to-binder ratio (water / all cementitious materials) |
| `a_b_ratio` | real | Aggregate-to-binder ratio |
| `water_premix_pct` | real | % of water added during pre-mix phase |
| `water_temperature_c` | real | Water temperature at mixing (C) |

### Test Conditions

| Column | Type | Description |
|--------|------|-------------|
| `test_age_days` | integer | Age at testing (default: 28) |
| `specimen_prep` | varchar | Specimen preparation method |
| `specimen_geometry` | varchar | Specimen shape (cube, cylinder, prism, dog-bone) |
| `specimen_length_mm` | real | Specimen dimension L |
| `specimen_width_mm` | real | Specimen dimension W |
| `specimen_height_mm` | real | Specimen dimension H |
| `test_orientation` | varchar | Loading direction relative to print layers |
| `test_orientation_code` | varchar | Coded orientation (X, Y, Z, XY_45, CAST) |
| `test_method_code` | varchar | Test standard reference (e.g., ASTM C39, EN 12390-3) |
| `n_specimens` | integer | Number of specimens averaged |
| `curing_regime` | varchar | Curing description (moist, sealed, ambient, steam) |
| `curing_regime_code` | varchar | Coded curing regime |
| `curing_temperature_c` | real | Curing temperature (C) |
| `curing_humidity_pct` | real | Curing relative humidity (%) |
| `curing_duration_days` | real | Curing duration in days |

### 3DCP Process Parameters

These columns capture the full extrusion printing process. Null for cast specimens.

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `is_3d_printed` | boolean | True if specimen was 3D printed (false = cast/moulded) | -- |
| `print_speed_mm_s` | real | Nozzle travel speed | mm/s |
| `layer_height_mm` | real | Deposited layer height | mm |
| `layer_time_gap_s` | real | Time interval between successive layers | seconds |
| `nozzle_diameter_mm` | real | Nozzle exit diameter | mm |
| `nozzle_shape` | varchar | Nozzle cross-section (circular, rectangular, custom) | -- |
| `nozzle_area_mm2` | real | Nozzle exit area | mm2 |
| `filament_width_mm` | real | Deposited filament width | mm |
| `layer_width_mm` | real | Layer width after deposition | mm |
| `extrusion_rate_l_min` | real | Volumetric extrusion rate | L/min |
| `num_layers` | integer | Total number of printed layers | -- |
| `path_length_mm` | real | Total toolpath length per layer | mm |
| `infill_pattern` | varchar | Internal fill pattern (solid, zigzag, contour) | -- |
| `contour_count` | integer | Number of perimeter contours | -- |
| `print_direction` | varchar | Primary print path direction | -- |

### Pumping System

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `pump_type` | varchar | Pump mechanism (piston, progressive cavity, peristaltic) | -- |
| `pump_pressure_bar` | real | Pump outlet pressure | bar |
| `pump_rotational_speed_rpm` | real | Pump motor speed | rpm |
| `pump_distance_m` | real | Hose length from pump to nozzle | m |
| `pipe_diameter_mm` | real | Delivery hose internal diameter | mm |
| `pumping_duration_s` | real | Total pumping time | seconds |

### Mixing Process

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `mixing_time_s` | real | Total mixing duration | seconds |
| `mixing_speed_rpm` | real | Mixer blade speed | rpm |
| `mixer_type` | varchar | Mixer type (pan, planetary, twin-shaft, continuous) | -- |
| `shear_rate_s` | real | Applied shear rate during mixing | 1/s |
| `admixture_addition_point` | varchar | When admixtures were added (dry, wet, delayed) | -- |

### Environmental Conditions

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `mix_temperature_c` | real | Concrete temperature at mixing | C |
| `ambient_temperature_c` | real | Ambient air temperature during printing | C |
| `ambient_humidity_pct` | real | Ambient relative humidity during printing | % |
| `wind_speed_m_s` | real | Wind speed during outdoor printing | m/s |

### Target Properties -- Fresh State

| Column | Type | Description | Unit | Test Method |
|--------|------|-------------|------|-------------|
| `slump_mm` | real | Slump height | mm | ASTM C143 |
| `spread_mm` | real | Slump flow spread diameter | mm | ASTM C1611 |
| `yield_stress_pa` | real | Static yield stress | Pa | Rheometer |
| `plastic_viscosity_pa_s` | real | Plastic viscosity | Pa.s | Rheometer |
| `static_yield_stress_pa` | real | Static yield stress (at rest) | Pa | Rheometer |
| `dynamic_yield_stress_pa` | real | Dynamic yield stress (during flow) | Pa | Rheometer |
| `thixotropy_pa_per_s` | real | Structural buildup rate (Athix) | Pa/s | Rheometer |
| `structuration_rate_pa_per_s` | real | Structuration rate | Pa/s | Rheometer |
| `open_time_min` | real | Workable window before set | minutes | -- |
| `green_strength_kpa` | real | Strength of fresh concrete (buildability) | kPa | -- |
| `air_content_fresh_pct` | real | Fresh-state air content | % | ASTM C231 |
| `unit_weight_fresh_kg_m3` | real | Fresh unit weight | kg/m3 | ASTM C138 |
| `setting_time_initial_min` | real | Initial set (Vicat needle) | minutes | ASTM C191 |
| `setting_time_final_min` | real | Final set (Vicat needle) | minutes | ASTM C191 |
| `bleeding_pct` | real | Bleeding water (% of mix water) | % | ASTM C232 |
| `temperature_fresh_c` | real | Concrete temperature at discharge | C | -- |
| `j_ring_mm` | real | J-Ring passing ability | mm | ASTM C1621 |
| `v_funnel_s` | real | V-Funnel flow time | seconds | EN 12350-9 |
| `l_box_ratio` | real | L-Box passing ratio (H2/H1) | -- | EN 12350-10 |
| `segregation_resistance_pct` | real | Sieve segregation | % | EN 12350-11 |

### Target Properties -- Mechanical (Hardened)

| Column | Type | Description | Unit | Test Method |
|--------|------|-------------|------|-------------|
| `compressive_strength_mpa` | real | Compressive strength | MPa | ASTM C39 / EN 12390-3 |
| `tensile_strength_mpa` | real | Direct tensile strength | MPa | ASTM C496 |
| `splitting_tensile_mpa` | real | Splitting tensile (Brazilian) | MPa | ASTM C496 |
| `flexural_strength_mpa` | real | Flexural (modulus of rupture) | MPa | ASTM C78 |
| `elastic_modulus_gpa` | real | Static elastic modulus | GPa | ASTM C469 |
| `bond_strength_mpa` | real | Bond / pull-off strength | MPa | ASTM C1583 |
| `fracture_energy_n_m` | real | Fracture energy (GF) | N/m | RILEM FMC-50 |
| `toughness_index` | real | Toughness index (I5, I10, I20) | -- | ASTM C1018 |
| `impact_resistance_j` | real | Impact energy | J | ACI 544.2R |
| `fatigue_life_cycles` | real | Fatigue life (cycles to failure) | -- | -- |
| `density_hardened_kg_m3` | real | Hardened density | kg/m3 | ASTM C642 |
| `poissons_ratio` | real | Poisson's ratio | -- | ASTM C469 |

### Target Properties -- 3DCP Interlayer

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `interlayer_bond_mpa` | real | Tensile bond between printed layers | MPa |
| `interlayer_shear_mpa` | real | Shear strength at layer interface | MPa |
| `air_content_deposited_pct` | real | Air content in deposited filament | % |
| `void_area_fraction_pct` | real | Void fraction at interlayer zone | % |
| `surface_roughness_avg` | real | Surface roughness of printed layer | -- |
| `surface_moisture_state` | varchar | Surface condition at interface (dry, SSD, wet) | -- |
| `surface_treatment` | varchar | Interface treatment (none, scratch, bonding agent) | -- |

### Target Properties -- Durability

| Column | Type | Description | Unit | Test Method |
|--------|------|-------------|------|-------------|
| `chloride_rcpt_coulombs` | real | Rapid chloride permeability (total charge) | Coulombs | ASTM C1202 |
| `chloride_migration_coeff` | real | Non-steady-state chloride migration | m2/s | NT BUILD 492 |
| `chloride_diffusion_coeff` | real | Apparent chloride diffusion | m2/s | ASTM C1556 |
| `carbonation_depth_1yr_mm` | real | Carbonation front depth at 1 year | mm | EN 12390-12 |
| `carbonation_rate_coeff` | real | Carbonation rate coefficient (KAC) | mm/sqrt(day) | EN 12390-12 |
| `drying_shrinkage_28d_ue` | real | 28-day drying shrinkage | microstrain | ASTM C157 |
| `autogenous_shrinkage_ue` | real | Autogenous shrinkage | microstrain | ASTM C1698 |
| `creep_coefficient` | real | Creep coefficient (phi) | -- | ASTM C512 |
| `freeze_thaw_cycles` | real | Cycles to 60% relative dynamic modulus | -- | ASTM C666 |
| `freeze_thaw_durability_factor` | real | Durability factor | -- | ASTM C666 |
| `freeze_thaw_mass_loss_pct` | real | Mass loss after freeze-thaw | % | -- |
| `sulfate_expansion_6mo_pct` | real | 6-month sulfate expansion | % | ASTM C1012 |
| `sulfate_expansion_12mo_pct` | real | 12-month sulfate expansion | % | ASTM C1012 |
| `asr_expansion_14d_pct` | real | 14-day ASR mortar bar expansion | % | ASTM C1260 |
| `asr_expansion_1yr_pct` | real | 1-year ASR concrete prism expansion | % | ASTM C1293 |
| `abrasion_depth_mm` | real | Abrasion depth | mm | ASTM C779 |
| `water_penetration_depth_mm` | real | Water penetration under pressure | mm | EN 12390-8 |
| `electrical_resistivity_kohm_cm` | real | Surface resistivity | kohm.cm | ASTM C1876 |
| `porosity_pct` | real | Total porosity (MIP or vacuum saturation) | % | ASTM C642 |
| `water_absorption_pct` | real | Water absorption by immersion | % | ASTM C642 |
| `sorptivity_mm_sqrt_s` | real | Sorptivity coefficient | mm/sqrt(s) | ASTM C1585 |
| `oxygen_permeability_m2` | real | Oxygen permeability coefficient | m2 | -- |
| `scaling_resistance_kg_m2` | real | De-icing salt scaling mass loss | kg/m2 | ASTM C672 |
| `corrosion_rate_ua_cm2` | real | Corrosion current density (Icorr) | uA/cm2 | ASTM C876 |
| `half_cell_potential_mv` | real | Half-cell corrosion potential | mV | ASTM C876 |
| `heat_of_hydration_kj_kg` | real | Heat of hydration | kJ/kg | ASTM C186 |

### Target Properties -- Thermal & Environmental

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `thermal_conductivity_w_mk` | real | Thermal conductivity | W/(m.K) |
| `specific_heat_j_kg_k` | real | Specific heat capacity | J/(kg.K) |
| `coeff_thermal_expansion_ue_c` | real | Coefficient of thermal expansion | microstrain/C |
| `fire_resistance_min` | real | Fire resistance duration | minutes |
| `embodied_carbon_kg_co2_m3` | real | Embodied CO2 (cradle-to-gate) | kg CO2/m3 |
| `embodied_energy_mj_m3` | real | Embodied energy | MJ/m3 |

### Target Properties -- Microstructure

| Column | Type | Description | Unit |
|--------|------|-------------|------|
| `degree_of_hydration` | real | Degree of hydration (0-1) | -- |
| `calcium_hydroxide_pct` | real | Ca(OH)2 content (TGA/XRD) | % |
| `pore_size_distribution_nm` | real | Critical pore diameter (MIP) | nm |

### Data Provenance

| Column | Type | Description |
|--------|------|-------------|
| `doi` | varchar | Digital Object Identifier of source publication |
| `source_citation` | varchar | Full citation string (for sources without DOI: theses, conference papers, internal reports) |
| `measurement_confidence` | varchar | Data reliability: `measured` (direct lab measurement), `calculated` (derived from other properties), `estimated` (approximated or inferred), `reported` (taken from literature without independent verification) |
| `lab_name` | varchar | Laboratory that performed the tests (enables inter-laboratory comparison) |
| `provenance_notes` | text | Free-text notes on data origin or quality concerns |

### Data Quality Flags

| Column | Type | Description |
|--------|------|-------------|
| `is_training_ready` | boolean | Record passes quality gates and is eligible for ML training |
| `is_synthetic` | boolean | True if generated by ML/optimization, not from real lab measurements |
| `outlier_flag` | boolean | Statistical outlier detected during quality audit |

### Exposure Classification (EN 206 / ACI 318)

| Column | Type | Description |
|--------|------|-------------|
| `exposure_class_freeze` | varchar | Freeze-thaw exposure (e.g., XF1-XF4) |
| `exposure_class_sulfate` | varchar | Sulfate exposure (e.g., S0-S3) |
| `exposure_class_chloride` | varchar | Chloride exposure (e.g., XD1-XD3, XS1-XS3) |
| `exposure_class_water` | varchar | Waterproofing requirement |
| `exposure_class_asr` | varchar | ASR risk classification |

---

## Units Convention

All material quantities are in **mass-% of total wet mix** (cement + SCMs + aggregates + water + admixtures + fibers = ~100%).

This convention was chosen because:
- It eliminates density assumptions required for kg/m3 conversion
- It is directly comparable across datasets with different total binder contents
- It normalizes naturally to a fixed scale (0-100%)

---

## Companion Tables

| Table | Purpose |
|-------|---------|
| `strength_measurements` | Multi-age strength data (1-365 days) linked by formulation ID |
| `sources` | Publication metadata (DOI, journal, year, license) |
| `test_methods` | Controlled vocabulary of test standards |
| `curing_regimes` | Standard curing condition definitions |

---

## License

**Creative Commons Attribution 4.0 International** ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).

You are free to use, adapt, and redistribute this schema for any purpose, including commercial use, provided you give appropriate credit to Sunnyday Technologies.

---

## Citation

If you use Open3DCP in your research, please cite:

> Sunnyday Technologies (2026). Open3DCP: Open Data Standard for 3D Concrete Printing. https://github.com/sunnyday-technologies/Open3DCP

---

*Open3DCP v1.0 -- Last updated: 2026-03-22*
*Maintained by [Sunnyday Technologies](https://sunn3d.com), Appleton WI*
