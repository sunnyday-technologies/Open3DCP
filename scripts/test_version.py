"""Guard independent converter patches without weakening schema version checks."""
from pathlib import Path
import tempfile
import unittest
from check_version import check_tool_version, checks

class VersionTests(unittest.TestCase):
    def check_versions(self, package, runtime, schema='1.8'):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'tools/ingest/open3dcp_ingest').mkdir(parents=True)
            (root/'tools/ingest/pyproject.toml').write_text(f'version = "{package}"\n')
            (root/'tools/ingest/open3dcp_ingest/__init__.py').write_text(f'__version__ = "{runtime}"\n')
            return check_tool_version(schema, tmp)
    def test_patch_independent(self):
        self.assertEqual(self.check_versions('1.8.1','1.8.1'), [])
    def test_original_release(self):
        self.assertEqual(self.check_versions('1.8.0','1.8.0'), [])
    def test_package_runtime_must_match(self):
        self.assertTrue(self.check_versions('1.8.1','1.8.2'))
    def test_wrong_schema_minor_rejected(self):
        self.assertTrue(self.check_versions('1.9.0','1.9.0'))
    def test_malformed_rejected(self):
        self.assertTrue(self.check_versions('1.8','1.8'))
    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(check_tool_version('1.8',tmp))
    def test_wrong_schema_major_rejected(self):
        self.assertTrue(self.check_versions('2.8.1','2.8.1'))
    def test_target_schema_still_guarded(self):
        self.assertIn('TARGET_SCHEMA_VERSION = "1.8"',checks('1.8.0','1.8')['tools/ingest/open3dcp_ingest/__init__.py'])

if __name__=='__main__':
    unittest.main()
