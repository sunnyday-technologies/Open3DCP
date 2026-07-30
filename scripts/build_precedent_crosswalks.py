#!/usr/bin/env python3
"""Generate the precedent/data-model crosswalk CSVs from sql/create_tables.sql.

Emits crosswalk/open3dcp_to_{amcdm,gemd,cpto}.csv — one row per mix_designs data
column, mapping it onto three external data models / ontologies:

  - AM-CDM  : Additive Manufacturing Common Data Model
              (github.com/AM-CDM/AM-CDM; Kuan et al. 2024, doi:10.1007/s40192-024-00341-x)
  - GEMD    : Graphical Expression of Materials Data, format v0.1
              (citrineinformatics.github.io/gemd-docs)
  - CPTO    : Concrete Production and Testing Ontology v1.0.1 (w3id.org/cpto;
              Meng et al. 2023, doi:10.1002/cepa.2955; built on PMDco 2.0 + PROV-O)

Deterministic: section-level defaults + column-level overrides, driven by the
schema's single source of truth (sql/create_tables.sql), the same pattern as the
figure scripts. Regenerate whenever the schema changes; the CSVs are committed.

Mapping classes (structural, for model/ontology targets — distinct from the
ingestion fidelity classes in crosswalk/README.md used for dataset crosswalks):

  exact      same quantity exists in the target; unit conversion at most
  normalized same information, restructured (column -> class instance/attribute)
  derived    computable from other mapped fields
  partial    target holds only a subset or coarser form of the information
  sidecar    needs a linked non-flat record (planned context/measurement sidecars)
  no_map     no target entity exists — for the 3DCP blocks this is the point:
             the extrusion vocabulary is Open3DCP's additive contribution
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "create_tables.sql"
OUT = ROOT / "crosswalk"

# (comment-prefix, section key) — first match wins; non-matching comments are notes
SECTION_KEYS = [
    ("Identity & Versioning", "identity"),
    ("COMPOSITION", "binders"),
    ("Alkali Activators", "activators"),
    ("Additional Modifiers", "modifiers"),
    ("Pigments", "pigments"),
    ("Aggregate Materials", "aggregates"),
    ("Fiber Reinforcement", "fibers"),
    ("Fiber characterization", "fiber_char"),
    ("Chemical Admixtures", "admixtures"),
    ("Clay / VMA", "clay_vma"),
    ("Water", "water"),
    ("KEY RATIOS", "ratios"),
    ("AGGREGATE CONDITIONING", "agg_conditioning"),
    ("MIX BASIS", "mix_basis"),
    ("TEST CONDITIONS", "test_conditions"),
    ("3DCP PROCESS PARAMETERS", "process"),
    ("Pumping System", "pumping"),
    ("Mixing Process", "mixing"),
    ("ENVIRONMENTAL CONDITIONS", "environment"),
    ("FRESH-STATE PROPERTIES", "fresh"),
    ("MECHANICAL PROPERTIES", "mechanical"),
    ("3DCP INTERLAYER", "interlayer"),
    ("DURABILITY", "durability"),
    ("THERMAL", "thermal"),
    ("MICROSTRUCTURE", "microstructure"),
    ("MEASUREMENT UNCERTAINTY", "uncertainty"),
    ("RAW DATA REFERENCES", "raw_refs"),
    ("DATA PROVENANCE", "provenance"),
    ("DATA QUALITY", "quality"),
    ("EXPOSURE", "exposure"),
]

BLOCK = {  # CPPC reporting block per section (informational)
    "identity": "Provenance",
    "binders": "Composition", "activators": "Composition", "modifiers": "Composition",
    "pigments": "Composition", "aggregates": "Composition", "fibers": "Composition",
    "fiber_char": "Composition", "admixtures": "Composition", "clay_vma": "Composition",
    "water": "Composition", "ratios": "Composition", "agg_conditioning": "Composition",
    "mix_basis": "Composition",
    "test_conditions": "Conditions", "environment": "Conditions", "exposure": "Conditions",
    "process": "Processing", "pumping": "Processing", "mixing": "Processing",
    "fresh": "Properties", "mechanical": "Properties", "interlayer": "Properties",
    "durability": "Properties", "thermal": "Properties", "microstructure": "Properties",
    "uncertainty": "Properties",
    "raw_refs": "Provenance", "provenance": "Provenance", "quality": "Provenance",
}

COL_RE = re.compile(
    r"^\s{4}(\w+)\s+(SERIAL|VARCHAR|REAL|INTEGER|BOOLEAN|TEXT|DATE|TIMESTAMPTZ)", re.I
)
COMMENT_RE = re.compile(r"^\s+--\s*(.+?)\s*$")


def parse_columns():
    in_table, section, cols = False, None, []
    for line in SQL.read_text(encoding="utf-8").splitlines():
        if line.startswith("CREATE TABLE IF NOT EXISTS mix_designs"):
            in_table = True
            continue
        if in_table and line.startswith(");"):
            break
        if not in_table:
            continue
        m = COMMENT_RE.match(line)
        if m:
            for prefix, key in SECTION_KEYS:
                if m.group(1).startswith(prefix):
                    section = key
                    break
            continue
        m = COL_RE.match(line)
        if m and m.group(2).upper() != "SERIAL":  # skip the SERIAL primary key
            if section is None:
                sys.exit(f"column {m.group(1)} appeared before any known section")
            cols.append((m.group(1), section))
    return cols


# --- AM-CDM ------------------------------------------------------------------
AMCDM_COMPOSITION = (
    "material: Material — constituent + dosage",
    "partial",
    "AM-CDM's composition model is alloy/powder-shaped; a multi-constituent "
    "cementitious mix needs a material-module domain extension",
)
AMCDM_PROCESS_NOTE = (
    "held as generic ProcessParameters; no controlled extrusion-3DCP vocabulary "
    "exists in AM-CDM — the Open3DCP process block is a candidate domain profile"
)
AMCDM_DEFAULTS = {
    "identity": ("material: Material — identity/lineage attributes", "normalized", ""),
    "binders": AMCDM_COMPOSITION, "activators": AMCDM_COMPOSITION,
    "modifiers": AMCDM_COMPOSITION, "pigments": AMCDM_COMPOSITION,
    "aggregates": AMCDM_COMPOSITION, "fibers": AMCDM_COMPOSITION,
    "admixtures": AMCDM_COMPOSITION, "clay_vma": AMCDM_COMPOSITION,
    "water": AMCDM_COMPOSITION,
    "fiber_char": ("material: Material — intrinsic properties", "normalized", ""),
    "ratios": ("material: Material — derived properties", "derived", ""),
    "agg_conditioning": ("material: Material — extrinsic state (storage/condition)", "partial", ""),
    "mix_basis": ("base: Measurement (value + unit + meta)", "partial",
                  "record-basis semantics; no direct AM-CDM concept"),
    "test_conditions": ("TIC: ticMaterialSpecimen / ticStandard", "normalized", ""),
    "process": ("build/process: Build -> ProcessStep -> ProcessParameters", "normalized", AMCDM_PROCESS_NOTE),
    "pumping": ("system/process: AMSystem component + ProcessParameters", "normalized", AMCDM_PROCESS_NOTE),
    "mixing": ("system/process: AMSystem component + ProcessParameters", "normalized", AMCDM_PROCESS_NOTE),
    "environment": ("build/TIC: build environment / ticEnvironment", "normalized", ""),
    "fresh": ("TIC: TestInspectionCharacterization -> TestResult", "normalized",
              "generic TestResult; no fresh-rheology vocabulary"),
    "mechanical": ("TIC: TestInspectionCharacterization -> TestResult", "normalized", ""),
    "interlayer": ("TIC: TestInspectionCharacterization -> TestResult", "normalized",
                   "generic TestResult; no interlayer-bond vocabulary"),
    "durability": ("TIC: TestInspectionCharacterization -> TestResult", "normalized", ""),
    "thermal": ("TIC: TestInspectionCharacterization -> TestResult", "normalized", ""),
    "microstructure": ("TIC: TestInspectionCharacterization -> TestResult", "normalized", ""),
    "uncertainty": ("base: Measurement (value + uncertainty meta)", "normalized", ""),
    "raw_refs": ("base: Document", "normalized", ""),
    "provenance": ("base: Document / Organization / Person", "normalized", ""),
    "quality": ("-", "no_map", "analysis-layer quality flags have no AM-CDM concept"),
    "exposure": ("material: Material specification", "partial",
                 "EN 206/ACI exposure classes have no AM-CDM concept"),
}
AMCDM_OVERRIDES = {
    "date_of_casting": ("build: Build / ProcessStep timing", "normalized", ""),
    "created_at": ("base: record metadata", "partial", ""),
    "is_3d_printed": ("process: process category (ISO/ASTM 52900)", "normalized",
                      "material extrusion exists as a 52900 category; no construction profile"),
    "test_orientation": ("TIC: ticMaterialSpecimen — orientation", "partial",
                         "no 3DCP layer-orientation coding vocabulary"),
    "test_orientation_code": ("TIC: ticMaterialSpecimen — orientation", "partial",
                              "no 3DCP layer-orientation coding vocabulary"),
    "lab_name": ("base: Organization", "normalized", ""),
    "measurement_confidence": ("-", "no_map",
                               "no measured/calculated/estimated/reported concept; carry as annotation"),
}

# --- GEMD --------------------------------------------------------------------
GEMD_COMPOSITION = (
    "IngredientSpec/IngredientRun (mass_fraction) -> mixing ProcessSpec -> MaterialSpec/Run",
    "normalized", "",
)
GEMD_PARAM_NOTE = ("no controlled 3DCP parameter templates exist; "
                   "project-defined AttributeTemplates required")
GEMD_DEFAULTS = {
    "identity": ("object identifiers / tags on MaterialSpec–MaterialRun", "normalized", ""),
    "binders": GEMD_COMPOSITION, "activators": GEMD_COMPOSITION,
    "modifiers": GEMD_COMPOSITION, "pigments": GEMD_COMPOSITION,
    "aggregates": GEMD_COMPOSITION, "fibers": GEMD_COMPOSITION,
    "admixtures": GEMD_COMPOSITION, "clay_vma": GEMD_COMPOSITION,
    "water": GEMD_COMPOSITION,
    "fiber_char": ("Property on the ingredient MaterialSpec", "normalized", ""),
    "ratios": ("derived Property on MaterialSpec", "derived", ""),
    "agg_conditioning": ("Condition on the mixing ProcessRun", "normalized", ""),
    "mix_basis": ("quantity basis on IngredientRun + tags", "normalized",
                  "GEMD quantities carry an explicit basis (mass/volume/number fraction, absolute)"),
    "test_conditions": ("Condition/Parameter on MeasurementSpec–MeasurementRun", "normalized", ""),
    "process": ("Parameter on the printing ProcessSpec–ProcessRun", "normalized", GEMD_PARAM_NOTE),
    "pumping": ("Parameter on the printing ProcessSpec–ProcessRun", "normalized", GEMD_PARAM_NOTE),
    "mixing": ("Parameter on the mixing ProcessSpec–ProcessRun", "normalized", GEMD_PARAM_NOTE),
    "environment": ("Condition on ProcessRun / MeasurementRun", "normalized", ""),
    "fresh": ("Property on MeasurementRun", "normalized", ""),
    "mechanical": ("Property on MeasurementRun", "normalized", ""),
    "interlayer": ("Property on MeasurementRun", "normalized", ""),
    "durability": ("Property on MeasurementRun", "normalized", ""),
    "thermal": ("Property on MeasurementRun", "normalized", ""),
    "microstructure": ("Property on MeasurementRun", "normalized", ""),
    "uncertainty": ("uncertainty on the value object (e.g. NormalReal)", "normalized",
                    "GEMD values carry native uncertainty"),
    "raw_refs": ("FileLink", "normalized", ""),
    "provenance": ("source / performed_by / tags on Runs", "partial",
                   "GEMD's Spec-vs-Run split (planned vs actual) has no flat-row equivalent"),
    "quality": ("tags", "partial", ""),
    "exposure": ("Condition / classification tag", "partial", ""),
}
GEMD_OVERRIDES = {}

# --- CPTO --------------------------------------------------------------------
CPTO_NOMAP_3DCP = ("-", "no_map",
                   "no printing/extrusion concepts in CPTO (verified: zero matches in the v1.0.1 RDF)")
CPTO_DEFAULTS = {
    "identity": ("PROV-O entity + cpto:Batch context", "partial", ""),
    "binders": ("cpto constituent class + QuantityInMix", "partial",
                "EN 197-1-oriented taxonomy; ASTM classes do not map 1:1"),
    "activators": ("-", "no_map", "alkali-activated systems are outside CPTO's EN 206 scope"),
    "modifiers": ("cpto:Addition / Additives", "partial", ""),
    "pigments": ("cpto:Pigments + QuantityInMix", "normalized", ""),
    "aggregates": ("cpto:Aggregate + QuantityInMix", "partial",
                   "no fineness-modulus or ASTM C33 size-number subdivision (EN d/D designations)"),
    "fibers": ("cpto:Fibres (Steel/Polymer)", "partial",
               "only steel/polymer fibre classes verified in v1.0.1"),
    "fiber_char": ("-", "no_map", "no fibre-geometry classes found in CPTO v1.0.1"),
    "admixtures": ("cpto:Admixture + QuantityInMix", "partial",
                   "no per-function admixture subclasses verified"),
    "clay_vma": ("cpto:Addition / Admixture", "partial", ""),
    "water": ("cpto:Water + QuantityInMix", "normalized", ""),
    "ratios": ("-", "no_map", ""),
    "agg_conditioning": ("-", "no_map", "aggregate moisture state not modeled"),
    "mix_basis": ("QuantityInMix unit handling", "partial",
                  "record-basis flags are Open3DCP conversion metadata"),
    "test_conditions": ("test metadata on determination classes", "partial", ""),
    "process": CPTO_NOMAP_3DCP,
    "pumping": CPTO_NOMAP_3DCP,
    "mixing": ("cpto:ConcreteMixer + mixing-process template", "partial", ""),
    "environment": ("-", "no_map", "only cpto:Site location context"),
    "fresh": ("-", "no_map", "no fresh-rheometry / 3DCP printability concepts in CPTO"),
    "mechanical": ("-", "no_map", "not in the verified v1.0.1 test inventory"),
    "interlayer": ("-", "no_map", "no interlayer/anisotropy concepts (cast concrete)"),
    "durability": ("-", "no_map", "not in the verified v1.0.1 test inventory"),
    "thermal": ("-", "no_map", ""),
    "microstructure": ("-", "no_map", ""),
    "uncertainty": ("PMDco value-specification pattern", "partial",
                    "CPTO adds none; PMDco 2.0 value specifications can carry uncertainty"),
    "raw_refs": ("PROV-O entities (imported)", "normalized", ""),
    "provenance": ("PROV-O attribution + cpto:ConcreteManufacturer / Site", "normalized", ""),
    "quality": ("-", "no_map", ""),
    "exposure": ("cpto:ExposureClass", "normalized", ""),
}
CPTO_OVERRIDES = {
    "batch_label": ("cpto:Batch", "normalized", ""),
    "material_class": ("cpto concrete-type classes (designed/prescribed, SCC, precast, ...)", "partial", ""),
    "date_of_casting": ("cpto casting/placement context (CastingDevice)", "partial", ""),
    "cement_type_1l": ("cpto:Cement (EN 197-1 CEM II/A-L)", "normalized", ""),
    "cement_unspecified": ("cpto:Cement + QuantityInMix", "normalized", "type stays unclassified"),
    "cac": ("-", "no_map", "outside CPTO's EN 197-1 cement enumeration"),
    "csa_cement": ("-", "no_map", "outside CPTO's EN 197-1 cement enumeration"),
    "fly_ash": ("cpto:FlyAsh + QuantityInMix", "normalized", ""),
    "fly_ash_type_f": ("cpto:FlyAsh + QuantityInMix", "partial", "no ASTM C618 F/C split in CPTO"),
    "fly_ash_type_c": ("cpto:FlyAsh + QuantityInMix", "partial", "no ASTM C618 F/C split in CPTO"),
    "silica_fume": ("cpto:SilicaFume + QuantityInMix", "normalized", ""),
    "slag": ("cpto:GGBS / BlastFurnaceSlag + QuantityInMix", "normalized", ""),
    "limestone": ("cpto:LimestonePowder + QuantityInMix", "normalized", ""),
    "nano_silica": ("cpto:Addition (Type II)", "partial", ""),
    "metakaolin": ("cpto:Addition (Type II)", "partial", ""),
    "pumice": ("cpto:Addition (Type II)", "partial", ""),
    "bottom_ash": ("cpto:Addition (Type II)", "partial", ""),
    "rice_husk_ash": ("cpto:Addition (Type II)", "partial", ""),
    "recycled_sand": ("cpto:Aggregate (recycled)", "normalized", ""),
    "steel_fiber": ("cpto:SteelFibre + QuantityInMix", "normalized", ""),
    "pp_fiber": ("cpto:PolymerFibre + QuantityInMix", "partial", ""),
    "pva_fiber": ("cpto:PolymerFibre + QuantityInMix", "partial", ""),
    "nylon_fiber": ("cpto:PolymerFibre + QuantityInMix", "partial", ""),
    "water_premix_pct": ("-", "no_map", "mixing-procedure detail not modeled"),
    "water_temperature_c": ("-", "no_map", "mixing-procedure detail not modeled"),
    "w_c_ratio": ("cpto:WaterCementRatio", "exact", ""),
    "w_b_ratio": ("cpto:EquivalentWaterCementRatio", "partial",
                  "w/b counts all cementitious mass; CPTO's equivalent w/c applies k-value weighting"),
    "test_age_days": ("cpto:SpecimenAge", "exact", ""),
    "test_method_code": ("cpto:DINStandard / ENStandard", "partial", "ASTM methods not modeled"),
    "curing_regime": ("curing/storage knowledge-graph templates", "partial",
                      "curing lives mainly in CPTO's companion KG templates"),
    "curing_regime_code": ("curing/storage knowledge-graph templates", "partial", ""),
    "curing_temperature_c": ("curing/storage knowledge-graph templates", "partial", ""),
    "curing_humidity_pct": ("curing/storage knowledge-graph templates", "partial", ""),
    "curing_duration_days": ("curing/storage knowledge-graph templates", "partial", ""),
    "design_strength_mpa": ("cpto:CompressiveStrengthClass", "partial", ""),
    "test_orientation": ("-", "no_map", "print-direction anisotropy has no cast-concrete analogue"),
    "test_orientation_code": ("-", "no_map", "print-direction anisotropy has no cast-concrete analogue"),
    "specimen_geometry": ("implied by CompressiveStrengthCube/Cylinder", "partial", ""),
    "slump_mm": ("cpto:Consistency / SlumpClass", "normalized", ""),
    "spread_mm": ("cpto:FlowTableTest / FlowSpread", "normalized", ""),
    "air_content_fresh_pct": ("cpto:EntrainedAir", "normalized", ""),
    "j_ring_mm": ("cpto:PassingAbility", "partial", ""),
    "l_box_ratio": ("cpto:PassingAbility", "partial", ""),
    "v_funnel_s": ("cpto:ViscosityOfConcrete", "partial", ""),
    "segregation_resistance_pct": ("cpto:SegregationResistance", "normalized", ""),
    "compressive_strength_mpa": ("cpto:DeterminationOfCompressiveStrength -> ConcreteCompressiveStrength",
                                 "normalized", "cube/cylinder via specimen geometry"),
    "splitting_tensile_mpa": ("cpto:TensileSplittingStrength", "normalized", ""),
    "elastic_modulus_gpa": ("cpto:DeterminationOfSecantModulusOfElasticity", "normalized", ""),
    "heat_of_hydration_kj_kg": ("cpto:DeterminationOfHeatOfHydration", "normalized", ""),
    "embodied_carbon_kg_co2_m3": ("-", "no_map", "LCA/GWP not modeled"),
    "measurement_confidence": ("-", "no_map", ""),
}

TARGETS = {
    "open3dcp_to_amcdm.csv": (AMCDM_DEFAULTS, AMCDM_OVERRIDES),
    "open3dcp_to_gemd.csv": (GEMD_DEFAULTS, GEMD_OVERRIDES),
    "open3dcp_to_cpto.csv": (CPTO_DEFAULTS, CPTO_OVERRIDES),
}


def main():
    cols = parse_columns()
    print(f"parsed {len(cols)} data columns from {SQL.relative_to(ROOT)}")
    for fname, (defaults, overrides) in TARGETS.items():
        counts = Counter()
        path = OUT / fname
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["open3dcp_column", "block", "target_entity", "mapping_class", "notes"])
            for col, section in cols:
                entity, mclass, note = overrides.get(col, defaults[section])
                counts[mclass] += 1
                w.writerow([col, BLOCK[section], entity, mclass, note])
        summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"wrote {path.relative_to(ROOT)}: {summary}")


if __name__ == "__main__":
    main()
