"""Version-transition safety and deterministic remote preflight drift tests."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from scripts.build_fedora_mvp import build
from scripts.install_fedora_mvp import install,verify
from scripts.uninstall_fedora_mvp import uninstall
from test_portable_engine_e2e import PortableEngineIntegrationTests

class ManifestedVersionTransitions(unittest.TestCase):
    def test_two_distinct_manifested_candidates_require_explicit_removal_and_can_roll_back(self):
        with tempfile.TemporaryDirectory(prefix='mvp-version-transition-') as root:
            root=Path(root);a=root/'a';b=root/'b';dest=root/'active'
            build(a);build(b)
            marker=b/'bin/proton-drive-sync'
            marker.write_bytes(marker.read_bytes()+b'\n# synthetic different version\n')
            manifest=json.loads((b/'MANIFEST.json').read_text())
            manifest['files']['bin/proton-drive-sync']=hashlib.sha256(marker.read_bytes()).hexdigest()
            (b/'MANIFEST.json').write_text(json.dumps(manifest))
            verify(a);verify(b)
            original=(a/'bin/proton-drive-sync').read_bytes()
            install(a,dest)
            with self.assertRaises(FileExistsError):install(b,dest)
            self.assertEqual((dest/'bin/proton-drive-sync').read_bytes(),original)
            uninstall(dest)
            install(b,dest)
            self.assertEqual((dest/'bin/proton-drive-sync').read_bytes(),marker.read_bytes())
            uninstall(dest)
            install(a,dest)
            self.assertEqual((dest/'bin/proton-drive-sync').read_bytes(),original)
            uninstall(dest)

class PreflightRevisionDrift(PortableEngineIntegrationTests):
    def test_remote_revision_changing_before_preflight_never_uploads(self):
        key='Inbox/changed.txt'
        self.cloud.put(key,b'ancestor')
        local=self.root/key;local.write_bytes(b'ancestor')
        self.ancestor(key)
        before=self.engine.BASE.read_bytes()
        local.write_bytes(b'new local')
        original=self.cloud.cli
        changed=[False]
        def injected(*args,**kwargs):
            if args[:2]==('filesystem','info') and not changed[0]:
                self.cloud.put(key,b'concurrent remote edit')
                changed[0]=True
            return original(*args,**kwargs)
        self.engine.v.cli=injected
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(self.cloud.content[key],b'concurrent remote edit')
        self.assertEqual(local.read_bytes(),b'new local')
        self.assertEqual(self.engine.BASE.read_bytes(),before)
        self.assertFalse(any(req[:2]==('filesystem','upload') for req in self.cloud.requests))
