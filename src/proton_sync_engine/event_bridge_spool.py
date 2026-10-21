"""Isolated SDK event-batch spool prototype, no network or production sync.

A pending batch never advances a verified cursor; recovery requires human review.
"""
from __future__ import annotations
from pathlib import Path
import json, os, stat, tempfile
from .event_cursor_contract import validate_batch, EventCursorBlocked

class BridgeBlocked(RuntimeError):
    pass


def _state_dir(root: Path):
    root=Path(root)
    if root.is_symlink() or not root.is_dir() or root.stat().st_mode & 0o077:
        raise BridgeBlocked('unsafe_bridge_directory')
    return root


def _read(root, filename):
    p=root/filename
    if p.is_symlink():raise BridgeBlocked('unsafe_bridge_state')
    if not p.exists():return None
    s=p.stat()
    if not stat.S_ISREG(s.st_mode) or s.st_mode & 0o077:
        raise BridgeBlocked('unsafe_bridge_state')
    try:return json.loads(p.read_text())
    except (ValueError,OSError) as exc:raise BridgeBlocked('corrupt_bridge_state') from exc


def _write(root, filename, record):
    fd,name=tempfile.mkstemp(prefix='.event-',dir=root)
    try:
        with os.fdopen(fd,'w') as f:
            os.fchmod(f.fileno(),0o600)
            json.dump(record,f)
            f.flush();os.fsync(f.fileno())
        os.replace(name,root/filename)
        dirfd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(dirfd)
        finally:os.close(dirfd)
    finally:
        if os.path.exists(name):os.unlink(name)


def stage_batch(root: Path, scope: str, events: list[dict]):
    root=_state_dir(root)
    if _read(root,'pending.json') is not None:raise BridgeBlocked('pending_batch_requires_review')
    cursor=_read(root,'cursor.json')
    if not isinstance(cursor,dict) or cursor.get('scope') != scope:
        raise BridgeBlocked('missing_or_mismatched_cursor')
    try:batch=validate_batch(scope,cursor.get('event_id'),events)
    except EventCursorBlocked as exc:raise BridgeBlocked(str(exc)) from exc
    if not events:return batch
    # No cursor advancement. A later processor must establish durable verified effects.
    _write(root,'pending.json',{'scope':scope,'previous':batch.previous_cursor,
                               'next':batch.next_cursor,'node_ids':list(batch.node_ids)})
    return batch


def initialize_cursor(root:Path,scope:str,event_id:str):
    root=_state_dir(root)
    if not scope or not event_id or _read(root,'cursor.json') is not None or _read(root,'pending.json') is not None:
        raise BridgeBlocked('cursor_initialization_refused')
    _write(root,'cursor.json',{'scope':scope,'event_id':event_id})
