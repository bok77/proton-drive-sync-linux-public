"""Explicit user-systemd lifecycle for the isolated Fedora MVP.

Install is inert; enabling the timer is a separate, precisely authorized action.
Never manages unrelated units. Configuration and bundle integrity are checked.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
from .service_integration import UNIT,TIMER,unit_text,timer_text
from .portable_paths import load_paths

INSTALL_CONSENT="I INSTALL ISOLATED MVP UNITS"
ENABLE_CONSENT="I ENABLE ISOLATED MVP TIMER"
PAUSE_CONSENT="I PAUSE ISOLATED MVP TIMER"
REMOVE_CONSENT="I REMOVE ISOLATED MVP UNITS"

def _unit_dir():
    d=Path.home()/".config/systemd/user"
    if d.is_symlink():raise PermissionError("Unsafe user systemd directory")
    if not d.exists():d.mkdir(parents=True,mode=0o700)
    if not d.is_dir():raise PermissionError("Invalid user systemd directory")
    return d

def _bundle(prefix):
    root=Path(prefix).expanduser().absolute()
    if root.is_symlink() or not root.is_dir() or root.is_relative_to(Path("/mnt/example-drive")):
        raise ValueError("Invalid installed bundle")
    data=json.loads((root/"MANIFEST.json").read_text())
    entries=data.get("files")
    if data.get("status")!="TEST_CANDIDATE_NOT_ACTIVATED" or not isinstance(entries,dict):
        raise ValueError("Invalid bundle manifest")
    for rel,sha in entries.items():
        path=root/rel
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError("Bundle integrity failed")
    files={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    if files!=set(entries)|{"MANIFEST.json"}:raise ValueError("Unexpected bundle files")
    return root

def _expected(config,prefix):
    cfg=Path(config).expanduser().absolute()
    if cfg.is_symlink() or not cfg.is_file() or cfg.stat().st_mode&0o077:
        raise PermissionError("Private config file mode 0600 required")
    paths=load_paths(cfg)
    if tuple(paths.managed_folders)!=("ProtonSync-Test",):
        raise PermissionError("Only isolated synthetic test folder is allowed")
    if paths.local_root.is_relative_to(Path("/mnt/example-drive")):
        raise PermissionError("Production tree excluded")
    root=_bundle(prefix)
    return {UNIT:unit_text(root/"bin/proton-portable-full",cfg),TIMER:timer_text()}

def _run(*args):
    return subprocess.run(["systemctl","--user",*args],capture_output=True,text=True,check=True,timeout=25)

def _check(d,expected):
    for name,content in expected.items():
        path=d/name
        if path.is_symlink() or not path.is_file() or path.read_text()!=content:
            raise ValueError(f"Unit missing or modified: {name}")

def status(config,prefix):
    expected=_expected(config,prefix)
    d=_unit_dir()
    present=[(d/name).exists() or (d/name).is_symlink() for name in expected]
    if any(present) and not all(present):
        return {"status":"PARTIAL_INSTALL_BLOCKED"}
    if not any(present):return {"status":"NOT_INSTALLED"}
    _check(d,expected)
    enabled=subprocess.run(
        ["systemctl","--user","is-enabled",TIMER],capture_output=True,text=True,timeout=10)
    active=subprocess.run(["systemctl","--user","is-active",TIMER],
                          capture_output=True,text=True,timeout=10)
    return {"status":"INSTALLED","timer_enabled":enabled.stdout.strip()=="enabled",
            "timer_active":active.stdout.strip()=="active"}

def install(config,prefix,consent):
    if consent!=INSTALL_CONSENT:raise PermissionError("Explicit install consent required")
    expected=_expected(config,prefix);d=_unit_dir()
    for name in expected:
        if (d/name).exists() or (d/name).is_symlink():
            raise FileExistsError(f"Unit already exists: {name}")
    created=[]
    try:
        for name,content in expected.items():
            path=d/name
            fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            created.append(path)
            with os.fdopen(fd,"w") as f:
                f.write(content);f.flush();os.fsync(f.fileno())
        _run("daemon-reload")
    except BaseException:
        for path in created:
            if path.exists() and not path.is_symlink():path.unlink()
        raise
    return {"status":"INSTALLED_NOT_ENABLED"}

def enable(config,prefix,consent):
    if consent!=ENABLE_CONSENT:raise PermissionError("Explicit activation consent required")
    expected=_expected(config,prefix);_check(_unit_dir(),expected)
    paths=load_paths(Path(config))
    state=paths.state_dir
    if (not (state/"initial_pairing_verified.json").is_file()
        or (state/"initial_pairing_verified.json").read_text()!="INITIAL_PAIRING_VERIFIED_V1"
        or (state/"initial_pairing_pending.json").exists()):
        raise PermissionError("Verified initial pairing required before activation")
    _run("enable","--now",TIMER)
    return status(config,prefix)

def pause(config,prefix,consent):
    if consent!=PAUSE_CONSENT:raise PermissionError("Explicit pause consent required")
    expected=_expected(config,prefix);_check(_unit_dir(),expected)
    _run("disable","--now",TIMER)
    _run("stop",UNIT)
    return status(config,prefix)

def uninstall(config,prefix,consent):
    if consent!=REMOVE_CONSENT:raise PermissionError("Explicit removal consent required")
    expected=_expected(config,prefix);d=_unit_dir();_check(d,expected)
    _run("disable","--now",TIMER)
    _run("stop",UNIT)
    _check(d,expected)
    for name in expected:(d/name).unlink()
    _run("daemon-reload")
    return {"status":"UNINSTALLED","config_and_state_retained":True}

RUN_ONCE_CONSENT="I RUN ISOLATED MVP ONCE"

def run_once(config,prefix,consent):
    """Start only the exact installed isolated service, never production sync.

    A running timer is intentionally rejected to keep the MVP proof one-shot.
    The UI must collect confirmation; starting is not evidence of completion.
    """
    if consent!=RUN_ONCE_CONSENT:
        raise PermissionError("Explicit single-run approval required")
    current=status(config,prefix)  # verifies config, manifest and exact unit text
    if current.get("status")!="INSTALLED" or current.get("timer_active") or current.get("timer_enabled"):
        raise PermissionError("Isolated service must be installed with its timer paused")
    paths=load_paths(Path(config))
    verified=paths.state_dir/"initial_pairing_verified.json"
    if (verified.is_symlink() or not verified.is_file()
        or verified.read_text()!="INITIAL_PAIRING_VERIFIED_V1"
        or (paths.state_dir/"initial_pairing_pending.json").exists()):
        raise PermissionError("Verified isolated pairing required")
    _run("start", "--no-block", UNIT)
    return {"status":"START_REQUESTED_NOT_COMPLETED","service":UNIT}
