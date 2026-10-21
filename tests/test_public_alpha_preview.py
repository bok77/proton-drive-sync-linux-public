"""Static routing guard: the opt-in alpha preview cannot add prod controls."""
import unittest
from pathlib import Path

class PublicAlphaPreviewTests(unittest.TestCase):
    def test_preview_is_separate_and_non_mutating(self):
        source=(Path(__file__).resolve().parents[1]/'src/proton_sync_desktop/app.py').read_text()
        segment=source.split('if getattr(app,"public_alpha",False):',1)[1].split('switch=Adw.ViewSwitcherBar',1)[0]
        self.assertIn('self.make_public_alpha_info()',segment)
        self.assertIn('self.make_public_alpha_settings()',segment)
        self.assertIn('else:',segment)
        for method in ('make_public_alpha_info','make_public_alpha_settings'):
            body=source.split('    def '+method+'(self):',1)[1].split('\n    def ',1)[0]
            for forbidden in ('backend.request_', 'backend.set_', 'systemctl', 'lc.install(', 'lc.run_once(', 'sync_full_now('):
                self.assertNotIn(forbidden,body)
        self.assertIn('public_alpha="--public-alpha" in sys.argv',source)
        refresh=source.split('    def refresh(self):',1)[1].split('    def ',1)[0]
        self.assertLess(refresh.index('if getattr(self.app,"public_alpha",False):'),refresh.index('data=backend.snapshot()'))
