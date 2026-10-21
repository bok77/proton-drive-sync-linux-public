"""Safety tests for portable engine setup and the non-executable source snapshot."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from proton_sync_engine.config import validated_config,installation_ready

class PortableEngineConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.mount=self.base/"mounted"
        self.local=self.mount/"Sync"
        self.local.mkdir(parents=True)
        self.state=self.base/"private-state"
        self.cli=self.base/"proton-drive"
        self.cli.write_text("#!/bin/sh\nexit 0\n")
        self.cli.chmod(0o700)
        self.values=dict(local_root=str(self.local),mount_root=str(self.mount),
                         state_dir=str(self.state),cli_executable=str(self.cli))
        self.runner=Mock(return_value=SimpleNamespace(returncode=0))

    def test_valid_synthetic_layout_is_read_only(self):
        config=validated_config(self.values,runner=self.runner)
        self.assertEqual(config.local_root,self.local)
        self.assertFalse(installation_ready(config))
        self.assertFalse(self.state.exists())
        self.runner.assert_called_once_with(
            ["mountpoint","-q",str(self.mount)],capture_output=True,timeout=5)

    def test_reject_missing_mount(self):
        runner=Mock(return_value=SimpleNamespace(returncode=1))
        with self.assertRaisesRegex(ValueError,"not mounted"):
            validated_config(self.values,runner=runner)

    def test_reject_unspecified_root(self):
        values={**self.values,"local_root":""}
        with self.assertRaisesRegex(ValueError,"configured explicitly"):
            validated_config(values,runner=self.runner)

    def test_reject_unsafe_root(self):
        with self.assertRaisesRegex(ValueError,"Dangerous"):
            validated_config({**self.values,"local_root":str(self.mount)},
                             runner=self.runner)

    def test_reject_local_outside_mount(self):
        out=self.base/"outside"
        out.mkdir()
        with self.assertRaisesRegex(ValueError,"outside"):
            validated_config({**self.values,"local_root":str(out)},
                             runner=self.runner)

    def test_reject_local_symlink(self):
        alias=self.base/"symlink"
        alias.symlink_to(self.local,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,"Symbolic"):
            validated_config({**self.values,"local_root":str(alias)},
                             runner=self.runner)

    def test_reject_state_inside_synced_tree(self):
        with self.assertRaisesRegex(ValueError,"State directory"):
            validated_config({**self.values,"state_dir":str(self.local/"state")},
                             runner=self.runner)

    def test_reject_non_executable_cli(self):
        self.cli.chmod(0o600)
        with self.assertRaisesRegex(ValueError,"executable"):
            validated_config(self.values,runner=self.runner)

    def test_reject_cloud_path_changes(self):
        with self.assertRaisesRegex(ValueError,"Unsupported cloud root"):
            validated_config({**self.values,"cloud_root":"/other"},
                             runner=self.runner)

    def test_reference_snapshots_are_not_executable(self):
        root=Path(__file__).resolve().parents[1]/"src/proton_sync_engine/reference"
        items=list(root.glob("*.py"))
        self.assertGreaterEqual(len(items),10)
        self.assertTrue(all(not (p.stat().st_mode & 0o111) for p in items))


if __name__=="__main__":
    unittest.main()
