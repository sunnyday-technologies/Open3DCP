#!/usr/bin/env python3
"""Generate crosswalk/units.csv — the machine-readable unit manifest, from sql/create_tables.sql.

Open3DCP embeds units in column names (compressive_strength_mpa) so a value can never be
entered or read under the wrong unit. That is a deliberate ergonomic choice for humans; this
manifest is its machine-readable counterpart, so a downstream consumer never has to parse a
column name to know what a number means, and never has to hard-code a conversion factor.

One row per mix_designs column:

  column, sql_type, section, unit, quantity_kind, si_mm_unit, si_mm_factor, fe_relevant, notes

`si_mm_factor` converts an Open3DCP value into the **SI(mm) consistent unit system** used by
finite-element codes (Abaqus and others), where length = mm, force = N, mass = tonne, time = s,
and the derived units follow: stress = MPa (= N/mm2), density = tonne/mm3, energy = mJ.
Requested by David Scheidt (ORCID 0009-0003-1996-4918) for a conversion-free structural export.

    value_si_mm = value_open3dcp * si_mm_factor

Factors are exact by construction (powers of ten and unit definitions); a blank factor means the
column is not a physical quantity (identifier, category, flag, date, file reference) or has no
meaningful FE analogue. `fe_relevant` flags the columns a structural model actually consumes.

Deterministic: suffix table + per-column overrides, driven by the schema's single source of
truth. Regenerate whenever the schema changes; the CSV is committed.

Run:  python scripts/build_units_manifest.py           # write
      python scripts/build_units_manifest.py --check   # verify committed CSV matches (CI)
"""
import csv
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "create_tables.sql"
OUT = ROOT / "crosswalk" / "units.csv"

COL_RE = re.compile(r"^\s{4}(\w+)\s+(SERIAL|VARCHAR|REAL|INTEGER|BOOLEAN|TEXT|DATE|TIMESTAMPTZ)", re.I)
SECTION_RE = re.compile(r"^\s+--\s*(?:-+\s*)?(.+?)\s*-*$")

# --- suffix -> (unit, quantity_kind, si_mm_unit, si_mm_factor) ----------------------------
# SI(mm): mm / N / tonne / s  =>  stress MPa, density tonne/mm3, energy mJ, power mW.
SUFFIX = [
    ("_mpa",            ("MPa",          "stress",              "MPa",           "1")),
    ("_gpa",            ("GPa",          "stress",              "MPa",           "1e3")),
    ("_kpa",            ("kPa",          "stress",              "MPa",           "1e-3")),
    ("_pa_per_s",       ("Pa/s",         "structuration_rate",  "MPa/s",         "1e-6")),
    ("_pa_s",           ("Pa*s",         "dynamic_viscosity",   "MPa*s",         "1e-6")),
    ("_pa",             ("Pa",           "stress",              "MPa",           "1e-6")),
    ("_kg_co2_m3",      ("kg CO2e/m3",   "gwp_intensity",       "tonne/mm3",     "1e-12")),
    ("_mj_m3",          ("MJ/m3",        "energy_density",      "mJ/mm3",        "1")),
    ("_kg_m3",          ("kg/m3",        "density",             "tonne/mm3",     "1e-12")),
    ("_kg_m2",          ("kg/m2",        "areal_mass",          "tonne/mm2",     "1e-9")),
    ("_kj_kg",          ("kJ/kg",        "specific_energy",     "mJ/tonne",      "1e9")),
    ("_j_kg_k",         ("J/(kg*K)",     "specific_heat",       "mJ/(tonne*K)",  "1e6")),
    ("_w_mk",           ("W/(m*K)",      "thermal_conductivity","mW/(mm*K)",     "1")),
    ("_ue_c",           ("microstrain/C","thermal_expansion",   "1/C",           "1e-6")),
    ("_ue",             ("microstrain",  "strain",              "1 (strain)",    "1e-6")),
    ("_n_m",            ("N/m",          "fracture_energy",     "N/mm",          "1e-3")),
    ("_mm_sqrt_s",      ("mm/s^0.5",     "sorptivity",          "mm/s^0.5",      "1")),
    ("_mm_s",           ("mm/s",         "velocity",            "mm/s",          "1")),
    ("_m_s",            ("m/s",          "velocity",            "mm/s",          "1e3")),
    ("_mm2",            ("mm2",          "area",                "mm2",           "1")),
    ("_m2",             ("m2",           "area",                "mm2",           "1e6")),
    ("_nm",             ("nm",           "length",              "mm",            "1e-6")),
    ("_mm",             ("mm",           "length",              "mm",            "1")),
    ("_m",              ("m",            "length",              "mm",            "1e3")),
    ("_l_min",          ("L/min",        "volumetric_flow",     "mm3/s",         "1e6/60")),
    ("_rpm",            ("rev/min",      "rotational_speed",    "1/s",           "1/60")),
    ("_bar",            ("bar",          "pressure",            "MPa",           "0.1")),
    ("_per_s",          ("1/s",          "rate",                "1/s",           "1")),
    ("_days",           ("d",            "time",                "s",             "86400")),
    ("_min",            ("min",          "time",                "s",             "60")),
    ("_s",              ("s",            "time",                "s",             "1")),
    ("_c",              ("degC",         "temperature",         "degC",          "1")),
    ("_pct",            ("%",            "fraction",            "1 (fraction)",  "1e-2")),
    ("_j",              ("J",            "energy",              "mJ",            "1e3")),
]

