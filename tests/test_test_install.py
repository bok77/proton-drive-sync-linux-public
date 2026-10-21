"""End-to-end tests of explicitly approved, isolated, non-running service install."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from proton_sync_engine import test_install
from proton_sync_engine.install_plan import UNIT_NAMES, _service_text

class TestInstallContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.source=self.base/"stage"
        (self.source/"units").mkdir(parents=True)
        self.root=self.base/"mount"/"Sync"
        (self.root/"Inbox").mkdir(parents=True)
        self.state=self.base/"state"
        self.install=self.base/"installation"
        self.units=self.base/"systemd-test-units"
        info={
            "status":"PREVIEW_ONLY",
            "activation_authorized":False,
            "local_root":str(self.root),
            "mount_root":str(self.root.parent),
            "state_dir":str(self.state),
            "staged_units":list(UNIT_NAMES.values()),
        }
        (self.source/"INSTALL_NOT_ACTIVATED.json").write_text(json.dumps(info))
        (self.source/"DO_NOT_ENABLE.txt").write_text(
            "No unit here is ready to enable; installer activation is NOT IMPLEMENTED.\n")
        for kind,name in UNIT_NAMES.items():
            (self.source/"units"/name).write_text(_service_text(kind))
        self.approval=test_install.APPROVAL

    def approved(self):
        return test_install.install_test(self.source,self.install,self.units,self.approval)

    def test_positive_install_verify_and_uninstall(self):
        result=self.approved()
        self.assertEqual(result["status"],"TEST_ONLY_NEVER_ACTIVATED")
        self.assertFalse(result["activation_authorized"])
        self.assertEqual(result,test_install.verify_test_install(self.install,self.units))
        for name in UNIT_NAMES.values():
            content=(self.units/name).read_text()
            self.assertIn("ExecCondition=/usr/bin/false",content)
            self.assertIn("ExecStart=/usr/bin/false",content)
            self.assertNotIn("[Install]",content)
        test_install.uninstall_test(self.install,self.units)
        self.assertFalse(self.install.exists())
        self.assertFalse(self.units.exists())
        self.assertTrue((self.root/"Inbox").is_dir())

    def test_negative_no_approval_makes_no_changes(self):
        with self.assertRaises(PermissionError):
            test_install.install_test(self.source,self.install,self.units,"yes")
        self.assertFalse(self.install.exists())

    def test_negative_existing_unit_dir_is_preserved(self):
        self.units.mkdir()
        sentinel=self.units/"something"
        sentinel.write_text("unrelated")
        with self.assertRaises(FileExistsError):
            self.approved()
        self.assertEqual(sentinel.read_text(),"unrelated")

    def test_negative_data_root_rejected(self):
        with self.assertRaises(ValueError):
            test_install.install_test(self.source,self.root/"nested",self.units,self.approval)

    def test_negative_tampered_service_cannot_be_removed(self):
        self.approved()
        service=self.units/UNIT_NAMES["full"]
        service.write_text("changed")
        with self.assertRaisesRegex(ValueError,"changed"):
            test_install.uninstall_test(self.install,self.units)
        self.assertEqual(service.read_text(),"changed")

    def test_negative_unknown_files_cannot_be_removed(self):
        self.approved()
        extra=self.units/"custom.service"
        extra.write_text("keep")
        with self.assertRaisesRegex(ValueError,"Unknown"):
            test_install.uninstall_test(self.install,self.units)
        self.assertEqual(extra.read_text(),"keep")

    def test_negative_invalid_stage_never_installs(self):
        with patch("proton_sync_engine.test_install.verify_stage",side_effect=ValueError("invalid")):
            with self.assertRaises(ValueError):
                self.approved()
        self.assertFalse(self.install.exists())

if __name__=="__main__":unittest.main()
