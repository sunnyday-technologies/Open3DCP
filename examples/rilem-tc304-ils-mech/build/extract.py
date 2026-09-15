#!/usr/bin/env python3
"""Export individual source-linked RILEM specimens; never pool incompatible tests."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3

SOURCE_SHA256 = "674839356d64bf9444b5b1eac8b198f68559129b571da9e82c53ae73c2a3e0df"
DOI = "10.5281/zenodo.12200570"
MIX_RE = re.compile(r"^EXP_FLEX_(01_a|13_a|19_a)_")
COLS = ["lab_name", "is_3d_printed", "specimen_prep", "specimen_length_mm",
        "specimen_width_mm", "specimen_height_mm", "test_orientation", "test_orientation_code",
        "test_method_code", "test_age_days", "flexural_strength_mpa", "n_specimens",
        "density_hardened_kg_m3", "measurement_confidence", "doi", "source_citation",
        "provenance_notes", "original_basis"]
CONTEXT = ["sample_id", "sample_code", "NAME", "TESTORIENTATION", "3-OR4-POINTBENDING",
           "PROCESSPARAMETERS", "SOURCEPRINTOBJECTNUMBER", "AGE", "EXTRACTIONMETHOD",
           "EXTRACTIONDATE", "TESTDATE", "LENGTH_VALUE", "LENGTH_UNIT", "WIDTH_D1_VALUE",
           "WIDTH_D1_UNIT", "HEIGHT_D2_VALUE", "HEIGHT_D2_UNIT", "SUPPORTSPANL_VALUE",
           "SUPPORTSPANL_UNIT", "LOADSPANONLYFOR4PBENDING_VALUE", "LOADSPANONLYFOR4PBENDING_UNIT",
           "APPLIEDLOADINGRATE_VALUE", "APPLIEDLOADINGRATE_UNIT", "F3PXNORF4PXN_VALUE",
           "F3PXNORF4PXN_UNIT", "DENSITY_VALUE", "DENSITY_UNIT"]

def num(v):
    if v is None or isinstance(v, bool):
        return None
    try:
        n = float(v)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None

def measured(r, key, units):
    value = num(r.get(key + "_VALUE"))
    if value is not None and r.get(key + "_UNIT") not in units:
        return None  # Preserve the raw value/unit in the companion ledger; do not guess a conversion.
    return value

def convert(records):
    out, context, inclusion, seen = [], [], [], set()
    for r in sorted(records, key=lambda r: (str(r.get("NAME")), str(r.get("sample_id")))):
        match = MIX_RE.match(r.get("NAME") or "")
        if not match:
            continue
        sid = r.get("sample_id")
        if sid is None or sid in seen:
            raise ValueError("Missing or duplicate specimen identity")
        seen.add(sid)
        age, strength = num(r.get("AGE")), num(r.get("F3PXNORF4PXN_VALUE"))
        reason = ("missing_or_nonfinite_age" if age is None else "outside_20_to_40_days" if not 20 <= age <= 40 else
                  "missing_nonfinite_or_negative_strength" if strength is None or strength < 0 else
                  "unrecognized_strength_unit" if r.get("F3PXNORF4PXN_UNIT") not in {"N/mm²", "MPa"} else "")
        inclusion.append({"sample_id": sid, "source_name": r.get("NAME"), "included": not reason,
                          "reason": reason or "included", "source_strength": r.get("F3PXNORF4PXN_VALUE"),
                          "source_strength_unit": r.get("F3PXNORF4PXN_UNIT")})
        if reason:
            continue
        strength = measured(r, "F3PXNORF4PXN", {"N/mm²", "MPa"})
        code = r.get("TESTORIENTATION")
        printed = False if code == "CAST" else True if re.fullmatch(r"[UVW]\.[UVW]", code or "") else None
        row = dict.fromkeys(COLS)
        row.update(lab_name="RILEM TC 304-ADC participating lab " + match[1].split("_")[0],
                   is_3d_printed=printed, specimen_prep="cast" if printed is False else "3d_printed" if printed else None,
                   specimen_length_mm=measured(r, "LENGTH", {"mm"}),
                   specimen_width_mm=measured(r, "WIDTH_D1", {"mm"}),
                   specimen_height_mm=measured(r, "HEIGHT_D2", {"mm"}),
                   test_orientation="cast" if printed is False else None,
                   test_orientation_code="CAST" if printed is False else None,
                   test_age_days=age, flexural_strength_mpa=strength, n_specimens=1,
                   density_hardened_kg_m3=measured(r, "DENSITY", {"kg/m³"}),
                   measurement_confidence="measured", doi=DOI,
                   source_citation="RILEM TC 304-ADC ILS-mech (2024), DOI " + DOI,
                   provenance_notes=f"Source specimen {sid} ({r.get('NAME')}); mix prefix {match[1]}; "
                   f"full orientation {code}; {r.get('3-OR4-POINTBENDING')}-point bending; "
                   f"condition {r.get('PROCESSPARAMETERS')}; source object {r.get('SOURCEPRINTOBJECTNUMBER')}. "
                   "One specimen, not an average. Full context: provenance.csv keyed by sample_id. "
                   "Unrecognized optional units remain only in the ledger. "
                   "No X/Y/Z projection, guessed material/print join, effect or uncertainty estimate.")
        out.append(row)
        context.append({"record_index": len(out), **{k: r.get(k) for k in CONTEXT}})
    return out, context, inclusion

def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def run(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("Source fingerprint differs from audited DOI export; review before replacing examples")
    with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as con:
        con.row_factory = sqlite3.Row
        records = [dict(r) for r in con.execute("SELECT * FROM exp_flex_sample_props_view")]
    rows, contexts, inclusion = convert(records)
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "rilem-tc304-ils-mech.open3dcp.csv", COLS, rows)
    write_csv(output / "provenance.csv", ["record_index"] + CONTEXT, contexts)
    write_csv(output / "inclusion.csv", ["sample_id", "source_name", "included", "reason", "source_strength", "source_strength_unit"], inclusion)
    report = {"source_sha256": digest, "source_doi": DOI,
              "selection": "01_a, 13_a, 19_a; finite nonnegative flexural strength in N/mm² or MPa; age 20–40 days",
              "selected_source_records": len(inclusion), "rows_committed": len(rows),
              "excluded": len(inclusion) - len(rows), "row_grain": "individual flexural specimen",
              "aggregation": "none", "parent_print_material_joins": "not performed; relationship chain needs curation"}
    (output / "extraction_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
        raise RuntimeError("Source changed during extraction")
    print(json.dumps(report))

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source")
    p.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    a = p.parse_args()
    run(a.source, a.output_dir)
