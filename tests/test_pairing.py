"""Synthetic first-pairing approval: no implicit acceptance or cloud writes."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from proton_sync_engine import pairing
from test_portable_engine_e2e import FakeCloud

class PairingSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"sync"
        (self.root/"Inbox").mkdir(parents=True)
        self.baseline=Path(self.temp.name)/"state"/"baseline.json"
        self.baseline.parent.mkdir(mode=0o700)
        self.cloud=FakeCloud()
    def local(self,name,data):
        target=self.root/"Inbox"/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    def put(self,name,data):
        self.cloud.put("Inbox/"+name,data)
    def scan(self):
        manifest={key:self.cloud.meta(key) for key in self.cloud.content}
        return manifest,{"Inbox"},[]
    @staticmethod
    def digest(meta):
        return meta["activeRevision"]["claimedDigests"]["sha1"]
    @staticmethod
    def rev(meta):
        return meta["activeRevision"]["uid"]
    def review(self):
        return pairing.compare(self.root,["Inbox"],self.scan,self.digest,self.rev)
    def approve(self,review,token=pairing.APPROVAL):
        return pairing.approve(self.root,["Inbox"],self.scan,self.digest,self.rev,
                               self.baseline,review,token)

    def test_positive_exact_pairing_and_readback(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        review=self.review()
        self.assertEqual(review["status"],"READY_FOR_EXPLICIT_APPROVAL")
        self.assertEqual(review["matched"],1)
        self.assertFalse(self.baseline.exists())
        result=self.approve(review)
        self.assertEqual(result["status"],"PAIRED")
        self.assertEqual(json.loads(self.baseline.read_text()),review["baseline"])
        self.assertFalse(self.cloud.requests)
        self.assertEqual(self.baseline.stat().st_mode & 0o777,0o600)

    def test_negative_no_approval(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        with self.assertRaises(PermissionError):
            self.approve(self.review(),"yes")
        self.assertFalse(self.baseline.exists())

    def test_negative_local_change_after_review(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        review=self.review()
        self.local("a.txt",b"changed")
        with self.assertRaisesRegex(RuntimeError,"STALE"):
            self.approve(review)
        self.assertFalse(self.baseline.exists())

    def test_negative_cloud_change_after_review(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        review=self.review()
        self.put("a.txt",b"changed")
        with self.assertRaisesRegex(RuntimeError,"STALE"):
            self.approve(review)
        self.assertFalse(self.baseline.exists())

    def test_negative_cloud_revision_change_with_identical_bytes(self):
        # The revision ID is part of the approval binding, even if the cloud
        # claims identical bytes/size after a new revision is created.
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        review=self.review()
        self.put("a.txt",b"same")
        self.assertEqual(self.review()["status"],"READY_FOR_EXPLICIT_APPROVAL")
        self.assertNotEqual(self.review()["sha256"],review["sha256"])
        with self.assertRaisesRegex(RuntimeError,"STALE"):
            self.approve(review)
        self.assertFalse(self.baseline.exists())

    def test_negative_missing_on_cloud(self):
        self.local("a.txt",b"local")
        result=self.review()
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(result["differences"][0]["reason"],"only_on_linux")
        with self.assertRaises(ValueError):
            self.approve(result)

    def test_negative_missing_on_local(self):
        self.put("a.txt",b"cloud")
        result=self.review()
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(result["differences"][0]["reason"],"only_in_cloud")

    def test_negative_symlink(self):
        outside=Path(self.temp.name)/"other"
        outside.write_bytes(b"data")
        (self.root/"Inbox"/"link.txt").symlink_to(outside)
        result=self.review()
        self.assertEqual(result["status"],"BLOCKED")
        self.assertTrue(result["errors"])

    def test_negative_duplicate_pairing(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        review=self.review()
        self.approve(review)
        with self.assertRaises(FileExistsError):
            self.approve(review)
        self.assertEqual(len(json.loads(self.baseline.read_text())),1)

    def test_negative_scan_error(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        def bad_scan():
            m,folders,errors=self.scan()
            return m,folders,[{"problem":"offline"}]
        result=pairing.compare(self.root,["Inbox"],bad_scan,self.digest,self.rev)
        self.assertEqual(result["status"],"BLOCKED")

    def test_negative_empty_pairing(self):
        self.assertEqual(self.review()["status"],"BLOCKED")

if __name__=="__main__":
    unittest.main()
