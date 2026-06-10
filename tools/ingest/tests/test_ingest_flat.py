"""Tests for the flat kg/m3 reader (`--kind flat`), the path that built the Meta and UNSW
worked-demonstration example. Previously untested; the missing-water regression below guards the
wet-mass "complete" fix (a binder+aggregate row with no water must not score the kg/m3 -> mass-%
projection as EXACT against a waterless denominator)."""
import csv
import pytest
from open3dcp_ingest import convert

# A small, complete flat kg/m3 mix: every constituent INCLUDING water is reported, so the wet-mass
# total closes and the kg/m3 -> mass-% projection should score EXACT.
_COMPLETE = {
    "mix_id": "M1", "material_class": "UHPC",
    "cement_kg_m3": "400", "fly_ash_kg_m3": "100", "silica_fume_kg_m3": "50",
    "water_kg_m3": "160", "superplasticizer_kg_m3": "8",
    "fine_agg_kg_m3": "1100", "coarse_agg_kg_m3": "0",
    "fiber_type": "steel", "fiber_kg_m3": "80", "fiber_length_mm": "13", "fiber_diameter_mm": "0.2",
    "age_days": "28", "compressive_strength_mpa": "150",
    "splitting_tensile_mpa": "9", "flexural_strength_mpa": "20",
}


def _write(tmp_path, row, drop=None):
    cols = [c for c in row if c != drop]
    p = tmp_path / "flat.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerow({c: row[c] for c in cols})
    return str(p)


def _value_fidelity(report):
    return next(d["score"] for d in report.to_dict()["dimensions"] if d["name"] == "value_fidelity")


def test_flat_complete_converts_and_scores_high(tmp_path):
    result, report = convert(_write(tmp_path, _COMPLETE), kind="flat")
    assert len(result.rows) == 1
    # every constituent incl. water reported -> mass-% conversion is exact -> high fidelity
    assert report.overall >= 75, report.to_dict()


def test_flat_missing_water_is_not_scored_exact(tmp_path):
    """Regression: a flat mix with NO water must not be rated as a closed wet-mass batch."""
    full = convert(_write(tmp_path, _COMPLETE), kind="flat")[1]
    no_water = convert(_write(tmp_path, _COMPLETE, drop="water_kg_m3"), kind="flat")[1]
    # without water the kg/m3 -> mass-% projection is inferred, not exact -> value fidelity drops
    assert _value_fidelity(no_water) < _value_fidelity(full), (
        _value_fidelity(no_water), _value_fidelity(full))


def test_flat_wb_ratio_derived(tmp_path):
    result, _ = convert(_write(tmp_path, _COMPLETE), kind="flat")
    # binder = cement + fly ash + silica fume = 550; water 160 -> w/b = 0.2909
    row = result.rows[0]
    numeric = [v for v in row.values() if isinstance(v, (int, float))]
    assert any(abs(v - round(160 / 550, 4)) < 1e-3 for v in numeric), row


def test_flat_routes_splitting_distinct_from_tensile(tmp_path):
    result, _ = convert(_write(tmp_path, _COMPLETE), kind="flat")
    row = result.rows[0]
    # the source reports splitting tensile (9 MPa); it must land in a splitting/tensile column,
    # not be silently dropped, and not be conflated with a direct tensile_strength value.
    assert any("split" in k.lower() and v == pytest.approx(9.0) for k, v in row.items()
               if isinstance(v, (int, float))), row


def test_flat_drops_nothing_silently(tmp_path):
    result, _ = convert(_write(tmp_path, _COMPLETE), kind="flat")
    # every source field is mapped, sidecar'd, or legitimately consumed by a mapping (selector/
    # metadata fields like the wet-mass denominator inputs); none vanish silently.
    accounted = result.n_mapped_fields + len(result.unmapped) + result.n_consumed_fields
    assert accounted >= result.n_source_fields, result
