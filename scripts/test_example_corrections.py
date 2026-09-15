"""Regression tests for source meaning, missingness and corrected export integrity."""
import csv
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
from check_examples import equivalent_csv

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'examples' / name / 'build/extract.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RILEM = module('rilem-tc304-ils-mech')
UF = module('uf-3dcp-mix')


def specimen(sid=1, **changes):
    row = dict(sample_id=sid, NAME=f'EXP_FLEX_01_a_spec_{sid}', AGE='28',
               TESTORIENTATION='U.W', F3PXNORF4PXN_VALUE='6.25', F3PXNORF4PXN_UNIT='N/mm²',
               PROCESSPARAMETERS='DEFAULT', SOURCEPRINTOBJECTNUMBER='1',
               LENGTH_VALUE='160', LENGTH_UNIT='mm')
    row['3-OR4-POINTBENDING'] = '3'
    row.update(changes)
    return row


def uf_fixture():
    headers = [''] * 118
    for i, val in UF.EXPECTED.items():
        headers[i] = val
    headers[99] = 'Plastic Viscosity (Pa.s)'
    row = [None] * 118
    for i, val in {4: 'fixture reference', 5: 'Portland cement + fly ash', 6: 'Portland cement',
                   7: .7, 14: 'fly ash', 15: .3, 40: .3, 97: .4, 98: 0, 99: 20, 103: 42}.items():
        row[i] = val
    return headers, row


