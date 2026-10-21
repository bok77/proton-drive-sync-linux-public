import tempfile,unittest
from pathlib import Path
from proton_sync_engine.v1_live_test_gate import evaluate
class V1LiveTestGateTests(unittest.TestCase):
    def test_missing_test_session_stays_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private';p.mkdir(mode=0o700)
            r=evaluate(root=p,scope='/my-files/ProtonSync-Test',independent_session_verified=False,explicit_live_approval=False)
            self.assertEqual(r.status,'BLOCKED')
            self.assertIn('INDEPENDENT_TEST_SESSION_UNVERIFIED',r.blockers)
    def test_wrong_scope_and_production_session_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private';p.mkdir(mode=0o700)
            r=evaluate(root=p,scope='/my-files/Personal',independent_session_verified=True,explicit_live_approval=True,production_session_reused=True)
            self.assertEqual(r.status,'BLOCKED')
            self.assertIn('PRODUCTION_SESSION_FORBIDDEN',r.blockers)
            self.assertIn('TEST_SCOPE_MISMATCH',r.blockers)
    def test_even_ready_does_not_start_live_operation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private';p.mkdir(mode=0o700)
            r=evaluate(root=p,scope='/my-files/ProtonSync-Test',independent_session_verified=True,explicit_live_approval=True)
            self.assertEqual(r.status,'READY_FOR_SEPARATE_MANUAL_REVIEW')
    def test_world_readable_directory_denied(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'private';p.mkdir(mode=0o755)
            r=evaluate(root=p,scope='/my-files/ProtonSync-Test',independent_session_verified=True,explicit_live_approval=True)
            self.assertEqual(r.status,'BLOCKED')
