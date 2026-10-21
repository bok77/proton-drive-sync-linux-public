"""Offline tests for guided sync UX and guarded systemd actions."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from proton_sync_desktop import backend
from proton_sync_desktop.sync_plan import ROUTES,route_descriptions,unavailable_route_indices
from proton_sync_desktop.i18n import action_text,EVENT_NAMES


class GuidedSyncPositiveTests(unittest.TestCase):
    """Prove route clarity and successful dispatch without touching cloud files."""

    def test_routes_are_explicit_in_both_languages(self):
        """All three routes must state a source, destination, and true cadence."""
        for lang in ("de","en"):
            rows=route_descriptions(lang)
            self.assertEqual(len(rows),3)
            for source,destination,cadence in rows:
                self.assertTrue(source and destination and cadence)
            self.assertIn("/mnt/example-sync-root",rows[0][0])
            self.assertIn("/my-files",rows[0][1])
            self.assertIn("10" if lang=="de" else "10",rows[1][2])
            self.assertIn("Fedora",action_text(lang,"sync_local_now"))

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_manual_full_sync_requests_existing_guarded_service(self,run):
        """The full-sync button must only request the predefined systemd unit."""
        run.return_value=SimpleNamespace(returncode=0,stderr="",stdout="")
        result=backend.request_full_sync()
        self.assertEqual(result.returncode,0)
        run.assert_called_once_with(
            ["systemctl","--user","start","--no-block","proton-bisync.service"],
            capture_output=True,text=True,timeout=6,
        )

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_local_sync_requests_existing_guarded_service(self,run):
        """No direct Proton CLI or destructive shell action is used by the GUI."""
        run.return_value=SimpleNamespace(returncode=0,stderr="",stdout="")
        backend.request_local_sync()
        self.assertIn("proton-bisync-quick.service",run.call_args.args[0])


class GuidedSyncNegativeTests(unittest.TestCase):
    """Prove absent services and errors cannot be shown as successful sync."""

    def test_missing_service_state_is_not_healthy(self):
        """An absent route must be marked unavailable, not silently assumed OK."""
        state={"local_timer":True,"cloud_timer":False}
        self.assertEqual(unavailable_route_indices(state),(1,2))

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_failed_manual_start_is_propagated(self,run):
        """Nonzero systemd results must be returned for explicit UI error display."""
        run.return_value=SimpleNamespace(returncode=1,stderr="unit missing",stdout="")
        result=backend.request_full_sync()
        self.assertNotEqual(result.returncode,0)
        self.assertIn("unit missing",result.stderr)

    @patch("proton_sync_desktop.backend.subprocess.run")
    def test_timeout_does_not_become_fake_success(self,run):
        """A timed-out service request is an error, not a success notification."""
        import subprocess
        run.side_effect=subprocess.TimeoutExpired(cmd=["systemctl"],timeout=6)
        with self.assertRaises(subprocess.TimeoutExpired):
            backend.request_full_sync()

    def test_route_does_not_promise_instant_cloud_download(self):
        """Cloud downloads are explicitly described as polling, not realtime."""
        for lang in ("de","en"):
            routes=route_descriptions(lang)
            self.assertIn("10",routes[1][2])
            self.assertNotIn("realtime",routes[2][2].lower())


if __name__=="__main__":
    unittest.main()
