"""Versioned, conservative Proton Drive CLI capability declaration.

A capability can only be enabled after a separately verified provider contract;
CLI help, a successful race test, and a successful command exit are insufficient.
"""
from dataclasses import dataclass

CONTRACT_VERSION = 1

@dataclass(frozen=True)
class CliCapabilities:
    contract_version: int = CONTRACT_VERSION
    conditional_existing_revision_write: bool = False
    atomic_create_only: bool = False
    verified_folder_create_only: bool = False
    skip_exit_zero_on_conflict: bool = True
    readback_required: bool = True


def supported_capabilities() -> CliCapabilities:
    return CliCapabilities()


def require_conditional_existing_write() -> None:
    if not supported_capabilities().conditional_existing_revision_write:
        from .existing_revision_guard import AtomicRevisionUnavailable
        raise AtomicRevisionUnavailable('conditional_revision_upload_unsupported')
