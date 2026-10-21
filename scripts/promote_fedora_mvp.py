"""Safely promote or roll back only a managed alpha desktop launcher.

Never alters another desktop entry or any systemd unit. The original package
is retained until a separate, independently approved cleanup.
"""
from pathlib import Path
import os
import tempfile
from .install_fedora_mvp import verify

CONSENT = 'I APPROVE ALPHA DESKTOP SWITCH'
APP_ID = 'io.github.protondrivesync.Alpha.desktop'
MARKER = 'X-ProtonSync-Managed-Alpha=true'


def _entry(prefix):
    return ('[Desktop Entry]\nType=Application\nName=Proton Drive Sync (Alpha)\n'
            'Exec=' + str(prefix / 'bin/proton-drive-sync') + ' --public-alpha\n'
            'Terminal=false\nCategories=Utility;\n' + MARKER + '\n')


def switch(old, new, launcher_dir, *, consent):
    """Atomically select a verified sibling without touching unrelated entries."""
    if consent != CONSENT:
        raise PermissionError('Explicit desktop switch approval required')
    previous, candidate = verify(old), verify(new)
    if previous == candidate or previous.parent != candidate.parent:
        raise ValueError('Distinct sibling installations required')
    directory = Path(launcher_dir).expanduser().absolute()
    if not directory.is_dir() or directory.is_symlink() or directory.stat().st_mode & 0o077:
        raise PermissionError('Private launcher directory required')
    target = directory / APP_ID
    if target.is_symlink():
        raise PermissionError('Symlinked launcher is forbidden')
    if target.exists() and target.read_text() != _entry(previous):
        raise PermissionError('Launcher not managed by the expected previous version')
    if not target.exists() and old != new:
        raise FileNotFoundError('Managed original launcher required; no takeover')
    fd, temporary = tempfile.mkstemp(prefix='.alpha-launcher-',dir=directory)
    try:
        with os.fdopen(fd,'w') as handle:
            handle.write(_entry(candidate));handle.flush();os.fsync(handle.fileno())
        os.chmod(temporary,0o600)
        os.replace(temporary,target)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)
    return {'status':'DESKTOP_SWITCHED','from':str(previous),'to':str(candidate),
            'old_package_preserved':True,'systemd_unchanged':True}


def register_initial(prefix, launcher_dir, *, consent):
    """Create a new alpha-only launcher; refuse to claim an existing one."""
    if consent != CONSENT:raise PermissionError('Explicit approval required')
    package=verify(prefix)
    directory=Path(launcher_dir).expanduser().absolute()
    if not directory.is_dir() or directory.is_symlink() or directory.stat().st_mode & 0o077:
        raise PermissionError('Private launcher directory required')
    target=directory/APP_ID
    fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as handle:handle.write(_entry(package))
    return target
