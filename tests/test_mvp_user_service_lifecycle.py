"""Lifecycle checks: isolated install, consent gates and safe rollback."""
import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from scripts.build_fedora_mvp import build
from scripts.install_fedora_mvp import install as install_bundle
from proton_sync_engine import user_service_lifecycle as m

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.home=self.root/"home"
        self.home.mkdir(mode=0o700)
        self.cfg=self.home/"config.json"
        self.cfg.write_text("{}")
        self.cfg.chmod(0o600)
        build(self.root/"bundle")
        install_bundle(self.root/"bundle",self.root/"installed")
        self.state=self.root/"state"
        self.state.mkdir(mode=0o700)
        (self.state/"initial_pairing_verified.json").write_text("INITIAL_PAIRING_VERIFIED_V1")
        self.patches=[
            patch.object(Path,"home",return_value=self.home),
            patch.object(m,"load_paths",return_value=SimpleNamespace(
                managed_folders=("ProtonSync-Test",),
                local_root=self.home/"test-local",state_dir=self.state)),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.commands=[]
        self.cmd=patch.object(m,"_run",side_effect=self._record)
        self.cmd.start();self.addCleanup(self.cmd.stop)
    def _record(self,*args):
        self.commands.append(args)
    def test_install_requires_consent_and_never_enables(self):
        with self.assertRaises(PermissionError):
            m.install(self.cfg,self.root/"installed","yes")
        self.assertEqual(m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)["status"],
                         "INSTALLED_NOT_ENABLED")
        self.assertEqual(self.commands,[("daemon-reload",)])
        self.assertEqual(len(list((self.home/".config/systemd/user").iterdir())),2)
    def test_duplicate_install_does_not_overwrite(self):
        m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
        with self.assertRaises(FileExistsError):
            m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
    def test_no_activation_without_separate_consent(self):
        m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
        with self.assertRaises(PermissionError):
            m.enable(self.cfg,self.root/"installed","yes")
        self.assertEqual(self.commands,[("daemon-reload",)])
    def test_enable_pause_remove_exact_paths(self):
        m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
        with patch.object(m,"status",return_value={"status":"MOCK_STATUS"}):
            m.enable(self.cfg,self.root/"installed",m.ENABLE_CONSENT)
            m.pause(self.cfg,self.root/"installed",m.PAUSE_CONSENT)
        self.assertEqual(m.uninstall(self.cfg,self.root/"installed",m.REMOVE_CONSENT)["status"],
                         "UNINSTALLED")
        self.assertEqual(self.commands,[
            ("daemon-reload",),("enable","--now",m.TIMER),
            ("disable","--now",m.TIMER),("stop",m.UNIT),
            ("disable","--now",m.TIMER),("stop",m.UNIT),("daemon-reload",)])
    def test_changed_unit_blocks_remove_before_systemctl(self):
        m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
        unit=self.home/".config/systemd/user"/m.UNIT
        unit.write_text("user edited")
        with self.assertRaises(ValueError):
            m.uninstall(self.cfg,self.root/"installed",m.REMOVE_CONSENT)
        self.assertEqual(self.commands,[("daemon-reload",)])
    def test_enable_blocked_before_verified_pairing(self):
        m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
        (self.state/"initial_pairing_verified.json").unlink()
        with self.assertRaises(PermissionError):
            m.enable(self.cfg,self.root/"installed",m.ENABLE_CONSENT)
        self.assertEqual(self.commands,[("daemon-reload",)])

    def test_production_folder_rejected(self):
        with patch.object(m,"load_paths",return_value=SimpleNamespace(
                managed_folders=("Personal",),local_root=self.home/"personal")):
            with self.assertRaises(PermissionError):
                m.install(self.cfg,self.root/"installed",m.INSTALL_CONSENT)
