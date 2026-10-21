"""Read-only fail-closed gates for an eventual third-party release.

Not a runtime change: production sync continues untouched. Never read secrets.
"""
from dataclasses import dataclass
from pathlib import Path
from .cli_storage_audit import inspect as inspect_storage
from .secret_boundary import inspect as inspect_secret_boundary

@dataclass(frozen=True)
class ProviderGate:
    credentials_mode: str
    secret_boundary_ok: bool
    cache_metadata_ok: bool
    event_sync_verified: bool
    conditional_revision_write_verified: bool
    status: str
    blockers: tuple[str,...]


def evaluate(*, credentials_mode: str | None, config: Path, keyring_dir: Path,
             app_dir: Path, cache_dir: Path, event_sync_verified: bool=False,
             conditional_revision_write_verified: bool=False, user_bus: bool=True) -> ProviderGate:
    mode=(credentials_mode or 'keychain').lower()
    blockers=[]
    if mode not in ('keychain','pass'):
        blockers.append('UNSAFE_OR_UNKNOWN_CREDENTIAL_STORE')
    secret=inspect_secret_boundary(config,keyring_dir,user_bus=user_bus)
    if mode=='keychain' and secret.status!='METADATA_ONLY':
        blockers.append('SECRET_BOUNDARY_UNVERIFIED')
    # For `pass`, actual GPG key and password-store setup require a separate proof.
    if mode=='pass':
        blockers.append('PASS_STORE_UNVERIFIED')
    app=inspect_storage(app_dir)
    cache=inspect_storage(cache_dir)
    metadata_ok=app.status=='METADATA_ONLY' and cache.status=='METADATA_ONLY'
    if not metadata_ok: blockers.append('CLI_LOCAL_METADATA_EXPOSURE')
    if not event_sync_verified: blockers.append('EVENT_BASED_SYNC_UNVERIFIED')
    if not conditional_revision_write_verified: blockers.append('ATOMIC_REVISION_WRITE_UNVERIFIED')
    blockers=tuple(sorted(set(blockers)))
    return ProviderGate(mode,secret.status=='METADATA_ONLY',metadata_ok,
                        event_sync_verified,conditional_revision_write_verified,
                        'PASS' if not blockers else 'BLOCKED',blockers)
