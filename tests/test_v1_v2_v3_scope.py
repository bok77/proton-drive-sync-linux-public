import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class VersionScopeTests(unittest.TestCase):
    def test_v1_is_test_only_and_not_sdk_dependent(self):
        v1=(ROOT/'V1.md').read_text()
        self.assertIn('/my-files/ProtonSync-Test',v1)
        self.assertIn('gesperrt',v1)
        self.assertIn('Kein eigener SDK-Login',v1)
        self.assertIn('NOT ACCEPTED',v1)
    def test_version_documents_exist(self):
        self.assertIn('Öffentlicher Release',(ROOT/'V2.md').read_text())
        self.assertIn('Komfortfunktionen',(ROOT/'V3.md').read_text())
