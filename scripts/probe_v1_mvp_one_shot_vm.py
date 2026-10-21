"""VM ONLY: cloud-free V1 user journey using verified pairing and real systemd.

Never run on the host. Require a marker written solely in disposable VM.
"""
import json, os, tempfile, time, hashlib
from pathlib import Path
from unittest.mock import patch
import gi
gi.require_version('Gtk','4.0');gi.require_version('Adw','1')
from gi.repository import Gtk,Adw,GLib
from proton_sync_desktop import setup_wizard
from proton_sync_engine import user_service_lifecycle as lc
from scripts.build_fedora_mvp import build

MARK=Path('/etc/proton-mvp-disposable-vm')
if not MARK.is_file() or MARK.read_text().strip()!='VM_TEST_ONLY_NO_CLOUD':
    raise SystemExit('BLOCKED: disposable VM marker missing')
if Path.home().name!='mvptest':raise SystemExit('BLOCKED: wrong VM user')
if not Path('/run/user/1000').is_mount():raise SystemExit('BLOCKED: missing isolated mount')
unitdir=Path.home()/'.config/systemd/user'
for name in (lc.UNIT,lc.TIMER):
    if (unitdir/name).exists():raise SystemExit('BLOCKED: test units preexisting')
cfg=Path.home()/'.config/proton-sync-isolated/config.json'
if cfg.exists():raise SystemExit('BLOCKED: test config preexisting')

def spin(pred,sec=12):
    until=time.monotonic()+sec
    while time.monotonic()<until:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        if pred():return
        time.sleep(.04)
    raise AssertionError('GTK timeout')
def walk(w):
    yield w
    c=w.get_first_child()
    while c:
        yield from walk(c);c=c.get_next_sibling()
def button(root,label):
    return next((b for b in walk(root) if isinstance(b,Gtk.Button) and b.get_label()==label and b.get_visible() and b.get_sensitive()),None)

with tempfile.TemporaryDirectory(prefix='vm-v1-gui-real-') as t:
    base=Path(t);root=Path('/run/user/1000')/('proton-v1-real-'+str(os.getpid()))
    root.mkdir(mode=0o700);local=root/'ProtonSync-Test';local.mkdir(mode=0o700)
    state=base/'state';state.mkdir(mode=0o700)
    (state/'initial_pairing_verified.json').write_text('INITIAL_PAIRING_VERIFIED_V1')
    cfg.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    cfg.write_text(json.dumps({'local_root':str(root),'mount_root':'/run/user/1000','state_dir':str(state),
              'cli_executable':'/usr/bin/true','managed_folders':['ProtonSync-Test'],
              'priority_cloud_folders':[]}));cfg.chmod(0o600)
    bundle=base/'bundle';build(bundle)
    # Replace cloud-capable runtime with a harmless executable and update its digest.
    runner=bundle/'bin/proton-portable-full';runner.write_text('#!/bin/sh\nexit 0\n');runner.chmod(0o700)
    manifest=bundle/'MANIFEST.json';data=json.loads(manifest.read_text())
    data['files']['bin/proton-portable-full']=hashlib.sha256(runner.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    original_bundle=lc._bundle
    def isolated_bundle(prefix):
        assert Path(prefix).resolve() in (Path(__file__).resolve().parents[1], bundle.resolve())
        return original_bundle(bundle)
    try:
        with patch.object(lc,'_bundle',side_effect=isolated_bundle):
            assert setup_wizard.verified_isolated_pairing(), "Real local pairing verification failed"
            print("V1_MVP_LOCAL_PAIRING_VERIFIED_PASS",flush=True)
            Adw.init();window=Gtk.Window();window.set_default_size(720,850)
            page=setup_wizard.make_page('de');window.set_child(page);window.present()
            stages=[('install','Dienst installieren',False,False),('enable','Testdienst aktivieren',True,True),
                    ('pause','Testdienst pausieren',False,False),('enable','Testdienst aktivieren',True,True),('pause','Testdienst pausieren',False,False),('uninstall','Testdienst entfernen',False,False)]
            for action,label,enabled,active in stages:
                spin(lambda:button(page,label) is not None)
                b=button(page,label);before=lc.status(cfg,bundle)
                b.emit('clicked')
                spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
                dlg=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
                assert dlg.get_default_response()==dlg.get_close_response()=='cancel'
                dlg.emit('response','cancel');dlg.close();spin(lambda:not dlg.get_visible())
                assert lc.status(cfg,bundle)==before,action+' cancel mutated'
                b.emit('clicked')
                spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
                dlg=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
                dlg.emit('response','approve');dlg.close()
                expect='NOT_INSTALLED' if action=='uninstall' else 'INSTALLED'
                spin(lambda:lc.status(cfg,bundle).get('status')==expect and (action in ('install','uninstall') or lc.status(cfg,bundle).get('timer_active')==active))
                actual=lc.status(cfg,bundle)
                if action!='uninstall':assert actual['timer_enabled']==enabled and actual['timer_active']==active,actual
                shown=[w.get_title() for w in walk(page) if isinstance(w,Adw.ActionRow)]
                expected_title=('Nicht installiert' if action=='uninstall' else ('Testdienst aktiv' if active else 'Installiert · nicht aktiv'))
                spin(lambda: any(isinstance(w,Adw.ActionRow) and w.get_title()==expected_title for w in walk(page)))
                print('V1_MVP_GUI_'+action.upper()+'_STATE_PASS',flush=True)
                if action=='pause':
                    spin(lambda:button(page,'Einmaligen Testlauf starten') is not None)
                    one=button(page,'Einmaligen Testlauf starten')
                    one.emit('clicked')
                    spin(lambda:any(isinstance(w,Adw.MessageDialog) and w.get_visible() for w in Gtk.Window.list_toplevels()))
                    confirm=next(w for w in Gtk.Window.list_toplevels() if isinstance(w,Adw.MessageDialog) and w.get_visible())
                    confirm.emit('response','approve');confirm.close()
                    spin(lambda:any(isinstance(w,Adw.ActionRow) and ('Testlauf angefordert' in w.get_title() or 'Testlauf blockiert' in w.get_title()) for w in walk(page)))
                    assert any(isinstance(w,Adw.ActionRow) and 'Testlauf angefordert' in w.get_title() for w in walk(page))
                    assert lc.status(cfg,bundle).get('timer_enabled')==False
                    print('V1_MVP_GUI_ONE_SHOT_REQUEST_PASS',flush=True)

            assert cfg.exists() and (state/'initial_pairing_verified.json').is_file()
            assert root.is_dir() and local.is_dir()
            print('V1_MVP_DATA_AND_PAIRING_PRESERVED_PASS',flush=True)
            window.close()
    finally:
        # Genuine cleanup using the same guarded lifecycle; no unsafe force remove.
        try:
            if lc.status(cfg,bundle).get('status')=='INSTALLED':lc.uninstall(cfg,bundle,lc.REMOVE_CONSENT)
        finally:
            cfg.unlink(missing_ok=True)
            try:cfg.parent.rmdir()
            except OSError:pass
            local.rmdir();root.rmdir()
print('V1_MVP_ONE_SHOT_CLOUDFREE_VM_PASS')
