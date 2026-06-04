import os
import pytest
from open3dcp_ingest import convert

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "uci_sample.csv")


def test_uci_converts_and_scores_high():
    result, report = convert(FIX, kind="uci")
    assert len(result.rows) == 3
    # UCI reports every constituent incl. water -> mass-% conversion is exact, fidelity high
    assert report.overall >= 75, report.to_dict()


def test_uci_mass_pct_sums_to_about_100():
    result, _ = convert(FIX, kind="uci")
    row0 = result.rows[0]
    mass_cols = ["cement_type_1", "slag", "fly_ash", "water",
                 "agg_size_57", "concrete_sand"]
    total = sum(row0.get(c) or 0.0 for c in mass_cols)
    # superplasticizer (~0.1%) excluded; the six bulk constituents should be ~100%
    assert 99.0 <= total <= 100.5, total


def test_uci_strength_and_age_exact():
    result, _ = convert(FIX, kind="uci")
    assert result.rows[0]["compressive_strength_mpa"] == pytest.approx(79.99)
    assert result.rows[0]["test_age_days"] == 28


def test_uci_drops_nothing_silently():
    result, _ = convert(FIX, kind="uci")
    # every populated source field is either mapped or in the sidecar
    assert result.n_mapped_fields + len(result.unmapped) >= result.n_source_fields
