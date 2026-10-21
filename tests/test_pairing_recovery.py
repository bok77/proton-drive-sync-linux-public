"""Recovery requires an unchanged review, fresh cloud checks and human consent."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from proton_sync_engine import pairing_recovery
import test_pairing_full_lifecycle as lifecycle
import unittest

class RecoveryTests(unittest.TestCase):
    run_engine=lifecycle.PairingLifecycleTests.run_engine
    approve=lifecycle.PairingLifecycleTests.approve
    def setUp(self):
        lifecycle.PairingLifecycleTests.setUp(self)
        # The interrupted state is created only after the approved pairing.
        self.approve()
        self.verified.write_text("INITIAL_PAIRING_VERIFIED_V1")

    def config_and_adapter(self):
        return self.config,self.adapter

    def preview(self):
        return pairing_recovery.inspect(self.config,self.adapter)

    def recover(self,review,consent=pairing_recovery.CONSENT):
        return pairing_recovery.recover(self.config,self.adapter,review,consent)

    def test_double_marker_explicit_recovery_then_reverify_then_normal_sync(self):
        review=self.preview()
        self.assertFalse(review["activation_authorized"])
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        with self.assertRaises(PermissionError):
            self.recover(review,"yes")
        self.assertTrue(self.verified.exists())
        self.assertEqual(self.recover(review)["status"],"RECHECK_REQUIRED")
        evidence=self.state/"initial_pairing_recovery_evidence.json"
        self.assertTrue(evidence.is_file())
        self.assertEqual(evidence.stat().st_mode & 0o777,0o600)
        self.assertEqual(__import__("json").loads(evidence.read_text())["review_sha256"],review["sha256"])
        self.assertFalse(self.verified.exists())
        self.assertTrue(self.pending.exists())
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),0)
        self.assertEqual({call[:2] for call in self.cloud.requests},{("filesystem","list")})
        self.assertTrue(self.verified.exists())
        self.assertFalse(self.pending.exists())
        self.assertEqual(self.run_engine(),0)

    def test_partial_marker_can_be_recovered_only_with_explicit_recheck(self):
        self.verified.write_text("INITIAL_PAIRING_VER")
        review=self.preview()
        self.assertEqual(self.recover(review)["status"],"RECHECK_REQUIRED")
        self.assertTrue(self.pending.exists())
        self.assertEqual(self.run_engine(),0)

    def test_cloud_changed_after_review_fails_without_marker_mutation(self):
        review=self.preview()
        self.cloud.put("Inbox/item.txt",b"remote drift")
        with self.assertRaises(RuntimeError):
            self.recover(review)
        self.assertTrue(self.verified.exists())
        self.assertTrue(self.pending.exists())
        self.assertEqual(self.item.read_bytes(),b"same")

    def test_local_changed_after_review_fails(self):
        review=self.preview()
        self.item.write_bytes(b"local drift")
        with self.assertRaises(RuntimeError):
            self.recover(review)
        self.assertTrue(self.verified.exists())

    def test_verified_marker_tampered_after_review_fails(self):
        review=self.preview()
        self.verified.write_text("partial-corrupt")
        with self.assertRaisesRegex(RuntimeError,"STALE"):
            self.recover(review)
        self.assertTrue(self.verified.exists())

    def test_corrupt_guard_never_recovers(self):
        self.pending.write_text("not-json")
        with self.assertRaises(Exception):
            self.preview()
        self.assertTrue(self.verified.exists())

    def test_missing_pending_never_recovers(self):
        self.pending.unlink()
        with self.assertRaisesRegex(RuntimeError,"NOT_AN_INTERRUPTED"):
            self.preview()
        self.assertTrue(self.verified.exists())

    def test_symlinked_marker_never_unlinked(self):
        self.verified.unlink()
        other=self.state/"protected"
        other.write_text("INITIAL_PAIRING_VERIFIED_V1")
        self.verified.symlink_to(other)
        with self.assertRaisesRegex(RuntimeError,"SYMLINK"):
            self.preview()
        self.assertEqual(other.read_text(),"INITIAL_PAIRING_VERIFIED_V1")

    def test_already_verified_without_pending_cannot_recover(self):
        self.pending.unlink()
        with self.assertRaises(RuntimeError):
            self.preview()
        self.assertTrue(self.verified.exists())

    def test_modified_baseline_blocks_recovery(self):
        self.engine.BASE.write_text("{}")
        with self.assertRaises(RuntimeError):
            self.preview()
        self.assertTrue(self.verified.exists())

    def test_existing_recovery_evidence_blocks_second_mutation(self):
        review=self.preview()
        evidence=self.state/"initial_pairing_recovery_evidence.json"
        evidence.write_text("previous review")
        with self.assertRaises(FileExistsError):
            self.recover(review)
        self.assertTrue(self.verified.exists())
        self.assertEqual(evidence.read_text(),"previous review")

    def test_replayed_approval_denied(self):
        review=self.preview()
        self.recover(review)
        with self.assertRaises(RuntimeError):
            self.recover(review)
        self.assertTrue(self.pending.exists())
        self.assertFalse(self.verified.exists())
