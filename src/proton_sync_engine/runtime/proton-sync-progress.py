"""Atomic per-run progress snapshots for local, priority and full sync.

Only actual completed-item counters are reported. A percentage always describes
a named bounded phase, never an invented estimate of overall completion.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from proton_sync_engine.portable_paths import paths as _load_runtime_paths
_runtime=_load_runtime_paths()
import tempfile
import time

STATE=_runtime.state_dir
ALLOWED={"local","priority","full"}
def update(kind:str,phase:str,done:int|None=None,total:int|None=None,
           *,status:str="running"):
    """Write a private progress snapshot and validate bounded counters.

    Unknown totals must be None. This method never touches synchronized data.
    """
    if kind not in ALLOWED:raise ValueError("unknown sync kind")
    if status not in ("running","complete","error"):raise ValueError("invalid status")
    if total is not None and (type(total)!=int or total<0):raise ValueError("invalid total")
    if done is not None and (type(done)!=int or done<0):raise ValueError("invalid done")
    if total is not None and done is not None and done>total:
        raise ValueError("done cannot exceed total")
    STATE.mkdir(parents=True,exist_ok=True,mode=0o700)
    state={"kind":kind,"phase":phase,"done":done,"total":total,
           "status":status,"updated_at":time.time(),"pid":os.getpid()}
    dest=STATE/("progress_"+kind+".json")
    fd,name=tempfile.mkstemp(prefix=".progress-",dir=STATE)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as file:
            json.dump(state,file,ensure_ascii=False)
            file.flush();os.fsync(file.fileno())
        os.chmod(name,0o600)
        os.replace(name,dest)
    finally:
        if os.path.exists(name):os.unlink(name)
    return state
