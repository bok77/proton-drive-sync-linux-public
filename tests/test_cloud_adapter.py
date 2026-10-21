"""Read-only adapter tests with no real cloud calls."""
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from proton_sync_engine import test_cloud_adapter
from proton_sync_engine.cli_diagnostics import CliError

class AdapterSafetyTests(unittest.TestCase):
    def test_only_cloud_list_is_issued(self):
        config=SimpleNamespace(local_root=Path("/tmp/test-sync"),
            cli_executable=Path("/tmp/test-cli"),managed_folders=("ProtonSync-Test",))
        result=SimpleNamespace(returncode=0,stdout="[]",stderr="")
        with patch.object(test_cloud_adapter,"load_paths",return_value=config):
            with patch.object(test_cloud_adapter,"execute",return_value=result) as runner:
                files,folders,errors=test_cloud_adapter.TestCloudAdapter("/tmp/test.json").scan()
        self.assertEqual(files,{})
        self.assertEqual(errors,[])
        self.assertEqual(runner.call_args.kwargs["timeout"],45)
        self.assertEqual(runner.call_args.args[1:3],("filesystem","list"))
    def test_cloud_error_is_blocking(self):
        config=SimpleNamespace(local_root=Path("/tmp/test-sync"),
            cli_executable=Path("/tmp/test-cli"),managed_folders=("ProtonSync-Test",))
        result=SimpleNamespace(returncode=1,stdout="",stderr="CLI_RATE_LIMIT",error_class=CliError.RATE_LIMIT)
        with patch.object(test_cloud_adapter,"load_paths",return_value=config),patch.object(
                test_cloud_adapter,"execute",return_value=result):
            _,_,errors=test_cloud_adapter.TestCloudAdapter("/tmp/test.json").scan()
        self.assertTrue(errors)
        self.assertEqual(errors[0]["reason"],"CLI_RATE_LIMIT")
    def test_blocked_mount_root_rejected(self):
        config=SimpleNamespace(local_root=Path("/mnt/example-drive/test-sync"),
            cli_executable=Path("/tmp/cli"),managed_folders=("ProtonSync-Test",))
        with patch.object(test_cloud_adapter,"load_paths",return_value=config):
            with self.assertRaises(PermissionError):
                test_cloud_adapter.TestCloudAdapter("/tmp/test.json")
    def test_personal_cli_allowed_only_for_isolated_readonly_folder(self):
        config=SimpleNamespace(local_root=Path("/tmp/sync"),
            cli_executable=Path.home()/".local/bin/proton-drive",
            managed_folders=("ProtonSync-Test",))
        with patch.object(test_cloud_adapter,"load_paths",return_value=config):
            adapter=test_cloud_adapter.TestCloudAdapter("/tmp/test.json")
        self.assertEqual(adapter.config.managed_folders,("ProtonSync-Test",))

    def test_another_cloud_folder_is_rejected(self):
        config=SimpleNamespace(local_root=Path("/tmp/sync"),
            cli_executable=Path.home()/".local/bin/proton-drive",
            managed_folders=("00_Inbox",))
        with patch.object(test_cloud_adapter,"load_paths",return_value=config):
            with self.assertRaises(PermissionError):
                test_cloud_adapter.TestCloudAdapter("/tmp/test.json")
