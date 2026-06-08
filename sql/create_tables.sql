-- ====================================================================
-- Open3DCP v1.7 — Reference SQL Implementation
-- https://github.com/sunnyday-technologies/Open3DCP
--
-- Apache License 2.0 — Sunnyday Technologies
--
-- This file creates the Open3DCP schema in PostgreSQL.
-- Adapt column types and constraints for your database engine.
-- All material quantities in mass-% of total wet mix (0-100).
-- Use NULL for unknown / not reported / not applicable values.
-- Use 0 only when the source explicitly reports zero dosage or absence.
-- Strengths in MPa, elastic modulus in GPa.
-- ====================================================================

BEGIN;

-- ===========================================
-- 1. mix_designs (main table)
-- ===========================================
CREATE TABLE IF NOT EXISTS mix_designs (

    -- Identity & Versioning
    id                          SERIAL PRIMARY KEY,
    mix_id                      VARCHAR(50) NOT NULL UNIQUE,
    name                        VARCHAR(200) NOT NULL,
    parent_mix_id               VARCHAR(50),
    version                     VARCHAR(20),
    material_class              VARCHAR(30),        -- (v1.7) Mix/binder system: OPC | blended_OPC | AAM | CAC | CSA | UHPC | mortar | paste | concrete. A classification (also lets ingestion route by chemistry), not free metadata.
    batch_label                 VARCHAR(100),       -- (v1.7) Physical batch sub-identifier within a mix design (provenance; distinguishes repeat batches of one formulation)
    date_of_casting             DATE,               -- (v1.7) Casting/pour date = t=0 of the curing clock; with the test date it yields test_age_days. Distinct from created_at (record creation).
    created_at                  TIMESTAMPTZ DEFAULT NOW(),

    -- -----------------------------------------
    -- COMPOSITION — Binder Materials (mass-%)
    -- -----------------------------------------
    cement_type_1               REAL,     -- OPC, ASTM C150 Type I
    cement_type_1_2             REAL,     -- General purpose / moderate sulfate, ASTM C150 Type I/II
    cement_type_1l              REAL,     -- Portland-limestone, ASTM C595 / EN 197-1 CEM II/A-L
    cement_type_2               REAL,     -- Moderate sulfate / moderate heat, ASTM C150 Type II
    cement_type_3               REAL,     -- High early strength / rapid hardening, ASTM C150 Type III
    cement_type_4               REAL,     -- Low-heat, ASTM C150 Type IV (rarely manufactured)
    cement_type_5               REAL,     -- High sulfate resistance, ASTM C150 Type V
    cac                         REAL,     -- Calcium aluminate cement, EN 14647
    csa_cement                  REAL,     -- Calcium sulfoaluminate cement
    fly_ash                     REAL,     -- Fly ash (class not specified)
    fly_ash_type_f              REAL,     -- Class F (SiO2+Al2O3+Fe2O3 >= 70%), ASTM C618
    fly_ash_type_c              REAL,     -- Class C (SiO2+Al2O3+Fe2O3 >= 50%), ASTM C618
    silica_fume                 REAL,     -- Microsilica, ASTM C1240
    nano_silica                 REAL,     -- Nano-SiO2 (<100 nm)
    slag                        REAL,     -- GGBFS, grade not specified, ASTM C989
    metakaolin                  REAL,     -- Calcined kaolin, reactivity grade not specified, ASTM C618 Class N
    limestone                   REAL,     -- Limestone filler, EN 12620
    pumice                      REAL,     -- Natural pozzolan, grade not specified, ASTM C618 Class N
    bottom_ash                  REAL,     -- Coal bottom ash
    rice_husk_ash               REAL,     -- Rice husk ash (pozzolan)

    -- Alkali Activators (mass-%)
    sodium_hydroxide            REAL,     -- NaOH (purity-adjusted solids)
    sodium_silicate             REAL,     -- Na2SiO3 solution (as-delivered liquid)
    potassium_hydroxide         REAL,     -- KOH (purity-adjusted solids)
    potassium_silicate          REAL,     -- K2SiO3 solution (as-delivered liquid)
    activator_ms_ratio          REAL,               -- SiO2/Na2O molar modulus
    na2o_dosage_pct             REAL,               -- Na2O as % of binder mass

    -- Additional Modifiers (mass-%)
    nano_clay                   REAL,     -- Nanoclay / montmorillonite
    mineral_powder              REAL,     -- Generic mineral powder / filler
    mwcnt                       REAL,     -- Multi-walled carbon nanotubes
    graphene_oxide              REAL,     -- Graphene oxide / rGO
    recycled_sand               REAL,     -- Recycled concrete aggregate sand

    -- Pigments (mass-%)
    -- Ultra-fine (~1 um), 1-5% dosage in architectural 3DCP.
    -- Significant impact on packing, water demand, microstructure.
    iron_oxide_pigment          REAL,     -- Fe2O3 red, FeOOH yellow, Fe3O4 black
    titanium_dioxide_pigment    REAL,     -- TiO2 white / photocatalytic
    chromium_oxide_pigment      REAL,     -- Cr2O3 green
    carbon_black_pigment        REAL,     -- Carbon black
    pigment_other               REAL,     -- Other/unspecified pigment

    -- Aggregate Materials (mass-%)
    -- Sand: US industry ordering terms, FM ranges adapted from ASTM C33 principles
    -- ASTM C33 defines fine aggregate as FM 2.3-3.1; subdivisions below are Open3DCP conventions
    -- Sand FM bins are a non-overlapping Open3DCP partition (half-open intervals, no gaps/overlaps);
    -- tie-break = lower bin. These are Open3DCP conventions, not ASTM C33 (C33 fine = FM 2.3-3.1).
    mason_sand                  REAL,     -- FM [1.0,1.6) (mason / plaster sand)
    fine_sand                   REAL,     -- FM [1.6,2.3)
    concrete_sand               REAL,     -- FM [2.3,3.1) (concrete sand / C33 sand)
    coarse_sand                 REAL,     -- FM [3.1,3.7] (torpedo sand)
    -- Coarse aggregate: ASTM C33 size numbers
    agg_size_89                 REAL,     -- #89: 3/8"-#16 sieve (9.5-1.18 mm)
    agg_size_8                  REAL,     -- #8:  3/8"-#8 sieve (9.5-2.36 mm) — pea gravel, 3DCP limit for most systems
    agg_size_7                  REAL,     -- #7:  1/2"-#4 (12.5-4.75 mm)
    agg_size_67                 REAL,     -- #67: 3/4"-#4 (19-4.75 mm) — common structural
    agg_size_6                  REAL,     -- #6:  3/4"-3/8" (19-9.5 mm)
    agg_size_57                 REAL,     -- #57: 1"-#4 (25-4.75 mm) — most common US concrete aggregate
    agg_size_5                  REAL,     -- #5:  1"-1/2" (25-12.5 mm)
    agg_size_467                REAL,     -- #467: 1.5"-#4 (37.5-4.75 mm) — common ready-mix
    agg_size_4                  REAL,     -- #4:  1.5"-3/4" (37.5-19 mm)
    agg_size_357                REAL,     -- #357: 2"-#4 (50-4.75 mm) — crusher run
    agg_size_3                  REAL,     -- #3:  2"-1" (50-25 mm)
    agg_size_2                  REAL,     -- #2:  2.5"-1.5" (63-37.5 mm)
    agg_size_1                  REAL,     -- #1:  3.5"-1.5" (90-37.5 mm) — large stone

    -- Fiber Reinforcement (mass-%)
    steel_fiber                 REAL,
    pp_fiber                    REAL,     -- Polypropylene
    glass_fiber                 REAL,     -- Alkali-resistant
    carbon_fiber                REAL,
    pva_fiber                   REAL,     -- Polyvinyl alcohol
    basalt_fiber                REAL,
    nylon_fiber                 REAL,
    aramid_fiber                REAL,
    cellulose_fiber             REAL,     -- Natural cellulose fiber, ASTM D7357 / ICC 1150 §301.1
    -- Fiber characterization (dominant fiber in the mix)
    fiber_length_mm             REAL,               -- Fiber length (e.g., 13 mm)
    fiber_diameter_mm           REAL,               -- Fiber diameter (e.g., 0.2 mm)
    fiber_aspect_ratio          REAL,               -- L/d ratio (e.g., 65 for Dramix 3D 65/35)
    fiber_tensile_strength_mpa  REAL,               -- Supplier-specified fiber tensile strength

    -- Chemical Admixtures (mass-% SOLIDS CONTENT)
    -- NOTE: Most commercial admixtures are liquid solutions (typically 20-40% solids).
    -- Convert using manufacturer TDS: e.g., 1.0% liquid at 30% solids = 0.3% in this schema.
    superplasticizer            REAL,     -- HRWR (PCE/SNF/SMF), ASTM C494 Type F/G — solids content
    water_reducer               REAL,     -- MRWR, ASTM C494 Type A — solids content
    accelerator                 REAL,     -- Set/strength accelerator, ASTM C494 Type C/E
    calcium_formate             REAL,     -- Organic salt accelerator (not classified under C494)
    retarder                    REAL,     -- Set retarder, ASTM C494 Type B/D
    air_entrainer               REAL,     -- Air-entraining admixture, ASTM C260
    vma                         REAL,     -- Viscosity-modifying admixture
    shrinkage_reducer           REAL,     -- Shrinkage-reducing admixture
    corrosion_inhibitor         REAL,     -- Corrosion-inhibiting admixture

    -- Clay / VMA Rheology Modifiers (mass-%)
    hpmc                        REAL,     -- Hydroxypropyl methylcellulose
    sepiolite_clay              REAL,     -- Chain silicate thixotropy agent
    attapulgite                 REAL,     -- Palygorskite
    calcium_bentonite           REAL,     -- Smectite

    -- Water
    water                       REAL,

    -- -----------------------------------------
    -- KEY RATIOS
    -- -----------------------------------------
    w_c_ratio                   REAL,               -- water / cement
    w_b_ratio                   REAL,               -- water / total binder
    a_b_ratio                   REAL,               -- aggregate / binder
    water_premix_pct            REAL,               -- % water added during pre-mix
    water_temperature_c         REAL,               -- Water temperature at mixing (C)

    -- -----------------------------------------
    -- AGGREGATE CONDITIONING
    -- (v1.7) As-batched aggregate moisture vs the SSD reference, so effective (free) mix water is
    -- recoverable when aggregates are batched off SSD. Recorded at mix level (not per fraction).
    -- free moisture = aggregate_moisture_content_pct - aggregate_absorption_pct
    -- -----------------------------------------
    aggregate_moisture_state    VARCHAR(20),        -- As-batched condition: oven_dry | air_dry | SSD | wet
    aggregate_absorption_pct    REAL,               -- 24-h aggregate absorption, % of oven-dry mass — ASTM C127/C128
    aggregate_moisture_content_pct REAL,            -- Total as-batched aggregate moisture, % of oven-dry mass — ASTM C566

    -- -----------------------------------------
    -- MIX BASIS (v1.6)
    -- kg/m3 is the PRIMARY reporting basis (industry standard: UCI/Yeh, RILEM, fib).
    -- The mass-% composition columns above are a derived secondary representation; these
    -- columns make the two bases losslessly interconvertible (no assumed density).
    -- -----------------------------------------
    original_basis              VARCHAR(20),        -- kg_m3 (primary) | mass_pct | volume | lb_yd3
    mix_density_kg_m3           REAL,               -- Total fresh wet-mix density (sum of kg/m3 constituents)
    total_binder_kg_m3          REAL,               -- Total cementitious content (kg/m3)

    -- -----------------------------------------
    -- TEST CONDITIONS
    -- -----------------------------------------
    test_age_days               INTEGER,
    specimen_prep               VARCHAR(50),        -- cast | 3d_printed
    -- Specimen geometry: all dimensions in mm
    -- Common mortar specimens: 50x50x50 mm cube (2"x2"x2"), 40x40x160 mm prism (ASTM C348/C349)
    -- Standard concrete specimens: 150x300 mm cylinder (6"x12"), 100x200 mm cylinder (4"x8"),
    --   150x150x150 mm cube (EN 12390), 100x100x400 mm prism (ASTM C78)
    specimen_geometry           VARCHAR(50),        -- cube | cylinder | prism | dog-bone | printed_beam
    specimen_length_mm          REAL,               -- L dimension (or height for cylinders)
    specimen_width_mm           REAL,               -- W dimension (or diameter for cylinders)
    specimen_height_mm          REAL,               -- H dimension
    test_orientation            VARCHAR(20),        -- perpendicular | parallel | diagonal | cast
    test_orientation_code       VARCHAR(10),        -- X | Y | Z | XY_45 | CAST
    test_method_code            VARCHAR(50),        -- e.g. ASTM_C39, EN_12390_3
    n_specimens                 INTEGER,
    curing_regime               VARCHAR(100),       -- moist | sealed | ambient | steam
    curing_regime_code          VARCHAR(50),
    curing_temperature_c        REAL,
    curing_humidity_pct         REAL,
    curing_duration_days        REAL,

    -- -----------------------------------------
    -- 3DCP PROCESS PARAMETERS
    -- -----------------------------------------
    is_3d_printed               BOOLEAN,
    print_speed_mm_s            REAL,
    layer_height_mm             REAL,
    layer_time_gap_s            REAL,               -- Interlayer time interval AT A POINT (local return time path_length/print_speed, and/or an operator-imposed rest); a primary control on interlayer bond via surface dehydration
    nozzle_diameter_mm          REAL,
    nozzle_shape                VARCHAR(20),        -- circular | rectangular | custom
    nozzle_area_mm2             REAL,
    filament_width_mm           REAL,
    layer_width_mm              REAL,
    extrusion_rate_l_min        REAL,
    num_layers                  INTEGER,
    path_length_mm              REAL,
    infill_pattern              VARCHAR(50),        -- solid | zigzag | contour
    contour_count               INTEGER,
    print_direction             VARCHAR(20),

    -- Pumping System
    pump_type                   VARCHAR(50),        -- piston | progressive_cavity | peristaltic
    pump_pressure_bar           REAL,
    pump_rotational_speed_rpm   REAL,
    pump_distance_m             REAL,
    pipe_diameter_mm            REAL,
    pumping_duration_s          REAL,

    -- Mixing Process
    mixing_time_s               REAL,
    mixing_speed_rpm            REAL,
    mixer_type                  VARCHAR(50),        -- pan | planetary | twin-shaft | continuous
    shear_rate_per_s            REAL,               -- Applied shear rate (1/s)
    admixture_addition_point    VARCHAR(50),        -- dry | wet | delayed
    aggregate_prewetted         BOOLEAN,            -- Aggregate pre-wetted/pre-soaked before batching (common 3DCP practice)

    -- -----------------------------------------
    -- ENVIRONMENTAL CONDITIONS
    -- -----------------------------------------
    mix_temperature_c           REAL,
    ambient_temperature_c       REAL,
    ambient_humidity_pct        REAL,
    wind_speed_m_s              REAL,

    -- -----------------------------------------
    -- FRESH-STATE PROPERTIES
    -- -----------------------------------------
    slump_mm                    REAL,               -- ASTM C143
    spread_mm                   REAL,               -- ASTM C1611
    yield_stress_pa             REAL,
    plastic_viscosity_pa_s      REAL,
    static_yield_stress_pa      REAL,
    dynamic_yield_stress_pa     REAL,
    thixotropy_pa_per_s         REAL,               -- Structural buildup rate (Athix)
    structuration_rate_pa_per_s REAL,
    open_time_min               REAL,
    green_strength_kpa          REAL,               -- Fresh buildability strength
    air_content_fresh_pct       REAL,               -- ASTM C231
    unit_weight_fresh_kg_m3     REAL,               -- ASTM C138
    setting_time_initial_min    REAL,               -- ASTM C191 (Vicat)
    setting_time_final_min      REAL,               -- ASTM C191 (Vicat)
    bleeding_pct                REAL,               -- ASTM C232
    temperature_fresh_c         REAL,
    j_ring_mm                   REAL,               -- ASTM C1621
    v_funnel_s                  REAL,               -- EN 12350-9
    l_box_ratio                 REAL,               -- EN 12350-10
    segregation_resistance_pct  REAL,               -- EN 12350-11

    -- -----------------------------------------
    -- MECHANICAL PROPERTIES (HARDENED)
    -- -----------------------------------------
    design_strength_mpa         REAL,               -- Target/specified compressive strength (f'c)
    compressive_strength_mpa    REAL,               -- Measured compressive strength, ASTM C39 / EN 12390-3
    tensile_strength_mpa        REAL,               -- Direct (uniaxial) tensile strength; no consensus ASTM method for concrete (RILEM dog-bone / pull-off ASTM C1583). NOT C496 (splitting).
    splitting_tensile_mpa       REAL,               -- Splitting (Brazilian/indirect) tensile, ASTM C496
    flexural_strength_mpa       REAL,               -- ASTM C78
    elastic_modulus_gpa         REAL,               -- ASTM C469
    bond_strength_mpa           REAL,               -- ASTM C1583
    fracture_energy_n_m         REAL,               -- RILEM FMC-50
    toughness_index             REAL,               -- Toughness index I5/I10/I20 (ASTM C1018, WITHDRAWN 2006; current methods ASTM C1609/C1399)
    impact_resistance_j         REAL,               -- ACI 544.2R
    fatigue_life_cycles         REAL,
    density_hardened_kg_m3      REAL,               -- ASTM C642
    poissons_ratio              REAL,               -- ASTM C469

    -- -----------------------------------------
    -- 3DCP INTERLAYER PROPERTIES
    -- -----------------------------------------
    interlayer_bond_mpa         REAL,
    interlayer_shear_mpa        REAL,
    air_content_deposited_pct   REAL,
    void_area_fraction_pct      REAL,
    surface_roughness_avg       REAL,
    surface_moisture_state      VARCHAR(20),        -- dry | SSD | wet
    surface_treatment           VARCHAR(50),        -- none | scratch | bonding_agent

    -- -----------------------------------------
    -- DURABILITY PROPERTIES
    -- -----------------------------------------
    chloride_rcpt_coulombs      REAL,               -- ASTM C1202
    chloride_migration_coeff    REAL,               -- NT BUILD 492 (m2/s)
    chloride_diffusion_coeff    REAL,               -- ASTM C1556 (m2/s)
    carbonation_depth_1yr_mm    REAL,               -- Carbonation front depth; EN 12390-12 is ACCELERATED (elevated CO2) -- use EN 12390-10 for natural 1-year exposure
    carbonation_rate_coeff      REAL,               -- mm/sqrt(day)
    drying_shrinkage_28d_ue     REAL,               -- ASTM C157 (microstrain)
    autogenous_shrinkage_ue     REAL,               -- ASTM C1698 (microstrain)
    creep_coefficient           REAL,               -- ASTM C512
    freeze_thaw_cycles          REAL,               -- ASTM C666
    freeze_thaw_durability_factor REAL,             -- ASTM C666
    freeze_thaw_mass_loss_pct   REAL,
    sulfate_expansion_6mo_pct   REAL,               -- ASTM C1012
    sulfate_expansion_12mo_pct  REAL,               -- ASTM C1012
    asr_expansion_14d_pct       REAL,               -- ASTM C1260
    asr_expansion_1yr_pct       REAL,               -- ASTM C1293
    abrasion_depth_mm           REAL,               -- ASTM C779
    water_penetration_depth_mm  REAL,               -- EN 12390-8
    electrical_resistivity_kohm_cm REAL,            -- ASTM C1876
    porosity_pct                REAL,               -- Permeable (open) voids by immersion/boiling, ASTM C642 (open porosity, not total; MIP/vacuum is a separate method)
    water_absorption_pct        REAL,               -- ASTM C642
    sorptivity_mm_sqrt_s        REAL,               -- ASTM C1585 (initial rate, first 6 hours)
    sorptivity_secondary_mm_sqrt_s REAL,            -- ASTM C1585 (secondary rate, day 1-7)
    oxygen_permeability_m2      REAL,
    scaling_resistance_kg_m2    REAL,               -- ASTM C672
    corrosion_rate_ua_cm2       REAL,               -- ASTM C876
    half_cell_potential_mv      REAL,               -- ASTM C876
    heat_of_hydration_kj_kg    REAL,               -- ASTM C186

    -- -----------------------------------------
    -- THERMAL & ENVIRONMENTAL
    -- -----------------------------------------
    thermal_conductivity_w_mk   REAL,
    specific_heat_j_kg_k        REAL,
    coeff_thermal_expansion_ue_c REAL,
    fire_resistance_min         REAL,               -- ASTM E119
    embodied_carbon_kg_co2_m3   REAL,
    embodied_energy_mj_m3      REAL,

    -- -----------------------------------------
    -- MICROSTRUCTURE
    -- -----------------------------------------
    degree_of_hydration         REAL,               -- 0-1
    calcium_hydroxide_pct       REAL,               -- TGA/XRD
    pore_size_distribution_nm   REAL,               -- Critical pore diameter (MIP)

    -- -----------------------------------------
    -- MEASUREMENT UNCERTAINTY (v1.6) — mirrors mean + standard_deviation + N
    -- Same unit as the corresponding base column. n_specimens already exists above.
    -- -----------------------------------------
    compressive_strength_stddev_mpa REAL,           -- Std-dev of compressive strength across specimens
    flexural_strength_stddev_mpa    REAL,           -- Std-dev of flexural strength
    tensile_strength_stddev_mpa     REAL,           -- Std-dev of tensile / splitting strength
    elastic_modulus_stddev_gpa      REAL,           -- Std-dev of elastic modulus
    interlayer_bond_stddev_mpa      REAL,           -- Std-dev of interlayer bond strength

    -- -----------------------------------------
    -- RAW DATA REFERENCES (v1.6) — link curve/image/HDF5 files the flat schema can't hold inline
    -- File payloads stay external (CSV/HDF5/image); these columns preserve the reference (FAIR).
    -- -----------------------------------------
    raw_data_doi                VARCHAR(255),       -- DOI of a deposited raw-data record
    stress_strain_file          VARCHAR(255),       -- Load-displacement / stress-strain curve file
    rheology_curve_file         VARCHAR(255),       -- Flow / structuration curve file
    microstructure_image        VARCHAR(255),       -- SEM / CT / crack-pattern image file
    raw_data_file               VARCHAR(255),       -- Generic table / HDF5 raw-data reference

    -- -----------------------------------------
    -- DATA PROVENANCE
    -- -----------------------------------------
    doi                         VARCHAR(255),
    source_citation             VARCHAR(500),
    measurement_confidence      VARCHAR(20),        -- measured | calculated | estimated | reported
    lab_name                    VARCHAR(100),
    provenance_notes            TEXT,

    -- -----------------------------------------
    -- DATA QUALITY FLAGS
    -- -----------------------------------------
    is_training_ready           BOOLEAN DEFAULT false,
    is_synthetic                BOOLEAN DEFAULT false,
    outlier_flag                BOOLEAN DEFAULT false,

    -- -----------------------------------------
    -- EXPOSURE CLASSIFICATION (EN 206 / ACI 318)
    -- -----------------------------------------
    exposure_class_freeze       VARCHAR(10),        -- XF1-XF4
    exposure_class_sulfate      VARCHAR(10),        -- S0-S3
    exposure_class_chloride     VARCHAR(10),        -- XD1-XD3, XS1-XS3
    exposure_class_water        VARCHAR(10),
    exposure_class_asr          VARCHAR(10)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_mix_designs_training
    ON mix_designs(is_training_ready)
    WHERE is_training_ready = true;
CREATE INDEX IF NOT EXISTS idx_mix_designs_compressive
    ON mix_designs(compressive_strength_mpa)
    WHERE compressive_strength_mpa IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mix_designs_3d_printed
    ON mix_designs(is_3d_printed)
    WHERE is_3d_printed = true;

-- ===========================================
-- 2. strength_measurements (multi-age data)
--
-- test_age_days uses fractional days for hourly resolution:
--   1 hour  = 0.042 days      6 hours = 0.25 days
--   2 hours = 0.083 days     12 hours = 0.5 days
--   4 hours = 0.167 days     24 hours = 1.0 days
-- Then daily (1-7 days), then standard ages: 14, 21, 28, 56, 91, 365 days.
--
-- Hourly resolution is critical for 3DCP: operators need to know when
-- printed elements can be moved, shipped, or receive the next pour.
-- Green strength (kPa range) at 1-6 hours determines handling time.
-- ===========================================
CREATE TABLE IF NOT EXISTS strength_measurements (
    id                      SERIAL PRIMARY KEY,
    formulation_id          INTEGER NOT NULL REFERENCES mix_designs(id) ON DELETE CASCADE,
    test_age_days           REAL NOT NULL,           -- Fractional days (0.042 = 1 hour)

    compressive_mpa         REAL,
    tensile_mpa             REAL,
    flexural_mpa            REAL,
    elastic_modulus_gpa     REAL,

    test_method_code        VARCHAR(50),
    specimen_count          INTEGER,
    std_dev                 REAL,

    created_at              TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(formulation_id, test_age_days)
);

-- ===========================================
-- 3. sources (publication metadata)
-- ===========================================
CREATE TABLE IF NOT EXISTS sources (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR(500) NOT NULL,
    authors             TEXT,
    year                INTEGER,
    publisher           VARCHAR(200),
    doi_url             VARCHAR(500),
    license             VARCHAR(200),
    source_url          VARCHAR(500),
    date_accessed       DATE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- 4. test_methods (controlled vocabulary)
-- ===========================================
CREATE TABLE IF NOT EXISTS test_methods (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) UNIQUE NOT NULL,
    standard        VARCHAR(100) NOT NULL,
    property_type   VARCHAR(50) NOT NULL,
    description     TEXT,
    specimen_shape  VARCHAR(50),
    loading_rate    VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO test_methods (code, standard, property_type, description, specimen_shape, loading_rate)
VALUES
    ('ASTM_C39',    'ASTM C39/C39M',     'compressive', 'Compressive Strength of Cylindrical Concrete Specimens', 'cylinder', '0.25 MPa/s'),
    ('ASTM_C78',    'ASTM C78/C78M',     'flexural',    'Flexural Strength of Concrete (Third-Point Loading)', 'beam', '0.86-1.21 MPa/min'),
    ('ASTM_C496',   'ASTM C496/C496M',   'tensile',     'Splitting Tensile Strength of Cylindrical Concrete Specimens', 'cylinder', '0.7-1.4 MPa/min'),
    ('EN_12390_3',  'EN 12390-3',        'compressive', 'Testing hardened concrete - Compressive strength', 'cube', '0.6 MPa/s'),
    ('EN_12390_5',  'EN 12390-5',        'flexural',    'Testing hardened concrete - Flexural strength', 'beam', '0.04-0.06 MPa/s'),
    ('EN_12390_6',  'EN 12390-6',        'tensile',     'Testing hardened concrete - Tensile splitting strength', 'cylinder', '0.04-0.06 MPa/s'),
    ('RILEM_3DCP',  'RILEM TC 304-ADC',  'compressive', '3D Concrete Printing test method', 'printed', 'variable')
ON CONFLICT (code) DO NOTHING;

-- ===========================================
-- 5. curing_regimes (controlled vocabulary)
-- ===========================================
CREATE TABLE IF NOT EXISTS curing_regimes (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    temperature_c   NUMERIC,
    humidity_pct    NUMERIC,
    duration_type   VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO curing_regimes (code, name, description, temperature_c, humidity_pct, duration_type)
VALUES
    ('WATER_20C',       'Water Curing 20C',     'Immersed in water at 20+/-2C per EN 12390-2', 20, 100, 'continuous'),
    ('WATER_23C',       'Water Curing 23C',     'Immersed in water at 23+/-2C per ASTM C192', 23, 100, 'continuous'),
    ('MOIST_ROOM',      'Moist Room',           'Storage in moist room at >=95% RH', 23, 95, 'continuous'),
    ('SEALED',          'Sealed Curing',        'Sealed in plastic wrap or container', 23, NULL, 'continuous'),
    ('STEAM_60C',       'Steam Curing 60C',     'Accelerated steam curing at 60C', 60, 100, 'accelerated'),
    ('STEAM_80C',       'Steam Curing 80C',     'Accelerated steam curing at 80C', 80, 100, 'accelerated'),
    ('AUTOCLAVE',       'Autoclave',            'High-pressure steam curing', 180, 100, 'accelerated'),
    ('AIR_DRY',         'Air Drying',           'Ambient air curing (laboratory conditions)', 23, 50, 'continuous'),
    ('FIELD',           'Field Conditions',     'Cured under actual field conditions', NULL, NULL, 'variable'),
    ('CARBONATION',     'CO2 Curing',           'Accelerated carbonation curing', 23, 50, 'accelerated')
ON CONFLICT (code) DO NOTHING;

-- ===========================================
-- 6. standard_test_ages (reference schedule)
--
-- Recommended testing ages for 3DCP. Hourly resolution
-- in the first 24 hours captures early green strength
-- development critical for handling and shipping decisions.
-- ===========================================
CREATE TABLE IF NOT EXISTS standard_test_ages (
    days            REAL PRIMARY KEY,
    description     VARCHAR(100),
    is_standard     BOOLEAN DEFAULT true,
    notes           TEXT
);

INSERT INTO standard_test_ages (days, description, is_standard, notes)
VALUES
    -- Hourly (first 24 hours) — green strength / handling time
    (0.042, '1 hour',    true, 'Early green strength — can the piece hold its own weight?'),
    (0.083, '2 hours',   true, 'Early green strength'),
    (0.125, '3 hours',   true, 'Early green strength'),
    (0.167, '4 hours',   true, 'Typical earliest handling time for fast-set 3DCP'),
    (0.25,  '6 hours',   true, 'Common earliest safe-to-move time'),
    (0.333, '8 hours',   true, 'Overnight print assessment'),
    (0.5,   '12 hours',  true, 'Half-day strength check'),
    (0.75,  '18 hours',  true, 'Pre-demold check'),
    (1.0,   '24 hours',  true, 'One-day strength — common shipping threshold'),
    -- Daily (days 1-7) — early strength development
    (2,  '2 days',  true, 'Early strength'),
    (3,  '3 days',  true, 'ASTM C39 optional early age'),
    (5,  '5 days',  true, 'Mid-week check'),
    (7,  '7 days',  true, 'Standard early age per ASTM C39'),
    -- Standard ages (days 14-365) — design verification
    (14, '14 days',  true, 'Intermediate'),
    (21, '21 days',  true, 'Pre-28 day verification'),
    (28, '28 days',  true, 'Standard design age per ACI 318'),
    (56, '56 days',  true, 'Extended curing — mixes with SCMs'),
    (91, '91 days',  true, 'Long-term strength (13 weeks)'),
    (365, '1 year',  true, 'Annual verification')
ON CONFLICT (days) DO NOTHING;

COMMIT;
