"""Pairing post-commit verification and guarded installer entry tests."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from proton_sync_engine import pairing, installer_pairing
from test_pairing import PairingSafetyTests

class PostCommitTests(PairingSafetyTests):
    def test_mutation_after_write_blocks_pairing_and_removes_new_baseline(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        review=self.review()
        real_compare=pairing.compare
        count=[0]
        def changed_after_write(*args,**kwargs):
            count[0]+=1
            if count[0]==2:
                self.put("a.txt",b"cloud changed just after baseline write")
            return real_compare(*args,**kwargs)
        with patch.object(pairing,"compare",side_effect=changed_after_write):
            with self.assertRaisesRegex(RuntimeError,"DRIFT_AFTER_WRITE"):
                self.approve(review)
        self.assertGreaterEqual(count[0],2)
        self.assertFalse(self.baseline.exists())

    def test_no_unintended_cloud_mutation_while_pairing(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        self.approve(self.review())
        self.assertEqual(self.cloud.content["Inbox/a.txt"],b"same")
        self.assertEqual(self.cloud.requests,[])


class InstallerPairingTests(PairingSafetyTests):
    def adapter(self):
        return SimpleNamespace(scan=self.scan,remote_digest=self.digest,meta_rev=self.rev)
    def config(self):
        return SimpleNamespace(local_root=self.root,managed_folders=("Inbox",),
                               state_dir=self.baseline.parent)

    def test_installer_preview_then_approved_baseline(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        self.baseline.parent.chmod(0o700)
        with patch.object(installer_pairing,"load_paths",return_value=self.config()):
            review=installer_pairing.review_pairing(Path("/test/config"),self.adapter())
            self.assertFalse(self.baseline.exists())
            self.assertEqual(review["status"],"READY_FOR_EXPLICIT_APPROVAL")
            outcome=installer_pairing.approve_pairing(
                Path("/test/config"),self.adapter(),review,pairing.APPROVAL)
        self.assertEqual(outcome["status"],"PAIRED")
        self.assertEqual(json.loads(self.baseline.read_text()),review["baseline"])
        guard=self.baseline.parent/"initial_pairing_pending.json"
        self.assertTrue(guard.is_file())
        self.assertEqual(json.loads(guard.read_text())["sha256"],review["sha256"])
        self.assertFalse((self.baseline.parent/"initial_pairing_verified.json").exists())

    def test_installer_stale_review_removes_pending_marker(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        self.baseline.parent.chmod(0o700)
        with patch.object(installer_pairing,"load_paths",return_value=self.config()):
            review=installer_pairing.review_pairing(Path("/test/config"),self.adapter())
            self.put("a.txt",b"changed")
            with self.assertRaisesRegex(RuntimeError,"STALE"):
                installer_pairing.approve_pairing(
                    Path("/test/config"),self.adapter(),review,pairing.APPROVAL)
        self.assertFalse(self.baseline.exists())
        self.assertFalse((self.baseline.parent/"initial_pairing_pending.json").exists())

    def test_installer_never_autopairs_on_preview(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        with patch.object(installer_pairing,"load_paths",return_value=self.config()):
            installer_pairing.review_pairing(Path("/test/config"),self.adapter())
        self.assertFalse(self.baseline.exists())

    def test_installer_denies_weak_state_permissions(self):
        self.local("a.txt",b"same")
        self.put("a.txt",b"same")
        self.baseline.parent.chmod(0o755)
        with patch.object(installer_pairing,"load_paths",return_value=self.config()):
            with self.assertRaises(PermissionError):
                installer_pairing.review_pairing(Path("/test/config"),self.adapter())
        self.assertFalse(self.baseline.exists())

    def test_installer_denies_repairing_existing_baseline(self):
        self.baseline.write_text("{}")
        with patch.object(installer_pairing,"load_paths",return_value=self.config()):
            with self.assertRaises(FileExistsError):
                installer_pairing.review_pairing(Path("/test/config"),self.adapter())


if __name__=="__main__":
    unittest.main()
