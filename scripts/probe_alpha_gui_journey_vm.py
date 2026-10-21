"""Disposable Fedora VM GUI-to-systemd-to-synthetic-evidence acceptance probe.

This executable must never be used on the development host or with cloud credentials.
"""
from pathlib import Path
from unittest.mock import patch
import hashlib,json,os,shutil,tempfile,time
import gi
gi.require_version('Gtk','4.0');gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop.app import Application,Window
from proton_sync_engine import user_service_lifecycle as lc
from proton_sync_engine import alpha_lifecycle
from scripts.build_fedora_mvp import build

marker=Path('/etc/proton-mvp-disposable-vm')
if not marker.is_file() or marker.read_text().strip()!='VM_TEST_ONLY_NO_CLOUD' or Path.home().name!='mvptest':
    raise SystemExit('BLOCKED: disposable VM required')
assert Gtk.init_check(), 'No graphical test display'
unitdir=Path.home()/'.config/systemd/user'
assert all(not (unitdir/n).exists() for n in (lc.UNIT,lc.TIMER)), 'Existing isolated units: abort'
profiledir=Path.home()/'.config/proton-drive-sync-alpha'
assert not profiledir.exists(), 'Existing independent profile: abort'

def spin(condition,limit=18):
    until=time.monotonic()+limit
    while time.monotonic()<until:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        if condition():return
        time.sleep(.05)
    raise AssertionError('GUI wait timed out')

def walk(widget):
    yield widget
    child=widget.get_first_child()
    while child:
        yield from walk(child)
        child=child.get_next_sibling()

def confirmation_dialogs(window):
    """Ignore informational notices left open after successful operations."""
    return [w for w in walk(window) if isinstance(w,Adw.AlertDialog)
            and w.get_mapped() and w.get_heading().startswith('Isolated alpha test:')]

def action(window,name):
    return next((w for w in walk(window) if isinstance(w,Gtk.Button) and w.get_label()==name),None)

with tempfile.TemporaryDirectory(prefix='alpha-gui-vm-',dir=str(Path.home())) as t:
    base=Path(t)
    root=base/'files';root.mkdir(mode=0o700)
    (root/'ProtonSync-Test').mkdir(mode=0o700)
    state=base/'state';state.mkdir(mode=0o700)
    (state/'initial_pairing_verified.json').write_text('INITIAL_PAIRING_VERIFIED_V1')
    profiledir.mkdir(mode=0o700)
    config=profiledir/'alpha-profile.json'
    config.write_text(json.dumps({'local_root':str(root),'mount_root':'/home',
        'state_dir':str(state),'cli_executable':'/usr/bin/true',
        'managed_folders':['ProtonSync-Test'],'priority_cloud_folders':[]}));config.chmod(0o600)
    bundle=base/'bundle';build(bundle)
    runner=bundle/'bin/proton-portable-full'
    runner.write_text('''#!/usr/bin/python3
import json,os
from pathlib import Path
config=json.loads(Path(os.environ['PROTON_SYNC_CONFIG']).read_text())
event=Path(config['state_dir'])/'events.jsonl'
with event.open('a') as out:
    out.write(json.dumps({'event':'run_end','uploaded':2,'remote_downloaded':1,'valid':0,'conflicts':0,'errors':0})+'\\n')
''')
    runner.chmod(0o700)
    manifest=bundle/'MANIFEST.json';payload=json.loads(manifest.read_text())
    payload['files']['bin/proton-portable-full']=hashlib.sha256(runner.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(payload))
    old_bundle=lc._bundle
    def vm_bundle(value):
        # GUI sources live in VM test checkout; map only those to the fresh validated bundle.
        request=Path(value).resolve()
        assert request in (Path(__file__).resolve().parents[1],bundle.resolve()),request
        return old_bundle(bundle)
    win=None
    try:
        with patch.object(lc,'_bundle',side_effect=vm_bundle):
            app=Application(lang_override='en',public_alpha=True)
            assert app.register()
            win=Window(app);win.present()
            assert list(win.pages)==['overview','settings']
            assert win.alpha_result.get_title()=='No single run yet'
            print('ALPHA_GUI_PROFILE_AND_REUSED_RESULT_PASS',flush=True)
            for operation,caption in [('install','Install isolated test service'),
                                       ('start_once','Run isolated test once'),
                                       ('remove','Remove isolated test service')]:
                button=action(win,caption)
                assert button is not None and button.get_sensitive(),caption
                button.emit('clicked')
                spin(lambda:bool(confirmation_dialogs(win)))
                dialog=confirmation_dialogs(win)[0]
                assert dialog.get_default_response()=='cancel'
                dialog.emit('response','cancel')
                dialog.close()
                spin(lambda:not bool(confirmation_dialogs(win)))
                assert alpha_lifecycle.status(bundle)['status']==('INSTALLED' if operation!='install' else 'NOT_INSTALLED')
                button.emit('clicked')
                spin(lambda:bool(confirmation_dialogs(win)))
                dialog=confirmation_dialogs(win)[0]
                dialog.emit('response','approve')
                dialog.close()
                if operation=='install':
                    spin(lambda:alpha_lifecycle.status(bundle)['status']=='INSTALLED')
                    print('ALPHA_GUI_INSTALL_PASS',flush=True)
                elif operation=='start_once':
                    spin(lambda:win.alpha_result.get_title()=='Test complete')
                    assert 'Upload: 2' in win.alpha_result.get_subtitle()
                    assert 'Download: 1' in win.alpha_result.get_subtitle()
                    print('ALPHA_GUI_VERIFIED_RUN_END_PASS',flush=True)
                else:
                    spin(lambda:alpha_lifecycle.status(bundle)['status']=='NOT_INSTALLED')
                    print('ALPHA_GUI_REMOVE_PASS',flush=True)
    finally:
        if win:win.close()
        if any((unitdir/name).exists() for name in (lc.UNIT,lc.TIMER)):
            # The existing controller may only remove the exact test units.
            with patch.object(lc,'_bundle',side_effect=vm_bundle):
                alpha_lifecycle.remove(bundle,consent=lc.REMOVE_CONSENT)
        assert all(not (unitdir/name).exists() for name in (lc.UNIT,lc.TIMER))
        config.unlink(missing_ok=True);profiledir.rmdir()
print('ALPHA_GUI_VM_JOURNEY_PASS')
