"""Cloud monitoring controls and safe preview regression tests."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from proton_sync_desktop import backend


class CloudMonitoringTests(unittest.TestCase):
    """Cloud choice controls both timers but never local inotify."""

    def test_positive_enable_both_timers(self):
        calls=[]
        def run(cmd,**kwargs):
            calls.append(cmd)
            return SimpleNamespace(returncode=0,stdout="enabled",stderr="")
        with patch.object(backend.subprocess,"run",side_effect=run),\
             patch.object(backend,"service_active",return_value=True):
            self.assertTrue(backend.set_cloud_monitor_enabled(True)["enabled"])
        toggles=[cmd for cmd in calls if "--now" in cmd]
        self.assertEqual(len(toggles),2)
        self.assertEqual({cmd[-1] for cmd in toggles},set(backend.CLOUD_TIMERS))
        self.assertFalse(any("watcher" in part for cmd in calls for part in cmd))

    def test_negative_reject_non_boolean(self):
        with self.assertRaises(ValueError):
            backend.set_cloud_monitor_enabled("off")

    def test_negative_restart_failure_rolls_back(self):
        calls=[]
        def run(cmd,**kwargs):
            calls.append(cmd)
            if "--now" in cmd and "disable" in cmd and len(
                [x for x in calls if "--now" in x and "disable" in x])==2:
                return SimpleNamespace(returncode=1,stdout="",stderr="cannot disable")
            return SimpleNamespace(returncode=0,stdout="enabled",stderr="")
        with patch.object(backend.subprocess,"run",side_effect=run):
            with self.assertRaises(RuntimeError):
                backend.set_cloud_monitor_enabled(False)
        self.assertTrue(any("enable" in cmd for cmd in calls if "--now" in cmd))

    def test_negative_one_missing_timer_not_reported_enabled(self):
        def run(cmd,**kwargs):
            return SimpleNamespace(returncode=0,
                stdout="disabled" if backend.CLOUD_TIMERS[1] in cmd else "enabled",
                stderr="")
        with patch.object(backend.subprocess,"run",side_effect=run),\
             patch.object(backend,"service_active",return_value=True):
            self.assertFalse(backend.cloud_monitor_enabled())


class ReadOnlyPreviewTests(unittest.TestCase):
    """The preview never starts a sync or executes a cloud deletion."""

    def test_positive_preview_reads_report(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            (folder/"pending_changes.json").write_text(
                '{"checked_at":"test","new_local":2,"possible_deletions":["x"],'
                '"probable_renames":[],"unmatched_new":["y"]}')
            with patch.object(backend,"STATE",folder):
                preview=backend.read_change_preview()
            self.assertEqual(preview["new_local"],2)
            self.assertEqual(preview["possible_deletions"],["x"])
            self.assertFalse(preview["cloud_changes_included"])

    def test_negative_missing_report_never_invents_changes(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(backend,"STATE",Path(td)):
                preview=backend.read_change_preview()
            self.assertEqual(preview["possible_deletions"],[])
            self.assertIsNone(preview["checked_at"])

if __name__=="__main__":unittest.main()
