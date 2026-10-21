"""Full synthetic pairing -> first verification -> restart lifecycle tests."""
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from proton_sync_engine import installer_pairing, pairing
from test_portable_engine_e2e import PortableEngineIntegrationTests

class PairingLifecycleTests(unittest.TestCase):
    run_engine=PortableEngineIntegrationTests.run_engine

    def setUp(self):
        PortableEngineIntegrationTests.setUp(self)
        self.config._allow_unverified_pairing_in_synthetic_tests=False
        self.state.chmod(0o700)
        self.item=self.root/"Inbox/item.txt"
        self.item.write_bytes(b"same")
        self.cloud.put("Inbox/item.txt",b"same")
        self.adapter=SimpleNamespace(scan=self.engine.scan,
            remote_digest=self.engine.remote_digest,
            meta_rev=self.engine.meta_rev)
        self.pending=self.state/"initial_pairing_pending.json"
        self.verified=self.state/"initial_pairing_verified.json"

    def approve(self):
        with patch.object(installer_pairing,"load_paths",return_value=self.config):
            review=installer_pairing.review_pairing(Path("/synthetic/private.json"),self.adapter)
            result=installer_pairing.approve_pairing(
                Path("/synthetic/private.json"),self.adapter,review,pairing.APPROVAL)
        return review,result

    def test_complete_pairing_first_start_second_start_and_later_edit(self):
        review,result=self.approve()
        self.assertEqual(result["status"],"PAIRED")
        self.assertTrue(self.pending.is_file())
        self.assertFalse(self.verified.exists())
        self.assertEqual(json.loads(self.engine.BASE.read_text()),review["baseline"])
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),0)
        self.assertTrue(self.verified.is_file())
        self.assertFalse(self.pending.exists())
        self.assertEqual({call[:2] for call in self.cloud.requests},{("filesystem","list")})
        self.assertEqual(self.item.read_bytes(),b"same")
        self.assertEqual(self.cloud.content["Inbox/item.txt"],b"same")
        self.assertEqual(self.run_engine(),0)
        self.item.write_bytes(b"legitimate later edit")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.cloud.content["Inbox/item.txt"],b"legitimate later edit")

    def test_incomplete_verified_marker_with_pending_blocks_no_cloud_calls(self):
        self.approve()
        self.verified.write_text("INITIAL_PAIRING_VER")
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertEqual(self.cloud.requests,[])
        self.assertTrue(self.pending.exists())
        self.assertEqual(self.item.read_bytes(),b"same")

    def test_complete_verified_marker_with_pending_blocks_no_cloud_calls(self):
        self.approve()
        self.verified.write_text("INITIAL_PAIRING_VERIFIED_V1")
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertEqual(self.cloud.requests,[])
        self.assertTrue(self.pending.exists())

    def test_corrupted_pending_preserves_baseline(self):
        self.approve()
        existing=self.engine.BASE.read_bytes()
        self.pending.write_text('{"version":1,"sha256":"wrong","matched":1}')
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertEqual(self.engine.BASE.read_bytes(),existing)
        self.assertTrue(self.pending.exists())
        self.assertFalse(self.verified.exists())
        self.assertEqual({call[:2] for call in self.cloud.requests},{("filesystem","list")})

    def test_remote_revision_change_after_approval_blocks(self):
        self.approve()
        self.cloud.put("Inbox/item.txt",b"cloud edit")
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertEqual(self.item.read_bytes(),b"same")
        self.assertEqual(self.cloud.content["Inbox/item.txt"],b"cloud edit")
        self.assertEqual({call[:2] for call in self.cloud.requests},{("filesystem","list")})

    def test_local_edit_after_approval_blocks(self):
        self.approve()
        self.item.write_bytes(b"local edit")
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertEqual(self.cloud.content["Inbox/item.txt"],b"same")
        self.assertFalse(self.verified.exists())
        self.assertEqual({call[:2] for call in self.cloud.requests},{("filesystem","list")})

    def test_corrupt_baseline_blocks(self):
        self.approve()
        self.engine.BASE.write_text('{"Inbox/item.txt":{"sha1":"bad","revision":"1"}}')
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.verified.exists())
        self.assertEqual({call[:2] for call in self.cloud.requests},{("filesystem","list")})

    def test_verified_marker_symlink_blocks(self):
        self.approve()
        self.pending.unlink()
        target=self.state/"outside.txt"
        target.write_text("INITIAL_PAIRING_VERIFIED_V1")
        self.verified.symlink_to(target)
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),43)
        self.assertEqual(self.cloud.requests,[])
        self.assertEqual(self.item.read_bytes(),b"same")

    def test_restart_after_verified_run_remains_idempotent(self):
        self.approve()
        self.assertEqual(self.run_engine(),0)
        self.cloud.requests.clear()
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.item.read_bytes(),b"same")
        self.assertTrue(self.verified.exists())
        self.assertFalse(self.pending.exists())
