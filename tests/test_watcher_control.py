"""Safeguards for explicitly controlling the local Linux file watcher."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from proton_sync_desktop import backend
from proton_sync_desktop.app import UI_TEXT

class WatcherControlTests(unittest.TestCase):
    """Separate local event detection from scheduled two-way synchronization."""

    def test_positive_toggle_on_and_readback(self):
        with patch.object(backend,"watcher_enabled",return_value=True),\
             patch.object(backend,"service_active",return_value=True),\
             patch.object(backend.subprocess,"run",return_value=SimpleNamespace(returncode=0,stderr="")) as run:
            result=backend.set_watcher_enabled(True)
            self.assertEqual(result,{"enabled":True,"active":True})
            self.assertEqual(run.call_args.args[0],
                ["systemctl","--user","enable","--now","proton-sync-watcher.service"])

    def test_positive_toggle_off_preserves_scheduled_timers(self):
        with patch.object(backend,"watcher_enabled",return_value=False),\
             patch.object(backend,"service_active",return_value=False),\
             patch.object(backend.subprocess,"run",return_value=SimpleNamespace(returncode=0,stderr="")) as run:
            result=backend.set_watcher_enabled(False)
            self.assertEqual(result,{"enabled":False,"active":False})
            call=run.call_args.args[0]
            self.assertEqual(call,
                ["systemctl","--user","disable","--now","proton-sync-watcher.service"])
            self.assertFalse(any(".timer" in a for a in call))

    def test_negative_unsupported_toggle_input(self):
        with self.assertRaises(ValueError):
            backend.set_watcher_enabled("off")

    def test_negative_systemd_failure(self):
        with patch.object(backend.subprocess,"run",
                          return_value=SimpleNamespace(returncode=1,stderr="permission denied")):
            with self.assertRaisesRegex(RuntimeError,"permission denied"):
                backend.set_watcher_enabled(False)

    def test_negative_readback_mismatch(self):
        with patch.object(backend.subprocess,"run",
                          return_value=SimpleNamespace(returncode=0,stderr="")),\
             patch.object(backend,"watcher_enabled",return_value=True),\
             patch.object(backend,"service_active",return_value=True):
            with self.assertRaisesRegex(RuntimeError,"readback"):
                backend.set_watcher_enabled(False)

    def test_positive_preference_off_does_not_restart(self):
        with patch.object(backend,"watcher_enabled",return_value=False),\
             patch.object(backend.subprocess,"run") as run:
            result=backend.restart_watcher()
            self.assertEqual(result.returncode,0)
            run.assert_not_called()

    def test_bilingual_product_terms(self):
        self.assertIn("Linux",UI_TEXT["de"]["watcher_explanation"])
        self.assertIn("Linux",UI_TEXT["en"]["watcher_explanation"])
        self.assertIn("Proton",UI_TEXT["de"]["full_note"])
        self.assertIn("Proton",UI_TEXT["en"]["full_note"])

if __name__=="__main__":
    unittest.main()
