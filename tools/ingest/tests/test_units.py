import math
import pytest
from open3dcp_ingest import units


def test_psi_to_mpa():
    assert units.convert(145.04, "psi", "MPa") == pytest.approx(1.0, rel=1e-3)


def test_gpa_passthrough_dimension():
    # 31000 MPa modulus reported in MPa -> stored as GPa
    assert units.convert(31000.0, "MPa", "GPa") == pytest.approx(31.0, rel=1e-6)


def test_percent_to_fraction_blocked_target():
    # converting to "%" target works (frac base)
    assert units.convert(50.0, "%", "%") == 50.0


def test_dimension_mismatch_raises():
    with pytest.raises(units.UnitError):
        units.convert(1.0, "mm", "MPa")
