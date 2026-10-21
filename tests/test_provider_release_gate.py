import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_engine.provider_release_gate import evaluate

class ProviderReleaseGateTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name);self.cfg=root/'config';self.cfg.write_text('{}');self.cfg.chmod(0o600)
        self.keys=root/'keys';self.keys.mkdir(mode=0o700)
        self.app=root/'app';self.app.mkdir(mode=0o700)
        self.cache=root/'cache';self.cache.mkdir(mode=0o700)
    def run_gate(self,mode='keychain',**kwargs):
        with patch('proton_sync_engine.secret_boundary.subprocess.run') as run:
            run.return_value.returncode=0
            run.return_value.stdout='org.freedesktop.secrets 1 user\n'
            return evaluate(credentials_mode=mode,config=self.cfg,keyring_dir=self.keys,
                            app_dir=self.app,cache_dir=self.cache,**kwargs)
    def test_default_blocks_unverified_provider_contract(self):
        result=self.run_gate()
        self.assertEqual(result.status,'BLOCKED')
        self.assertIn('EVENT_BASED_SYNC_UNVERIFIED',result.blockers)
        self.assertIn('ATOMIC_REVISION_WRITE_UNVERIFIED',result.blockers)
    def test_unsafe_credentials_always_block(self):
        result=self.run_gate('unsafe_file',event_sync_verified=True,conditional_revision_write_verified=True)
        self.assertIn('UNSAFE_OR_UNKNOWN_CREDENTIAL_STORE',result.blockers)
    def test_insecure_cache_blocks_and_does_not_read_contents(self):
        (self.cache/'PRIVATE').write_text('SECRET');(self.cache/'PRIVATE').chmod(0o644)
        result=self.run_gate(event_sync_verified=True,conditional_revision_write_verified=True)
        self.assertIn('CLI_LOCAL_METADATA_EXPOSURE',result.blockers)
        self.assertNotIn('PRIVATE',repr(result))
    def test_all_evidence_must_be_explicitly_supplied(self):
        result=self.run_gate(event_sync_verified=True,conditional_revision_write_verified=True)
        self.assertEqual(result.status,'PASS')