# Columns whose meaning the suffix table cannot infer, or which have no FE analogue.
OVERRIDES = {
    # composition: every constituent column is mass-% of total wet mix (v1.7 dual basis)
    "__composition__":       ("mass-% of total wet mix", "mass_fraction", "1 (fraction)", "1e-2",
                              "kg/m3 recoverable exactly via total_batched_mass_kg_m3"),
    "w_c_ratio":             ("1", "ratio", "1", "1", ""),
    "w_b_ratio":             ("1", "ratio", "1", "1", ""),
    "a_b_ratio":             ("1", "ratio", "1", "1", ""),
    "activator_ms_ratio":    ("1", "molar_ratio", "1", "1", ""),
    "poissons_ratio":        ("1", "ratio", "1", "1", ""),
    "l_box_ratio":           ("1", "ratio", "1", "1", ""),
    "degree_of_hydration":   ("1", "fraction", "1", "1", "0-1"),
    "toughness_index":       ("1", "index", "1", "1", "ASTM C1018 I5/I10/I20"),
    "creep_coefficient":     ("1", "ratio", "1", "1", ""),
    "fiber_aspect_ratio":    ("1", "ratio", "1", "1", "L/d"),
    "fine_agg_fineness_modulus": ("1", "index", "1", "1",
                              "ASTM C136 fineness modulus - dimensionless sum of cumulative retained %/100"),
    "freeze_thaw_cycles":    ("cycles", "count", "cycles", "1", ""),
    "fatigue_life_cycles":   ("cycles", "count", "cycles", "1", ""),
    "freeze_thaw_durability_factor": ("1", "index", "1", "1", "ASTM C666"),
    "num_layers":            ("layers", "count", "layers", "1", ""),
    "contour_count":         ("passes", "count", "passes", "1", ""),
    "n_specimens":           ("specimens", "count", "specimens", "1", ""),
    "surface_roughness_avg": ("mm", "length", "mm", "1", "unit assumed mm; state the method in provenance_notes"),
    "cement_strength_class_mpa": ("MPa", "classification", "", "",
                                  "EN 197-1 class label (32.5|42.5|52.5) verified on the EN 196-1 "
                                  "reference mortar - a cement descriptor, NOT a mix stress; do not feed to FE"),
    "chloride_rcpt_coulombs":("C", "electric_charge", "", "", "no FE analogue"),
    "chloride_migration_coeff": ("m2/s", "diffusivity", "mm2/s", "1e6", ""),
    "chloride_diffusion_coeff": ("m2/s", "diffusivity", "mm2/s", "1e6", ""),
    "carbonation_rate_coeff":("mm/d^0.5", "carbonation_rate", "mm/s^0.5", "1/293.938769", "1/sqrt(86400)"),
    "electrical_resistivity_kohm_cm": ("kohm*cm", "resistivity", "", "", "no FE analogue"),
    "corrosion_rate_ua_cm2": ("uA/cm2", "current_density", "", "", "no FE analogue"),
    "half_cell_potential_mv":("mV", "electric_potential", "", "", "no FE analogue"),
    "oxygen_permeability_m2":("m2", "intrinsic_permeability", "mm2", "1e6", ""),
    "fire_resistance_min":   ("min", "time", "s", "60", "rating, not a material property"),
    "pore_size_distribution_nm": ("nm", "length", "mm", "1e-6", "critical pore diameter (MIP)"),
}

