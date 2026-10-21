"""Regression tests for live three-card UX and truthful progress semantics."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from proton_sync_desktop import backend
from proton_sync_desktop.app import UI_TEXT


class CardInterfaceTests(unittest.TestCase):
    """Check that the three independent actions map to exactly their own services."""

    def test_positive_three_bilingual_cards(self):
        """Each card must have its own translatable heading and action."""
        for locale in ("de","en"):
            for key in ("local_title","priority_title","full_title",
                        "upload_now","check_now","full_now",
                        "running","source","destination"):
                self.assertTrue(UI_TEXT[locale][key])

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_positive_priority_action_uses_existing_service(self,run):
        """Manual priority checking may invoke only the guarded systemd unit."""
        run.return_value=SimpleNamespace(returncode=0,stdout="",stderr="")
        backend.request_priority_sync()
        run.assert_called_once_with(
            ["systemctl","--user","start","--no-block","proton-cloud-priority.service"],
            capture_output=True,text=True,timeout=6)

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_negative_priority_action_failure_not_silenced(self,run):
        """A failed systemd request must be available for UI error reporting."""
        run.return_value=SimpleNamespace(returncode=1,stdout="",stderr="Service missing")
        result=backend.request_priority_sync()
        self.assertEqual(result.returncode,1)
        self.assertIn("missing",result.stderr)

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_negative_priority_timeout_not_reported_as_success(self,run):
        """Systemd timeouts cannot be converted to fabricated success."""
        import subprocess
        run.side_effect=subprocess.TimeoutExpired(cmd=["systemctl"],timeout=6)
        with self.assertRaises(subprocess.TimeoutExpired):
            backend.request_priority_sync()


if __name__=="__main__":
    unittest.main()
