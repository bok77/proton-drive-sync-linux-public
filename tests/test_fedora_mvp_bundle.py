"""Isolated build/install contract; no user services or cloud credentials."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/"scripts"/path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class FedoraBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.bundle=self.root/"bundle"
        self.install=self.root/"installed"
        self.build=load("mvp_build","build_fedora_mvp.py")
        self.installer=load("mvp_install","install_fedora_mvp.py")

    def test_build_install_readback_and_launcher(self):
        summary=self.build.build(self.bundle)
        self.assertEqual(summary["status"],"TEST_CANDIDATE_NOT_ACTIVATED")
        self.assertGreater(summary["files"],30)
        result=self.installer.install(self.bundle,self.install)
        self.assertEqual(result["status"],"INSTALLED_NOT_ACTIVATED")
        self.assertTrue((self.install/"bin/proton-drive-sync").is_file())
        self.assertTrue((self.install/"src/proton_sync_engine/runtime/proton-bisync.py").is_file())
        self.assertFalse((self.install/"units").exists())
        self.installer.verify(self.install)

    def test_no_overwrite_existing_installation(self):
        self.build.build(self.bundle)
        self.install.mkdir()
        with self.assertRaises(FileExistsError):
            self.installer.install(self.bundle,self.install)
        self.assertEqual(list(self.install.iterdir()),[])

    def test_tampered_bundle_is_rejected(self):
        self.build.build(self.bundle)
        (self.bundle/"bin/proton-drive-sync").write_text("modified")
        with self.assertRaisesRegex(ValueError,"integrity"):
            self.installer.install(self.bundle,self.install)
        self.assertFalse(self.install.exists())

    def test_symlinked_bundle_is_rejected(self):
        self.build.build(self.bundle)
        link=self.root/"link"
        link.symlink_to(self.bundle,target_is_directory=True)
        with self.assertRaises(ValueError):
            self.installer.verify(link)
