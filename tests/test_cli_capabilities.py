import unittest
from dataclasses import FrozenInstanceError
from proton_sync_engine.cli_capabilities import supported_capabilities, CONTRACT_VERSION, require_conditional_existing_write
from proton_sync_engine.existing_revision_guard import AtomicRevisionUnavailable

class CliCapabilityContractTests(unittest.TestCase):
    def test_versioned_conservative_contract(self):
        cap=supported_capabilities()
        self.assertEqual(cap.contract_version,CONTRACT_VERSION)
        self.assertFalse(cap.conditional_existing_revision_write)
        self.assertFalse(cap.atomic_create_only)
        self.assertFalse(cap.verified_folder_create_only)
        self.assertTrue(cap.skip_exit_zero_on_conflict)
        self.assertTrue(cap.readback_required)
        with self.assertRaises(FrozenInstanceError):cap.atomic_create_only=True

    def test_existing_write_denied_with_unverified_capability(self):
        with self.assertRaises(AtomicRevisionUnavailable):
            require_conditional_existing_write()
