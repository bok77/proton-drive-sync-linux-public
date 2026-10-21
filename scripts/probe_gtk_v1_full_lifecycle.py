"""Real GTK four-step dialog/control probe; synthetic isolated backend only."""
import time
from unittest.mock import patch
import gi
gi.require_version('Gtk','4.0')
gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop import setup_wizard
from proton_sync_engine import user_service_lifecycle as lc

def spin(predicate,seconds=7):
    limit=time.monotonic()+seconds
    while time.monotonic()<limit:
        while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
        if predicate():return
        time.sleep(.02)
    raise AssertionError('GTK state timeout')

def walk(widget):
    yield widget
    node=widget.get_first_child()
    while node:
        yield from walk(node)
        node=node.get_next_sibling()

def button(box,label):
    return next((x for x in walk(box) if isinstance(x,Gtk.Button) and x.get_label()==label and x.get_visible() and x.get_sensitive()),None)

Adw.init()
state={'installed':False,'enabled':False}
actions=[]
def status(*_):
    return {'status':'INSTALLED' if state['installed'] else 'NOT_INSTALLED',
            'timer_enabled':state['enabled'],'timer_active':state['enabled']}
def mutate(action):
    def func(*_):
        actions.append(action)
        if action=='install':state['installed']=True
        elif action=='enable':state['enabled']=True
        elif action=='pause':state['enabled']=False
        elif action=='uninstall':state['installed']=False
        return status()
    return func
with (patch.object(lc,'status',side_effect=status),
      patch.object(lc,'install',side_effect=mutate('install')),
      patch.object(lc,'enable',side_effect=mutate('enable')),
      patch.object(lc,'pause',side_effect=mutate('pause')),
      patch.object(lc,'uninstall',side_effect=mutate('uninstall')),
      patch.object(setup_wizard,'verified_isolated_pairing',return_value=True)):
    window=Gtk.Window();window.set_default_size(720,850)
    box=setup_wizard.make_page('de');window.set_child(box);window.present()
    for action,label in [('install','Dienst installieren'),('enable','Testdienst aktivieren'),
                         ('pause','Testdienst pausieren'),('uninstall','Testdienst entfernen')]:
        # Uninstall is a secondary option when installed but paused.
        spin(lambda:button(box,label) is not None)
        control=button(box,label)
        control.emit('clicked')
        spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
        dialog=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
        assert dialog.get_default_response()==dialog.get_close_response()=='cancel'
        before=tuple(actions)
        dialog.emit('response','cancel');dialog.close()
        spin(lambda:not dialog.get_visible())
        assert tuple(actions)==before
        control.emit('clicked')
        spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
        dialog=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
        dialog.emit('response','approve');dialog.close()
        spin(lambda:len(actions)==len(before)+1)
        expected={'install':(True,False),'enable':(True,True),
                  'pause':(True,False),'uninstall':(False,False)}[action]
        spin(lambda:(state['installed'],state['enabled'])==expected)
        if action=='install':spin(lambda:button(box,'Testdienst aktivieren') is not None)
        if action=='enable':spin(lambda:button(box,'Testdienst pausieren') is not None)
        if action=='pause':spin(lambda:button(box,'Testdienst entfernen') is not None)
        if action=='uninstall':spin(lambda:button(box,'Dienst installieren') is not None)
    window.close()
assert actions==['install','enable','pause','uninstall']
print('GTK_V1_FOUR_ACTIONS_CANCEL_CONFIRM_SYNTHETIC_PASS')
