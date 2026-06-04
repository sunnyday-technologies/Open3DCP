import pytest
from open3dcp_ingest import transforms as T


def test_kg_m3_to_mass_pct_exact_when_complete():
    ctx = {"total_wet_mass_kg_m3": 2000.0, "total_wet_mass_is_complete": True}
    r = T.kg_m3_to_mass_pct(540.0, ctx=ctx)
    assert r.value == pytest.approx(27.0)
    assert r.fidelity == T.EXACT
    assert r.assumed is False


def test_kg_m3_to_mass_pct_lossy_when_incomplete():
    ctx = {"total_wet_mass_kg_m3": 2000.0, "total_wet_mass_is_complete": False}
    r = T.kg_m3_to_mass_pct(540.0, ctx=ctx)
    assert r.fidelity == T.LOSSY and r.assumed is True


def test_kg_m3_to_mass_pct_sidecar_when_total_unknown():
    r = T.kg_m3_to_mass_pct(540.0, ctx={})
    assert r.value is None and r.fidelity == T.LOSSY


def test_enum_map_hit_and_miss():
    hit = T.enum_map("direct", mapping={"direct": "measured"})
    assert hit.value == "measured" and hit.fidelity == T.CATEGORICAL and not hit.assumed
    miss = T.enum_map("weird", mapping={"direct": "measured"})
    assert miss.value == "weird" and miss.assumed is True


def test_ml_m3_always_routes_to_sidecar():
    r = T.ml_m3_to_mass_pct(5.0, ctx={"total_wet_mass_kg_m3": 2000.0})
    assert r.value is None and r.assumed is True
