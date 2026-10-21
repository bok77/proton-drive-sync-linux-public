"""Resolve an isolated alpha profile without touching legacy production state.

Profile discovery is read-only. It neither authenticates nor activates a sync.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from .portable_paths import load_paths, RuntimePaths

PROFILE_NAME = 'alpha-profile.json'

@dataclass(frozen=True)
class AlphaProfile:
    """An explicitly scoped, private profile usable for future alpha adapters."""
    config_path: Path
    paths: RuntimePaths


def load_alpha_profile(config_dir: Path | None = None) -> AlphaProfile:
    """Reject missing, symlinked, shared, production, or non-test profiles."""
    home = Path.home().resolve()
    base = Path(config_dir) if config_dir is not None else home / '.config' / 'proton-drive-sync-alpha'
    if not base.is_absolute() or base.is_symlink() or not base.is_dir():
        raise ValueError('Private alpha configuration directory required')
    if base.stat().st_uid != os.getuid() or base.stat().st_mode & 0o077:
        raise PermissionError('Alpha configuration directory must be owned and private')
    config = base / PROFILE_NAME
    if config.is_symlink() or not config.is_file() or config.stat().st_uid != os.getuid():
        raise PermissionError('Independent alpha profile required')
    paths = load_paths(config)
    if paths.managed_folders != ('ProtonSync-Test',):
        raise ValueError('Alpha may manage only ProtonSync-Test')
    for path in (paths.local_root, paths.state_dir):
        if path.is_symlink() or not path.is_relative_to(home):
            raise ValueError('Alpha paths must stay inside the current user home')
        if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
            raise PermissionError('Alpha paths must be private')
    if paths.local_root == paths.state_dir or paths.state_dir.is_relative_to(paths.local_root):
        raise ValueError('Alpha state and local sync root must be separate')
    if paths.cli_executable.is_relative_to(home / '.config'):
        raise ValueError('CLI executable cannot be under configuration directory')
    return AlphaProfile(config, paths)


def public_alpha_profile_status(config_dir: Path | None = None) -> str:
    """Return only a coarse display state; never leak private local paths."""
    try:
        load_alpha_profile(config_dir)
    except (ValueError, PermissionError, OSError, KeyError, TypeError):
        return 'NOT_CONFIGURED'
    return 'CONFIGURED_NOT_ACTIVATED'
