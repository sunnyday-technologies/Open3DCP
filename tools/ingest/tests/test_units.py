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


def test_lb_yd3_to_kg_m3():
    # the common US batch-ticket concentration unit
    assert units.convert(1.0, "lb_yd3", "kg_m3") == pytest.approx(0.593276, rel=1e-4)


def test_short_ton_to_kg():
    assert units.convert(1.0, "short_ton", "kg") == pytest.approx(907.18474, rel=1e-6)


def test_metric_tonne_to_kg():
    assert units.convert(1.0, "metric_ton", "kg") == pytest.approx(1000.0, rel=1e-9)


def test_short_vs_long_ton_spread():
    short = units.convert(1.0, "short_ton", "kg")
    long_ = units.convert(1.0, "long_ton", "kg")
    assert (long_ - short) / short == pytest.approx(0.12, abs=0.01)


def test_ambiguous_ton_rejected():
    for tok in ("ton", "tons", "t", "T"):
        with pytest.raises(units.UnitError):
            units.convert(1.0, tok, "kg")
