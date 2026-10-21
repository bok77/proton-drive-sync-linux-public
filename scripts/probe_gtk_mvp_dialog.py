"""Real Gtk/Adw dialog probe on disposable display; never touches systemd."""
import time
from unittest.mock import patch
import gi
gi.require_version('Gtk','4.0')
gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop import setup_wizard
from proton_sync_engine import user_service_lifecycle as lc

def spin(cond, seconds=5):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)
        if cond(): return True
        time.sleep(.02)
    raise AssertionError('Timed out waiting for GTK state')

def walk(widget):
    yield widget
    child=widget.get_first_child()
    while child:
        yield from walk(child)
        child=child.get_next_sibling()

Adw.init()
actions=[]
state={'status':'NOT_INSTALLED'}
def status(*_args):
    return {'status':state['status'],'timer_enabled':False,'timer_active':False}
def install(*args):
    actions.append('install')
    state['status']='INSTALLED'
    return {'status':'INSTALLED_NOT_ENABLED'}
with patch.object(lc,'status',side_effect=status),patch.object(lc,'install',side_effect=install),patch.object(setup_wizard,'verified_isolated_pairing',return_value=True):
    window=Gtk.Window()
    window.set_default_size(600,800)
    box=setup_wizard.make_page('de')
    window.set_child(box)
    window.present()
    spin(lambda:any(isinstance(w,Gtk.Button) and w.get_label()=='Dienst installieren' and w.get_sensitive() for w in walk(box)))
    button=next(w for w in walk(box) if isinstance(w,Gtk.Button) and w.get_label()=='Dienst installieren')
    button.emit('clicked')
    spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
    dialog=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
    assert dialog.get_default_response()=='cancel'
    assert dialog.get_close_response()=='cancel'
    assert 'Test' in dialog.get_body() or 'isoliert' in dialog.get_body()
    dialog.emit('response','cancel')
    dialog.close()
    spin(lambda:not dialog.get_visible())
    assert not actions, f'Cancel mutated: {actions}'
    button.emit('clicked')
    spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
    dialog=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
    dialog.emit('response','approve')
    dialog.close()
    spin(lambda:actions==['install'])
    spin(lambda:any(isinstance(w,Gtk.Button) and w.get_label()=='Testdienst aktivieren' and w.get_sensitive() for w in walk(box)))
    assert state['status']=='INSTALLED'
    window.close()
print('GTK_DIALOG_CANCEL_NO_MUTATION_PASS')
print('GTK_DIALOG_EXPLICIT_CONFIRM_PASS')
print('GTK_STATEFUL_NEXT_ACTION_PASS')
