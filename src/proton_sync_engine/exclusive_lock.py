"""Exclusive process lock for pairing, recovery and portable runtime.

One stable lock inode inside a private state directory. Fail closed on
contention, nonregular files and unsafe permissions; never remove lock file.
"""
from __future__ import annotations
from contextlib import contextmanager
import errno
import fcntl
import os
import stat
from pathlib import Path

class PairingBusy(RuntimeError):
    pass

@contextmanager
def exclusive(state_dir):
    state=Path(state_dir)
    if not state.is_dir() or state.is_symlink() or state.stat().st_mode & 0o077:
        raise PermissionError("Private pairing state directory required")
    lock=state/"pairing_runtime.lock"
    if lock.is_symlink():
        raise PermissionError("Symlink pairing lock refused")
    fd=os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
    try:
        meta=os.fstat(fd)
        path_meta=lock.lstat()
        if (not stat.S_ISREG(meta.st_mode) or meta.st_mode & 0o077
            or (meta.st_dev,meta.st_ino)!=(path_meta.st_dev,path_meta.st_ino)):
            raise PermissionError("Unsafe pairing lock inode")
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in (errno.EAGAIN,errno.EWOULDBLOCK):
                raise PairingBusy("PAIRING_OR_RUNTIME_BUSY") from exc
            raise
        try:
            yield
        finally:
            fcntl.flock(fd,fcntl.LOCK_UN)
    finally:
        os.close(fd)
