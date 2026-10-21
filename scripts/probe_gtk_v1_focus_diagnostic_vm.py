"""VM Xvfb real X11 keyboard events against GTK; mocked backend, no cloud."""
import subprocess,time,os
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
    print('FOCUS_AFTER_ESC',str(win.get_focus()),'BUTTON_FOCUS',b.has_focus(),flush=True)
    for delay in (0.1,0.3,0.7):
        end=time.monotonic()+delay
        while time.monotonic()<end:
            while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
            time.sleep(.02)
        print('FOCUS_WAIT',delay, 'winfocus',str(win.get_focus()), 'button',b.has_focus(),flush=True)
    print('FOCUS_GRAB',b.grab_focus(),flush=True)
    end=time.monotonic()+0.7
    while time.monotonic()<end:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        time.sleep(.02)
    print('FOCUS_AFTER_GRAB',b.has_focus(),flush=True)
    if os.environ.get('V1_REQUIRE_WM')=='1':
        assert b.has_focus(), 'focus was not restored with window manager'
    key('Tab')
    end=time.monotonic()+0.15
    while time.monotonic()<end:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        time.sleep(.02)
    print('FOCUS_AFTER_TAB',str(win.get_focus()), 'is_focusable',bool(win.get_focus() and win.get_focus().get_focusable()),flush=True)
    key('shift+Tab')
    end=time.monotonic()+0.15
    while time.monotonic()<end:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        time.sleep(.02)
    print('FOCUS_AFTER_SHIFT_TAB',str(win.get_focus()), 'is_focusable',bool(win.get_focus() and win.get_focus().get_focusable()),flush=True)
    if os.environ.get('V1_REQUIRE_WM')=='1':
        assert b.has_focus(), 'Shift+Tab must return to original button'
        print('V1_REAL_WM_ESCAPE_FOCUS_TAB_SHIFT_TAB_PASS')
    win.close()
