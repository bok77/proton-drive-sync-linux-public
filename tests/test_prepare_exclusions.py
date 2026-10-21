"""Private exclusions must exist before second engine start."""
import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from proton_sync_engine import prepare_exclusions

class ExclusionsPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state=Path(self.tmp.name)/"state"
        self.state.mkdir(mode=0o700)
        self.target=self.state/"settings.json"
        self.config=SimpleNamespace(state_dir=self.state,exclusion_settings=self.target)
        self.patcher=patch.object(prepare_exclusions,"load_paths",return_value=self.config)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
    def test_new_defaults_are_private_and_idempotent(self):
        self.assertEqual(prepare_exclusions.initialize(Path("/synthetic/config"))["status"],"CREATED_DEFAULTS")
        self.assertEqual(self.target.stat().st_mode & 0o777,0o600)
        self.assertEqual(json.loads(self.target.read_text()),prepare_exclusions.DEFAULT)
        self.assertEqual(prepare_exclusions.initialize(Path("/synthetic/config"))["status"],"ALREADY_PRESENT")
    def test_custom_existing_rules_are_never_replaced(self):
        self.target.write_text('{"exclusions":{"file_patterns":["important"],"directory_names":[],"custom_relative_prefixes":[]}}')
        self.target.chmod(0o600)
        original=self.target.read_bytes()
        with self.assertRaises(FileExistsError):
            prepare_exclusions.initialize(Path("/synthetic/config"))
        self.assertEqual(original,self.target.read_bytes())
    def test_symlink_rejected(self):
        other=self.state/"other"
        other.write_text("keep")
        self.target.symlink_to(other)
        with self.assertRaises(PermissionError):
            prepare_exclusions.initialize(Path("/synthetic/config"))
        self.assertEqual(other.read_text(),"keep")
    def test_weak_state_permissions_rejected(self):
        self.state.chmod(0o755)
        with self.assertRaises(PermissionError):
            prepare_exclusions.initialize(Path("/synthetic/config"))
        self.assertFalse(self.target.exists())
