"""Static dialog guard tests: not a substitute for GNOME click / accessibility E2E."""
import unittest
from pathlib import Path

SRC=(Path(__file__).resolve().parents[1]/"src/proton_sync_desktop/setup_wizard.py")

class DialogSafetyContract(unittest.TestCase):
    def test_confirmation_defaults_to_cancel_and_requires_approve(self):
        code=SRC.read_text()
        self.assertIn('dialog.set_default_response("cancel")',code)
        self.assertIn('dialog.set_close_response("cancel")',code)
        self.assertIn('response=="approve"',code)
        self.assertIn('dialog.connect("response"',code)
        self.assertIn('dialog.set_transient_for(parent)',code)
    def test_backend_still_receives_separate_action_grants(self):
        code=SRC.read_text()
        for action in ('install','enable','pause','uninstall'):
            self.assertIn('"'+action+'"',code)
        for token in ('lc.INSTALL_CONSENT','lc.ENABLE_CONSENT','lc.PAUSE_CONSENT','lc.REMOVE_CONSENT'):
            self.assertIn(token,code)
        self.assertIn('lc.status(config,Path(__file__).resolve().parents[2])',code)
