#!/usr/bin/env python3
"""Reproduce the Meta SustainableConcrete (BOxCrete) -> Open3DCP curated excerpt.

The source is a single flat kg/m3 table released by Meta (Meta Platforms / FAIR) with the
University of Illinois Urbana-Champaign and Amrize, under the MIT license:

    https://github.com/facebookresearch/SustainableConcrete  ->  data/boxcrete_data.csv

That file is NOT re-hosted here. Download it from the repo, then run:

    python build/extract.py /path/to/boxcrete_data.csv

This selects a representative six-mix excerpt (plain / fly-ash / slag / ternary, mortar and
concrete, spanning the carbon and strength range) and writes the canonical flat CSV that the
`open3dcp-ingest --kind flat` reader consumes. Source-specific unit quirks are converted here and
documented: compressive strength psi -> MPa (x 0.00689476), slump in -> mm (x 25.4). Constituent
masses (kg/m3) and the GWP figure are copied unchanged. Each (mix x curing age) becomes one row.
"""
import csv
import os
import sys

PSI_TO_MPA = 0.00689476
IN_TO_MM = 25.4

# Fixed, diverse selection (reproducible). Plain OPC vs fly-ash vs slag vs ternary; mortar + concrete;
# GWP 204-521 kg CO2/m3; 28-day strength 26-110 MPa. Each mix carries its full 1-28 d age series.
MIXES = ["Mix_84", "Mix_103", "Mix_121", "Mix_88", "Mix_14", "Mix_1"]

# canonical output columns the `flat` reader understands
COLS = ["mix_id", "material_class", "cement_kg_m3", "fly_ash_kg_m3", "slag_kg_m3",
        "water_kg_m3", "superplasticizer_kg_m3", "fine_agg_kg_m3", "coarse_agg_kg_m3",
        "age_days", "specimen_geometry", "test_method", "curing_temp_c",
        "compressive_strength_mpa", "compressive_strength_std_mpa", "n_specimens",
        "embodied_carbon_kg_co2_m3", "slump_mm"]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main(src):
    with open(src, newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("Mix Name") in MIXES]
    out = []
    for r in rows:
        cem = num(r["Cement (kg/m3)"]) or 0.0
        fa = num(r["Fly Ash (kg/m3)"]) or 0.0
        sl = num(r["Slag (kg/m3)"]) or 0.0
        coarse = num(r["Coarse Aggregates (kg/m3)"]) or 0.0
        mean_psi = num(r["Strength (Mean)"])
        std_psi = num(r["Strength (Std)"])
        slump_in = num(r["Slump (in)"])
        out.append({
            "mix_id": r["Mix Name"],
            # Portland system; blended when an SCM (fly ash / slag) is present.
            "material_class": "blended_OPC" if (fa > 0 or sl > 0) else "OPC",
            "cement_kg_m3": cem, "fly_ash_kg_m3": fa, "slag_kg_m3": sl,
            "water_kg_m3": num(r["Water (kg/m3)"]),
            "superplasticizer_kg_m3": num(r["HRWR (kg/m3)"]),  # high-range water reducer
            "fine_agg_kg_m3": num(r["Fine Aggregate (kg/m3)"]),
            "coarse_agg_kg_m3": coarse,
            "age_days": num(r["Time"]),
            # The source has no specimen-geometry or test-method column, so these are recorded as NULL
            # (not inferred). An earlier version guessed cylinder/cube from coarse-aggregate presence and
            # coded it EN 12390-3 — an invented assumption that violated the schema's "NULL is not zero,
            # and not a stand-in for an assumption" rule. If the upstream testing description is later
            # confirmed (US mortar cubes would be ASTM C109), populate these from that source.
            "specimen_geometry": None,
            "test_method": None,
            "curing_temp_c": num(r["Temp (C)"]),
            "compressive_strength_mpa": round(mean_psi * PSI_TO_MPA, 2) if mean_psi is not None else None,
            "compressive_strength_std_mpa": round(std_psi * PSI_TO_MPA, 2) if std_psi is not None else None,
            "n_specimens": int(num(r["# of measurements"])) if num(r["# of measurements"]) else None,
            "embodied_carbon_kg_co2_m3": num(r["GWP"]),
            "slump_mm": round(slump_in * IN_TO_MM, 1) if slump_in is not None else None,
        })
    out.sort(key=lambda d: (d["mix_id"], d["age_days"] or 0))
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta-sustainableconcrete.csv")
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for d in out:
            w.writerow({k: ("" if d.get(k) is None else d.get(k)) for k in COLS})
    print(f"wrote {len(out)} rows ({len(MIXES)} mixes) -> {dest}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python build/extract.py /path/to/boxcrete_data.csv")
    main(sys.argv[1])
