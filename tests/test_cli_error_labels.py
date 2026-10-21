import unittest
from proton_sync_desktop.cli_error_labels import error_label
from proton_sync_engine.cli_diagnostics import CliError

class CliErrorLabelsTests(unittest.TestCase):
    def test_all_categories_in_both_languages(self):
        for category in CliError:
            for lang in ('de','en'):
                self.assertTrue(error_label(category,lang))
                self.assertNotIn('SECRET',error_label(category,lang))
    def test_unknown_input_never_reflects_sensitive_text(self):
        self.assertNotIn('private-token',error_label('private-token'))
        self.assertIn('Proton',error_label(CliError.AUTH,'de'))
