-- ====================================================================
-- Open3DCP v1.0 — Reference SQL Implementation
-- https://github.com/sunnyday-technologies/Open3DCP
--
-- Apache License 2.0 — Sunnyday Technologies
--
-- This file creates the Open3DCP schema in PostgreSQL.
-- Adapt column types and constraints for your database engine.
-- All material quantities in mass-% of total wet mix (0-100).
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
    created_at                  TIMESTAMPTZ DEFAULT NOW(),

    -- -----------------------------------------
    -- COMPOSITION — Binder Materials (mass-%)
    -- -----------------------------------------
    cement_type_1               REAL DEFAULT 0,     -- OPC, ASTM C150 Type I
    cement_type_1l              REAL DEFAULT 0,     -- Portland-limestone, EN 197-1 CEM II/A-L
    cement_type_3               REAL DEFAULT 0,     -- Rapid hardening, ASTM C150 Type III
    cement_type_4               REAL DEFAULT 0,     -- Low-heat, ASTM C150 Type IV
    cac                         REAL DEFAULT 0,     -- Calcium aluminate cement, EN 14647
    csa_cement                  REAL DEFAULT 0,     -- Calcium sulfoaluminate cement
    fly_ash                     REAL DEFAULT 0,     -- Fly ash (class not specified)
    fly_ash_type_f              REAL DEFAULT 0,     -- Class F (SiO2+Al2O3+Fe2O3 >= 70%), ASTM C618
    fly_ash_type_c              REAL DEFAULT 0,     -- Class C (SiO2+Al2O3+Fe2O3 >= 50%), ASTM C618
    silica_fume                 REAL DEFAULT 0,     -- Microsilica, ASTM C1240
    nano_silica                 REAL DEFAULT 0,     -- Nano-SiO2 (<100 nm)
    slag                        REAL DEFAULT 0,     -- GGBFS, ASTM C989
    metakaolin                  REAL DEFAULT 0,     -- Calcined kaolin, ASTM C618 Class N
    limestone                   REAL DEFAULT 0,     -- Limestone filler, EN 12620
    pumice                      REAL DEFAULT 0,     -- Natural pozzolan, ASTM C618 Class N
    bottom_ash                  REAL DEFAULT 0,     -- Coal bottom ash

    -- Aggregate Materials (mass-%, FM-graded for sand)
    fine_sand                   REAL DEFAULT 0,     -- FM 1.6-2.2 (Open3DCP convention)
    medium_sand                 REAL DEFAULT 0,     -- FM 2.3-3.0 (Open3DCP convention)
    coarse_sand                 REAL DEFAULT 0,     -- FM 3.1-3.7 (Open3DCP convention)
    agg_4mm                     REAL DEFAULT 0,     -- Nominal max 4 mm
    agg_6mm                     REAL DEFAULT 0,     -- 4-6 mm
    agg_10mm                    REAL DEFAULT 0,     -- 6-10 mm
    agg_14mm                    REAL DEFAULT 0,     -- 10-14 mm
    agg_20mm                    REAL DEFAULT 0,     -- 14-20 mm

    -- Fiber Reinforcement (mass-%)
    steel_fiber                 REAL DEFAULT 0,
    pp_fiber                    REAL DEFAULT 0,     -- Polypropylene
    glass_fiber                 REAL DEFAULT 0,     -- Alkali-resistant
    carbon_fiber                REAL DEFAULT 0,
    pva_fiber                   REAL DEFAULT 0,     -- Polyvinyl alcohol
    basalt_fiber                REAL DEFAULT 0,
    nylon_fiber                 REAL DEFAULT 0,
    aramid_fiber                REAL DEFAULT 0,
    fiber_length_mm             REAL,               -- Dominant fiber length

    -- Chemical Admixtures (mass-%)
    superplasticizer            REAL DEFAULT 0,     -- HRWR, ASTM C494 Type F/G
    water_reducer               REAL DEFAULT 0,     -- MRWR, ASTM C494 Type A
    accelerator                 REAL DEFAULT 0,     -- ASTM C494 Type C/E
    calcium_formate             REAL DEFAULT 0,     -- Organic salt accelerator
    retarder                    REAL DEFAULT 0,     -- ASTM C494 Type B/D
    air_entrainer               REAL DEFAULT 0,     -- ASTM C260
    vma                         REAL DEFAULT 0,     -- Viscosity-modifying admixture
    shrinkage_reducer           REAL DEFAULT 0,
    corrosion_inhibitor         REAL DEFAULT 0,

    -- Clay / VMA Rheology Modifiers (mass-%)
    hpmc                        REAL DEFAULT 0,     -- Hydroxypropyl methylcellulose
    sepiolite_clay              REAL DEFAULT 0,     -- Chain silicate thixotropy agent
    attapulgite                 REAL DEFAULT 0,     -- Palygorskite
    calcium_bentonite           REAL DEFAULT 0,     -- Smectite

    -- Water
    water                       REAL DEFAULT 0,

    -- -----------------------------------------
    -- KEY RATIOS
    -- -----------------------------------------
    w_c_ratio                   REAL,               -- water / cement
    w_b_ratio                   REAL,               -- water / total binder
    a_b_ratio                   REAL,               -- aggregate / binder
    water_premix_pct            REAL,               -- % water added during pre-mix
    water_temperature_c         REAL,               -- Water temperature at mixing (C)

    -- -----------------------------------------
    -- TEST CONDITIONS
    -- -----------------------------------------
    test_age_days               INTEGER DEFAULT 28,
    specimen_prep               VARCHAR(50),        -- cast | 3d_printed
    specimen_geometry           VARCHAR(50),        -- cube | cylinder | prism | dog-bone
    specimen_length_mm          REAL,
    specimen_width_mm           REAL,
    specimen_height_mm          REAL,
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
    is_3d_printed               BOOLEAN DEFAULT false,
    print_speed_mm_s            REAL,
    layer_height_mm             REAL,
    layer_time_gap_s            REAL,               -- Interlayer time interval
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
    shear_rate_s                REAL,               -- Applied shear rate (1/s)
    admixture_addition_point    VARCHAR(50),        -- dry | wet | delayed

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
    compressive_strength_mpa    REAL,               -- ASTM C39 / EN 12390-3
    tensile_strength_mpa        REAL,               -- ASTM C496
    splitting_tensile_mpa       REAL,               -- ASTM C496
    flexural_strength_mpa       REAL,               -- ASTM C78
    elastic_modulus_gpa         REAL,               -- ASTM C469
    bond_strength_mpa           REAL,               -- ASTM C1583
    fracture_energy_n_m         REAL,               -- RILEM FMC-50
    toughness_index             REAL,               -- ASTM C1018
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
    carbonation_depth_1yr_mm    REAL,               -- EN 12390-12
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
    porosity_pct                REAL,               -- ASTM C642
    water_absorption_pct        REAL,               -- ASTM C642
    sorptivity_mm_sqrt_s        REAL,               -- ASTM C1585
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
    fire_resistance_min         REAL,
    embodied_carbon_kg_co2_m3   REAL,
    embodied_energy_mj_m3      REAL,

    -- -----------------------------------------
    -- MICROSTRUCTURE
    -- -----------------------------------------
    degree_of_hydration         REAL,               -- 0-1
    calcium_hydroxide_pct       REAL,               -- TGA/XRD
    pore_size_distribution_nm   REAL,               -- Critical pore diameter (MIP)

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
-- ===========================================
CREATE TABLE IF NOT EXISTS strength_measurements (
    id                      SERIAL PRIMARY KEY,
    formulation_id          INTEGER NOT NULL REFERENCES mix_designs(id) ON DELETE CASCADE,
    test_age_days           REAL NOT NULL,

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

COMMIT;
