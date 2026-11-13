import csv
from decimal import Decimal
import json

import pytest

from open3dcp_ingest import convert
from open3dcp_ingest.cli import _write_outputs


def test_canonical_roundtrip_retains_replicates_precision_and_null(tmp_path):
    source = tmp_path / 'canonical.csv'
    source.write_text('mix_id,water,compressive_strength_mpa,is_3d_printed,doi,x_specimen,private_field\n'
                      'A,10.1234567890123456789,0,false,10.1234/example,S1,retained\n'
                      'A,10.1234567890123456789,,false,10.1234/example,S2,also retained\n')
    result, report = convert(str(source), kind='canonical')
    assert len(result.rows) == 2
    assert result.rows[0]['water'] == Decimal('10.1234567890123456789')
    assert result.rows[0]['compressive_strength_mpa'] == 0
    assert result.rows[1]['compressive_strength_mpa'] is None
    assert result.rows[0]['is_3d_printed'] is False
    assert 'private_field' not in result.rows[0]
    assert [u.value for u in result.unmapped] == ['retained', 'also retained']
    output, *_ = _write_outputs(result, report, str(source), str(tmp_path / 'output'))
    second, _ = convert(output, kind='canonical')
    assert second.rows == result.rows
    traces = (tmp_path / 'output/canonical.trace.jsonl').read_text().splitlines()
    assert {json.loads(t)['row'] for t in traces} == {0, 1}


@pytest.mark.parametrize('body', [
    'water,water\n1,2\n', 'water\nNaN\n', 'water\nInfinity\n',
    'is_3d_printed\nperhaps\n', 'water\n1,2\n', 'water,doi\n1\n',
])
def test_canonical_rejects_ambiguous_or_nonfinite_input(tmp_path, body):
    source = tmp_path / 'bad.csv'
    source.write_text(body)
    with pytest.raises(ValueError):
        convert(str(source), kind='canonical')


def test_flat_preserves_unknown_and_invalid_original_fields(tmp_path):
    source = tmp_path / 'flat.csv'
    source.write_text('cement_kg_m3,water_kg_m3,source_specimen,unknown_additive_kg_m3\n300,invalid,A,3\n')
    result, _ = convert(str(source), kind='flat')
    retained = {u.source: u.value for u in result.unmapped}
    assert retained['source.source_specimen'] == 'A'
    assert retained['source.unknown_additive_kg_m3'] == '3'
    assert retained['source.water_kg_m3'] == 'invalid'


def test_flat_identity_and_unknown_mass_are_not_lost(tmp_path):
    source = tmp_path / 'flat.csv'
    source.write_text('mix_id,doi,cement_kg_m3,water_kg_m3,fine_agg_kg_m3,unknown_kg_m3\n'
                      'A,10.1234/example,300,150,1000,5\n')
    result, _ = convert(str(source), kind='flat')
    assert result.rows[0]['mix_id'] == 'A'
    assert result.rows[0]['doi'] == '10.1234/example'
    water = [t for t in result.trace if t.target == 'water']
    assert water and any(t.fidelity != 'exact' for t in water)


def test_schema_registry_is_bound_to_public_ddl():
    import hashlib
    from pathlib import Path
    import open3dcp_ingest.canonical as canonical
    root = Path(__file__).resolve().parents[3]
    manifest = json.loads(Path(canonical.__file__).with_name('canonical_schema.json').read_text())
    assert hashlib.sha256((root / manifest['source']).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == manifest['source_sha256_lf']
    assert len(manifest['columns']) == 280
