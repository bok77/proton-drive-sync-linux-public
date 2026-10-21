"""Offline tests: translations, exclusion validation, and private-data hygiene."""
import sys
import tempfile
import unittest
from pathlib import Path

from proton_sync_desktop import backend
from proton_sync_desktop.i18n import STRINGS,translate,validate

class LocalizationTests(unittest.TestCase):
    def test_keys_match(self):
        self.assertGreater(validate(),50)
    def test_both_languages(self):
        self.assertEqual(translate("de","settings"),"Einstellungen")
        self.assertEqual(translate("en","settings"),"Settings")
        self.assertEqual(translate("de","sync_now"),"Jetzt abgleichen")
        self.assertEqual(translate("en","sync_now"),"Sync now")
    def test_text_nonempty(self):
        self.assertTrue(all(value for pack in STRINGS.values() for value in pack.values()))

class StateTests(unittest.TestCase):
    def test_missing_status_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(backend.read_json(Path(d)/"missing.json"),{})
    def test_bad_json_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json";p.write_text("{broken")
            self.assertEqual(backend.read_json(p),{})
    def test_reject_bad_directory(self):
        with self.assertRaises(ValueError):
            backend.save_exclusions(["*.tmp"],["../secrets"])
    def test_reject_null_pattern(self):
        with self.assertRaises(ValueError):
            backend.save_exclusions(["bad\0thing"],[])
    def test_atomic_settings(self):
        with tempfile.TemporaryDirectory() as d:
            original=backend.CONFIG
            try:
                backend.CONFIG=Path(d)/"settings.json"
                backend.save_exclusions(["*.swp","*~"],["__pycache__"])
                loaded=backend.settings()
                self.assertEqual(loaded["exclusions"]["file_patterns"],["*.swp","*~"])
                self.assertEqual(loaded["exclusions"]["directory_names"],["__pycache__"])
            finally:backend.CONFIG=original

if __name__=="__main__":unittest.main()
