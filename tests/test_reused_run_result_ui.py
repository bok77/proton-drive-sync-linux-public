"""Both GTK entry points reuse the same authoritative V1 result presenter."""
import unittest
from pathlib import Path
from unittest.mock import Mock
from proton_sync_desktop.run_result_ui import show_result

class ReusedResultTests(unittest.TestCase):
    def test_success_and_attention_are_evidence_driven(self):
        for errors,expected in ((0,'Test complete'),(1,'Run with conflicts/errors')):
            row=Mock()
            self.assertTrue(show_result(row,{'status':'SUCCESS' if errors==0 else 'ATTENTION',
                  'uploaded':1,'remote_downloaded':2,'conflicts':0,'errors':errors},'en'))
            row.set_title.assert_called_with(expected)
            self.assertIn('Upload: 1',row.set_subtitle.call_args.args[0])
    def test_pending_does_not_emit_success(self):
        row=Mock()
        self.assertFalse(show_result(row,{'status':'PENDING'},'en'))
        row.set_subtitle.assert_not_called()
    def test_unknown_does_not_forge_counters(self):
        row=Mock()
        self.assertTrue(show_result(row,{'status':'UNKNOWN'},'en'))
        row.set_subtitle.assert_not_called()
    def test_existing_wizard_and_alpha_share_presenter(self):
        root=Path(__file__).resolve().parents[1]/'src/proton_sync_desktop'
        wizard=(root/'setup_wizard.py').read_text()
        alpha=(root/'app.py').read_text()
        self.assertIn('result_row=make_result_row(language)',wizard)
        self.assertIn('show_result(result_row,evidence,language)',wizard)
        self.assertIn('self.alpha_result=make_result_row(self.app.language)',alpha)
        self.assertIn('show_result(self.alpha_result,evidence,self.app.language)',alpha)
        self.assertIn('alpha_lifecycle,operation',alpha)
