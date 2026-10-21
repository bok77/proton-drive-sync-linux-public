"""Synthetic concurrent creates on both portable engine entry paths."""
from types import SimpleNamespace
from test_portable_engine_e2e import PortableEngineIntegrationTests

class ConcurrentNewFile(PortableEngineIntegrationTests):
    def test_concurrent_remote_creation_must_not_overwrite_or_advance_baseline(self):
        key='Inbox/new-local.txt'
        self.engine.BASE.write_text('{}')
        local=self.root/key
        local.write_bytes(b'local version')
        original=self.cloud.cli
        injected=[False]
        def concurrent(*args,**kwargs):
            if args[:2]==('filesystem','upload') and not injected[0]:
                self.cloud.put(key,b'concurrent remote version')
                injected[0]=True
            return original(*args,**kwargs)
        self.engine.v.cli=concurrent
        self.assertNotEqual(self.run_engine(),0)
        self.assertTrue(injected[0])
        self.assertEqual(self.cloud.content[key],b'concurrent remote version')
        self.assertEqual(local.read_bytes(),b'local version')
        self.assertNotIn(key,__import__('json').loads(self.engine.BASE.read_text()))
        uploads=[req for req in self.cloud.requests if req[:2]==('filesystem','upload')]
        self.assertEqual(len(uploads),1)
        self.assertEqual(uploads[0][3:5],('skip',str(local)))
        # CLI skip returned 0, yet mismatching readback must fail and keep baseline.
        self.assertEqual(self.cloud.revisions[key], '1')
