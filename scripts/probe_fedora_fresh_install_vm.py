"""Disposable Fedora VM: install, inspect, reject unsafe removal, and uninstall.

No cloud provider request, systemd installation, or production path modification.
"""
from pathlib import Path
import json,os,subprocess,tempfile
from scripts.build_fedora_mvp import build
from scripts.install_fedora_mvp import install,verify
from scripts.uninstall_fedora_mvp import uninstall

marker=Path('/etc/proton-mvp-disposable-vm')
if (not marker.is_file() or marker.read_text().strip()!='VM_TEST_ONLY_NO_CLOUD'
    or Path.home().name!='mvptest'):
    raise SystemExit('BLOCKED: disposable Fedora VM only')
units=Path.home()/'.config/systemd/user'
protected=['proton-sync-watcher.service','proton-bisync.timer',
           'proton-bisync-quick.timer','proton-cloud-priority.timer']
before={name:(units/name).read_bytes() if (units/name).is_file() else None for name in protected}
with tempfile.TemporaryDirectory(prefix='alpha-fresh-install-',dir=str(Path.home())) as temp:
    root=Path(temp)
    bundle=root/'candidate'; build(bundle)
    fresh_home=root/'fresh-profile';fresh_home.mkdir(mode=0o700)
    prefix=fresh_home/'installed'
    assert install(bundle,prefix)['status']=='INSTALLED_NOT_ACTIVATED'
    verify(prefix)
    result=subprocess.run([str(prefix/'bin/proton-drive-sync'),'--self-test'],
        env={**os.environ,'HOME':str(fresh_home)},capture_output=True,text=True,timeout=30)
    assert result.returncode==0, result.stderr
    assert 'L10N_OK' in result.stdout and 'BACKEND_OK' in result.stdout
    print('FEDORA_FRESH_INSTALL_SELFTEST_PASS',flush=True)
    try:install(bundle,prefix)
    except FileExistsError:pass
    else:raise AssertionError('Overwriting an existing installation was accepted')
    print('FEDORA_OVERWRITE_DENIED_PASS',flush=True)
    extra=prefix/'user-owned-file';extra.write_text('retain')
    try:uninstall(prefix)
    except (ValueError,RuntimeError):pass
    else:raise AssertionError('Unknown installation file deletion was accepted')
    assert extra.read_text()=='retain'
    extra.unlink()
    print('FEDORA_UNKNOWN_FILE_GUARD_PASS',flush=True)
    assert uninstall(prefix)['status']=='REMOVED_CANDIDATE_ONLY'
    assert not prefix.exists() and fresh_home.exists()
    print('FEDORA_FRESH_UNINSTALL_PASS',flush=True)
for name,original in before.items():
    path=units/name
    assert (path.read_bytes() if path.is_file() else None)==original,name
print('FEDORA_PRODUCTION_UNIT_FENCE_PASS',flush=True)
