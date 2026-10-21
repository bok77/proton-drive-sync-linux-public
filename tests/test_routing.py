"""Tests for editable folder routes and transactional systemd timer changes."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from proton_sync_desktop import routing


class RouteEditorTests(unittest.TestCase):
    """Positive and negative tests without touching real systemd or files."""

    def test_positive_configure_cloud_folder_and_cadence(self):
        """A valid cloud subfolder and supported cadence must roundtrip."""
        data={**routing.DEFAULT,"priority_cloud_folders":["00_Inbox","40_Knowledge/example-workflow/Current"],
              "interval_minutes":{"local":10,"priority":15,"full":120}}
        valid=routing.validate(data)
        self.assertEqual(valid["priority_cloud_folders"][0],"00_Inbox")
        self.assertEqual(routing.calendar_expression(120),"*-*-* 00/2:00:00")

    def test_negative_reject_parent_traversal(self):
        """A malicious cloud folder must never be accepted."""
        with self.assertRaises(ValueError):
            routing.validate_folder("00_Inbox/../../Secrets")

    def test_negative_reject_root_change(self):
        """Changing the baseline-bound local root requires a separate migration."""
        bad={**routing.DEFAULT,"local_root":"/tmp/different"}
        with self.assertRaises(ValueError):
            routing.validate(bad)

    def test_negative_reject_incorrect_interval(self):
        """Unsupported schedules may never produce arbitrary timer units."""
        bad={**routing.DEFAULT,"interval_minutes":{"local":2,"priority":10,"full":60}}
        with self.assertRaises(ValueError):
            routing.validate(bad)

    def test_negative_duplicate_cloud_folders(self):
        """Identical priority routes would generate inconsistent repeated scans."""
        bad={**routing.DEFAULT,"priority_cloud_folders":["00_Inbox","00_Inbox"]}
        with self.assertRaises(ValueError):
            routing.validate(bad)

    def test_positive_apply_timer_and_config(self):
        """Real service unit files are updated only after a valid staged change."""
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            units=base/"units";units.mkdir()
            conf=base/"routing.json"
            for name,unit in routing.SERVICES.items():
                (units/unit).write_text(routing.timer_text(name,routing.DEFAULT["interval_minutes"][name]))
            new={**routing.DEFAULT,"interval_minutes":{"local":10,"priority":15,"full":120}}
            with patch.object(routing,"CONFIG",conf), patch("pathlib.Path.home",return_value=base):
                # routing.apply uses user's unit directory; create in test home.
                systemd=base/".config/systemd/user";systemd.mkdir(parents=True)
                for name,unit in routing.SERVICES.items():
                    (systemd/unit).write_text(routing.timer_text(name,routing.DEFAULT["interval_minutes"][name]))
                cmds=[]
                def fake(cmd,**kwargs):
                    cmds.append(cmd)
                    return SimpleNamespace(returncode=0,stdout="",stderr="")
                result=routing.apply(new,executor=fake)
                self.assertEqual(result["interval_minutes"]["priority"],15)
                self.assertEqual(json.loads(conf.read_text())["interval_minutes"]["full"],120)
                self.assertIn("00/2", (systemd/routing.SERVICES["full"]).read_text())
                self.assertEqual(sum(c[2]=="restart" for c in cmds if len(c)>2),3)

    def test_negative_rollback_timer_on_failure(self):
        """A failed systemd restart restores prior timer files and settings."""
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);units=home/".config/systemd/user";units.mkdir(parents=True)
            prior={}
            for name,unit in routing.SERVICES.items():
                value=routing.timer_text(name,routing.DEFAULT["interval_minutes"][name])
                (units/unit).write_text(value);prior[unit]=value
            new={**routing.DEFAULT,"interval_minutes":{"local":10,"priority":15,"full":120}}
            conf=home/"routing.json"
            with patch.object(routing,"CONFIG",conf),patch("pathlib.Path.home",return_value=home):
                counter=[0]
                def flaky(cmd,**kwargs):
                    if "restart" in cmd:
                        counter[0]+=1
                        if counter[0]==1:return SimpleNamespace(returncode=1)
                    return SimpleNamespace(returncode=0)
                with self.assertRaises(RuntimeError):
                    routing.apply(new,executor=flaky)
                for unit,contents in prior.items():
                    self.assertEqual((units/unit).read_text(),contents)
                self.assertEqual(routing.load()["interval_minutes"]["local"],5)


if __name__=="__main__":
    unittest.main()

class CloudFolderSelectionTests(unittest.TestCase):
    """Ensure typed and chosen cloud paths cannot silently target invalid nodes."""

    @patch("proton_sync_desktop.backend.subprocess.run")
    @patch("proton_sync_desktop.backend.HOME")
    def test_positive_existing_cloud_folder(self,home,run):
        from proton_sync_desktop import backend
        with tempfile.TemporaryDirectory() as td:
            h=Path(td);home.__truediv__.side_effect=lambda item:h/item
            (h/".local/bin").mkdir(parents=True)
            (h/".local/bin/proton-drive").write_text("test")
            run.return_value=SimpleNamespace(returncode=0,stdout=json.dumps({"type":"folder"}))
            self.assertTrue(backend.verify_cloud_directories(["00_Inbox"]))

    @patch("proton_sync_desktop.backend.subprocess.run")
    @patch("proton_sync_desktop.backend.HOME")
    def test_negative_missing_cloud_folder(self,home,run):
        from proton_sync_desktop import backend
        with tempfile.TemporaryDirectory() as td:
            h=Path(td);home.__truediv__.side_effect=lambda item:h/item
            (h/".local/bin").mkdir(parents=True)
            (h/".local/bin/proton-drive").write_text("test")
            run.return_value=SimpleNamespace(returncode=1,stdout="")
            with self.assertRaises(ValueError):
                backend.verify_cloud_directories(["00_Inbox/does-not-exist"])
