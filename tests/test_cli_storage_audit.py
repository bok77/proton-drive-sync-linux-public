from pathlib import Path
import tempfile
import unittest
from proton_sync_engine.cli_storage_audit import inspect

class StorageAuditTests(unittest.TestCase):
    def test_private_file_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'cache';p.mkdir(mode=0o700)
            f=p/'file.json';f.write_text('secret-do-not-read');f.chmod(0o600)
            self.assertEqual(inspect(p).status,'METADATA_ONLY')
    def test_world_readable_file_is_blocked_without_disclosing_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'cache';p.mkdir(mode=0o700)
            f=p/'PRIVATE_NAME';f.write_text('secret');f.chmod(0o644)
            result=inspect(p)
            self.assertEqual(result.status,'BLOCKED')
            self.assertNotIn('PRIVATE_NAME',repr(result))
            f.chmod(0o600)
            p.chmod(0o755)
            self.assertEqual(inspect(p).status,'BLOCKED')
