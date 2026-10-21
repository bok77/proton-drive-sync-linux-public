"""An update must stage next to an intact, never overwritten installation."""
import tempfile,unittest
from pathlib import Path
from scripts.build_fedora_mvp import build
from scripts.install_fedora_mvp import install,verify
from scripts.stage_fedora_mvp_update import stage_update
from scripts.uninstall_fedora_mvp import uninstall

class StagedUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.candidate=self.root/'bundle';build(self.candidate)
        self.previous=self.root/'installed-v1';install(self.candidate,self.previous)
        self.next=self.root/'installed-v2'

    def test_update_preserves_both_packages_until_separate_approval(self):
        result=stage_update(self.previous,self.candidate,self.next)
        self.assertEqual(result['status'],'STAGED_NOT_ACTIVATED')
        self.assertTrue(result['launcher_unchanged'])
        verify(self.previous);verify(self.next)
        uninstall(self.next)
        verify(self.previous)

    def test_update_rejects_overwriting_existing_install(self):
        with self.assertRaises(ValueError):stage_update(self.previous,self.candidate,self.previous)
        verify(self.previous)

    def test_update_rejects_non_sibling_target(self):
        with self.assertRaises(ValueError):stage_update(self.previous,self.candidate,self.root/'other'/'nested')
        verify(self.previous)

    def test_update_refuses_tampered_previous_package(self):
        (self.previous/'bin/proton-drive-sync').write_text('tampered')
        with self.assertRaises(ValueError):stage_update(self.previous,self.candidate,self.next)
        self.assertFalse(self.next.exists())
