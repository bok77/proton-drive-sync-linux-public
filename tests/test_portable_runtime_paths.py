"""Tests for an inert, path-decoupled engine candidate and strict JSON setup."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from proton_sync_engine import portable_paths

class PortableRuntimePathsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name)
        self.mount=self.home/"data"
        self.root=self.mount/"Proton"
        (self.root/"Inbox").mkdir(parents=True)
        self.cli=self.home/"proton-drive"
        self.cli.write_text("#!/bin/sh\nexit 0\n")
        self.cli.chmod(0o700)
        self.config_file=self.home/"config.json"
        self.data={
            "local_root":str(self.root),
            "mount_root":str(self.mount),
            "state_dir":str(self.home/"state"),
            "cli_executable":str(self.cli),
            "managed_folders":["Inbox"],
            "priority_cloud_folders":["Inbox"],
        }
        self.store()

    def store(self):
        self.config_file.write_text(json.dumps(self.data))
        self.config_file.chmod(0o600)

    def load(self):
        with patch("proton_sync_engine.portable_paths.validated_config") as validate:
            validate.return_value=SimpleNamespace(
                local_root=self.root, mount_root=self.mount, state_dir=self.home/"state",
                cli_executable=self.cli)
            return portable_paths.load_paths(self.config_file)

    def test_positive_synthetic_portable_roots(self):
        loaded=self.load()
        self.assertEqual(loaded.managed_folders,("Inbox",))
        self.assertEqual(portable_paths.priority_folders(loaded),[("Inbox",)])
        self.assertEqual(loaded.local_root,self.root)
        self.assertFalse((self.home/"state").exists())

    def test_negative_no_config_refuses_runtime_import(self):
        env=os.environ.copy()
        env.pop("PROTON_SYNC_CONFIG",None)
        env["PYTHONPATH"]=str(Path(__file__).resolve().parents[1]/"src")
        engine=Path(__file__).resolve().parents[1]/"src/proton_sync_engine/runtime/proton-bisync.py"
        p=subprocess.run([sys.executable,str(engine)],env=env,
                         capture_output=True,text=True,timeout=6)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("PROTON_SYNC_CONFIG is required",p.stderr)

    def test_negative_world_readable_config(self):
        self.config_file.chmod(0o644)
        with self.assertRaisesRegex(ValueError,"private"):
            self.load()

    def test_negative_path_traversal(self):
        self.data["priority_cloud_folders"]=["Inbox/../../elsewhere"]
        self.store()
        with self.assertRaisesRegex(ValueError,"Unsafe"):
            self.load()

    def test_negative_unmanaged_priority_folder(self):
        self.data["priority_cloud_folders"]=["Other"]
        self.store()
        with self.assertRaisesRegex(ValueError,"outside managed"):
            self.load()

    def test_negative_absent_managed_folder(self):
        self.data["managed_folders"]=["Missing"]
        self.data["priority_cloud_folders"]=["Missing"]
        self.store()
        with self.assertRaisesRegex(ValueError,"missing"):
            self.load()

    def test_negative_duplicate_managed_folders(self):
        self.data["managed_folders"]=["Inbox","Inbox"]
        self.store()
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            self.load()

    def test_static_no_machine_specific_paths(self):
        folder=Path(__file__).resolve().parents[1]/"src/proton_sync_engine/runtime"
        files=list(folder.glob("*.py"))
        self.assertEqual(len(files),12)
        for file in files:
            source=file.read_text()
            self.assertNotIn("/mnt/example-drive",source,file.name)
            self.assertNotIn(".local/bin",source,file.name)
            self.assertNotIn("Projekte/",source,file.name)
            self.assertFalse(file.stat().st_mode&0o111)

if __name__=="__main__":unittest.main()
