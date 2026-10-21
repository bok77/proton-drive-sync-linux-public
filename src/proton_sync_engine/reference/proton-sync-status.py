#!/usr/bin/env python3
"""Compact human-readable status for Proton Drive bidirectional synchronization."""
import datetime,json,subprocess
from pathlib import Path
STATE=Path.home()/".local/state/proton-bisync"
def read(name):
    try:return json.loads((STATE/name).read_text())
    except (OSError,ValueError):return {}
def state(unit):
    p=subprocess.run(["systemctl","--user","is-active",unit],capture_output=True,text=True)
    return p.stdout.strip()
def time_label(rec):
    if not rec:return "noch kein Abschluss"
    return rec.get("time","unbekannt")
h=read("health.json")
pending=read("pending_changes.json")
base=read("baseline.json")
print("PROTON DRIVE ↔ FEDORA")
print("Cloud-Ablage:  /mnt/example-sync-root")
print("Baseline:     ",len(base),"Dateien")
print("Gesundheit:   ","OK" if h.get("healthy") else "PRÜFEN ("+"; ".join(h.get("issues",["noch keine Messung"]))+")")
for label,key in (("Fedora → Cloud","quick"),("Cloud ↔ Fedora","full")):
    rec=h.get(key) or {}
    print(label+":",time_label(rec))
    if rec:
        print("  ",", ".join(f"{k}: {rec[k]}" for k in ("checked","hashes","uploaded","remote_downloaded","conflicts","errors") if k in rec))
print("Echtzeit-Watcher:",state("proton-sync-watcher.service"))
q=subprocess.run(["/usr/bin/python3",str(Path.home()/".local/bin/proton-sync-queue.py"),"stats"],capture_output=True,text=True)
print("Ausstehende Dateisystem-Ereignisse:",q.stdout.strip() if q.returncode==0 else "unbekannt")
print("Ausschlusskonfiguration:",Path.home()/".config/proton-bisync/settings.json")
print("Lokale Löschkandidaten:",len(pending.get("possible_deletions",[])))
print("Mögliche Umbenennungen:",len(pending.get("probable_renames",[])))
print("Cloud-Papierkorb: nach 24 h und 3 bestätigten Prüfungen; endgültiges Löschen AUS")
reconcile=read("reconcile_candidates.json")
print("Ausstehende lokale Lösch-/Umbenennungsvorgänge:",len(reconcile))
remote=read("remote_missing_candidates.json")
print("Cloud-seitig fehlende Dateien zur Quarantäneprüfung:",len(remote))
print("Lokale Quarantäne: /mnt/example-sync-quarantine")
for unit in ("proton-bisync-quick.timer","proton-cloud-priority.timer","proton-bisync.timer","proton-sync-health.timer"):
    print(unit+":",state(unit))
print("Detailberichte:",STATE)
