"""Regression tests for dashboard timer controls and secondary preview copy."""
import unittest

from proton_sync_desktop import routing
from proton_sync_desktop.app import DASHBOARD_TEXT


class DashboardIntervalTests(unittest.TestCase):
    """The dashboard must expose each real configurable systemd cadence."""

    def test_positive_all_three_schedules_have_real_supported_intervals(self):
        for kind in ("local", "priority", "full"):
            self.assertIn(routing.DEFAULT["interval_minutes"][kind], routing.SUPPORTED[kind])
            self.assertGreaterEqual(len(routing.SUPPORTED[kind]), 3)

    def test_positive_translated_save_and_interval_headings(self):
        for lang in ("de", "en"):
            for key in ("schedule_heading", "local_schedule", "priority_schedule",
                        "full_schedule", "schedule_save", "schedule_saved"):
                self.assertTrue(DASHBOARD_TEXT[lang][key])

    def test_negative_unsupported_intervals_fail_validation(self):
        proposed={**routing.DEFAULT,"interval_minutes":{"local":1,"priority":10,"full":60}}
        with self.assertRaises(ValueError):
            routing.validate(proposed)

    def test_negative_preview_description_cannot_imply_file_modification(self):
        self.assertIn("nichts verändert", DASHBOARD_TEXT["de"]["preview_explain"])
        self.assertIn("without modifying", DASHBOARD_TEXT["en"]["preview_explain"])

if __name__ == "__main__":
    unittest.main()
