"""Offline/failure matrix and independent HOME install lifecycle gates."""
import os,subprocess,tempfile,unittest
from pathlib import Path
from scripts import build_fedora_mvp,install_fedora_mvp
from scripts.uninstall_fedora_mvp import uninstall

class IndependentHomeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="fedora-clean-home-proof-")
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.home=self.root/"home"
        self.home.mkdir(mode=0o700)
        build_fedora_mvp.build(self.root/"bundle")
        install_fedora_mvp.install(self.root/"bundle",self.root/"installed")

    def test_install_launch_uninstall_in_fresh_home(self):
        proc=subprocess.run(
            [str(self.root/"installed/bin/proton-drive-sync"),"--self-test"],
            env={**os.environ,"HOME":str(self.home)},
            capture_output=True,text=True,timeout=30)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertIn("L10N_OK",proc.stdout)
        self.assertIn("BACKEND_OK",proc.stdout)
        self.assertEqual(uninstall(self.root/"installed")["status"],"REMOVED_CANDIDATE_ONLY")
        self.assertFalse((self.root/"installed").exists())
        self.assertTrue(self.home.is_dir())

    def test_uninstall_refuses_unknown_file(self):
        unknown=self.root/"installed/unknown-user-file"
        unknown.write_text("must survive")
        with self.assertRaises(ValueError):
            uninstall(self.root/"installed")
        self.assertEqual(unknown.read_text(),"must survive")
        self.assertTrue((self.root/"installed").exists())

    def test_uninstall_refuses_tampered_payload(self):
        app=self.root/"installed/bin/proton-drive-sync"
        app.write_text("modified")
        with self.assertRaises(ValueError):
            uninstall(self.root/"installed")
        self.assertEqual(app.read_text(),"modified")
