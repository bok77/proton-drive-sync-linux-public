"""Fail-closed alpha profile boundaries with synthetic local state only."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_engine.alpha_profile import load_alpha_profile, public_alpha_profile_status
from proton_sync_engine.config import validated_config

class AlphaProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.cfg = self.home / '.config' / 'proton-drive-sync-alpha'
        self.cfg.mkdir(parents=True, mode=0o700)
        self.root = self.home / 'files'
        self.root.mkdir(mode=0o700)
        (self.root / 'ProtonSync-Test').mkdir(mode=0o700)
        self.state = self.home / 'state'
        self.state.mkdir(mode=0o700)
        self.cli = Path('/usr/bin/true')
        self.settings = {'local_root': str(self.root), 'mount_root': str(self.home),
                         'state_dir': str(self.state), 'cli_executable': str(self.cli),
                         'managed_folders': ['ProtonSync-Test'], 'priority_cloud_folders': []}
        self.file = self.cfg / 'alpha-profile.json'
        self.write()

    def write(self):
        self.file.write_text(json.dumps(self.settings))
        self.file.chmod(0o600)

    def load(self):
        with patch('proton_sync_engine.alpha_profile.Path.home', return_value=self.home), \
             patch('proton_sync_engine.portable_paths.validated_config',side_effect=lambda settings: validated_config(settings,require_mount=False)):
            return load_alpha_profile(self.cfg)

    def test_valid_separate_profile_never_activates(self):
        self.assertEqual(self.load().paths.managed_folders, ('ProtonSync-Test',))
        with patch('proton_sync_engine.alpha_profile.Path.home', return_value=self.home), \
             patch('proton_sync_engine.portable_paths.validated_config',side_effect=lambda settings: validated_config(settings,require_mount=False)):
            self.assertEqual(public_alpha_profile_status(self.cfg), 'CONFIGURED_NOT_ACTIVATED')

    def test_profile_missing_blocks(self):
        self.file.unlink()
        with self.assertRaises(PermissionError): self.load()

    def test_foreign_managed_folder_blocks(self):
        self.settings['managed_folders'] = ['Other']
        self.write()
        with self.assertRaises((ValueError, PermissionError)): self.load()

    def test_world_readable_configuration_blocks(self):
        self.cfg.chmod(0o755)
        with self.assertRaises(PermissionError): self.load()

    def test_symlinked_configuration_blocks(self):
        self.file.rename(self.cfg/'target.json')
        self.file.symlink_to(self.cfg/'target.json')
        with self.assertRaises(PermissionError): self.load()

    def test_state_under_data_root_blocks(self):
        self.state = self.root / 'state'
        self.state.mkdir(mode=0o700)
        self.settings['state_dir'] = str(self.state)
        self.write()
        with self.assertRaises(ValueError): self.load()
