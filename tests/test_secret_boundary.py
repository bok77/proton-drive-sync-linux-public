import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_engine.secret_boundary import inspect

class SecretBoundaryTests(unittest.TestCase):
    def test_private_metadata_without_reading_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cfg=root/'private.json';cfg.write_text('TOKEN_MUST_NOT_APPEAR');cfg.chmod(0o600)
            keys=root/'keyring';keys.mkdir(mode=0o700)
            with patch('proton_sync_engine.secret_boundary.subprocess.run') as run:
                run.return_value.returncode=0
                run.return_value.stdout='org.freedesktop.secrets 42 keyring\n'
                result=inspect(cfg,keys)
            self.assertEqual(result.status,'METADATA_ONLY')
            self.assertNotIn('TOKEN',repr(result))
            self.assertEqual(run.call_count,1)
    def test_insecure_and_symlink_paths_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cfg=root/'config';cfg.write_text('x');cfg.chmod(0o644)
            keys=root/'keyring';keys.mkdir(mode=0o700)
            self.assertEqual(inspect(cfg,keys,user_bus=False).status,'BLOCKED')
            cfg.chmod(0o600)
            link=root/'symlink';link.symlink_to(cfg)
            self.assertFalse(inspect(link,keys,user_bus=False).configuration_private)
            keys.chmod(0o755)
            self.assertFalse(inspect(cfg,keys,user_bus=False).keyring_directory_private)
