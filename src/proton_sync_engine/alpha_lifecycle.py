"""Delegate alpha lifecycle operations to the existing isolated service controller.

No production service names are accepted. Every request revalidates the
independent alpha profile and the bundle before forwarding an action.
"""
from __future__ import annotations
from pathlib import Path
from .alpha_profile import load_alpha_profile
from . import user_service_lifecycle as lifecycle


def _context(bundle: Path, config_dir: Path | None = None):
    """Resolve a private profile and intact bundle without changing state."""
    profile = load_alpha_profile(config_dir)
    package = lifecycle._bundle(bundle)
    if package.is_relative_to(profile.paths.local_root) or package.is_relative_to(profile.paths.state_dir):
        raise PermissionError('Installed runtime must not reside inside synchronized data or state')
    expected = lifecycle._expected(profile.config_path, package)
    if set(expected) != {lifecycle.UNIT, lifecycle.TIMER}:
        raise PermissionError('Unexpected isolated unit identity')
    return profile.config_path, package


def status(bundle: Path, config_dir: Path | None = None):
    """Read the exact alpha service status without activating any unit."""
    config, package = _context(bundle, config_dir)
    return lifecycle.status(config, package)


def install(bundle: Path, *, consent: str, config_dir: Path | None = None):
    """Install only the inert isolated service after explicit approval."""
    if consent != lifecycle.INSTALL_CONSENT:
        raise PermissionError('Explicit alpha installation approval required')
    config, package = _context(bundle, config_dir)
    return lifecycle.install(config, package, consent)


def start_once(bundle: Path, *, consent: str, config_dir: Path | None = None):
    """Request one run through existing pairing, timer, and manifest guards."""
    if consent != lifecycle.RUN_ONCE_CONSENT:
        raise PermissionError('Explicit one-shot approval required')
    config, package = _context(bundle, config_dir)
    return lifecycle.run_once(config, package, consent)


def remove(bundle: Path, *, consent: str, config_dir: Path | None = None):
    """Remove only the matching isolated units, retaining config and data."""
    if consent != lifecycle.REMOVE_CONSENT:
        raise PermissionError('Explicit alpha removal approval required')
    config, package = _context(bundle, config_dir)
    return lifecycle.uninstall(config, package, consent)
