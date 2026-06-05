import datetime
import os

import pytest

from open3dcp_ingest import convert
from open3dcp_ingest.crosswalk import Crosswalk
from open3dcp_ingest.ingest import build_relational_mappings, ingest

# Committed, reproducible relational fixture (regenerate with make_relational_sample.py).
FIX = os.path.join(os.path.dirname(__file__), "fixtures", "relational_sample.xlsx")
# Optional: point at a real 15-tab relational template to exercise the full schema.
TEMPLATE = os.environ.get("OPEN3DCP_RELATIONAL_TEMPLATE", "")


def _convert():
    return convert(FIX, kind="relational")


def test_relational_fixture_ingests_at_grade_A():
    result, report = _convert()
    assert len(result.rows) == 1
    # After v1.7 intelligent-ingestion fixes the representative fixture scores in the A band.
    assert report.overall >= 90, report.to_dict()


def test_classification_and_batch_timeline_mapped():
    """material_class / batch_label / date_of_casting were sidecar fields before v1.7."""
    result, _ = _convert()
    row = result.rows[0]
    assert row["material_class"] == "OPC"
    assert row["batch_label"] == "B-2024-017"
    assert row["date_of_casting"] is not None


def test_cement_pivot_resolves():
    result, _ = _convert()
    assert any("cement_type_1" in row for row in result.rows)


def test_data_type_routes_curve_to_file_column():
    """A `data` record with data_type=curve routes its file to stress_strain_file (not sidecar)."""
    result, _ = _convert()
    row = result.rows[0]
    assert row.get("stress_strain_file") == "ss_curve_b17.csv"
    # the scalar in the same test still lands in its property column (+ std-dev)
    assert row.get("compressive_strength_mpa") == 52.0
    assert row.get("compressive_strength_stddev_mpa") == 2.1


def test_curve_axis_descriptor_folded_into_provenance():
    """data.strain.units is a curve descriptor -> provenance_notes, not silent loss."""
    result, _ = _convert()
    notes = result.rows[0].get("provenance_notes", "")
    assert "strain.units=mm/mm" in notes


def test_wet_mass_denominator_includes_admixtures():
    """mix_density must include the superplasticizer mass (400+30+60+800+900+4 + water 171.5)."""
    result, _ = _convert()
    assert result.rows[0]["mix_density_kg_m3"] == pytest.approx(2365.5)


def test_structural_form_type_is_the_only_real_drop():
    """The single field that legitimately stays relational is the only non-key sidecar entry."""
    result, _ = _convert()
    real = sorted({u.source for u in result.unmapped
                   if not (u.source.rsplit(".", 1)[-1] == "id"
                           or u.source.rsplit(".", 1)[-1].endswith("_id"))})
    assert real == ["specimens.structural_form_type"]


def test_test_age_derived_from_casting_and_test_date():
    """When no explicit age is given, age = test date - date_of_pouring."""
    cw = Crosswalk.load()
    mappings = build_relational_mappings(cw)
    rec = {
        "material_batches.date_of_pouring": datetime.date(2024, 3, 1),
        "tests.date_of_testing": datetime.date(2024, 3, 29),
        "_ctx": {},
    }
    result = ingest([rec], mappings, cw.quantity_map, cw, source_kind="relational")
    assert result.rows[0]["test_age_days"] == 28


@pytest.mark.skipif(not (TEMPLATE and os.path.exists(TEMPLATE)),
                    reason="no private relational template configured (set OPEN3DCP_RELATIONAL_TEMPLATE)")
def test_private_template_reports_loss_dimensions():
    result, report = convert(TEMPLATE, kind="relational")
    assert len(result.unmapped) >= 1
    names = {d.name for d in report.dimensions}
    assert {"relational_integrity", "file_data_capture", "value_fidelity"} <= names
