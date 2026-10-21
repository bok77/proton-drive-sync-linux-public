"""GTK dashboard autosave behavior without triggering real systemd changes."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch

from proton_sync_desktop.app import Window
from proton_sync_desktop import routing


class FakeDashboard:
    """A lightweight callback receiver for exercising the actual UI handlers."""

    def __init__(self):
        self._updating_intervals=False
        self._saving_intervals=False
        self._interval_pending=None
        self._apply_pending_interval=Mock()


class ImmediateCadenceTests(unittest.TestCase):
    """Selections are immediately queued, not delayed until explicit saving."""

    def test_positive_choice_starts_autosave(self):
        dashboard=FakeDashboard()
        selector=SimpleNamespace(get_selected=lambda:1)
        Window.interval_changed(dashboard,selector,None,"local")
        self.assertEqual(dashboard._interval_pending,("local",10))
        dashboard._apply_pending_interval.assert_called_once()

    def test_positive_coalesce_during_save(self):
        dashboard=FakeDashboard()
        dashboard._saving_intervals=True
        for index in (2,3):
            selector=SimpleNamespace(get_selected=lambda i=index:i)
            Window.interval_changed(dashboard,selector,None,"priority")
        self.assertEqual(dashboard._interval_pending,("priority",30))
        dashboard._apply_pending_interval.assert_not_called()

    def test_negative_programmatic_selection_never_writes(self):
        dashboard=FakeDashboard()
        dashboard._updating_intervals=True
        selector=SimpleNamespace(get_selected=lambda:3)
        Window.interval_changed(dashboard,selector,None,"full")
        self.assertIsNone(dashboard._interval_pending)
        dashboard._apply_pending_interval.assert_not_called()

    def test_negative_invalid_choice_does_not_apply(self):
        dashboard=FakeDashboard()
        selector=SimpleNamespace(get_selected=lambda:999)
        Window.interval_changed(dashboard,selector,None,"full")
        dashboard._apply_pending_interval.assert_not_called()

    def test_negative_failed_write_reverts_to_persisted_selection(self):
        dashboard=FakeDashboard()
        dashboard._interval_pending=None
        dashboard._saving_intervals=True
        dashboard.d=lambda key:key
        dashboard.dialog=Mock()
        dashboard.interval_feedback=SimpleNamespace(set_text=Mock())
        dashboard.cadence_controls={
            name:SimpleNamespace(set_selected=Mock())
            for name in ("local","priority","full")
        }
        with patch.object(routing,"load",return_value=routing.DEFAULT):
            done=Window._interval_write_finished(dashboard,"local",15,"write failed")
        self.assertFalse(done)
        dashboard.dialog.assert_called_once_with("schedule_failed","write failed")
        dashboard.cadence_controls["local"].set_selected.assert_called_with(0)
        self.assertFalse(dashboard._saving_intervals)


if __name__=="__main__":
    unittest.main()