class SourceMeaningTests(unittest.TestCase):
    def test_incompatible_specimens_never_aggregate(self):
        first = specimen()
        second = specimen(2, AGE='29', PROCESSPARAMETERS='DEV1', WIDTH_D1_VALUE='100', WIDTH_D1_UNIT='mm')
        second['3-OR4-POINTBENDING'] = '4'
        out, context, _ = RILEM.convert([first, second])
        self.assertEqual([r['n_specimens'] for r in out], [1, 1])
        self.assertEqual([r['test_age_days'] for r in out], [28, 29])
        self.assertEqual([r['3-OR4-POINTBENDING'] for r in context], ['3', '4'])

    def test_compound_orientation_retained_without_projection(self):
        out, context, _ = RILEM.convert([specimen()])
        self.assertIsNone(out[0]['test_orientation_code'])
        self.assertEqual(context[0]['TESTORIENTATION'], 'U.W')
        self.assertIn('full orientation U.W', out[0]['provenance_notes'])

    def test_cast_does_not_inherit_print_settings(self):
        out, _, _ = RILEM.convert([specimen(TESTORIENTATION='CAST')])
        self.assertFalse(out[0]['is_3d_printed'])
        self.assertEqual(out[0]['specimen_prep'], 'cast')
        self.assertNotIn('layer_height_mm', out[0])

    def test_nonfinite_missing_and_outside_window_excluded(self):
        out, _, ledger = RILEM.convert([specimen(1, AGE='nan'), specimen(2, AGE='19'),
                                        specimen(3, F3PXNORF4PXN_VALUE='inf'), specimen(4, F3PXNORF4PXN_VALUE='0')])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['flexural_strength_mpa'], 0)
        self.assertEqual(sum(r['included'] for r in ledger), 1)

    def test_corrupt_source_units_not_interpreted(self):
        out, _, ledger = RILEM.convert([specimen(F3PXNORF4PXN_UNIT='N/mm130')])
        self.assertFalse(out)
        self.assertEqual(ledger[0]['reason'], 'unrecognized_strength_unit')
        self.assertEqual(ledger[0]['source_strength_unit'], 'N/mm130')
        out, context, _ = RILEM.convert([specimen(DENSITY_VALUE='2100', DENSITY_UNIT='kg/m132')])
        self.assertIsNone(out[0]['density_hardened_kg_m3'])
        self.assertEqual(context[0]['DENSITY_UNIT'], 'kg/m132')

    def test_duplicate_source_identity_rejected(self):
        with self.assertRaises(ValueError):
            RILEM.convert([specimen(), specimen()])

    def test_prefix_match_does_not_take_similarly_named_mix(self):
        self.assertFalse(RILEM.convert([specimen(NAME='EXP_FLEX_01_ax_spec_1')])[0])

    def test_uf_preserves_name_ratio_and_missing_distinctions(self):
        headers, row = uf_fixture()
        out, provenance, cells = UF.convert(headers, [row])
        self.assertIsNone(out[0]['material_class'])
        self.assertIsNone(out[0]['is_3d_printed'])
        self.assertEqual(provenance[0]['binder1_label'], 'Portland cement')
        bycol = {r['column_index_zero_based']: r for r in cells}
        self.assertEqual(bycol[14]['source_value'], 'fly ash')
        self.assertEqual(bycol[15]['source_value'], '0.3')
        self.assertTrue(bycol[16]['missing'])

    def test_uf_no_default_cement(self):
        headers, row = uf_fixture()
        row[5] = row[6] = None
        out, _, _ = UF.convert(headers, [row])
        self.assertIsNone(out[0]['material_class'])
        self.assertIn('Binder1: not reported', out[0]['provenance_notes'])

    def test_uf_units_and_zero(self):
        headers, row = uf_fixture()
        out, _, _ = UF.convert(headers, [row])
        self.assertEqual(out[0]['static_yield_stress_pa'], 400)
        self.assertEqual(out[0]['dynamic_yield_stress_pa'], 0)
        self.assertEqual(out[0]['plastic_viscosity_pa_s'], 20)

    def test_uf_header_unit_change_rejected(self):
        headers, row = uf_fixture()
        headers[97] = 'Static Yield Stress (Pa)'
        with self.assertRaises(ValueError):
            UF.convert(headers, [row])
        headers, row = uf_fixture()
        headers[99] = 'Plastic Viscosity (kPa.s)'
        with self.assertRaises(ValueError):
            UF.convert(headers, [row])

    def test_csv_reproduction_tolerates_only_machine_precision_noise(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a.csv', Path(d) / 'b.csv'
            a.write_text('total_batched_mass_kg_m3,source\n2426.2,reported\n')
            b.write_text('total_batched_mass_kg_m3,source\n2426.2000000000003,reported\n')
            self.assertTrue(equivalent_csv(a, b))
            for text in ['total_batched_mass_kg_m3,source\n2426.21,reported\n', 'total_batched_mass_kg_m3,source\n2426.2,inferred\n',
                         'total_batched_mass_kg_m3,source\n,reported\n', 'total_batched_mass_kg_m3,source\nNaN,reported\n',
                         'source,total_batched_mass_kg_m3\nreported,2426.2\n', 'total_batched_mass_kg_m3,source\n2426.2,reported\n2426.2,reported\n']:
                b.write_text(text)
                self.assertFalse(equivalent_csv(a, b), text)
            a.write_text('source\n2426.2\n')
            b.write_text('source\n2426.2000000000003\n')
            self.assertFalse(equivalent_csv(a, b))
            a.write_text('source\nreported,extra\n')
            b.write_text('source\nreported,different\n')
            self.assertFalse(equivalent_csv(a, b))

    def test_uf_all_ages_not_truncated_by_output_cap(self):
        headers, row = uf_fixture()
        records = []
        for i in range(15):
            r = list(row); r[4] = f'reference {i}'; r[100:104] = [10, 20, 30, 40]
            records.append(r)
        out, provenance, _ = UF.convert(headers, records)
        self.assertEqual(len(provenance), 10)
        self.assertEqual(len(out), 40)
        self.assertEqual([r['test_age_days'] for r in out[-4:]], [1, 3, 7, 28])

    def test_uf_limits_per_reference_and_requires_reference(self):
        headers, row = uf_fixture()
        missing = list(row); missing[4] = None
        out, provenance, _ = UF.convert(headers, [row, row, row, missing])
        self.assertEqual(len(out), 2)
        self.assertEqual([r['source_row'] for r in provenance], [2, 3])

    def test_uf_nonfinite_measurement_not_admitted(self):
        headers, row = uf_fixture(); row[97] = 'nan'
        self.assertFalse(UF.convert(headers, [row])[0])

    def test_committed_export_identity_and_metadata(self):
        for name in ['rilem-tc304-ils-mech', 'uf-3dcp-mix']:
            folder = ROOT / 'examples' / name
            with (folder / f'{name}.open3dcp.csv').open(encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            rec = json.loads((folder / 'record.json').read_text(encoding='utf-8'))
            report = json.loads((folder / 'extraction_report.json').read_text(encoding='utf-8'))
            self.assertEqual(len(rows), rec['rows_committed'])
            self.assertEqual(len(rows), report['rows_committed'])
            with (folder / 'provenance.csv').open(encoding='utf-8') as f:
                provenance = list(csv.DictReader(f))
            if name.startswith('rilem'):
                self.assertEqual(len(rows), len(provenance))
                self.assertEqual(len(rows), len({p['sample_id'] for p in provenance}))
                self.assertTrue(all(r['n_specimens'] == '1' for r in rows))
                for r, p in zip(rows, provenance):
                    self.assertEqual(float(r['flexural_strength_mpa']), float(p['F3PXNORF4PXN_VALUE']))
                    self.assertEqual(float(r['test_age_days']), float(p['AGE']))
            else:
                self.assertEqual(len(rows), sum(int(p['age_rows']) for p in provenance))
                self.assertTrue(all(not r['material_class'] and not r['is_3d_printed'] for r in rows))


if __name__ == '__main__':
    unittest.main()
