"""Portable Fedora systemd integration: explicit install; never auto-enable."""
from __future__ import annotations
import json,os,shlex,subprocess
from pathlib import Path
from .portable_paths import load_paths
from .exclusive_lock import exclusive

UNIT="proton-mvp-isolated-full.service"
APPROVAL="I APPROVE ISOLATED MVP SERVICE INSTALL"
def unit_text(runtime,config):
    runtime=Path(runtime).absolute()
    config=Path(config).absolute()
    for value in (runtime,config):
        if "\n" in str(value) or "\r" in str(value) or "%" in str(value):
            raise ValueError("Unsafe systemd path")
    # systemd unit command quoting, no shell invocation or network credentials.
    return ("[Unit]\nDescription=Proton Drive portable isolated MVP full sync\n"
            "ConditionPathExists="+str(config)+"\n\n"
            "[Service]\nType=oneshot\n"
            "Environment="+shlex.quote("PROTON_SYNC_CONFIG="+str(config))+"\n"
            "Environment=PYTHONDONTWRITEBYTECODE=1\n"
            "ExecStart="+str(runtime)+"\n"
            "NoNewPrivileges=true\nUMask=0077\n"
            "TimeoutStartSec=600\n"
            )
def preview(config_file,install_prefix):
    config=load_paths(Path(config_file))
    assert config.managed_folders
    prefix=Path(install_prefix).expanduser().absolute()
    from scripts.install_fedora_mvp import verify
    verify(prefix)
    runtime=prefix/"bin/proton-portable-full"
    return {"status":"READY_FOR_INERT_SERVICE_INSTALL",
            "unit_name":UNIT,"text":unit_text(runtime,config_file),
            "activation_authorized":False}
def stage(config_file,install_prefix,units_dir,consent):
    if consent!=APPROVAL:raise PermissionError("Explicit service-file installation consent required")
    data=preview(config_file,install_prefix)
    config=load_paths(Path(config_file))
    unitdir=Path(units_dir).expanduser().absolute()
    if (not unitdir.is_dir() or unitdir.is_symlink()
        or unitdir.stat().st_mode & 0o077):
        raise PermissionError("Private existing unit directory required")
    # Avoid touching existing systemd user directory during test stage.
    if unitdir==Path.home()/".config/systemd/user":
        raise PermissionError("Live service directory needs a separate release gate")
    target=unitdir/UNIT
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            handle.write(data["text"]);handle.flush();os.fsync(handle.fileno())
    except BaseException:
        if target.is_file() and not target.is_symlink():target.unlink()
        raise
    return {"status":"STAGED_NOT_ENABLED","unit":str(target),"activation_authorized":False}
def remove(units_dir,expected_text):
    target=Path(units_dir).expanduser().absolute()/UNIT
    if target.is_symlink() or not target.is_file() or target.read_text()!=expected_text:
        raise ValueError("Unit modified or missing: refusing delete")
    target.unlink()
    return {"status":"STAGED_UNIT_REMOVED","activation_authorized":False}


TIMER = "proton-mvp-isolated-full.timer"


def timer_text():
    """Generate a valid 30-minute systemd timer (not enabled)."""
    return "\n".join((
        "[Unit]",
        "Description=Schedule isolated Proton Drive MVP sync",
        "",
        "[Timer]",
        f"Unit={UNIT}",
        "OnCalendar=*-*-* *:00,30:00",
        "Persistent=false",
        "AccuracySec=1min",
        "",
        "[Install]",
        "WantedBy=timers.target",
        "",
    ))

def stage_pair(config_file,install_prefix,units_dir,consent):
    """Stage service and timer together, without systemctl or activation."""
    if consent != APPROVAL:
        raise PermissionError("Explicit installation approval required")
    info=preview(config_file,install_prefix)
    directory=Path(units_dir).expanduser().absolute()
    if (not directory.is_dir() or directory.is_symlink()
        or directory.stat().st_mode & 0o077
        or directory == Path.home()/".config/systemd/user"):
        raise PermissionError("Private non-live unit directory required")
    contents={UNIT:info["text"],TIMER:timer_text()}
    for name in contents:
        target=directory/name
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Existing unit: {name}")
    created=[]
    try:
        for name,text in contents.items():
            target=directory/name
            fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            created.append(target)
            with os.fdopen(fd,"w",encoding="utf-8") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException:
        for target in created:
            if target.is_file() and not target.is_symlink():
                target.unlink()
        raise
    return {"status":"STAGED_SERVICE_AND_TIMER_NOT_ENABLED",
            "units":[str(directory/name) for name in contents],
            "activation_authorized":False}

def remove_pair(units_dir,expected_service):
    """Remove a staged pair only if both contents are exactly as expected."""
    directory=Path(units_dir).expanduser().absolute()
    content={UNIT:expected_service,TIMER:timer_text()}
    for name,expected in content.items():
        target=directory/name
        if target.is_symlink() or not target.is_file() or target.read_text()!=expected:
            raise ValueError(f"Refusing changed/missing unit: {name}")
    for name in content:
        (directory/name).unlink()
    return {"status":"STAGED_PAIR_REMOVED","activation_authorized":False}
