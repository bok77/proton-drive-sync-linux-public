"""Fail-closed installer planning and isolated staging for a future Linux client.

No systemd user directory is touched. Nothing is enabled or executed. Staged
service units deliberately fail startup until separately reviewed runtime
activation, initial baseline pairing and rollback have been implemented.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from .portable_paths import load_paths

UNIT_NAMES={
    "full":"proton-portable-sync-full.service",
    "quick":"proton-portable-sync-quick.service",
    "priority":"proton-portable-sync-priority.service",
}
ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/"proton_sync_engine"/"runtime"

def plan(config_file:Path)->dict:
    """Validate a private explicit configuration; describe writes, do none."""
    config=load_paths(config_file)
    return {
        "status":"PREVIEW_ONLY",
        "activation_authorized":False,
        "local_root":str(config.local_root),
        "mount_root":str(config.mount_root),
        "cloud_root":config.base.cloud_root,
        "state_dir":str(config.state_dir),
        "cli_executable":str(config.cli_executable),
        "managed_folders":list(config.managed_folders),
        "priority_cloud_folders":list(config.priority_folders),
        "staged_units":list(UNIT_NAMES.values()),
        "warning":"Staged units are permanently blocked. No sync, activation, baseline or credentials.",
    }

def _service_text(kind:str)->str:
    """Valid systemd syntax with an unconditional fail-closed execution gate."""
    if kind not in UNIT_NAMES:
        raise ValueError("Unsupported unit")
    name=UNIT_NAMES[kind]
    return (
        "[Unit]\n"
        "Description=Proton portable sync ("+kind+") — NOT ACTIVATED\n\n"
        "[Service]\n"
        "Type=oneshot\n"
        "ExecCondition=/usr/bin/false\n"
        "ExecStart=/usr/bin/false\n"
        "NoNewPrivileges=true\n"
        "ProtectSystem=strict\n"
        "PrivateTmp=true\n"
        "UMask=0077\n"
        "StandardOutput=journal\n"
        "StandardError=journal\n"
    )

def stage(config_file:Path,output_dir:Path)->dict:
    """Create inert install artifacts *only* inside a new empty test directory.

    Never touches real systemd unit paths or user data. On failure remove the
    incomplete stage but preserve any preexisting destination directory.
    """
    summary=plan(config_file)
    dest=Path(output_dir).expanduser()
    if not dest.is_absolute() or dest.is_symlink():
        raise ValueError("Staging destination must be absolute and non-symlink")
    if dest.exists():
        raise FileExistsError("Refusing to overwrite any existing staging directory")
    if dest==Path.home() or dest==Path("/") or dest==summary["local_root"]:
        raise ValueError("Unsafe staging destination")
    config=load_paths(config_file)
    if dest.is_relative_to(config.local_root) or dest.is_relative_to(config.mount_root):
        raise ValueError("Staging cannot be inside the synchronized filesystem")
    if dest.is_relative_to(config.state_dir):
        raise ValueError("Staging cannot overlap engine state")
    parent=dest.parent.resolve(strict=True)
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("Staging parent must be a real directory")
    # Parent can be chosen only in a workspace; no mutation of user services.
    dest.mkdir(mode=0o700)
    try:
        units=dest/"units"
        units.mkdir(mode=0o700)
        for key,name in UNIT_NAMES.items():
            path=units/name
            path.write_text(_service_text(key),encoding="utf-8")
            path.chmod(0o600)
        descriptor=dest/"INSTALL_NOT_ACTIVATED.json"
        descriptor.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
        descriptor.chmod(0o600)
        (dest/"DO_NOT_ENABLE.txt").write_text(
            "Non-executable preview only. Runtime is not accepted.\n"
            "No unit here is ready to enable; installer activation is NOT IMPLEMENTED.\n",
            encoding="utf-8")
        return summary
    except Exception:
        shutil.rmtree(dest)
        raise

def verify_stage(output_dir:Path)->dict:
    """Read back an inert staging directory without executing anything.

    Reject missing, unexpected, tampered or symlinked files. The returned
    preview is informational; it never grants permission to activate units.
    """
    dest=Path(output_dir)
    expected={"units","INSTALL_NOT_ACTIVATED.json","DO_NOT_ENABLE.txt"}
    if not dest.is_dir() or dest.is_symlink():
        raise ValueError("Stage directory missing or unsafe")
    if {p.name for p in dest.iterdir()}!=expected:
        raise ValueError("Unexpected staged files")
    units=dest/"units"
    if not units.is_dir() or units.is_symlink():
        raise ValueError("Unsafe unit directory")
    if {p.name for p in units.iterdir()}!=set(UNIT_NAMES.values()):
        raise ValueError("Unexpected staged service units")
    for kind,name in UNIT_NAMES.items():
        unit=units/name
        if not unit.is_file() or unit.is_symlink() or unit.read_text()!=_service_text(kind):
            raise ValueError("Staged service does not match inert template")
    descriptor=dest/"INSTALL_NOT_ACTIVATED.json"
    guard=dest/"DO_NOT_ENABLE.txt"
    if descriptor.is_symlink() or guard.is_symlink() or not guard.is_file():
        raise ValueError("Unsafe staging metadata")
    summary=json.loads(descriptor.read_text())
    if not isinstance(summary,dict) or summary.get("status")!="PREVIEW_ONLY":
        raise ValueError("Invalid stage status")
    if summary.get("activation_authorized") is not False:
        raise ValueError("Activation is not allowed")
    if summary.get("staged_units")!=list(UNIT_NAMES.values()):
        raise ValueError("Unexpected unit manifest")
    if "ready to enable" not in guard.read_text():
        raise ValueError("Missing activation warning")
    return summary

def unstage(output_dir:Path)->None:
    """Refuse general deletion: only remove our exact known inert stage files."""
    dest=Path(output_dir)
    verify_stage(dest)
    unitdir=dest/"units"
    # Explicitly remove only named files, never recursively delete unknowns.
    for name in UNIT_NAMES.values():
        (unitdir/name).unlink()
    unitdir.rmdir()
    (dest/"INSTALL_NOT_ACTIVATED.json").unlink()
    (dest/"DO_NOT_ENABLE.txt").unlink()
    dest.rmdir()

def main(argv=None):
    parser=argparse.ArgumentParser(description="Inert installer preview (never starts services)")
    parser.add_argument("--config",type=Path,required=True)
    parser.add_argument("--stage",type=Path)
    parser.add_argument("--remove-stage",type=Path)
    parser.add_argument("--verify-stage",type=Path)
    args=parser.parse_args(argv)
    if sum(v is not None for v in (args.stage,args.remove_stage,args.verify_stage))>1:
        parser.error("Choose one of stage, verify or remove")
    if args.verify_stage:
        print(json.dumps(verify_stage(args.verify_stage),indent=2,ensure_ascii=False))
        return 0
    if args.remove_stage:
        unstage(args.remove_stage)
        print("Staging files removed, no systemd changes made")
        return 0
    info=stage(args.config,args.stage) if args.stage else plan(args.config)
    print(json.dumps(info,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    sys.exit(main())
