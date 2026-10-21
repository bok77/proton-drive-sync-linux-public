#!/usr/bin/env python3
"""Recursive Linux inotify watcher, persistent queue and debounced systemd dispatch."""
import ctypes, ctypes.util, errno, importlib.util, json, os, select, sqlite3, struct, subprocess, sys, time
from pathlib import Path

ROOT=Path("/mnt/example-sync-root")
STATE=Path.home()/".local/state/proton-bisync"
DB=STATE/"local_events.sqlite3"
SPEC=importlib.util.spec_from_file_location("sync_exclude",str(Path.home()/".local/bin/proton-sync-exclusions.py"))
ex=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(ex)
CFG=ex.settings()["watcher"]
FOLDERS=("00_Inbox","10_Private","20_Records","30_Learning",
         "40_Knowledge","50_Projects","60_Media","70_Backups",
         "80_Vault","90_Archive")
IN_MODIFY=0x2; IN_ATTRIB=0x4; IN_CLOSE_WRITE=0x8; IN_MOVED_FROM=0x40
IN_MOVED_TO=0x80; IN_CREATE=0x100; IN_DELETE=0x200; IN_DELETE_SELF=0x400
IN_MOVE_SELF=0x800; IN_UNMOUNT=0x2000; IN_Q_OVERFLOW=0x4000; IN_IGNORED=0x8000
IN_ONLYDIR=0x1000000; IN_ISDIR=0x40000000
MASK=IN_CLOSE_WRITE|IN_MOVED_FROM|IN_MOVED_TO|IN_CREATE|IN_DELETE|IN_DELETE_SELF|IN_MOVE_SELF|IN_UNMOUNT
libc=ctypes.CDLL(ctypes.util.find_library("c"),use_errno=True)
libc.inotify_init1.argtypes=[ctypes.c_int];libc.inotify_init1.restype=ctypes.c_int
libc.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32];libc.inotify_add_watch.restype=ctypes.c_int
libc.inotify_rm_watch.argtypes=[ctypes.c_int,ctypes.c_int];libc.inotify_rm_watch.restype=ctypes.c_int

def dbopen():
    STATE.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=15,isolation_level=None)
    db.execute("PRAGMA busy_timeout=15000")
    db.execute("CREATE TABLE IF NOT EXISTS pending (folder TEXT PRIMARY KEY, changed_at REAL NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS control (key TEXT PRIMARY KEY,value TEXT NOT NULL)")
    return db

def put(db,rel):
    db.execute("INSERT INTO pending(folder,changed_at) VALUES(?,?) ON CONFLICT(folder) DO UPDATE SET changed_at=excluded.changed_at",
               (rel,time.time()))

def special(db,reason):
    db.execute("INSERT OR REPLACE INTO control(key,value) VALUES('needs_full_scan',?)",(reason,))
    put(db,".")

def dispatch(db):
    rows=db.execute("SELECT COUNT(*), MIN(changed_at) FROM pending").fetchone()
    count,oldest=rows
    if not count:return
    if count>int(CFG["max_queued_directories"]):
        special(db,"queue_size_exceeded")
    if time.time()-oldest<float(CFG["debounce_seconds"]):return
    # Best-effort trigger; queue is NOT deleted by the watcher.
    p=subprocess.run(["systemctl","--user","start","--no-block","proton-bisync-quick.service"],
                     capture_output=True,text=True,timeout=12)
    if p.returncode:
        print("WATCHER_TRIGGER_FAILED",p.stderr[-180:],flush=True)
    else:
        print("WATCHER_DISPATCH",count,flush=True)

def main():
    if subprocess.run(["mountpoint","-q","/mnt/example-drive"]).returncode:raise RuntimeError("/mnt/example-drive unavailable")
    db=dbopen()
    fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
    if fd<0:raise OSError(ctypes.get_errno(),"inotify_init1 failed")
    watched={}
    def add(p):
        if p.is_symlink() or not p.is_dir():return
        rel=p.relative_to(ROOT).as_posix()
        if ex.excluded(rel,directory=True):return
        w=libc.inotify_add_watch(fd,os.fsencode(str(p)),MASK|IN_ONLYDIR)
        if w<0:
            special(db,"cannot_watch_directory")
            return
        watched[w]=p
    def walk(start):
        for directory,dirs,_ in os.walk(start,followlinks=False):
            d=Path(directory)
            dirs[:]=[name for name in dirs if not (d/name).is_symlink() and
                     not ex.excluded((d/name).relative_to(ROOT).as_posix(),directory=True)]
            add(d)
            if len(watched)>int(CFG["max_directories"]):
                special(db,"watch_limit_exceeded")
                raise RuntimeError("configured watch limit exceeded")
    for folder in FOLDERS:
        p=ROOT/folder
        if p.is_dir():walk(p)
    print("WATCHER_READY",len(watched),"folders",flush=True)
    last_dispatch=0
    while True:
        ready,_,_=select.select([fd],[],[],float(CFG["check_interval_seconds"]))
        if ready:
            while True:
                try:raw=os.read(fd,262144)
                except BlockingIOError:break
                if not raw:break
                off=0
                while off+16<=len(raw):
                    wd,mask,cookie,length=struct.unpack_from("iIII",raw,off);off+=16
                    name=raw[off:off+length].split(b"\0",1)[0];off+=length
                    if mask&IN_Q_OVERFLOW:
                        special(db,"inotify_queue_overflow");continue
                    parent=watched.get(wd)
                    if parent is None:continue
                    target=parent/os.fsdecode(name) if name else parent
                    if mask&IN_IGNORED:
                        watched.pop(wd,None);continue
                    if mask&IN_UNMOUNT:
                        special(db,"filesystem_unmounted");continue
                    rel=target.relative_to(ROOT).as_posix()
                    if ex.excluded(rel,directory=bool(mask&IN_ISDIR)):continue
                    if mask&IN_ISDIR and mask&(IN_CREATE|IN_MOVED_TO):
                        if target.is_dir():
                            try:walk(target)
                            except RuntimeError:pass
                    put(db,parent.relative_to(ROOT).as_posix())
        now=time.time()
        if now-last_dispatch>=float(CFG["check_interval_seconds"]):
            try:dispatch(db)
            except Exception as e:print("DISPATCH_EXCEPTION",str(e)[:180],flush=True)
            last_dispatch=now

if __name__=="__main__":main()
