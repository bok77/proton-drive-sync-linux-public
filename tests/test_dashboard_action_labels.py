"""Guard the distinction between the mutating sync action and read-only preview."""
import unittest
from proton_sync_desktop.app import DASHBOARD_TEXT


class DashboardActionLabelsTests(unittest.TestCase):
    """Bilingual task descriptions must communicate their different effects."""

    def test_positive_primary_sync_action_explains_changes(self):
        self.assertEqual(DASHBOARD_TEXT["de"]["main_button"], "Jetzt synchronisieren")
        self.assertIn("übernimmt", DASHBOARD_TEXT["de"]["main_explain"])
        self.assertIn("applies", DASHBOARD_TEXT["en"]["main_explain"])

    def test_positive_preview_action_explains_read_only(self):
        self.assertEqual(DASHBOARD_TEXT["de"]["preview"], "Änderungen vorab prüfen")
        self.assertIn("nichts verändert", DASHBOARD_TEXT["de"]["preview_explain"])
        self.assertIn("without modifying", DASHBOARD_TEXT["en"]["preview_explain"])

    def test_negative_preview_label_is_not_a_sync_command(self):
        for lang in ("de", "en"):
            self.assertNotEqual(DASHBOARD_TEXT[lang]["preview"], DASHBOARD_TEXT[lang]["main_button"])
            self.assertNotIn("synchronisieren", DASHBOARD_TEXT[lang]["preview"].lower())
            self.assertNotIn("sync now", DASHBOARD_TEXT[lang]["preview"].lower())


if __name__ == "__main__":
    unittest.main()
