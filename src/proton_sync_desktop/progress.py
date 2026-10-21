"""Safe presentation of genuine progress snapshots from the sync engine."""
from __future__ import annotations
import json
import time
from pathlib import Path

ALLOWED={"local","priority","full"}
PHASES={"tracked_files","file_comparison","cloud_inventory","new_files",
        "remaining_changes","finished"}

def interpret(record:dict|None,service_active:bool,now:float|None=None)->dict:
    """Return progress only for an active service with valid fresh counters.

    Never synthesize a percentage when total is unknown, nonpositive or stale.
    """
    if not service_active:return {"mode":"idle","fraction":None}
    if not isinstance(record,dict):return {"mode":"working","fraction":None,"phase":"unknown"}
    phase=record.get("phase")
    if phase not in PHASES or record.get("status")!="running":
        return {"mode":"working","fraction":None,"phase":"unknown"}
    age=(now if now is not None else time.time())-record.get("updated_at",0)
    if not 0<=age<=3600:return {"mode":"working","fraction":None,"phase":phase}
    done=record.get("done");total=record.get("total")
    if type(done)==int and type(total)==int and total>0 and 0<=done<=total:
        return {"mode":"measured","fraction":done/total,"done":done,"total":total,"phase":phase}
    return {"mode":"working","fraction":None,"phase":phase}

def read_progress(state:Path,kind:str,active:bool)->dict:
    """Read a progress file as metadata without accessing synchronized data."""
    if kind not in ALLOWED:raise ValueError("Invalid progress kind")
    try:
        record=json.loads((state/("progress_"+kind+".json")).read_text())
    except (OSError,ValueError):
        record=None
    return interpret(record,active)
