import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_engine import user_service_lifecycle as lc
class OneShotTests(unittest.TestCase):
    def test_rejects_missing_consent(self):
        with self.assertRaises(PermissionError):lc.run_once('/no/config','/no/bundle','not approved')
    def test_rejects_uninstalled_or_active_timer(self):
        for state in ({'status':'NOT_INSTALLED'}, {'status':'INSTALLED','timer_active':True,'timer_enabled':True}):
            with self.subTest(state=state),patch.object(lc,'status',return_value=state),self.assertRaises(PermissionError):
                lc.run_once('/config','/bundle',lc.RUN_ONCE_CONSENT)
    def test_starts_only_isolated_unit_if_paused_and_verified(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d);(state/'initial_pairing_verified.json').write_text('INITIAL_PAIRING_VERIFIED_V1')
            paths=type('P',(),{'state_dir':state})()
            with patch.object(lc,'status',return_value={'status':'INSTALLED','timer_active':False,'timer_enabled':False}),patch.object(lc,'load_paths',return_value=paths),patch.object(lc,'_run') as run:
                self.assertEqual(lc.run_once('/config','/bundle',lc.RUN_ONCE_CONSENT)['status'],'START_REQUESTED_NOT_COMPLETED')
                run.assert_called_once_with('start','--no-block',lc.UNIT)
    def test_pending_marker_denied(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d);(state/'initial_pairing_verified.json').write_text('INITIAL_PAIRING_VERIFIED_V1');(state/'initial_pairing_pending.json').write_text('')
            paths=type('P',(),{'state_dir':state})()
            with patch.object(lc,'status',return_value={'status':'INSTALLED','timer_active':False,'timer_enabled':False}),patch.object(lc,'load_paths',return_value=paths),self.assertRaises(PermissionError):
                lc.run_once('/config','/bundle',lc.RUN_ONCE_CONSENT)
