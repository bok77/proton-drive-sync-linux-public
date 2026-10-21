"""First activation gate: no reconciliation until exact approved snapshot agrees.

The gate is conservative and read-only. It is *not* a cross-system transaction:
a subsequent concurrent change remains possible and production activation is
separately forbidden.
"""
from __future__ import annotations
import json
from pathlib import Path
from . import pairing

GUARD_FILE="initial_pairing_pending.json"

def check(root,managed,baseline_path,guard_path,scan,remote_digest,meta_rev):
    baseline_path=Path(baseline_path)
    guard_path=Path(guard_path)
    if not guard_path.is_file() or guard_path.is_symlink():
        raise RuntimeError("INITIAL_PAIRING_GUARD_MISSING")
    if not baseline_path.is_file() or baseline_path.is_symlink():
        raise RuntimeError("INITIAL_BASELINE_MISSING")
    guard=json.loads(guard_path.read_text())
    baseline=json.loads(baseline_path.read_text())
    if not isinstance(guard,dict) or guard.get("version")!=1:
        raise RuntimeError("INITIAL_GUARD_MALFORMED")
    if not isinstance(baseline,dict) or not baseline:
        raise RuntimeError("INITIAL_BASELINE_MALFORMED")
    report=pairing.compare(root,managed,scan,remote_digest,meta_rev)
    if report["status"]!="READY_FOR_EXPLICIT_APPROVAL":
        raise RuntimeError("INITIAL_PAIRING_CHANGED_OR_CONFLICT")
    if (report["sha256"]!=guard.get("sha256")
        or report["baseline"]!=baseline
        or report["matched"]!=guard.get("matched")):
        raise RuntimeError("INITIAL_PAIRING_REVISION_MISMATCH")
    return {"status":"INITIAL_PAIRING_VERIFIED","matched":report["matched"]}

def pending_guard_data(review):
    if (not isinstance(review,dict)
        or review.get("status")!="READY_FOR_EXPLICIT_APPROVAL"
        or not isinstance(review.get("sha256"),str)
        or len(review["sha256"])!=64
        or not isinstance(review.get("matched"),int)
        or review["matched"]<1):
        raise ValueError("Invalid initial pairing review")
    return {"version":1,"sha256":review["sha256"],"matched":review["matched"]}
