"""Dashboard scheduling test: systemd-sourced next run and verified completion."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime
from proton_sync_desktop import backend

class ScheduleDashboardTests(unittest.TestCase):
    """Present planned times as plans and completed times only with valid evidence."""

    @patch.object(backend,"service_active",return_value=True)
    @patch.object(backend.subprocess,"run")
    def test_positive_next_run_from_systemd(self,run,_active):
        """Read the exact planned time from systemd rather than adding an interval."""
        run.return_value=SimpleNamespace(returncode=0,stdout="Tue 2026-10-20 09:00:06 CEST\n")
        self.assertEqual(backend.next_full_sync_schedule(),"2026-10-20 09:00")
        self.assertIn("NextElapseUSecRealtime",run.call_args.args[0])

    @patch.object(backend,"service_active",return_value=False)
    @patch.object(backend.subprocess,"run")
    def test_negative_disabled_timer_has_no_next_run(self,run,_active):
        """An inactive timer must never show a made-up next execution."""
        self.assertIsNone(backend.next_full_sync_schedule())
        run.assert_not_called()

    @patch.object(backend,"service_active",return_value=True)
    @patch.object(backend.subprocess,"run")
    def test_negative_empty_or_invalid_systemd_timestamp(self,run,_active):
        """Unscheduled or broken dates must appear as unknown."""
        for value in ("n/a","", "Tue 2026-02-30 09:00:00 CET"):
            run.return_value=SimpleNamespace(returncode=0,stdout=value)
            self.assertIsNone(backend.next_full_sync_schedule())

    def test_positive_last_full_run_requires_authoritative_success(self):
        record={"event":"run_end","time":"2026-10-20T08:20:47+0200",
                "errors":0,"conflicts":0,"tracked":10973}
        success=backend.verified_full_success(record)
        self.assertEqual(success.strftime("%d.%m.%Y, %H:%M"),"20.10.2026, 08:20")

    def test_last_success_survives_newer_failed_run(self):
        good={"event":"run_end","time":"2026-10-20T08:20:47+0200",
              "errors":0,"conflicts":0,"tracked":10973}
        failed={**good,"time":"2026-10-20T09:22:00+0200","errors":1}
        best=backend.last_successful_full_record(failed,[failed,good])
        self.assertEqual(best,good)

    def test_negative_failed_or_unfinished_runs_not_success(self):
        base={"event":"run_end","time":"2026-10-20T08:20:47+0200",
              "errors":0,"conflicts":0,"tracked":10973}
        for wrong in ({"event":"run_start"},{"errors":2},{"conflicts":1},
                      {"tracked":0},{"time":"bad"}):
            record={**base,**wrong}
            self.assertIsNone(backend.verified_full_success(record))

if __name__=="__main__":
    unittest.main()
