"""Managed launcher promotion and rollback must be isolated and reversible."""
import tempfile,unittest
from pathlib import Path
from scripts.build_fedora_mvp import build
from scripts.install_fedora_mvp import install,verify
from scripts.promote_fedora_mvp import CONSENT,APP_ID,register_initial,switch

class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);bundle=self.root/'bundle';build(bundle)
        self.old=self.root/'v1';self.new=self.root/'v2'
        install(bundle,self.old);install(bundle,self.new)
        self.apps=self.root/'apps';self.apps.mkdir(mode=0o700)

    def test_promotion_then_rollback(self):
        register_initial(self.old,self.apps,consent=CONSENT)
        self.assertEqual(switch(self.old,self.new,self.apps,consent=CONSENT)['status'],'DESKTOP_SWITCHED')
        self.assertIn(str(self.new), (self.apps/APP_ID).read_text())
        switch(self.new,self.old,self.apps,consent=CONSENT)
        self.assertIn(str(self.old),(self.apps/APP_ID).read_text())
        verify(self.old);verify(self.new)

    def test_existing_unmanaged_launcher_is_preserved(self):
        target=self.apps/APP_ID;target.write_text('unrelated content')
        with self.assertRaises(PermissionError):switch(self.old,self.new,self.apps,consent=CONSENT)
        self.assertEqual(target.read_text(),'unrelated content')

    def test_missing_launcher_cannot_be_taken_over(self):
        with self.assertRaises(FileNotFoundError):switch(self.old,self.new,self.apps,consent=CONSENT)

    def test_denied_without_consent(self):
        with self.assertRaises(PermissionError):register_initial(self.old,self.apps,consent='')
        self.assertFalse((self.apps/APP_ID).exists())
