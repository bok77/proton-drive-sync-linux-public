"""Isolated installer-preview tests; all files live in disposable directories."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from proton_sync_engine import install_plan

class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.mount=self.base/"mount"
        self.root=self.mount/"Sync"
        (self.root/"Inbox").mkdir(parents=True)
        self.cli=self.base/"proton-drive"
        self.cli.write_text("#!/bin/sh\nexit 0\n")
        self.cli.chmod(0o700)
        self.config_file=self.base/"config.json"
        data={"mount_root":str(self.mount),
              "local_root":str(self.root),
              "state_dir":str(self.base/"state"),
              "cli_executable":str(self.cli),
              "managed_folders":["Inbox"],
              "priority_cloud_folders":["Inbox"]}
        self.config_file.write_text(json.dumps(data))
        self.config_file.chmod(0o600)
        self.dest=self.base/"inert-stage"
        # Synthetic mount cannot be a real mountpoint without privileges.
        # Keep the real path-safety validator; disable mount probing only here.
        from proton_sync_engine import portable_paths
        validator=portable_paths.validated_config
        patcher=patch(
            "proton_sync_engine.portable_paths.validated_config",
            side_effect=lambda settings: validator(settings,require_mount=False))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_preview_produces_no_files(self):
        result=install_plan.plan(self.config_file)
        self.assertFalse(result["activation_authorized"])
        self.assertEqual(result["status"],"PREVIEW_ONLY")
        self.assertFalse(self.dest.exists())

    def test_stage_is_inert_and_removable(self):
        result=install_plan.stage(self.config_file,self.dest)
        self.assertFalse(result["activation_authorized"])
        self.assertEqual(len(list((self.dest/"units").glob("*.service"))),3)
        for unit in (self.dest/"units").glob("*.service"):
            text=unit.read_text()
            self.assertIn("ExecCondition=/usr/bin/false",text)
            self.assertIn("ExecStart=/usr/bin/false",text)
            self.assertNotIn("[Install]",text)
        self.assertEqual(install_plan.verify_stage(self.dest)["status"],"PREVIEW_ONLY")
        install_plan.unstage(self.dest)
        self.assertFalse(self.dest.exists())
        self.assertTrue(self.root.exists())

    def test_existing_destination_is_never_overwritten(self):
        self.dest.mkdir()
        sentinel=self.dest/"important"
        sentinel.write_text("keep")
        with self.assertRaises(FileExistsError):
            install_plan.stage(self.config_file,self.dest)
        self.assertEqual(sentinel.read_text(),"keep")

    def test_stage_refuses_user_data_area(self):
        with self.assertRaisesRegex(ValueError,"synchronized filesystem"):
            install_plan.stage(self.config_file,self.root/"stage")

    def test_unsafe_extra_stage_content_blocks_removal(self):
        install_plan.stage(self.config_file,self.dest)
        extra=self.dest/"keep-me"
        extra.write_text("important")
        with self.assertRaisesRegex(ValueError,"Unexpected"):
            install_plan.unstage(self.dest)
        self.assertEqual(extra.read_text(),"important")

    def test_changed_unit_blocks_removal(self):
        install_plan.stage(self.config_file,self.dest)
        unit=self.dest/"units"/install_plan.UNIT_NAMES["full"]
        unit.write_text("CHANGED")
        with self.assertRaisesRegex(ValueError,"does not match"):
            install_plan.unstage(self.dest)
        self.assertEqual(unit.read_text(),"CHANGED")

    def test_bad_configuration_blocks_stage_without_writes(self):
        self.config_file.chmod(0o644)
        with self.assertRaises(ValueError):
            install_plan.stage(self.config_file,self.dest)
        self.assertFalse(self.dest.exists())

    def test_refuses_nonexistent_or_non_owned_stage(self):
        with self.assertRaises(ValueError):
            install_plan.unstage(self.dest)

if __name__=="__main__":
    unittest.main()
