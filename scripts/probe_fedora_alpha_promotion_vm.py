"""Disposable Fedora VM: verify a reversible alpha-only desktop promotion."""
import tempfile
from pathlib import Path
from scripts.build_fedora_mvp import build
from scripts.install_fedora_mvp import install, verify
from scripts.promote_fedora_mvp import CONSENT, APP_ID, register_initial, switch
from scripts.uninstall_fedora_mvp import uninstall

assert Path('/etc/proton-mvp-disposable-vm').read_text().strip()=='VM_TEST_ONLY_NO_CLOUD'
assert Path.home().name=='mvptest'
with tempfile.TemporaryDirectory(prefix='alpha-launcher-proof-',dir=str(Path.home())) as t:
    root=Path(t);bundle=root/'bundle';build(bundle)
    old=root/'v1';new=root/'v2';apps=root/'applications';apps.mkdir(mode=0o700)
    install(bundle,old);install(bundle,new)
    unrelated=apps/'other.desktop';unrelated.write_text('preserve me')
    register_initial(old,apps,consent=CONSENT)
    assert switch(old,new,apps,consent=CONSENT)['status']=='DESKTOP_SWITCHED'
    assert str(new) in (apps/APP_ID).read_text()
    print('VM_ALPHA_DESKTOP_PROMOTION_PASS',flush=True)
    assert switch(new,old,apps,consent=CONSENT)['status']=='DESKTOP_SWITCHED'
    assert str(old) in (apps/APP_ID).read_text()
    print('VM_ALPHA_DESKTOP_ROLLBACK_PASS',flush=True)
    assert unrelated.read_text()=='preserve me'
    verify(old);verify(new)
    (apps/APP_ID).unlink()
    uninstall(new);uninstall(old)
    print('VM_ALPHA_PACKAGES_AND_UNRELATED_FILES_PRESERVED_PASS',flush=True)
