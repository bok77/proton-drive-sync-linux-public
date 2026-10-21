"""Read-only systemd and sync-state adapter. Does not inspect user documents."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import re
from datetime import datetime

HOME=Path.home()
STATE=HOME/".local/state/proton-bisync"
CONFIG=HOME/".config/proton-bisync/settings.json"
ROOT=Path("/mnt/example-sync-root")
UNITS={
"watcher":"proton-sync-watcher.service",
"local_timer":"proton-bisync-quick.timer",
"cloud_timer":"proton-cloud-priority.timer",
"full_timer":"proton-bisync.timer",
"health_timer":"proton-sync-health.timer",
}
ALLOWED_EVENTS={
"quick_run_end","run_end","priority_run_end","reconcile_run_end",
"quick_uploaded_verified","quick_new_uploaded_verified","priority_downloaded_verified",
"reconcile_renamed_verified","reconcile_trashed","conflict","upload_error","download_error",
"cloud_removed_local_quarantined","watcher_trigger","reconcile_error",
}
def read_json(path:Path,default=None):
    """Read an optional JSON state file without treating missing data as healthy."""
    if default is None:default={}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError,ValueError,PermissionError):
        return default

def service_active(name):
    """Return True only when the specified systemd user unit is active."""
    try:
        result=subprocess.run(["systemctl","--user","is-active",name],
            capture_output=True,text=True,timeout=3,check=False)
        return result.returncode==0 and result.stdout.strip()=="active"
    except (OSError,subprocess.TimeoutExpired):
        return False

def next_full_sync_schedule():
    """Read systemd's real next full-scan trigger; never infer from an interval.

    Return a local date+time string (YYYY-MM-DD HH:MM) or None when the timer
    is disabled, missing, inactive, or systemd has no next trigger.
    """
    if not service_active("proton-bisync.timer"):
        return None
    try:
        result=subprocess.run(
            ["systemctl","--user","show","proton-bisync.timer",
             "-p","NextElapseUSecRealtime","--value"],
            capture_output=True,text=True,timeout=5,check=False)
        if result.returncode:
            return None
        match=re.search(r"\b(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}):\d{2}\b",
                        result.stdout)
        if not match:
            return None
        # Reject invalid calendar dates even if systemd returns unexpected text.
        datetime.strptime(match.group(1)+" "+match.group(2),"%Y-%m-%d %H:%M")
        return match.group(1)+" "+match.group(2)
    except (OSError,ValueError,subprocess.TimeoutExpired):
        return None


def verified_full_success(record):
    """Extract only a completed, conflict-free full run from health evidence.

    Timer state and mere initiation are never evidence of a successful sync.
    """
    if not isinstance(record,dict) or record.get("event")!="run_end":
        return None
    if record.get("errors")!=0 or record.get("conflicts")!=0:
        return None
    if type(record.get("tracked")) is not int or record["tracked"]<=0:
        return None
    try:
        when=datetime.strptime(record["time"],"%Y-%m-%dT%H:%M:%S%z")
    except (TypeError,KeyError,ValueError):
        return None
    return when


def count_pending():
    """Read pending inotify queue length using a read-only SQLite connection."""
    db=STATE/"local_events.sqlite3"
    if not db.exists():return 0
    try:
        with sqlite3.connect(f"file:{db}?mode=ro",uri=True,timeout=2) as con:
            return int(con.execute("SELECT COUNT(*) FROM pending").fetchone()[0])
    except (sqlite3.Error,OSError):
        return None

def latest_events(limit=18):
    """Read a bounded tail of the event journal, ignoring unsupported records."""
    p=STATE/"events.jsonl"
    if not p.exists():return []
    try:
        # Only inspect last 256 KiB. Avoid unbounded GUI memory consumption.
        with p.open("rb") as f:
            f.seek(0,os.SEEK_END);size=f.tell();f.seek(max(0,size-262144))
            raw=f.read().decode("utf-8",errors="replace")
        lines=raw.splitlines()
        if size>262144:lines=lines[1:]
        events=[]
        for line in lines:
            try:
                event=json.loads(line)
                if event.get("event") in ALLOWED_EVENTS:events.append(event)
            except ValueError:continue
        return events[-limit:][::-1]
    except (OSError,PermissionError):
        return []

def last_successful_full_record(full, events):
    """Retain the latest *successful* run even when the newest run failed.

    Failed, unfinished or conflicted runs cannot replace the last verified
    success shown in the dashboard.
    """
    candidates=[full]+[entry for entry in events if entry.get("event")=="run_end"]
    valid=[(verified_full_success(record),record) for record in candidates]
    valid=[(when,record) for when,record in valid if when is not None]
    if not valid:
        return None
    return max(valid,key=lambda item:item[0])[1]


def snapshot():
    """Collect GUI-safe metadata without reading any personal file contents."""
    health=read_json(STATE/"health.json")
    baseline=read_json(STATE/"baseline.json")
    rename=read_json(STATE/"reconcile_candidates.json")
    remote=read_json(STATE/"remote_missing_candidates.json")
    events=latest_events(200)
    last_success=last_successful_full_record(health.get("full") or {},events)
    priority=next((e for e in events if e.get("event")=="priority_run_end"),{})
    quick=health.get("quick") or {}
    full=health.get("full") or {}
    return {
        "healthy":health.get("healthy"),
        "issues":health.get("issues",[]),
        "tracked":len(baseline),
        "pending":count_pending(),
        "pending_deletes":len(rename)+len(remote),
        "quick":quick,
        "full":full,
        "full_last_success":verified_full_success(last_success) if last_success else None,
        "full_next_scheduled":next_full_sync_schedule(),
        "full_running":service_active("proton-bisync.service"),
        "priority":priority,
        "events":events[:20],
        "services":{key:service_active(unit) for key,unit in UNITS.items()},
        "captured_at":datetime.now().astimezone().strftime("%H:%M:%S"),
    }

def settings():
    """Load user-controlled exclusion settings or a non-destructive default."""
    return read_json(CONFIG,{"version":1,"exclusions":{"file_patterns":[],"directory_names":[],"custom_relative_prefixes":[]}})

def save_exclusions(patterns,dirs):
    """Atomically store safe new-file exclusions; reject invalid directory paths."""
    for value in patterns+dirs:
        if len(value)>256 or "\0" in value or "\n" in value:raise ValueError("Invalid exclusion entry")
    if any("/" in v or "\\" in v or v in (".","..") for v in dirs):
        raise ValueError("Invalid directory name")
    current=settings()
    exclusions=current.setdefault("exclusions",{})
    exclusions["file_patterns"]=patterns
    exclusions["directory_names"]=dirs
    CONFIG.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    import tempfile
    fd,temp=tempfile.mkstemp(prefix=".settings-",dir=CONFIG.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(current,f,ensure_ascii=False,indent=2)
            f.flush();os.fsync(f.fileno())
        os.chmod(temp,0o600)
        os.replace(temp,CONFIG)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def request_local_sync():
    """Ask systemd to start the existing guarded local upload/reconcile cycle."""
    return subprocess.run(["systemctl","--user","start","--no-block",
           "proton-bisync-quick.service"],capture_output=True,text=True,timeout=6)

def restart_watcher():
    """Reload changed exclusion rules only if the user enabled monitoring.

    An intentional OFF setting must never be overridden by saving settings.
    """
    if not watcher_enabled():
        return subprocess.CompletedProcess(args=[],returncode=0,stdout="",stderr="")
    return subprocess.run(["systemctl","--user","restart","--no-block",
           "proton-sync-watcher.service"],capture_output=True,text=True,timeout=6)

def watcher_enabled():
    """Check the persistent user choice, distinct from service health."""
    try:
        result=subprocess.run(["systemctl","--user","is-enabled",
                               "proton-sync-watcher.service"],
                              capture_output=True,text=True,timeout=5)
        return result.returncode==0 and result.stdout.strip() in ("enabled","enabled-runtime")
    except (OSError,subprocess.TimeoutExpired):
        return False

def set_watcher_enabled(enabled:bool):
    """Apply an explicit ON/OFF choice to the persistent systemd user service.

    The five-minute fallback and all cloud timers are left untouched.
    A successful return requires reading back both desired and active states.
    """
    if type(enabled) is not bool:
        raise ValueError("Watcher choice must be a boolean")
    command=["systemctl","--user","enable" if enabled else "disable",
             "--now","proton-sync-watcher.service"]
    result=subprocess.run(command,capture_output=True,text=True,timeout=20)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Watcher configuration failed")
    actual_enabled=watcher_enabled()
    actual_active=service_active("proton-sync-watcher.service")
    if actual_enabled!=enabled or actual_active!=enabled:
        raise RuntimeError("Watcher state readback did not match requested setting")
    return {"enabled":actual_enabled,"active":actual_active}


def request_full_sync():
    """Start the existing full bidirectional cloud scan without bypassing its lock.

    The systemd service retains mount safety checks and serializes against
    local and priority services. Returns CompletedProcess, not proof of completion.
    """
    return subprocess.run(["systemctl", "--user", "start", "--no-block",
                           "proton-bisync.service"], capture_output=True,
                          text=True, timeout=6)


def list_cloud_directories(path="/my-files"):
    """List decrypted Proton cloud subfolders without changing any files.

    Returns a sequence of verified (display name, absolute cloud path). The
    chooser never trusts names that contain path separators or dot traversal.
    """
    from . import routing
    if path != "/my-files":
        routing.validate_folder(path)
    cli=HOME/".local/bin/proton-drive"
    if not cli.is_file():raise RuntimeError("Official Proton Drive CLI not installed")
    response=subprocess.run([str(cli),"filesystem","list",path,"-j"],
        capture_output=True,text=True,timeout=35)
    if response.returncode:
        raise RuntimeError("Could not list cloud folder")
    items=json.loads(response.stdout)
    if not isinstance(items,list):raise ValueError("Invalid cloud directory list")
    results=[]
    for item in items:
        if item.get("type")!="folder":continue
        name=item.get("name") or {}
        if not name.get("ok"):continue
        value=name.get("value")
        if not isinstance(value,str) or value in (".","..") or "/" in value or "\\" in value:continue
        prefix=path.rstrip("/")+"/"+value
        try:routing.validate_folder(prefix)
        except ValueError:continue
        results.append((value,prefix))
    return sorted(results,key=lambda entry:entry[0].casefold())


def verify_cloud_directories(folders):
    """Reject nonexistent or non-folder cloud selections before applying a route.

    This is a read-only CLI preflight; it never creates, moves or deletes data.
    """
    from . import routing
    cli=HOME/".local/bin/proton-drive"
    if not cli.is_file():raise RuntimeError("Proton CLI not available")
    for folder in folders:
        relative=routing.validate_folder(folder)
        command=[str(cli),"filesystem","info","/my-files/"+relative,"-j"]
        result=subprocess.run(command,capture_output=True,text=True,timeout=25)
        if result.returncode:raise ValueError("Cloud folder not found: "+relative)
        info=json.loads(result.stdout)
        if info.get("type")!="folder":raise ValueError("Not a cloud folder: "+relative)
    return True


def request_priority_sync():
    """Request existing priority cloud scanner; never bypass the shared sync lock."""
    return subprocess.run(["systemctl","--user","start","--no-block",
                           "proton-cloud-priority.service"],
                          capture_output=True,text=True,timeout=6)


CLOUD_TIMERS=("proton-cloud-priority.timer","proton-bisync.timer")

def cloud_monitor_enabled():
    """Return True only if both periodic cloud timer units are enabled and active."""
    for unit in CLOUD_TIMERS:
        enabled=subprocess.run(["systemctl","--user","is-enabled",unit],
                               capture_output=True,text=True,timeout=5)
        if enabled.returncode or enabled.stdout.strip() not in ("enabled","enabled-runtime"):
            return False
        if not service_active(unit):
            return False
    return True


def set_cloud_monitor_enabled(enabled:bool):
    """Enable or disable both cloud timers together with rollback on failures.

    Changes only future scheduling, not running jobs or the Linux event watcher.
    Confirm each unit through systemd readback before reporting success.
    """
    if type(enabled) is not bool:
        raise ValueError("Cloud monitoring choice must be boolean")
    original={}
    for unit in CLOUD_TIMERS:
        check=subprocess.run(["systemctl","--user","is-enabled",unit],
                             capture_output=True,text=True,timeout=5)
        original[unit]=check.returncode==0 and check.stdout.strip() in ("enabled","enabled-runtime")
    try:
        for unit in CLOUD_TIMERS:
            result=subprocess.run(["systemctl","--user","enable" if enabled else "disable",
                                   "--now",unit],capture_output=True,text=True,timeout=20)
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or "Failed to configure "+unit)
        if cloud_monitor_enabled()!=enabled:
            raise RuntimeError("Cloud monitoring readback mismatch")
        return {"enabled":enabled,"active":enabled}
    except Exception:
        for unit,was_enabled in original.items():
            subprocess.run(["systemctl","--user","enable" if was_enabled else "disable",
                            "--now",unit],capture_output=True,text=True,timeout=20)
        raise


def read_change_preview():
    """Read an existing offline local-change report; never initiate sync or deletion."""
    report=read_json(STATE/"pending_changes.json")
    return {
        "checked_at":report.get("checked_at"),
        "new_local":report.get("new_local",0),
        "possible_deletions":report.get("possible_deletions",[]),
        "probable_renames":report.get("probable_renames",[]),
        "unmatched_new":report.get("unmatched_new",[]),
        "cloud_changes_included":False,
    }


def create_change_preview():
    """Read-only, full two-way inventory preview.

    Uses the production cloud scanner but does not call upload/download/trash.
    The result is not approval to apply because filesystem and cloud states
    may change after analysis.
    """
    script=HOME/"Projekte/proton-drive-sync-linux/scripts/preview_bidirectional.py"
    result=subprocess.run(["/usr/bin/python3",str(script)],
                          capture_output=True,text=True,timeout=3600)
    if result.returncode:
        raise RuntimeError("Bidirectional preview blocked: "+result.stderr[-350:])
    report=read_json(STATE/"bidirectional_preview.json")
    if not (report.get("read_only") is True and report.get("complete_inventory") is True
            and report.get("cloud_changes_included") is True
            and isinstance(report.get("changes"),list)):
        raise RuntimeError("Preview report missing or incomplete")
    return report
