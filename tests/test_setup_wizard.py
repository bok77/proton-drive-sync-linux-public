"""GNOME setup wizard is accessible, localized and fail-closed."""
import unittest
from pathlib import Path

from proton_sync_desktop import setup_wizard
from proton_sync_desktop import app

class SetupWizardTests(unittest.TestCase):
    def test_complete_localized_copy(self):
        for lang in ("de","en"):
            text=setup_wizard.COPY[lang]
            for key in ("title","one","two","three","four","demo","blocked","confirm"):
                self.assertTrue(text[key],(lang,key))
            self.assertIn("BLOCKED",text["demo_body"])

    def test_wizard_is_connected_to_application(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/app.py").read_text()
        self.assertIn('self.pages["setup"]=self.tabs.add_titled',source)
        self.assertIn('make_setup_wizard(app.language)',source)
        self.assertIn('if not verified_isolated_pairing():',source)

    def test_activation_is_not_enabled(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/setup_wizard.py").read_text()
        self.assertIn('button.set_sensitive(False)',source)
        self.assertIn("approve_pairing(",source)
        self.assertIn("I APPROVE EXACT INITIAL PAIRING",source)
        self.assertIn('review.get("status")!="READY_FOR_EXPLICIT_APPROVAL"',source)
        self.assertNotIn("request_full_sync",source)
        self.assertNotIn("subprocess",source)

    def test_guided_service_controls_confirm_and_keep_backend_guards(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/setup_wizard.py").read_text()
        self.assertIn('Adw.MessageDialog(',source)
        self.assertIn('dialog.set_default_response("cancel")',source)
        self.assertIn('dialog.set_close_response("cancel")',source)
        self.assertIn('lc.status(config,Path(__file__).resolve().parents[2])',source)
        self.assertIn('grants={"install":lc.INSTALL_CONSENT',source)
        self.assertIn('service_busy["value"]',source)
        self.assertIn('service_state.update(primary="install",secondary=None)',source)
        self.assertIn('service_state.update(primary="pause",secondary="uninstall")',source)
        self.assertNotIn('service_consent=Gtk.Entry()',source)

    def test_verified_pairing_controls_are_removed_but_service_remains(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/setup_wizard.py").read_text()
        self.assertIn("def verified_isolated_pairing():",source)
        self.assertIn('state/"initial_pairing_verified.json"',source)
        self.assertIn('body.remove(obsolete)',source)
        self.assertLess(source.index('body.remove(obsolete)'),source.index('service_group=group('))

    def test_single_primary_action_and_optional_secondary(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/setup_wizard.py").read_text()
        self.assertIn('primary.add_css_class("suggested-action")',source)
        self.assertIn('control.set_visible(action is not None)',source)

    def test_preview_is_explicitly_demonstration_only(self):
        for lang in ("de","en"):
            self.assertIn("test",setup_wizard.COPY[lang]["demo_title"].lower())
