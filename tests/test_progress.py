"""Positive and negative tests for truthfully reported synchronization progress."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from proton_sync_desktop.progress import interpret,read_progress

class ProgressSafetyTests(unittest.TestCase):
    """A percentage is visible only for fresh, bounded engine counters."""

    def test_running_status_takes_priority_over_success(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/app.py").read_text()
        self.assertIn('"running_headline":"Synchronisierung läuft"',source)
        self.assertIn('self.d("running_headline") if full_running',source)

    def test_overview_reports_all_active_sync_directions(self):
        source=(Path(__file__).resolve().parents[1]/
                "src/proton_sync_desktop/app.py").read_text()
        self.assertIn('backend.service_active("proton-bisync-quick.service")',source)
        self.assertIn('backend.service_active("proton-cloud-priority.service")',source)
        self.assertIn('self.progress_spinner.start()',source)
        self.assertIn('self.progress_spinner.stop()',source)
        self.assertIn('self.monitor_hero=hero;outer.append(hero)',source)

    def test_positive_measured_phase(self):
        event={"phase":"file_comparison","done":250,"total":1000,
               "status":"running","updated_at":1000}
        result=interpret(event,True,now=1002)
        self.assertEqual(result["mode"],"measured")
        self.assertEqual(result["fraction"],0.25)

    def test_negative_unknown_total(self):
        event={"phase":"cloud_inventory","done":None,"total":None,
               "status":"running","updated_at":1000}
        result=interpret(event,True,now=1002)
        self.assertEqual(result["mode"],"working")
        self.assertIsNone(result["fraction"])

    def test_negative_inactive_service_hides_stale_progress(self):
        event={"phase":"file_comparison","done":20,"total":20,
               "status":"running","updated_at":1000}
        self.assertEqual(interpret(event,False,now=1001)["mode"],"idle")

    def test_negative_stale_counter_not_reused(self):
        event={"phase":"tracked_files","done":12,"total":100,
               "status":"running","updated_at":1000}
        result=interpret(event,True,now=9000)
        self.assertIsNone(result["fraction"])

    def test_negative_impossible_counter(self):
        event={"phase":"file_comparison","done":200,"total":100,
               "status":"running","updated_at":1000}
        self.assertIsNone(interpret(event,True,now=1001)["fraction"])

    def test_negative_missing_progress_document(self):
        with tempfile.TemporaryDirectory() as td:
            state=read_progress(Path(td),"local",True)
            self.assertEqual(state["mode"],"working")

if __name__=="__main__":unittest.main()
