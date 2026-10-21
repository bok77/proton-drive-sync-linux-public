#!/usr/bin/env python3
"""Fast local-to-Proton sync; baseline gated, one file at a time, fail closed."""
import importlib.util, json, os, subprocess, sys, time
from pathlib import Path
from proton_sync_engine.portable_paths import paths as _load_runtime_paths
_runtime=_load_runtime_paths()
_progress_spec=importlib.util.spec_from_file_location("proton_progress",str(Path(__file__).resolve().parent/"proton-sync-progress.py"))
_progress=importlib.util.module_from_spec(_progress_spec);_progress_spec.loader.exec_module(_progress)
import importlib.util as _ilu
_exspec=_ilu.spec_from_file_location("proton_exclusions",str(Path(__file__).resolve().parent/"proton-sync-exclusions.py"))
exc=_ilu.module_from_spec(_exspec);_exspec.loader.exec_module(exc)
spec=importlib.util.spec_from_file_location("pbi", str(Path(__file__).resolve().parent/"proton-bisync.py"))
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
ROOT=b.ROOT
STATE=b.STATE
BASE=b.BASE
CACHE=STATE/"local_stat_cache.json"
def stamp(p):
    try:
        if p.is_symlink() or not p.is_file(): return None
        s=p.stat()
        return [s.st_size,s.st_mtime_ns,s.st_ctime_ns]
    except FileNotFoundError: return None
def save_json(path,obj):
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(obj,ensure_ascii=False))
    os.replace(temp,path)
