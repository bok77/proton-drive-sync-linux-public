import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_engine.sdk_live_preflight import check
class LivePreflightTests(unittest.TestCase):
    def test_absent_runtime_and_auth_fail_closed(self):
        with patch('proton_sync_engine.sdk_live_preflight.shutil.which',return_value=None):
            r=check(sdk_manifest=Path('/no/sdk.json'),isolated_config=Path('/no/test.json'),test_scope='ProtonSync-Test')
        self.assertEqual(r.status,'BLOCKED')
        self.assertIn('BUN_RUNTIME_MISSING',r.blockers)
        self.assertIn('ISOLATED_AUTH_NOT_VERIFIED',r.blockers)
    def test_even_verified_inputs_require_manual_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'sdk.json';a.write_text('{}')
            b=Path(tmp)/'config.json';b.write_text('{}')
            with patch('proton_sync_engine.sdk_live_preflight.shutil.which',return_value='/usr/bin/bun'):
                r=check(sdk_manifest=a,isolated_config=b,test_scope='ProtonSync-Test',explicit_test_session_proof=True)
            self.assertEqual(r.blockers,('HUMAN_LIVE_PROOF_GATE_REQUIRED',))
