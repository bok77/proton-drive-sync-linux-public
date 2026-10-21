"""Alpha lifecycle delegation must stay fail-closed and non-production."""
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from proton_sync_engine import alpha_lifecycle as alpha
from proton_sync_engine import user_service_lifecycle as lc

class AlphaLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.cfg=Path('/tmp/private-alpha/alpha-profile.json')
        self.bundle=Path('/tmp/private-alpha-bundle')
        self.profile=SimpleNamespace(config_path=self.cfg,paths=SimpleNamespace(
            local_root=Path('/tmp/alpha-data'),state_dir=Path('/tmp/alpha-state')))

    def guards(self):
        return (patch.object(alpha,'load_alpha_profile',return_value=self.profile),
                patch.object(lc,'_bundle',return_value=self.bundle),
                patch.object(lc,'_expected',return_value={lc.UNIT:'service',lc.TIMER:'timer'}))

    def test_unauthorized_calls_cannot_reach_lifecycle(self):
        for action in ('install','start_once','remove'):
            with self.subTest(action=action),patch.object(lc,{'install':'install','start_once':'run_once','remove':'uninstall'}[action]) as target:
                with self.assertRaises(PermissionError):getattr(alpha,action)(self.bundle,consent='')
                target.assert_not_called()

    def test_only_existing_isolated_controller_is_used(self):
        for action,delegate,consent in (
            ('install','install',lc.INSTALL_CONSENT),
            ('start_once','run_once',lc.RUN_ONCE_CONSENT),
            ('remove','uninstall',lc.REMOVE_CONSENT)):
            guards=self.guards()
            with self.subTest(action=action),guards[0],guards[1],guards[2],patch.object(lc,delegate,return_value={'status':'OK'}) as target:
                self.assertEqual(getattr(alpha,action)(self.bundle,consent=consent)['status'],'OK')
                target.assert_called_once_with(self.cfg,self.bundle,consent)

    def test_status_read_only(self):
        a,b,c=self.guards()
        with a,b,c,patch.object(lc,'status',return_value={'status':'NOT_INSTALLED'}) as target:
            self.assertEqual(alpha.status(self.bundle)['status'],'NOT_INSTALLED')
            target.assert_called_once_with(self.cfg,self.bundle)

    def test_refuse_bundle_inside_synced_data(self):
        self.profile.paths.local_root=Path('/tmp')
        a,b,c=self.guards()
        with a,b,c,patch.object(lc,'install') as install,self.assertRaises(PermissionError):
            alpha.install(self.bundle,consent=lc.INSTALL_CONSENT)
        install.assert_not_called()

    def test_refuse_unexpected_unit_identity(self):
        a,b,_=self.guards()
        with a,b,patch.object(lc,'_expected',return_value={'proton-bisync.timer':'unsafe'}),self.assertRaises(PermissionError):
            alpha.status(self.bundle)
