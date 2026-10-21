"""Disposable Fedora VM only: real systemd lifecycle via alpha delegation.

Run using a cloud-free, manifest-checked stub. Never run on a host account.
"""
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import hashlib,json,os,tempfile,shutil
from proton_sync_engine import alpha_lifecycle as alpha
from proton_sync_engine import user_service_lifecycle as lc
from scripts.build_fedora_mvp import build

marker=Path('/etc/proton-mvp-disposable-vm')
if not marker.is_file() or marker.read_text().strip()!='VM_TEST_ONLY_NO_CLOUD' or Path.home().name!='mvptest':
    raise SystemExit('BLOCKED: disposable VM required')
unit_dir=Path.home()/'.config/systemd/user'
if any((unit_dir/name).exists() for name in (lc.UNIT,lc.TIMER)):
    raise SystemExit('BLOCKED: existing isolated units')
with tempfile.TemporaryDirectory(prefix='alpha-vm-proof-') as t:
    base=Path(t)
    config_dir=base/'profile';config_dir.mkdir(mode=0o700)
    data=Path('/run/user/1000')/('alpha-vm-'+str(os.getpid()));data.mkdir(mode=0o700)
    (data/'ProtonSync-Test').mkdir(mode=0o700)
    state=base/'state';state.mkdir(mode=0o700)
    (state/'initial_pairing_verified.json').write_text('INITIAL_PAIRING_VERIFIED_V1')
    config=config_dir/'alpha-profile.json'
    config.write_text(json.dumps({'local_root':str(data),'mount_root':'/run/user/1000',
        'state_dir':str(state),'cli_executable':'/usr/bin/true',
        'managed_folders':['ProtonSync-Test'],'priority_cloud_folders':[]}))
    config.chmod(0o600)
    bundle=base/'bundle';build(bundle)
    stub=bundle/'bin/proton-portable-full';stub.write_text('#!/bin/sh\nexit 0\n');stub.chmod(0o700)
    manifest=bundle/'MANIFEST.json';payload=json.loads(manifest.read_text());payload['files']['bin/proton-portable-full']=hashlib.sha256(stub.read_bytes()).hexdigest();manifest.write_text(json.dumps(payload))
    profile=SimpleNamespace(config_path=config,paths=SimpleNamespace(local_root=data,state_dir=state))
    try:
        # Use original service install/start/uninstall with real VM user systemd.
        # The private profile fixture only bypasses the VM's mountpoint shape.
        with patch.object(alpha,'load_alpha_profile',return_value=profile):
            result=alpha.install(bundle,consent=lc.INSTALL_CONSENT,config_dir=config_dir)
            assert result['status']=='INSTALLED_NOT_ENABLED'
            assert alpha.status(bundle,config_dir)['status']=='INSTALLED'
            print('ALPHA_REAL_SYSTEMD_INSTALL_PASS',flush=True)
            run=alpha.start_once(bundle,consent=lc.RUN_ONCE_CONSENT,config_dir=config_dir)
            assert run['status']=='START_REQUESTED_NOT_COMPLETED'
            print('ALPHA_REAL_SYSTEMD_START_REQUEST_PASS',flush=True)
            removed=alpha.remove(bundle,consent=lc.REMOVE_CONSENT,config_dir=config_dir)
            assert removed['status']=='UNINSTALLED'
            print('ALPHA_REAL_SYSTEMD_REMOVE_PASS',flush=True)
    finally:
        if any((unit_dir/name).exists() for name in (lc.UNIT,lc.TIMER)):
            raise RuntimeError('FAIL-CLOSED: isolated units remain; manual VM cleanup needed')
        shutil.rmtree(data)
print('ALPHA_VM_CLOUDFREE_LIFECYCLE_PASS')
