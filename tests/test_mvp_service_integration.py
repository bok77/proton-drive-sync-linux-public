"""Isolated tests for portable systemd integration."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from proton_sync_engine import service_integration as service


class ServiceIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.units = self.root / "units"
        self.units.mkdir(mode=0o700)

        self.config = self.root / "config.json"
        self.config.write_text("{}")
        self.config.chmod(0o600)

        self.install = self.root / "installation"

        self.example = {
            "status": "READY_FOR_INERT_SERVICE_INSTALL",
            "unit_name": service.UNIT,
            "text": service.unit_text(
                "/tmp/synthetic/bin/proton-portable-full",
                self.config,
            ),
            "activation_authorized": False,
        }

    def stage(self, consent=service.APPROVAL):
        with (
            patch.object(service, "preview",
                         return_value=self.example),
            patch.object(service, "load_paths",
                         return_value=SimpleNamespace(
                             state_dir=self.root)),
        ):
            return service.stage(
                self.config,
                self.install,
                self.units,
                consent,
            )

    def test_explicit_install_and_remove(self):
        result = self.stage()

        self.assertEqual(result["status"], "STAGED_NOT_ENABLED")
        self.assertFalse(result["activation_authorized"])

        path = self.units / service.UNIT
        self.assertTrue(path.is_file())

        content = path.read_text()

        self.assertIn("Type=oneshot", content)
        self.assertIn("NoNewPrivileges=true", content)
        self.assertIn("PROTON_SYNC_CONFIG=", content)

        removed = service.remove(self.units, content)

        self.assertEqual(
            removed["status"],
            "STAGED_UNIT_REMOVED",
        )
        self.assertFalse(path.exists())

    def test_consent_required(self):
        with self.assertRaises(PermissionError):
            self.stage("yes")

        self.assertEqual(list(self.units.iterdir()), [])

    def test_existing_unit_not_overwritten(self):
        self.stage()

        path = self.units / service.UNIT
        original = path.read_bytes()

        with self.assertRaises(FileExistsError):
            self.stage()

        self.assertEqual(path.read_bytes(), original)

    def test_modified_unit_not_deleted(self):
        self.stage()

        path = self.units / service.UNIT
        original = path.read_text()
        path.write_text(original + "\n# modified\n")

        with self.assertRaises(ValueError):
            service.remove(self.units, original)

        self.assertTrue(path.exists())

    def test_unsafe_permissions_blocked(self):
        self.units.chmod(0o755)

        with self.assertRaises(PermissionError):
            self.stage()

    def test_symlink_not_overwritten(self):
        protected = self.root / "protected"
        protected.write_text("unchanged")

        link = self.units / service.UNIT
        link.symlink_to(protected)

        with self.assertRaises((FileExistsError, OSError)):
            self.stage()

        self.assertEqual(
            protected.read_text(),
            "unchanged",
        )


if __name__ == "__main__":
    unittest.main()

class TimerPairTests(ServiceIntegrationTests):
    def pair(self, consent=service.APPROVAL):
        with (
            patch.object(service,"preview",return_value=self.example),
            patch.object(service,"load_paths",return_value=SimpleNamespace(state_dir=self.root)),
        ):
            return service.stage_pair(self.config,self.install,self.units,consent)

    def test_timer_has_real_newlines_and_no_autostart_service(self):
        timer=service.timer_text()
        self.assertTrue(timer.startswith("[Unit]\n"))
        self.assertIn("\n[Timer]\n",timer)
        self.assertIn("WantedBy=timers.target",timer)
        self.assertNotIn("WantedBy=default.target",self.example["text"])
        self.assertEqual(timer.count("OnCalendar="),1)

    def test_stage_both_then_remove(self):
        result=self.pair()
        self.assertEqual(result["status"],"STAGED_SERVICE_AND_TIMER_NOT_ENABLED")
        self.assertFalse(result["activation_authorized"])
        self.assertEqual(len(list(self.units.iterdir())),2)
        removed=service.remove_pair(self.units,self.example["text"])
        self.assertEqual(removed["status"],"STAGED_PAIR_REMOVED")
        self.assertEqual(list(self.units.iterdir()),[])

    def test_pair_requires_explicit_approval(self):
        with self.assertRaises(PermissionError):
            self.pair("yes")
        self.assertEqual(list(self.units.iterdir()),[])

    def test_existing_timer_prevents_partial_stage(self):
        target=self.units/service.TIMER
        target.write_text("user owned")
        with self.assertRaises(FileExistsError):
            self.pair()
        self.assertEqual(target.read_text(),"user owned")
        self.assertFalse((self.units/service.UNIT).exists())

    def test_modified_timer_prevents_any_removal(self):
        self.pair()
        target=self.units/service.TIMER
        target.write_text(target.read_text()+"# user modification\n")
        with self.assertRaises(ValueError):
            service.remove_pair(self.units,self.example["text"])
        self.assertTrue((self.units/service.UNIT).exists())
        self.assertTrue(target.exists())
