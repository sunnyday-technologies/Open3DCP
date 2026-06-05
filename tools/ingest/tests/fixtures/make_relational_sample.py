#!/usr/bin/env python3
"""Build `relational_sample.xlsx` -- a small, committed relational-template fixture.

Purpose: make the relational ingestion-fidelity example REPRODUCIBLE. The published
fidelity numbers used to come from a private .xlsx behind an env var (the integration
test skipped without it), so the "relational template" score could not be re-derived by
a reader. This synthetic fixture is a minimal but representative slice of the 15-tab
relational concrete-database template -- one batch -> one specimen -> one test -> three
`data` rows (a scalar + a stress-strain curve + its strain axis) -- and deliberately
includes the structural/metadata + curve-descriptor fields that a flat projection has to
account for:

    material_batches.material_class      -> mix/binder classification
    material_batches.batch_label         -> physical batch sub-identifier
    material_batches.date_of_pouring     -> casting date (t=0 of the curing clock)
    specimens.structural_form_type       -> structural form (stays relational)
    data.<q>.data_type                   -> scalar | curve | image (routing metadata)
    data.strain.units                    -> curve axis descriptor

Regenerate with:  python tools/ingest/tests/fixtures/make_relational_sample.py
"""
from __future__ import annotations

import datetime as _dt
import os

from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "relational_sample.xlsx")


def _sheet(wb, title, header, rows):
    ws = wb.create_sheet(title=title)
    ws.append(header)
    for r in rows:
        ws.append([r.get(h) for h in header])
    return ws


def build():
    wb = Workbook()
    wb.remove(wb.active)  # drop the default sheet; every tab is explicit

    # --- material_batches: mix design in kg/m3 (the field/industry primary basis) ------
    _sheet(wb, "material_batches",
           ["batch_id", "source_id", "material_class", "batch_label", "date_of_pouring",
            "cement_type", "cement_content_kg_m3", "silica_fume_content_kg_m3",
            "fly_ash_content_kg_m3", "fly_ash_class", "fine_aggregate_content_kg_m3",
            "coarse_aggregate_content_kg_m3", "max_aggregate_size_mm",
            "superplasticizer_content_kg_m3", "superplasticizer_type",
            "water_binder_ratio", "air_content_percent_volume_concrete", "printable"],
           [{
               "batch_id": "B1", "source_id": "S1",
               "material_class": "OPC", "batch_label": "B-2024-017",
               "date_of_pouring": _dt.date(2024, 3, 1),
               "cement_type": "ASTM_C150_Type_I", "cement_content_kg_m3": 400.0,
               "silica_fume_content_kg_m3": 30.0, "fly_ash_content_kg_m3": 60.0,
               "fly_ash_class": "F", "fine_aggregate_content_kg_m3": 800.0,
               "coarse_aggregate_content_kg_m3": 900.0, "max_aggregate_size_mm": 10.0,
               "superplasticizer_content_kg_m3": 4.0, "superplasticizer_type": "PCE",
               "water_binder_ratio": 0.35, "air_content_percent_volume_concrete": 2.0,
               "printable": "yes",
           }])

    # --- specimens: batch x geometry x form (structural_form_type stays relational) ----
    _sheet(wb, "specimens",
           ["specimen_id", "batch_id", "source_id", "specimen_geometry",
            "structural_form_type"],
           [{"specimen_id": "SP1", "batch_id": "B1", "source_id": "S1",
             "specimen_geometry": "cylinder", "structural_form_type": "wall_element"}])

    # --- tests: procedure / curing / age ----------------------------------------------
    _sheet(wb, "tests",
           ["test_id", "specimen_id", "age_days", "curing_condition", "test_type",
            "initial_env_temperature_C", "initial_env_relative_humidity_percent"],
           [{"test_id": "T1", "specimen_id": "SP1", "age_days": 28,
             "curing_condition": "MOIST_ROOM", "test_type": "cylinder_compression",
             "initial_env_temperature_C": 23.0,
             "initial_env_relative_humidity_percent": 95.0}])

    # --- data: one scalar (compressive) + a stress-strain curve + its strain axis ------
    _sheet(wb, "data",
           ["data_id", "test_id", "quantity_reported", "quantity_reported_mean",
            "quantity_reported_standard_deviation", "units", "data_type",
            "number_of_specimens", "extraction_methods", "file_name"],
           [
               {"data_id": "D1", "test_id": "T1", "quantity_reported": "compressive_strength",
                "quantity_reported_mean": 52.0, "quantity_reported_standard_deviation": 2.1,
                "units": "MPa", "data_type": "scalar", "number_of_specimens": 3,
                "extraction_methods": "direct", "file_name": None},
               {"data_id": "D2", "test_id": "T1", "quantity_reported": "stress_strain",
                "quantity_reported_mean": None, "quantity_reported_standard_deviation": None,
                "units": "MPa", "data_type": "curve", "number_of_specimens": 3,
                "extraction_methods": "digitized", "file_name": "ss_curve_b17.csv"},
               {"data_id": "D3", "test_id": "T1", "quantity_reported": "strain",
                "quantity_reported_mean": None, "quantity_reported_standard_deviation": None,
                "units": "mm/mm", "data_type": "curve", "number_of_specimens": 3,
                "extraction_methods": "digitized", "file_name": None},
           ])

    wb.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
