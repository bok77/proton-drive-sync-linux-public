import unittest
from proton_sync_desktop.setup_wizard import COPY
class V1PilotLimitationsTests(unittest.TestCase):
    def test_pairing_notice_is_explicit_for_both_languages(self):
        self.assertIn('bestehender Cloud-Dateien',COPY['de']['status'])
        self.assertIn('existing cloud files',COPY['en']['status'])
        self.assertIn('nicht aktualisieren',COPY['de']['compare_info'])
        self.assertIn('cannot update',COPY['en']['compare_info'])
