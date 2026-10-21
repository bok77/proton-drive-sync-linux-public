"""VM Xvfb real X11 keyboard events against GTK; mocked backend, no cloud."""
import subprocess,time
from unittest.mock import patch
import gi
gi.require_version('Gtk','4.0');gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop import setup_wizard
from proton_sync_engine import user_service_lifecycle as lc

def spin(predicate,seconds=7):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        if predicate():return
        time.sleep(.025)
    raise AssertionError('keyboard-event timeout')
def children(w):
    yield w
    c=w.get_first_child()
    while c:
        yield from children(c);c=c.get_next_sibling()
def key(*keys):subprocess.run(['xdotool','key','--clearmodifiers',*keys],check=True,timeout=5)

Adw.init();mutations=[]
with (patch.object(setup_wizard,'verified_isolated_pairing',return_value=True),
      patch.object(lc,'status',return_value={'status':'NOT_INSTALLED'}),
      patch.object(lc,'install',side_effect=lambda *_:mutations.append('install'))):
    win=Gtk.Window(title='V1-KEYBOARD-VM-TEST');win.set_default_size(800,900)
    page=setup_wizard.make_page('de');win.set_child(page);win.present()
    spin(lambda:any(isinstance(w,Gtk.Button) and w.get_label()=='Dienst installieren' and w.get_sensitive() for w in children(page)))
    b=next(w for w in children(page) if isinstance(w,Gtk.Button) and w.get_label()=='Dienst installieren')
    subprocess.run(['xdotool','search','--name','V1-KEYBOARD-VM-TEST','windowfocus','--sync'],check=True,timeout=5)
    assert b.grab_focus();spin(b.has_focus)
    key('Return')
    spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
    key('Escape')
    spin(lambda:not any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
    assert mutations==[],mutations
    print('V1_REAL_KEY_ENTER_DIALOG_ESC_NO_MUTATION_PASS')
    win.close()
