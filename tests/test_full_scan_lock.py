"""A full scan must wait for a shared lock, not falsely return success."""
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

class FullScanLockTests(unittest.TestCase):
    """Exercise the same flock options used by the production full-run wrapper."""

    def test_positive_full_job_waits_then_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock=str(Path(tmp)/"sync.lock")
            holder=subprocess.Popen(
                ["/usr/bin/flock","-x",lock,"/bin/sleep","0.3"])
            try:
                time.sleep(0.08)
                started=time.monotonic()
                contender=subprocess.run(
                    ["/usr/bin/flock","-E","75","-w","2",lock,
                     "/bin/sh","-c","echo FULL_RAN"],
                    capture_output=True,text=True,timeout=5)
                self.assertEqual(contender.returncode,0)
                self.assertEqual(contender.stdout.strip(),"FULL_RAN")
                self.assertGreater(time.monotonic()-started,0.12)
            finally:
                holder.wait(timeout=5)

    def test_negative_busy_lock_reports_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock=str(Path(tmp)/"sync.lock")
            holder=subprocess.Popen(
                ["/usr/bin/flock","-x",lock,"/bin/sleep","2"])
            try:
                time.sleep(0.08)
                blocked=subprocess.run(
                    ["/usr/bin/flock","-E","75","-w","1",lock,
                     "/bin/sh","-c","echo MUST_NOT_RUN"],
                    capture_output=True,text=True,timeout=5)
                self.assertEqual(blocked.returncode,75)
                self.assertNotIn("MUST_NOT_RUN",blocked.stdout)
            finally:
                holder.wait(timeout=5)

    def test_reference_wrapper_has_full_wait_contract(self):
        wrapper=(Path(__file__).resolve().parents[1]/
                 "packaging/reference/proton-sync-run.sh").read_text()
        self.assertIn('if [[ "${1:-}" == full ]]',wrapper)
        self.assertIn('flock -E 75 -w 1800',wrapper)
        self.assertIn('flock -E 0 -n',wrapper)


if __name__=="__main__":unittest.main()
