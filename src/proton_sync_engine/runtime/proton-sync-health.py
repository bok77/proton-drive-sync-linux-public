#!/usr/bin/env python3
"""Proton sync health and notification; does not modify synchronized documents."""
import datetime as dt
import json
import os
from pathlib import Path
from proton_sync_engine.portable_paths import paths as _load_runtime_paths
_runtime=_load_runtime_paths()
import shutil
import subprocess
import time

STATE=_runtime.state_dir
EVENTS=STATE/"events.jsonl"
HEALTH=STATE/"health.json"
ALERT=STATE/"last_alert.json"
PENDING=STATE/"pending_changes.json"

def last_runs():
    result={}
    if not EVENTS.exists(): return result
    for line in EVENTS.open(encoding="utf-8"):
        try: rec=json.loads(line)
        except json.JSONDecodeError:continue
        kind=rec.get("event")
        if kind in ("quick_run_end","run_end"):
            result[kind]=rec
    return result

def seconds_old(iso):
    try:
        when=dt.datetime.strptime(iso,"%Y-%m-%dT%H:%M:%S%z")
        return (dt.datetime.now(dt.timezone.utc)-when.astimezone(dt.timezone.utc)).total_seconds()
    except Exception:return None

def systemd_state(unit):
    p=subprocess.run(["systemctl","--user","is-active",unit],capture_output=True,text=True)
    return p.stdout.strip()

def main():
    STATE.mkdir(parents=True,exist_ok=True)
    results=last_runs();messages=[]
    quick=results.get("quick_run_end");full=results.get("run_end")
    for label,record,limit in (("Schnellabgleich",quick,3600),("Cloud-Vollabgleich",full,10800)):
        if record is None: messages.append(label+": kein erfolgreicher Abschluss bekannt")
        else:
            age=seconds_old(record.get("time",""))
            if age is None or age>limit:
                messages.append(label+": letzter Abschluss zu alt")
            if record.get("errors",0): messages.append(label+": "+str(record["errors"])+" Fehler")
            if record.get("conflicts",0): messages.append(label+": "+str(record["conflicts"])+" Konflikte")
    try:
        free=shutil.disk_usage(_runtime.mount_root).free
        if free < 5*1024**3:messages.append("Low free space at configured mount (< 5 GiB)")
    except OSError:messages.append("Unable to read space at configured mount")
    for unit in ("proton-bisync-quick.timer","proton-cloud-priority.timer","proton-bisync.timer"):
        if systemd_state(unit)!="active":messages.append(unit+": nicht aktiv")
    # An intentionally disabled watcher is a preference, not a broken service.
    enabled=subprocess.run(["systemctl","--user","is-enabled","proton-sync-watcher.service"],
                           capture_output=True,text=True).stdout.strip() in ("enabled","enabled-runtime")
    if enabled and systemd_state("proton-sync-watcher.service")!="active":
        messages.append("Dateiwächter unerwartet gestoppt; zeitgesteuerter Abgleich bleibt aktiv")
    try:
        import sqlite3
        q=STATE/"local_events.sqlite3"
        if q.exists():
            with sqlite3.connect(q,timeout=5) as c:
                pending_count,oldest=c.execute("SELECT COUNT(*),MIN(changed_at) FROM pending").fetchone()
                marker=c.execute("SELECT value FROM control WHERE key='needs_full_scan'").fetchone()
            if pending_count and oldest and time.time()-oldest>1800:
                messages.append("Lokale Ereignisse seit mehr als 30 Minuten unbearbeitet")
            if marker:
                messages.append("Watcher meldet Vollscanbedarf: "+str(marker[0])[:100])
    except Exception as ex:
        messages.append("Ereigniswarteschlange nicht lesbar: "+str(ex)[:100])
    if systemd_state("proton-bisync-quick.service")=="failed":
        messages.append("Schnellabgleich-Dienst fehlgeschlagen")
    if systemd_state("proton-bisync.service")=="failed":
        messages.append("Cloud-Vollabgleich-Dienst fehlgeschlagen")
    pending={}
    if PENDING.exists():
        try:
            pending=json.loads(PENDING.read_text())
            if pending.get("possible_deletions"): messages.append("Lokale Löschkandidaten erkannt")
            if pending.get("probable_renames"): messages.append("Umbenennungen zur Prüfung erkannt")
        except Exception:
            messages.append("Änderungsbericht kann nicht gelesen werden")
    status={"timestamp":dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds"),
            "healthy":len(messages)==0,"issues":messages,"quick":quick,"full":full,
            "pending":{"probable_renames":len(pending.get("probable_renames",[])),
                       "possible_deletions":len(pending.get("possible_deletions",[]))}}
    temp=HEALTH.with_suffix(".tmp")
    temp.write_text(json.dumps(status,ensure_ascii=False,indent=2))
    os.replace(temp,HEALTH)
    signature="\n".join(sorted(messages))
    previous={}
    if ALERT.exists():
        try:previous=json.loads(ALERT.read_text())
        except (ValueError,OSError):pass
    if messages and (signature!=previous.get("signature") or time.time()-previous.get("timestamp",0)>21600):
        print("WARN:", "; ".join(messages),flush=True)
        if shutil.which("notify-send"):
            subprocess.run(["notify-send","-u","normal","Proton Drive Sync: Prüfung nötig",
                            "; ".join(messages)[:300]],capture_output=True,timeout=10,check=False)
        ALERT.write_text(json.dumps({"signature":signature,"timestamp":time.time()}))
    else:
        print("OK" if not messages else "WARN (already notified): "+"; ".join(messages),flush=True)
    if not messages and previous.get("signature"):
        ALERT.write_text(json.dumps({"signature":"","timestamp":time.time()}))
    return 0 if not messages else 1

if __name__=="__main__":raise SystemExit(main())
