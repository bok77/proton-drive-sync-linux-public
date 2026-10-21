"""Independent real GTK/Xvfb error-path probe; no CLI, cloud or systemd calls."""
import time
from pathlib import Path
from unittest.mock import patch
import gi
gi.require_version('Gtk','4.0')
gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop import setup_wizard
from proton_sync_desktop.cli_error_labels import safe_pairing_error

def walk(widget):
    yield widget
    child=widget.get_first_child()
    while child:
        yield from walk(child)
        child=child.get_next_sibling()

def until(condition,seconds=8):
    limit=time.monotonic()+seconds
    while time.monotonic()<limit:
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)
        if condition():return
        time.sleep(.03)
    raise AssertionError('GTK wait timed out')

Adw.init()
for language in ('de','en'):
    window=Gtk.Window()
    window.set_child(setup_wizard.make_page(language))
    window.present()
    root=window.get_child()
    fields=[w for w in walk(root) if isinstance(w,Gtk.Entry)]
    assert fields, 'Configuration input missing'
    fields[0].set_text('/synthetic/isolation/test.json')
    buttons=[w for w in walk(root) if isinstance(w,Gtk.Button)]
    inspect_button=next(w for w in buttons if w.get_label()==setup_wizard.COPY[language]['demo'])
    approve_button=next(w for w in buttons if w.get_label()==setup_wizard.COPY[language]['confirm'])
    for category in ('AUTH','RATE_LIMIT','TIMEOUT','CONFLICT','PROVIDER_ERROR'):
        with patch('proton_sync_engine.test_cloud_adapter.inspect',return_value={
            'matched':0,'differences':[], 'errors':[{'path':'private-secret-path','reason':'CLI_'+category}],
            'status':'BLOCKED'}):
            inspect_button.emit('clicked')
            expected=safe_pairing_error('CLI_'+category,language)
            until(lambda:any(isinstance(w,Adw.ActionRow) and w.get_subtitle()==expected for w in walk(root)))
        assert not approve_button.get_sensitive(), 'Blocked inventory enabled approval'
    # Raw untrusted text must not become a visible error row.
    with patch('proton_sync_engine.test_cloud_adapter.inspect',side_effect=RuntimeError('TOKEN_PRIVATE_123')):
        inspect_button.emit('clicked')
        unknown=safe_pairing_error(None,language)
        until(lambda:any(isinstance(w,Adw.ActionRow) and w.get_title()=='BLOCKED' and w.get_subtitle()==unknown for w in walk(root)))
        assert not any('TOKEN_PRIVATE_123' in (w.get_title() or '')+(w.get_subtitle() or '') for w in walk(root) if isinstance(w,Adw.ActionRow))
    window.close()
    print('GTK_CLI_ERRORS_'+language.upper()+'_PASS')
