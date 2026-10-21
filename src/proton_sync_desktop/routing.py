"""Validated editable sync settings without changing the established root or baseline.

The authoritative bidirectional mapping stays /my-files <-> /mnt/example-sync-root.
Users may configure additional priority cloud subfolders and periodic timer
cadences. All writes require strict validation and readback; never mutate
the baseline, move user documents or silently widen deletion scope.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

CONFIG=Path.home()/".config/proton-bisync/routing.json"
ROOT=Path("/mnt/example-sync-root")
REMOTE_ROOT="/my-files"
DEFAULT={
    "version":1,
    "local_root":str(ROOT),
    "remote_root":REMOTE_ROOT,
    "priority_cloud_folders":["00_Inbox","40_Knowledge/example-workflow/Current"],
    "interval_minutes":{"local":5,"priority":10,"full":60},
}
SUPPORTED={
    "local":(5,10,15,30),
    "priority":(5,10,15,30,60),
    "full":(30,60,120,180),
}
SERVICES={
    "local":"proton-bisync-quick.timer",
    "priority":"proton-cloud-priority.timer",
    "full":"proton-bisync.timer",
}

def validate_folder(raw:str)->str:
    """Accept only a cloud subfolder within /my-files with safe path components."""
    if not isinstance(raw,str):raise ValueError("Folder must be text")
    value=raw.strip().replace("\\","/")
    if value.startswith("/my-files/"):
        value=value[len("/my-files/"):]
    elif value.startswith("/"):
        raise ValueError("Use a subfolder of /my-files")
    if not value or len(value)>400:
        raise ValueError("Choose a non-empty cloud subfolder")
    parts=value.split("/")
    if any(p in ("",".","..") or len(p)>120 or "\x00" in p for p in parts):
        raise ValueError("Unsafe folder path")
    return "/".join(parts)

def validate(data:dict)->dict:
    """Return a normalized routing config and reject unsafe root or schedule drift."""
    if not isinstance(data,dict) or data.get("version")!=1:
        raise ValueError("Unsupported routing schema")
    if data.get("local_root")!=str(ROOT) or data.get("remote_root")!=REMOTE_ROOT:
        raise ValueError("Root migration requires a separate verified migration")
    raw=data.get("priority_cloud_folders")
    if not isinstance(raw,list) or not raw or len(raw)>12:
        raise ValueError("Configure between 1 and 12 priority folders")
    folders=[validate_folder(v) for v in raw]
    if len(set(folders))!=len(folders):raise ValueError("Duplicate priority folder")
    cadence=data.get("interval_minutes")
    if not isinstance(cadence,dict):raise ValueError("Missing intervals")
    result={}
    for key,values in SUPPORTED.items():
        n=cadence.get(key)
        if type(n) is not int or n not in values:raise ValueError("Unsupported interval for "+key)
        result[key]=n
    return {**DEFAULT,"priority_cloud_folders":folders,"interval_minutes":result}

def load()->dict:
    """Read the stored plan; missing settings preserve current operational defaults."""
    if not CONFIG.exists():return validate(DEFAULT)
    return validate(json.loads(CONFIG.read_text(encoding="utf-8")))

def atomic_write(path:Path,data:dict):
    """Write a private UTF-8 JSON config atomically to the same filesystem."""
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,temp=tempfile.mkstemp(prefix=".routing-",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as out:
            json.dump(data,out,ensure_ascii=False,indent=2)
            out.flush();os.fsync(out.fileno())
        os.chmod(temp,0o600);os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def calendar_expression(minutes:int)->str:
    """Provide verified systemd OnCalendar syntax for a supported cadence."""
    if minutes==60:return "hourly"
    if minutes==120:return "*-*-* 00/2:00:00"
    if minutes==180:return "*-*-* 00/3:00:00"
    if minutes not in (5,10,15,30):raise ValueError("Unsupported frequency")
    return f"*-*-* *:0/{minutes}:00"

def timer_text(name:str,minutes:int)->str:
    """Generate one user timer with the original unit semantics intact."""
    if name not in SERVICES or minutes not in SUPPORTED[name]:
        raise ValueError("Unsupported timer")
    title={"local":"Local file changes","priority":"Priority cloud changes","full":"Full cloud scan"}[name]
    return ("[Unit]\nDescription="+title+"\n\n[Timer]\nOnCalendar="+calendar_expression(minutes)+
            "\nPersistent=true\nRandomizedDelaySec=15s\nUnit="+SERVICES[name].replace(".timer",".service")+
            "\n\n[Install]\nWantedBy=timers.target\n")

def apply(new_data:dict,executor=subprocess.run)->dict:
    """Apply validated intervals to systemd without changing content or mapping.

    Write all three timer units after generating them, validate with
    systemd-analyze, reload and restart; on failure restore previous files and
    config. The sync baseline is never touched.
    """
    new=validate(new_data)
    old=load()
    unit_dir=Path.home()/".config/systemd/user"
    changes={}
    for name,unit in SERVICES.items():
        path=unit_dir/unit
        changes[path]=path.read_text(encoding="utf-8") if path.exists() else None
    units={unit_dir/SERVICES[name]:timer_text(name,new["interval_minutes"][name]) for name in SERVICES}
    try:
        for path,content in units.items():
            path.write_text(content,encoding="utf-8")
        cmd=executor(["systemctl","--user","daemon-reload"],capture_output=True,text=True,timeout=15)
        if cmd.returncode:raise RuntimeError("systemd reload failed")
        for unit in SERVICES.values():
            cmd=executor(["systemctl","--user","restart",unit],capture_output=True,text=True,timeout=20)
            if cmd.returncode:raise RuntimeError("Timer restart failed: "+unit)
        atomic_write(CONFIG,new)
        if load()!=new:raise RuntimeError("Config readback mismatch")
        return new
    except Exception:
        for path,content in changes.items():
            if content is None:path.unlink(missing_ok=True)
            else:path.write_text(content,encoding="utf-8")
        try:
            executor(["systemctl","--user","daemon-reload"],capture_output=True,text=True,timeout=15)
            for unit in SERVICES.values():
                executor(["systemctl","--user","restart",unit],capture_output=True,text=True,timeout=20)
        except Exception:pass
        atomic_write(CONFIG,old)
        raise
