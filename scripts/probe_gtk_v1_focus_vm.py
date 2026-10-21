"""VM Xvfb GTK focus and safe default review, no real systemd mutation."""
import time
from unittest.mock import patch
import gi
gi.require_version('Gtk','4.0');gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop import setup_wizard
from proton_sync_engine import user_service_lifecycle as lc

def until(check):
    deadline=time.monotonic()+6
    while time.monotonic()<deadline:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        if check():return
        time.sleep(.03)
    raise AssertionError('focus state timeout')
def walk(w):
    yield w
    c=w.get_first_child()
    while c:
        yield from walk(c);c=c.get_next_sibling()

Adw.init();changes=[]
with (patch.object(setup_wizard,'verified_isolated_pairing',return_value=True),
      patch.object(lc,'status',return_value={'status':'NOT_INSTALLED'}),
      patch.object(lc,'install',side_effect=lambda *a:changes.append('install'))):
    window=Gtk.Window();window.set_default_size(700,800)
    page=setup_wizard.make_page('de');window.set_child(page);window.present()
    until(lambda:any(isinstance(w,Gtk.Button) and w.get_label()=='Dienst installieren' and w.get_sensitive() for w in walk(page)))
    btn=next(w for w in walk(page) if isinstance(w,Gtk.Button) and w.get_label()=='Dienst installieren')
    assert btn.get_focusable(), 'action must be keyboard focusable'
    assert btn.grab_focus(), 'action must accept programmatic focus'
    until(lambda:btn.has_focus())
    btn.emit('clicked')
    until(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
    dlg=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
    assert dlg.get_modal() and dlg.get_default_response()=='cancel' and dlg.get_close_response()=='cancel'
    dlg.emit('response','cancel');dlg.close();until(lambda:not dlg.get_visible())
    assert not changes
    until(lambda:btn.get_sensitive())
    # Xvfb may not return focus after the transient closes; test that the
    # action stays operable, and retain the actual focus-restoration gap.
    assert btn.get_visible() and btn.get_sensitive() and btn.get_focusable()
    window.close()
print('V1_GTK_FOCUSABLE_ACTION_PASS')
print('V1_GTK_MODAL_CANCEL_DEFAULT_PASS')
print('V1_GTK_CANCEL_ACTION_STAYS_FOCUSABLE_PASS')
