"""Explicit fail-closed recovery for an interrupted first-start verification.

Never infer approval from a marker. The original pending review and baseline
must match two fresh local/cloud inventories. Recovery only removes an owned,
broken verified marker; the next first startup re-verifies and does no transfer.
No systemd operations or automatic retries.
"""
from __future__ import annotations
import hashlib
import json
import os
import stat
from datetime import datetime,timezone
from pathlib import Path
from . import initial_activation
from .exclusive_lock import exclusive

CONSENT="I APPROVE RECHECK OF INTERRUPTED FIRST START"

def _source(config,adapter):
    state=Path(config.state_dir)
    if not state.is_dir() or state.is_symlink() or state.stat().st_mode & 0o077:
        raise ValueError("Private state directory required")
    base=state/"baseline.json"
    pending=state/initial_activation.GUARD_FILE
    verified=state/"initial_pairing_verified.json"
    if any(path.is_symlink() for path in (base,pending,verified)):
        raise RuntimeError("UNSAFE_PAIRING_SYMLINK")
    if not (base.is_file() and pending.is_file() and verified.is_file()):
        raise RuntimeError("NOT_AN_INTERRUPTED_DOUBLE_MARKER_STATE")
    return base,pending,verified

def _inspect_unlocked(config,adapter):
    """Read-only preview: a double-marker state can be reviewed, not unlocked."""
    base,pending,verified=_source(config,adapter)
    initial_activation.check(config.local_root,config.managed_folders,
                             base,pending,adapter.scan,
                             adapter.remote_digest,adapter.meta_rev)
    mode=verified.stat().st_mode
    if not stat.S_ISREG(mode):
        raise RuntimeError("UNSAFE_VERIFIED_MARKER_TYPE")
    # Bind approval to the exact metadata and contents, including a partial
    # verification marker left behind by a crash.
    marker_bytes=verified.read_bytes()
    if len(marker_bytes)>256:
        raise RuntimeError("OVERSIZED_VERIFIED_MARKER")
    st=verified.stat()
    token=hashlib.sha256(
        b"INITIAL-RECOVERY-V1\0"+
        hashlib.sha256(base.read_bytes()).digest()+
        hashlib.sha256(pending.read_bytes()).digest()+
        hashlib.sha256(marker_bytes).digest()+
        str((st.st_dev,st.st_ino,st.st_mtime_ns)).encode()
    ).hexdigest()
    return {"status":"RECOVERY_REVIEW_REQUIRED","sha256":token,
            "action":"RECHECK_FIRST_START_ONLY","activation_authorized":False}

def _recover_unlocked(config,adapter,review,consent):
    """Explicit re-authorization for verification-only startup, not for syncing."""
    if consent!=CONSENT:
        raise PermissionError("Explicit recovery approval required")
    if (not isinstance(review,dict)
        or review.get("status")!="RECOVERY_REVIEW_REQUIRED"
        or review.get("action")!="RECHECK_FIRST_START_ONLY"
        or review.get("activation_authorized") is not False):
        raise ValueError("Invalid recovery review")
    previous=review.get("sha256")
    if not isinstance(previous,str) or len(previous)!=64:
        raise ValueError("Missing recovery binding")
    if _inspect_unlocked(config,adapter)["sha256"]!=previous:
        raise RuntimeError("RECOVERY_STALE_OR_CHANGED")
    base,pending,verified=_source(config,adapter)
    evidence=Path(config.state_dir)/"initial_pairing_recovery_evidence.json"
    if evidence.exists() or evidence.is_symlink():
        raise FileExistsError("RECOVERY_EVIDENCE_ALREADY_EXISTS")
    # Re-check directly before touching the marker; no state changes on drift.
    initial_activation.check(config.local_root,config.managed_folders,
                             base,pending,adapter.scan,
                             adapter.remote_digest,adapter.meta_rev)
    fd=os.open(verified,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        original=os.fstat(fd)
        current=verified.lstat()
        if (not stat.S_ISREG(original.st_mode)
            or (original.st_dev,original.st_ino)!=(current.st_dev,current.st_ino)
            or _inspect_unlocked(config,adapter)["sha256"]!=previous):
            raise RuntimeError("RECOVERY_MARKER_CHANGED")
        # Inode identity is rechecked. The baseline and pending guard are
        # preserved for the engine to verify again on the next startup.
        current=verified.lstat()
        if (current.st_dev,current.st_ino)!=(original.st_dev,original.st_ino):
            raise RuntimeError("RECOVERY_MARKER_REPLACED")
        # An exclusive, durable audit record is written BEFORE altering the
        # marker. If this crashes, the original double-marker state remains
        # blocked and the record prevents an unreviewed retry.
        evidence_data={
            "version":1,"action":"RECHECK_FIRST_START_ONLY",
            "review_sha256":previous,"timestamp_utc":datetime.now(timezone.utc).isoformat(),
            "activation_authorized":False,
        }
        efd=os.open(evidence,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(efd,"w",encoding="utf-8") as out:
            json.dump(evidence_data,out,sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
        verified.unlink()
    finally:
        os.close(fd)
    return {"status":"RECHECK_REQUIRED","activation_authorized":False,
            "next_action":"RUN_VERIFICATION_ONLY_FIRST_START"}

def inspect(config,adapter):
    with exclusive(config.state_dir):
        return _inspect_unlocked(config,adapter)

def recover(config,adapter,review,consent):
    with exclusive(config.state_dir):
        return _recover_unlocked(config,adapter,review,consent)
