"""Metadata-only checks for isolated CLI configuration and desktop secret service.

Never enumerate, query, unlock or read keyring items or authentication tokens.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import stat
import subprocess

@dataclass(frozen=True)
class BoundaryReport:
    configuration_private: bool
    configuration_directory_private: bool
    keyring_directory_private: bool | None
    secret_service_present: bool | None
    status: str


def _private(path: Path, *, directory: bool) -> bool:
    """Fail closed for missing, symlink or non-owner-only paths."""
    if path.is_symlink():
        return False
    try:
        info=path.stat()
    except OSError:
        return False
    return (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)) and not(info.st_mode & 0o077)


def inspect(config: Path, keyring_dir: Path, *, user_bus: bool=True) -> BoundaryReport:
    config=Path(config).expanduser()
    keyring_dir=Path(keyring_dir).expanduser()
    cfg_ok=_private(config,directory=False)
    parent_ok=_private(config.parent,directory=True)
    keyring_ok=_private(keyring_dir,directory=True) if keyring_dir.exists() or keyring_dir.is_symlink() else None
    bus=None
    if user_bus:
        try:
            proc=subprocess.run(['busctl','--user','--no-pager','list'],capture_output=True,text=True,timeout=3,check=False)
            bus=proc.returncode==0 and any(line.split(maxsplit=1)[0]=='org.freedesktop.secrets' for line in proc.stdout.splitlines() if line.strip())
        except (OSError,subprocess.TimeoutExpired):
            bus=None
    # Keyring contents and token storage location are deliberately not verified.
    status='METADATA_ONLY' if cfg_ok and parent_ok and keyring_ok is not False and bus is True else 'BLOCKED'
    return BoundaryReport(cfg_ok,parent_ok,keyring_ok,bus,status)
