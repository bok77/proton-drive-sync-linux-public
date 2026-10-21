"""Characterize non-atomic CLI upload: synthetic only, no production calls."""
from types import SimpleNamespace
from test_portable_engine_e2e import PortableEngineIntegrationTests

from unittest.mock import patch
from proton_sync_engine.existing_revision_guard import AtomicRevisionUnavailable

class AfterPreflightRace(PortableEngineIntegrationTests):
    def test_unsupported_conditional_update_stops_before_race(self):
        key='Inbox/race.txt'
        self.cloud.put(key,b'original')
        local=self.root/key
        local.write_bytes(b'original')
        self.ancestor(key)
        baseline=self.engine.BASE.read_bytes()
        local.write_bytes(b'local-change')
        original=self.cloud.cli
        raced=[False]
        def cli(*args,**kwargs):
            if args[:2]==('filesystem','upload'):
                self.cloud.put(key,b'concurrent-remote-change')
                raced[0]=True
            return original(*args,**kwargs)
        self.engine.v.cli=cli
        with patch('proton_sync_engine.existing_revision_guard.require_atomic_revision_update',
                   side_effect=AtomicRevisionUnavailable('conditional_revision_upload_unsupported')):
            self.assertNotEqual(self.run_engine(),0)
        self.assertFalse(raced[0], 'Unconditional upload must not be invoked')
        self.assertEqual(self.cloud.content[key],b'original')
        self.assertEqual(local.read_bytes(),b'local-change')
        self.assertEqual(self.engine.BASE.read_bytes(),baseline)
        self.assertFalse(any(req[:2]==('filesystem','upload') for req in self.cloud.requests))