def main():
    if subprocess.run(["mountpoint","-q",str(_runtime.mount_root)]).returncode: return 32
    if not BASE.is_file():return 32
    STATE.mkdir(parents=True,exist_ok=True)
    old=json.loads(BASE.read_text()); baseline=dict(old)
    _progress.update("local","tracked_files",done=0,total=len(old))
    cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
    newcache={}
    stats={"checked":0,"hashes":0,"uploaded":0,"conflicts":0,"errors":0}
    def issue(typ,path,detail):
        stats["conflicts" if typ=="conflict" else "errors"]+=1
        b.log(typ,path=path,detail=detail)
    # Fast scan: 11k stat calls, with SHA-1 computed only after metadata differs.
    for _index,(rel,ancestor) in enumerate(old.items(),1):
        if _index%100==0 or _index==len(old):
            _progress.update("local","tracked_files",done=_index-1,total=len(old))
        p=ROOT/rel; state=stamp(p)
        if not state:
            b.log("local_missing_pending",path=rel)
            continue
        previous=cache.get(rel)
        if previous and previous.get("stat")==state and previous.get("sha1")==ancestor.get("sha1"):
            newcache[rel]=previous;stats["checked"]+=1;continue
        before=b.local_digest(p);stats["hashes"]+=1;stats["checked"]+=1
        if state and time.time_ns()-state[1] < 30_000_000_000:
            # Do not upload files that an editor may still be writing.
            newcache[rel]={"stat":state,"sha1":before}
            continue
        if before==ancestor.get("sha1"):
            newcache[rel]={"stat":state,"sha1":before}
            continue
        # Local edit: cloud revision must match common ancestor immediately before upload.
        parts=rel.split("/")
        try:
            remote=b.v.remote_path(parts)
            pre=b.v.cli("filesystem","info",remote,"-j",timeout=180)
            if pre.returncode: raise RuntimeError("remote_preflight_failed")
            meta=json.loads(pre.stdout)
            if b.meta_rev(meta)!=ancestor.get("revision") or b.remote_digest(meta)!=ancestor.get("sha1"):
                issue("conflict",rel,"remote_changed_since_baseline")
                continue
            if b.local_digest(p)!=before: raise RuntimeError("local_changed_during_preflight")
            from proton_sync_engine.existing_revision_guard import require_atomic_revision_update
            require_atomic_revision_update()
            response=b.v.cli("filesystem","upload","-f","create-new-revision",str(p),b.v.remote_path(parts[:-1]),timeout=1800)
            if response.returncode: raise RuntimeError("upload_failed "+(response.stderr or response.stdout)[-200:])
            read=b.v.cli("filesystem","info",remote,"-j",timeout=180)
            if read.returncode: raise RuntimeError("readback_failed")
            latest=json.loads(read.stdout)
            if b.remote_digest(latest)!=before or b.local_digest(p)!=before:
                raise RuntimeError("postupload_digest_mismatch")
            baseline[rel]={"sha1":before,"revision":b.meta_rev(latest)}
            newcache[rel]={"stat":stamp(p),"sha1":before}
            stats["uploaded"]+=1
            b.log("quick_uploaded_verified",path=rel)
        except Exception as ex:issue("error",rel,str(ex)[:240])
    # Scan regular local files; never upload staging, symlinks or paths outside managed roots.
    _progress.update("local","new_files",done=None,total=None)
    known=set(old)
    # A local rename must not accidentally create a duplicate cloud file.
    missing_sha={}
    for source, ancestor in old.items():
        original=ROOT/source
        if not original.is_file() or original.is_symlink():
            digest=ancestor.get("sha1")
            missing_sha.setdefault(digest,[]).append(source)
    for folder in b.v.FOLDERS:
        root=ROOT/folder
        if not root.is_dir() or root.is_symlink():continue
        for parent,dirs,files in os.walk(root,followlinks=False):
            parent=Path(parent)
            dirs[:]=[n for n in dirs if not (parent/n).is_symlink() and not exc.excluded((parent/n).relative_to(ROOT).as_posix(),directory=True)]
            for name in files:
                p=parent/name
                if p.is_symlink() or not p.is_file():continue
                rel=p.relative_to(ROOT).as_posix()
                if rel in known:continue
                if exc.excluded(rel):continue
                # New folders are handled in the thorough run, not the fast path.
                parts=rel.split("/")
                remote=b.v.remote_path(parts)
                try:
                    probe=b.v.cli("filesystem","info",remote,"-j",timeout=90)
                    if probe.returncode==0:
                        issue("conflict",rel,"untracked_remote_exists")
                        continue
                    # Verify the remote parent exists before creating a file.
                    parentinfo=b.v.cli("filesystem","info",b.v.remote_path(parts[:-1]),"-j",timeout=90)
                    if parentinfo.returncode:continue
                    parentmeta=json.loads(parentinfo.stdout)
                    if parentmeta.get("type")!="folder":continue
                    snapshot=stamp(p)
                    if snapshot and time.time_ns()-snapshot[1] < 30_000_000_000:
                        continue
                    first=b.local_digest(p);stats["hashes"]+=1
                    if stamp(p)!=snapshot:raise RuntimeError("new_file_changed_while_reading")
                    if first in missing_sha:
                        b.log("local_rename_pending",path=rel,sources=missing_sha[first][:3])
                        continue
                    upload=b.v.cli("filesystem","upload","-f","skip",str(p),b.v.remote_path(parts[:-1]),timeout=1800)
                    if upload.returncode:raise RuntimeError("upload_failed")
                    verify=b.v.cli("filesystem","info",remote,"-j",timeout=90)
                    if verify.returncode:raise RuntimeError("readback_failed")
                    meta=json.loads(verify.stdout)
                    if b.remote_digest(meta)!=first or b.local_digest(p)!=first:
                        raise RuntimeError("upload_readback_mismatch")
                    baseline[rel]={"sha1":first,"revision":b.meta_rev(meta)}
                    newcache[rel]={"stat":stamp(p),"sha1":first}
                    stats["uploaded"]+=1
                    b.log("quick_new_uploaded_verified",path=rel)
                except Exception as ex:issue("error",rel,str(ex)[:200])
    # Files moved/deleted locally remain in the remote cloud until reviewed.
    b.write_baseline(baseline)
    save_json(CACHE,newcache)
    b.log("quick_run_end",**stats,tracked=len(baseline))
    success=not (stats["errors"] or stats["conflicts"])
    _progress.update("local","finished",status="complete" if success else "error")
    return 0 if success else 1
if __name__=="__main__":sys.exit(main())
