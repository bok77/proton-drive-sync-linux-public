"""Process-exclusion tests including lock contention and crashed lock owner."""
import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_engine.exclusive_lock import exclusive,PairingBusy
from proton_sync_engine import installer_pairing,pairing_recovery
from test_pairing_full_lifecycle import PairingLifecycleTests

def _die_while_locked(directory,pipe):
    with exclusive(directory):
        pipe.send("locked")
        # Parent must observe contention while the lock is definitely held.
        # Without a barrier the child may exit before parent attempts flock.
        pipe.recv()
        pipe.close()
        os._exit(17)

class LockProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state=Path(self.tmp.name)/"private"
        self.state.mkdir(mode=0o700)

    def test_nested_lock_is_denied_not_reentrant(self):
        with exclusive(self.state):
            with self.assertRaisesRegex(PairingBusy,"BUSY"):
                with exclusive(self.state):
                    pass
        with exclusive(self.state):
            pass

    def test_crash_releases_kernel_lock_without_deleting_inode(self):
        parent,child=multiprocessing.Pipe()
        process=multiprocessing.Process(target=_die_while_locked,args=(self.state,child))
        process.start()
        try:
            self.assertTrue(parent.poll(5),"Child failed to acquire the kernel lock")
            self.assertEqual(parent.recv(),"locked")
            with self.assertRaises(PairingBusy):
                with exclusive(self.state):
                    pass
            parent.send("exit")
        finally:
            if process.is_alive():
                try:
                    parent.send("exit")
                except (BrokenPipeError,EOFError,OSError):
                    pass
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join()
        self.assertEqual(process.exitcode,17)
        with exclusive(self.state):
            self.assertTrue((self.state/"pairing_runtime.lock").exists())

    def test_symlinked_lock_is_refused(self):
        (self.state/"other").write_text("do not touch")
        (self.state/"pairing_runtime.lock").symlink_to(self.state/"other")
        with self.assertRaises(PermissionError):
            with exclusive(self.state):
                pass
        self.assertEqual((self.state/"other").read_text(),"do not touch")

    def test_non_private_state_is_refused(self):
        self.state.chmod(0o755)
        with self.assertRaises(PermissionError):
            with exclusive(self.state):
                pass

class RuntimeLockTests(unittest.TestCase):
    run_engine=PairingLifecycleTests.run_engine
    approve=PairingLifecycleTests.approve
    setUp=PairingLifecycleTests.setUp
    def test_runtime_cannot_run_when_pairing_lock_is_held(self):
        self.approve()
        self.cloud.requests.clear()
        with exclusive(self.state):
            self.assertEqual(self.run_engine(),44)
        self.assertEqual(self.cloud.requests,[])
        self.assertTrue(self.pending.exists())
        self.assertFalse(self.verified.exists())
        self.assertEqual(self.run_engine(),0)

    def test_installer_review_contends_with_runtime(self):
        with patch.object(installer_pairing,"load_paths",return_value=self.config):
            with exclusive(self.state):
                with self.assertRaises(PairingBusy):
                    installer_pairing.review_pairing(Path("/synthetic/private.json"),self.adapter)

    def test_recovery_cannot_preview_during_runtime(self):
        self.approve()
        self.verified.write_text("INITIAL_PAIRING_VERIFIED_V1")
        with exclusive(self.state):
            with self.assertRaises(PairingBusy):
                pairing_recovery.inspect(self.config,self.adapter)
        self.assertTrue(self.verified.exists())
        self.assertTrue(self.pending.exists())