# Columns a structural / thermal FE model actually consumes.
FE_RELEVANT = {
    "compressive_strength_mpa", "design_strength_mpa", "tensile_strength_mpa", "splitting_tensile_mpa",
    "flexural_strength_mpa", "elastic_modulus_gpa", "poissons_ratio", "density_hardened_kg_m3",
    "unit_weight_fresh_kg_m3", "fracture_energy_n_m", "bond_strength_mpa",
    "interlayer_bond_mpa", "interlayer_shear_mpa",
    "yield_stress_pa", "static_yield_stress_pa", "dynamic_yield_stress_pa", "plastic_viscosity_pa_s",
    "thixotropy_pa_per_s", "structuration_rate_pa_per_s", "green_strength_kpa",
    "thermal_conductivity_w_mk", "specific_heat_j_kg_k", "coeff_thermal_expansion_ue_c",
    "heat_of_hydration_kj_kg", "drying_shrinkage_28d_ue", "autogenous_shrinkage_ue",
    "creep_coefficient", "layer_height_mm", "layer_width_mm", "filament_width_mm",
    "nozzle_diameter_mm", "nozzle_area_mm2", "print_speed_mm_s", "layer_time_gap_s", "num_layers",
    "compressive_strength_stddev_mpa", "flexural_strength_stddev_mpa", "tensile_strength_stddev_mpa",
    "elastic_modulus_stddev_gpa", "interlayer_bond_stddev_mpa",
}

COMPOSITION_SECTIONS = {
    "Binder Materials", "Alkali Activators", "Additional Modifiers", "Pigments",
    "Aggregate Materials", "Fiber Reinforcement", "Chemical Admixtures",
    "Clay / VMA Rheology Modifiers", "Water",
}
# Non-mass columns living inside composition sections (characterization / metadata, not a mass-%).
NOT_A_MASS = re.compile(
    r"(_mm|_mpa|_pct|_ratio|_designation|_standard|_class|_class_mpa|_modulus|_kg_m3)$")


def parse_columns():
    cols, section, in_table = [], "Identity & Versioning", False
    for line in SQL.read_text(encoding="utf-8").splitlines():
        if "CREATE TABLE IF NOT EXISTS mix_designs" in line:
            in_table = True
            continue
        if in_table and re.match(r"^\s*\);", line):
            break
        if not in_table:
            continue
        if line.strip().startswith("--"):
            m = SECTION_RE.match(line)
            if m:
                label = m.group(1).strip()
                if label and (label.isupper() or "(mass-%)" in label or label.istitle()):
                    label = label.split("—")[-1].split("--")[-1].strip()
                    label = re.sub(r"\s*\(mass-%\)\s*$", "", label)
                    if 2 < len(label) < 60 and not label.startswith("NOTE"):
                        section = label
            continue
        m = COL_RE.match(line)
        if m:
            col, typ = m.group(1), m.group(2).upper()
            if col == "id":
                continue
            cols.append((col, typ, section))
    return cols


def classify(col, sql_type, section):
    """-> (unit, quantity_kind, si_mm_unit, si_mm_factor, notes)"""
    if col in OVERRIDES:
        return OVERRIDES[col]
    if sql_type in ("VARCHAR", "TEXT", "DATE", "TIMESTAMPTZ", "BOOLEAN"):
        kind = {"BOOLEAN": "flag", "DATE": "date", "TIMESTAMPTZ": "timestamp"}.get(sql_type, "categorical")
        return ("-", kind, "", "", "")
    for suffix, (unit, kind, si_unit, factor) in SUFFIX:
        if col.endswith(suffix):
            return (unit, kind, si_unit, factor, "")
    if section in COMPOSITION_SECTIONS and not NOT_A_MASS.search(col):
        return OVERRIDES["__composition__"]
    return ("", "UNMAPPED", "", "", "")


def render(cols):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["column", "sql_type", "section", "unit", "quantity_kind",
                "si_mm_unit", "si_mm_factor", "fe_relevant", "notes"])
    unmapped = []
    for col, typ, section in cols:
        unit, kind, si_unit, factor, notes = classify(col, typ, section)
        if kind == "UNMAPPED":
            unmapped.append(col)
        w.writerow([col, typ.lower(), section, unit, kind, si_unit, factor,
                    "yes" if col in FE_RELEVANT else "", notes])
    return buf.getvalue(), unmapped


def main(check_only=False):
    cols = parse_columns()
    text, unmapped = render(cols)
    if unmapped:
        print("FAIL: columns with no unit classification — add a suffix rule or an override:")
        for c in unmapped:
            print(f"  - {c}")
        return 1
    print(f"parsed {len(cols)} data columns from {SQL.relative_to(ROOT)}")
    if check_only:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"FAIL: {OUT.relative_to(ROOT)} is stale — run scripts/build_units_manifest.py")
            return 1
        print(f"checked {OUT.relative_to(ROOT)}: up to date")
        return 0
    OUT.write_text(text, encoding="utf-8")
    fe = sum(1 for c, _, _ in cols if c in FE_RELEVANT)
    conv = text.count("\n") - 1
    print(f"wrote {OUT.relative_to(ROOT)}: {conv} columns, {fe} flagged FE-relevant")
    return 0


if __name__ == "__main__":
    sys.exit(main(check_only="--check" in sys.argv))
