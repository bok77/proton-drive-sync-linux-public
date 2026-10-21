"""First portable runtime startup must verify pairing before any file writes."""
import json
import unittest
from pathlib import Path
from proton_sync_engine import pairing,initial_activation
from test_portable_engine_e2e import PortableEngineIntegrationTests

class InitialActivationE2E(unittest.TestCase):
    run_engine=PortableEngineIntegrationTests.run_engine
    ancestor=PortableEngineIntegrationTests.ancestor
    def setUp(self):
        PortableEngineIntegrationTests.setUp(self)
        self.config._allow_unverified_pairing_in_synthetic_tests=False
        self.file=self.root/"Inbox/test.txt"
        self.file.write_bytes(b"original")
        self.cloud.put("Inbox/test.txt",b"original")
        self.ancestor("Inbox/test.txt")
        self.pending=self.state/"initial_pairing_pending.json"
        self.verified=self.state/"initial_pairing_verified.json"

    def prep(self):
        review=pairing.compare(self.root,("Inbox",),self.engine.scan,
                               self.engine.remote_digest,self.engine.meta_rev)
        assert review["status"]=="READY_FOR_EXPLICIT_APPROVAL"
        self.pending.write_text(json.dumps(initial_activation.pending_guard_data(review)))
        return review

    def test_no_pairing_marker_blocks_without_cloud_call(self):
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.cloud.requests)
        self.assertFalse(self.verified.exists())
        self.assertEqual(self.file.read_bytes(),b"original")

    def test_first_start_verifies_only_and_next_sync_idempotent(self):
        self.prep()
        self.assertEqual(self.run_engine(),0)
        self.assertTrue(self.verified.is_file())
        self.assertFalse(self.pending.exists())
        self.assertEqual(self.file.read_bytes(),b"original")
        self.assertEqual(self.cloud.content["Inbox/test.txt"],b"original")
        self.assertEqual({x[0:2] for x in self.cloud.requests},{("filesystem","list")})
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.file.read_bytes(),b"original")

    def test_changed_remote_revision_blocks_without_transfers(self):
        self.prep()
        self.cloud.put("Inbox/test.txt",b"modified remote")
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.verified.exists())
        self.assertTrue(self.pending.exists())
        self.assertEqual(self.file.read_bytes(),b"original")
        self.assertEqual(self.cloud.content["Inbox/test.txt"],b"modified remote")
        self.assertEqual({x[0:2] for x in self.cloud.requests},{("filesystem","list")})

    def test_changed_remote_revision_identical_content_blocks(self):
        self.prep()
        self.cloud.put("Inbox/test.txt",b"original")
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.verified.exists())
        self.assertEqual(self.file.read_bytes(),b"original")

    def test_changed_local_file_blocks_without_transfers(self):
        self.prep()
        self.file.write_bytes(b"local modified")
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.verified.exists())
        self.assertEqual(self.cloud.content["Inbox/test.txt"],b"original")

    def test_added_cloud_file_blocks_without_download(self):
        self.prep()
        self.cloud.put("Inbox/new.txt",b"new cloud data")
        self.assertEqual(self.run_engine(),43)
        self.assertFalse((self.root/"Inbox/new.txt").exists())

    def test_corrupt_guard_blocks(self):
        self.pending.write_text('{"version":1,"sha256":"bad","matched":1}')
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.verified.exists())

    def test_corrupt_verified_marker_blocks(self):
        self.verified.write_text("wrong")
        self.assertEqual(self.run_engine(),43)
        self.assertFalse(self.cloud.requests)
