"""Isolated installer proof: explicit approval, inert units and safe uninstall.

This does NOT authorize a working cloud-sync runtime. Its only installable
artifact is an unconditional fail-closed systemd service definition. No
live user-systemd directory, cloud account, or sync data is ever touched.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

from .install_plan import UNIT_NAMES, _service_text, verify_stage

APPROVAL="I APPROVE ISOLATED TEST INSTALL"
MANIFEST="portable-test-install.json"

def _files():
    return {name:_service_text(kind).encode("utf-8") for kind,name in UNIT_NAMES.items()}

def _validate_target(destination:Path,service_dir:Path,source_stage:Path):
    dest=Path(destination)
    services=Path(service_dir)
    if not dest.is_absolute() or not services.is_absolute():
        raise ValueError("Absolute test paths required")
    for item in (dest,services):
        if item==Path("/") or item==Path.home() or item.is_symlink():
            raise ValueError("Unsafe installation path")
    if dest==services or dest.is_relative_to(services) or services.is_relative_to(dest):
        raise ValueError("Install and service directories must be separate")
    # This development proof is restricted to a disposable temporary sandbox.
    # Never permit root- or user-level systemd directories, even with approval.
    sandbox=Path(__import__("tempfile").gettempdir()).resolve(strict=True)
    if not dest.is_relative_to(sandbox) or not services.is_relative_to(sandbox):
        raise ValueError("Only disposable temporary test installations are allowed")
    if dest.exists() or services.exists():
        raise FileExistsError("Refusing to overwrite an existing installation")
    if dest.is_relative_to(source_stage) or services.is_relative_to(source_stage):
        raise ValueError("Staging paths must not overlap")
    for path in (dest,services):
        parent=path.parent
        if not parent.is_dir() or parent.is_symlink() or parent.resolve()!=parent:
            raise ValueError("Target parent must already exist and be a real directory")
    # Never install under the user's actual systemd directory.
    user_systemd=Path.home()/".config/systemd/user"
    if dest==user_systemd or services==user_systemd:
        raise ValueError("Actual user systemd installation not supported")
    if dest.is_relative_to(user_systemd) or services.is_relative_to(user_systemd):
        raise ValueError("Actual user systemd installation not supported")
    return dest,services

def install_test(stage_dir:Path,destination:Path,service_dir:Path,approval:str):
    """Copy verified inert templates into two new, isolated target directories."""
    if approval!=APPROVAL:
        raise PermissionError("Explicit isolated test approval required")
    info=verify_stage(stage_dir)
    root=Path(info["local_root"])
    mount=Path(info["mount_root"])
    state=Path(info["state_dir"])
    dest,services=_validate_target(destination,service_dir,Path(stage_dir))
    for path in (dest,services):
        if path.is_relative_to(mount) or path.is_relative_to(root) or path.is_relative_to(state):
            raise ValueError("Test installation cannot overlap configured data or state")
    # Ensure a self-contained test record without user credentials.
    files=_files()
    manifest={
        "schema":1,
        "status":"TEST_ONLY_NEVER_ACTIVATED",
        "activation_authorized":False,
        "unit_names":sorted(files),
        "sha256":{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},
    }
    dest.mkdir(mode=0o700)
    try:
        services.mkdir(mode=0o700)
        for name,data in files.items():
            path=services/name
            with path.open("xb") as out:
                out.write(data)
            path.chmod(0o600)
        record=dest/MANIFEST
        with record.open("x") as out:
            json.dump(manifest,out,sort_keys=True,indent=2)
        record.chmod(0o600)
        verify_test_install(dest,services)
        return manifest
    except Exception:
        # Roll back ONLY the exact files just created in empty new directories.
        for name in files:
            (services/name).unlink(missing_ok=True) if services.is_dir() else None
        if services.is_dir():
            services.rmdir()
        (dest/MANIFEST).unlink(missing_ok=True)
        dest.rmdir()
        raise

def verify_test_install(destination:Path,service_dir:Path):
    dest=Path(destination)
    services=Path(service_dir)
    if not dest.is_dir() or dest.is_symlink() or not services.is_dir() or services.is_symlink():
        raise ValueError("Missing or unsafe test install")
    if {f.name for f in dest.iterdir()}!={MANIFEST}:
        raise ValueError("Unknown installation files")
    if {f.name for f in services.iterdir()}!=set(_files()):
        raise ValueError("Unknown installed service files")
    record=dest/MANIFEST
    if record.is_symlink() or record.stat().st_mode & 0o077:
        raise ValueError("Unsafe installation manifest")
    manifest=json.loads(record.read_text())
    if (manifest.get("status")!="TEST_ONLY_NEVER_ACTIVATED" or
        manifest.get("activation_authorized") is not False):
        raise ValueError("Activation evidence mismatch")
    if manifest.get("unit_names")!=sorted(_files()):
        raise ValueError("Unexpected service names")
    for name,data in _files().items():
        file=services/name
        if file.is_symlink() or not file.is_file() or file.read_bytes()!=data:
            raise ValueError("Installed service was changed")
        if manifest.get("sha256",{}).get(name)!=hashlib.sha256(data).hexdigest():
            raise ValueError("Installed hash mismatch")
    return manifest

def uninstall_test(destination:Path,service_dir:Path):
    """Remove only readback-verified test artifacts; never touch personal files."""
    verify_test_install(destination,service_dir)
    dest=Path(destination)
    services=Path(service_dir)
    for name in _files():
        (services/name).unlink()
    services.rmdir()
    (dest/MANIFEST).unlink()
    dest.rmdir()
