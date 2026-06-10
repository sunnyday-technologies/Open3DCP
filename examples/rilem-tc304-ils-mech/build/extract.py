#!/usr/bin/env python3
"""Reproduce the RILEM TC 304-ADC ILS-mech → Open3DCP excerpt.

This example is HAND-CURATED from the openBIS-exported SQLite (a dedicated open3dcp-ingest SQLite
reader is a planned follow-up). The source database is NOT re-hosted here — download it from the DOI:

    https://doi.org/10.5281/zenodo.12200570   (file: 2024-06-21_openbis.db, CC BY 4.0)

then run:

    python build/extract.py /path/to/2024-06-21_openbis.db

It denormalizes material + print + flexural/tensile views for a few participating labs, aggregates
per (mix × test × orientation) into mean / std-dev / n, maps the RILEM U/V/W orientation onto Open3DCP
X/Y/Z/CAST, and writes ../rilem-tc304-ils-mech.open3dcp.csv. Values are real; nothing is synthesized.
The print travel-velocity field is unit-inconsistent in the source and is deliberately omitted.
"""
import csv
import re
import sqlite3
import statistics as st
import sys

MIXES = ["01_a", "13_a", "19_a"]
COLS = ["lab_name", "is_3d_printed", "test_orientation", "test_orientation_code", "test_age_days",
        "flexural_strength_mpa", "flexural_strength_stddev_mpa", "tensile_strength_mpa",
        "tensile_strength_stddev_mpa", "n_specimens", "static_yield_stress_pa", "spread_mm",
        "w_b_ratio", "layer_height_mm", "layer_time_gap_s", "extrusion_rate_l_min", "num_layers",
        "nozzle_shape", "nozzle_area_mm2", "density_hardened_kg_m3", "measurement_confidence",
        "doi", "source_citation", "provenance_notes", "total_binder_kg_m3",
        "original_basis"]
CITE = ("RILEM TC 304-ADC interlaboratory study on mechanical properties of 3D printed concrete "
        "(2024). DOI 10.5281/zenodo.12200570.")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def orient(code):
    """RILEM U/V/W (U=print path, V=transverse, W=build) → Open3DCP layer-relative orientation."""
    if code == "CAST":
        return (False, "cast (moulded reference)", "CAST")
    first = code.split(".")[0]
    # Field-unambiguous labels: U and V both lie IN the layer plane, so "parallel to layers" alone
    # would not distinguish them. What predicts the flexural number is which interface the load bends:
    # along the print path (X) bends the interlayer planes; the build axis (Z) crosses them.
    return {"W": (True, "across layers (build axis)", "Z"),
            "U": (True, "along print path (in-plane longitudinal; flexure loads the interlayer planes)", "X"),
            "V": (True, "in-plane transverse", "Y")}.get(
            first, (True, f"printed ({code})", "?"))


def pfx(name, tag):
    m = re.match(rf"{tag}_(\d+_[a-z])", name or "")
    return m.group(1) if m else None


def main(db):
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row; cur = con.cursor()
    mat = {pfx(r["NAME"], "MATERIAL"): r for r in cur.execute("SELECT * FROM material_sample_props_view")}
    prn = {}
    for r in cur.execute("SELECT * FROM print_sample_props_view"):
        k = pfx(r["NAME"], "PRINT")
        if k and k not in prn:
            prn[k] = r
    rows = []
    for mix in MIXES:
        M, P = mat.get(mix), prn.get(mix)
        lab = f"RILEM TC 304-ADC participating lab {mix.split('_')[0]}"
        yld = num(M["RHEOLOGICALSTATICYIELDSTRESS_VALUE"]) if M else None
        spread = num(M["SPREADDIAMETER_VALUE"]) if M else None
        wb = num(M["WATERTOBINDERRATIO"]) if M else None
        brand = M["BRANDANDPRODUCTNAME"] if M else None
        lh = num(P["AVERAGELAYERHEIGHTWITHIN5MINUTES_VALUE"]) if P else None
        lt = num(P["VERTICALLAYERINTERVALTIME_VALUE"]) if P else None
        er = num(P["MATERIALEXTRUSIONRATE_VALUE"]) if P else None
        nl = num(P["NUMBEROFVERTICALLAYERS"]) if P else None
        nw = num(P["NOZZLEORIFICEDIMENSIONSIFRECTANGULARWIDTH_VALUE"]) if P else None
        nh = num(P["NOZZLEORIFICEDIMENSIONSIFRECTANGULARHEIGHT_VALUE"]) if P else None
        narea = (nw * nh) if (nw and nh) else None
        note = (f"Commercial premix: {brand}; constituent breakdown not disclosed by supplier."
                if brand else "Commercial premix; constituents not disclosed.")
        note += " Print travel velocity in source is unit-inconsistent and omitted."

        flex = {}
        cur.execute("SELECT TESTORIENTATION, AGE, F3PXNORF4PXN_VALUE, DENSITY_VALUE "
                    "FROM exp_flex_sample_props_view WHERE NAME LIKE ?", (f"EXP_FLEX_{mix}_%",))
        for o, a, v, d in cur.fetchall():
            v, a = num(v), num(a)
            if v is None or a is None or a < 20 or a > 40:
                continue
            flex.setdefault(o, {"v": [], "d": [], "age": a})
            flex[o]["v"].append(v)
            if num(d):
                flex[o]["d"].append(num(d))
        kept = [o for o in sorted(flex, key=lambda o: (o != "CAST", -len(flex[o]["v"]))) if len(flex[o]["v"]) >= 4][:3]
        for o in kept:
            g = flex[o]; printed, otext, ocode = orient(o)
            dens = round(st.mean(g["d"]), 0) if g["d"] else None
            rows.append({**{c: None for c in COLS}, "lab_name": lab, "is_3d_printed": printed,
                         "test_orientation": otext, "test_orientation_code": ocode, "test_age_days": int(g["age"]),
                         "flexural_strength_mpa": round(st.mean(g["v"]), 2),
                         "flexural_strength_stddev_mpa": round(st.pstdev(g["v"]), 2) if len(g["v"]) > 1 else None,
                         "n_specimens": len(g["v"]), "static_yield_stress_pa": yld, "spread_mm": spread,
                         "w_b_ratio": wb, "layer_height_mm": lh, "layer_time_gap_s": lt, "extrusion_rate_l_min": er,
                         "num_layers": int(nl) if nl else None, "nozzle_shape": "rectangular" if narea else None,
                         "nozzle_area_mm2": narea, "density_hardened_kg_m3": dens, "measurement_confidence": "measured",
                         "doi": "10.5281/zenodo.12200570", "source_citation": CITE,
                         "provenance_notes": f"{note} RILEM orientation code: {o}.",
                         })  # original_basis stays NULL: commercial premixes disclose no constituent
                             # masses, so no reporting basis exists to record (NULL != 0 doctrine).
                             # Density is in density_hardened_kg_m3; no total_batched_mass either.
    con.close()
    with open("../rilem-tc304-ils-mech.open3dcp.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLS})
    print(f"wrote {len(rows)} rows -> ../rilem-tc304-ils-mech.open3dcp.csv")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python build/extract.py /path/to/2024-06-21_openbis.db")
    main(sys.argv[1])
