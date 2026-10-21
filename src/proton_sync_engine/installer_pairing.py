"""Installer-facing pairing review. No service activation or implicit pairing."""
from __future__ import annotations

from pathlib import Path
import json
import os

from .initial_activation import GUARD_FILE, pending_guard_data

from . import pairing
from .exclusive_lock import exclusive
from .portable_paths import load_paths

def _review_pairing_unlocked(config_file:Path,remote_adapter):
    """Read-only installer review using an explicitly supplied cloud adapter.

    Adapter must expose scan(), remote_digest(metadata), meta_rev(metadata).
    Callers must inspect the review and never treat it as implicit acceptance.
    """
    config=load_paths(config_file)
    if (config.state_dir/"baseline.json").exists():
        raise FileExistsError("An existing sync baseline cannot be paired again")
    return pairing.compare(config.local_root,config.managed_folders,
                           remote_adapter.scan,remote_adapter.remote_digest,
                           remote_adapter.meta_rev)

def _approve_pairing_unlocked(config_file:Path,remote_adapter,review:dict,approval:str):
    """Approval always requires a fresh config and remote/local comparison.

    This only establishes a paired baseline; it never enables systemd,
    installs runtime files or authorizes live cloud synchronization.
    """
    config=load_paths(config_file)
    if not config.state_dir.is_dir() or config.state_dir.is_symlink():
        raise ValueError("Private state directory must already exist")
    if config.state_dir.stat().st_mode & 0o077:
        raise ValueError("Private state directory permissions required")
    if approval!=pairing.APPROVAL:
        raise PermissionError("Exact pairing approval required")
    pending=config.state_dir/GUARD_FILE
    verified=config.state_dir/"initial_pairing_verified.json"
    if pending.exists() or pending.is_symlink() or verified.exists():
        raise FileExistsError("Initial pairing state already exists")
    record=pending_guard_data(review)
    fd=os.open(pending,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    identity=os.fstat(fd)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as file:
            json.dump(record,file,sort_keys=True)
            file.flush()
            os.fsync(file.fileno())
        return pairing.approve(
            config.local_root,config.managed_folders,
            remote_adapter.scan,remote_adapter.remote_digest,
            remote_adapter.meta_rev,config.state_dir/"baseline.json",
            review,approval)
    except BaseException:
        try:
            stat=pending.lstat()
            if (stat.st_dev,stat.st_ino)==(identity.st_dev,identity.st_ino):
                pending.unlink()
        except FileNotFoundError:
            pass
        raise

def review_pairing(config_file:Path,remote_adapter):
    config=load_paths(config_file)
    with exclusive(config.state_dir):
        return _review_pairing_unlocked(config_file,remote_adapter)

def approve_pairing(config_file:Path,remote_adapter,review:dict,approval:str):
    config=load_paths(config_file)
    with exclusive(config.state_dir):
        return _approve_pairing_unlocked(config_file,remote_adapter,review,approval)
