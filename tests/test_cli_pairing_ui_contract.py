import unittest
from proton_sync_desktop.cli_error_labels import safe_pairing_error

class PairingErrorContract(unittest.TestCase):
    def test_specific_classified_errors_in_both_languages(self):
        for code in ('AUTH','RATE_LIMIT','TIMEOUT','CONFLICT','PROVIDER_ERROR'):
            for lang in ('de','en'):
                result=safe_pairing_error('CLI_'+code,lang)
                self.assertTrue(result)
                self.assertNotEqual(result,safe_pairing_error('unexpected raw',lang))
    def test_untrusted_text_and_token_never_render(self):
        for source in ('unauthorized token=private','CLI_INVALID token=secret','CLI_AUTH secret',None):
            out=safe_pairing_error(source)
            self.assertNotIn('secret',out)
            self.assertNotIn('private',out)
            self.assertEqual(out,safe_pairing_error(None))
