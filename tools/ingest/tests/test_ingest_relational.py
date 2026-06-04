import os
import pytest
from open3dcp_ingest import convert

# Integration test against a relational concrete-database .xlsx template.
# Set OPEN3DCP_RELATIONAL_TEMPLATE to a local template path to run it; skipped otherwise.
TEMPLATE = os.environ.get("OPEN3DCP_RELATIONAL_TEMPLATE", "")

pytestmark = pytest.mark.skipif(
    not (TEMPLATE and os.path.exists(TEMPLATE)),
    reason="no relational template configured (set OPEN3DCP_RELATIONAL_TEMPLATE)")


def test_relational_template_ingests():
    result, report = convert(TEMPLATE, kind="relational")
    assert len(result.rows) >= 1
    assert 0 <= report.overall <= 100


def test_relational_cement_pivot_resolves():
    result, _ = convert(TEMPLATE, kind="relational")
    # an ASTM_C150_Type_I batch should pivot into cement_type_1
    assert any("cement_type_1" in row for row in result.rows)


def test_relational_reports_loss_dimensions():
    result, report = convert(TEMPLATE, kind="relational")
    # the flat schema can't hold everything; the report must name the loss dimensions
    assert len(result.unmapped) >= 1
    names = {d.name for d in report.dimensions}
    assert {"relational_integrity", "file_data_capture", "value_fidelity"} <= names
