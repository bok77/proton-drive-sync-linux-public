#!/usr/bin/env python3
"""Conservative Proton Drive two-way synchronization using a verified common ancestor."""
import hashlib, importlib.util, json, os, subprocess, sys, tempfile, time
from pathlib import Path
_progress_spec=importlib.util.spec_from_file_location("proton_progress",str(Path.home()/".local/bin/proton-sync-progress.py"))
_progress=importlib.util.module_from_spec(_progress_spec);_progress_spec.loader.exec_module(_progress)
_exspec=importlib.util.spec_from_file_location("proton_exclusions",str(Path.home()/".local/bin/proton-sync-exclusions.py"))
exc=importlib.util.module_from_spec(_exspec);_exspec.loader.exec_module(exc)

SPEC=importlib.util.spec_from_file_location("proton_verify",str(Path.home()/".local/bin/proton-verified-download.py"))
v=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)
ROOT=v.ROOT; STATE=Path.home()/".local/state/proton-bisync"; BASE=STATE/"baseline.json"
STAGE=ROOT/".verified-staging"
QUARANTINE_ROOT=Path("/mnt/example-sync-quarantine")
def log(event,**kwargs):
    msg=json.dumps({"time":time.strftime("%Y-%m-%dT%H:%M:%S%z"),"event":event,**kwargs},ensure_ascii=False)
    print(msg,flush=True)
    with (STATE/"events.jsonl").open("a") as out: out.write(msg+"\n")
def hash_file(p):
    h=hashlib.sha1()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def local_digest(p):
    if p.is_symlink() or not p.is_file(): return None
    return hash_file(p)
def remote_digest(m):
    r=m.get("activeRevision") or {}
    d=(r.get("claimedDigests") or {}).get("sha1")
    return d.lower() if isinstance(d,str) and len(d)==40 else None
def meta_rev(m): return (m.get("activeRevision") or {}).get("uid")
def checked_remote(m):
    d=remote_digest(m)
    size=(m.get("activeRevision") or {}).get("claimedSize")
    return d is not None and isinstance(size,int) and size>=0
def scan():
    files={}; folders=set([""]); errors=[]
    def walk(parts):
        path=v.remote_path(parts)
        try:
            res=v.cli("filesystem","list",path,"-j",timeout=300)
            if res.returncode: raise RuntimeError((res.stderr or res.stdout)[-250:])
            entries=json.loads(res.stdout)
            if not isinstance(entries,list): raise ValueError("Bad listing")
            for m in entries:
                obj=m.get("name") or {}; name=obj.get("value") if obj.get("ok") else None
                if not v.safe_name(name):
                    errors.append({"path":path,"problem":"unsupported_name"});continue
                child=parts+[name]; rel="/".join(child)
                if m.get("type")=="folder":
                    folders.add(rel); walk(child)
                elif m.get("type")=="file":
                    if rel in files: errors.append({"path":rel,"problem":"duplicate_name"})
                    else: files[rel]=m
                else: errors.append({"path":rel,"problem":"unsupported_type"})
        except Exception as exc: errors.append({"path":path,"problem":str(exc)[:300]})
    for name in v.FOLDERS:
        folders.add(name);walk([name])
    return files,folders,errors
def write_baseline(data):
    tmp=BASE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False))
    os.replace(tmp,BASE)
def main():
    if subprocess.run(["mountpoint","-q","/mnt/example-drive"]).returncode: raise RuntimeError("No /mnt/example-drive mount")
    STATE.mkdir(parents=True,exist_ok=True)
    STAGE.mkdir(parents=True,exist_ok=True)
    _progress.update("full","cloud_inventory")
    manifest,folders,errors=scan()
    if errors:
        for e in errors[:30]:log("scan_error",**e)
        log("aborted_scan",errors=len(errors))
        _progress.update("full","finished",status="error")
        return 2
    log("scan_ok",files=len(manifest),folders=len(folders))
    old=json.loads(BASE.read_text()) if BASE.exists() else None
    if old is None:
        baseline={}; conflicts=[]
        for rel,m in manifest.items():
            p=ROOT/rel; d=remote_digest(m)
            if not checked_remote(m):
                conflicts.append((rel,"no_remote_sha1"));continue
            if local_digest(p)==d:
                baseline[rel]={"sha1":d,"revision":meta_rev(m)}
            else: conflicts.append((rel,"not_identical_at_baseline"))
        write_baseline(baseline)
        for rel,why in conflicts[:30]:log("initial_conflict",path=rel,reason=why)
        log("baseline_created",tracked=len(baseline),unmatched=len(conflicts))
        # Avoid publishing files until all matched initial files have a safe ancestor.
        return 0 if not conflicts else 3
    baseline=dict(old); results={"remote_downloaded":0,"uploaded":0,"valid":0,"conflicts":0,"errors":0}
    # Preserve empty cloud directories locally too, never traverse symlinks.
    for folder in sorted(folders,key=lambda x:(x.count("/"),x)):
        if not folder: continue
        path=ROOT/folder
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            results["conflicts"]+=1;log("conflict",path=folder,reason="local_directory_conflict")
            continue
        path.mkdir(parents=True,exist_ok=True)
    def conflict(rel,why):
        results["conflicts"]+=1
        log("conflict",path=rel,reason=why)
    # Never permit deleting on either side. File moves/renames remain human decisions.
    _progress.update("full","file_comparison",done=0,total=len(manifest))
    for _index,(rel,m) in enumerate(manifest.items(),1):
        if _index%50==0 or _index==len(manifest):
            _progress.update("full","file_comparison",done=_index-1,total=len(manifest))
        p=ROOT/rel; remote=remote_digest(m); ancestor=old.get(rel)
        if not checked_remote(m): conflict(rel,"cloud_digest_unavailable");continue
        if p.is_symlink(): conflict(rel,"local_symlink");continue
        loc=local_digest(p)
        rev=meta_rev(m)
        if ancestor:
            same_cloud=(rev==ancestor.get("revision") and remote==ancestor.get("sha1"))
            same_local=(loc==ancestor.get("sha1"))
            if loc==remote:
                baseline[rel]={"sha1":remote,"revision":rev}
                results["valid"]+=1
            elif same_cloud and loc is not None:
                # Local-only change: upload a new cloud revision, never replace/trash.
                if not p.is_file(): conflict(rel,"local_nonregular");continue
                remote_parent=v.remote_path(rel.split("/")[:-1])
                try:
                    fresh=v.cli("filesystem","info",v.remote_path(rel.split("/")),"-j",timeout=180)
                    if fresh.returncode: raise RuntimeError("remote_preflight_failed")
                    current=json.loads(fresh.stdout)
                    if meta_rev(current)!=ancestor.get("revision") or remote_digest(current)!=ancestor.get("sha1"):
                        raise RuntimeError("remote_changed_before_upload")
                    if local_digest(p)!=loc: raise RuntimeError("local_changed_before_upload")
                    cmd=v.cli("filesystem","upload","-f","create-new-revision",str(p),remote_parent,timeout=1800)
                    if cmd.returncode: raise RuntimeError("upload_exit: "+(cmd.stderr or cmd.stdout)[-200:])
                    info=v.cli("filesystem","info",v.remote_path(rel.split("/")),"-j",timeout=180)
                    if info.returncode: raise RuntimeError("upload_readback_failed")
                    new=json.loads(info.stdout)
                    if remote_digest(new)!=loc: raise RuntimeError("upload_hash_mismatch")
                    baseline[rel]={"sha1":loc,"revision":meta_rev(new)}
                    results["uploaded"]+=1;log("uploaded_verified",path=rel)
                except Exception as ex: results["errors"]+=1;log("upload_error",path=rel,error=str(ex)[:220])
            elif same_local and loc is not None:
                # Remote-only edit: download to same-filesystem staging, verify and atomically replace.
                try:
                    with tempfile.TemporaryDirectory(prefix="item-",dir=STAGE) as temp:
                        res=v.cli("filesystem","download","-f","skip",v.remote_path(rel.split("/")),temp,timeout=1800)
                        c=Path(temp)/p.name
                        if res.returncode: raise RuntimeError("download_exit: "+(res.stderr or res.stdout)[-200:])
                        ok,reason=v.digest_ok(c,m)
                        if not ok: raise RuntimeError(reason)
                        if local_digest(p)!=loc: raise RuntimeError("local_changed_during_download")
                        os.replace(c,p)
                    baseline[rel]={"sha1":remote,"revision":rev}
                    results["remote_downloaded"]+=1;log("downloaded_verified",path=rel)
                except Exception as ex: results["errors"]+=1;log("download_error",path=rel,error=str(ex)[:220])
            elif loc is None and same_cloud and not p.exists():
                log("local_missing_pending",path=rel)
            else: conflict(rel,"both_changed_or_file_missing")
        elif loc==remote:
            baseline[rel]={"sha1":remote,"revision":rev}
            results["valid"]+=1
        elif loc is None and not p.exists():
            # New cloud file: parent must remain a real directory.
            try:
                if p.parent.is_symlink(): raise RuntimeError("parent_symlink")
                p.parent.mkdir(parents=True,exist_ok=True)
                with tempfile.TemporaryDirectory(prefix="item-",dir=STAGE) as temp:
                    res=v.cli("filesystem","download","-f","skip",v.remote_path(rel.split("/")),temp,timeout=1800)
                    c=Path(temp)/p.name
                    if res.returncode: raise RuntimeError((res.stderr or res.stdout)[-220:])
                    ok,reason=v.digest_ok(c,m)
                    if not ok: raise RuntimeError(reason)
                    if p.exists(): raise RuntimeError("local_appeared")
                    os.replace(c,p)
                baseline[rel]={"sha1":remote,"revision":rev}
                results["remote_downloaded"]+=1;log("downloaded_verified",path=rel)
            except Exception as ex: results["errors"]+=1;log("download_error",path=rel,error=str(ex)[:220])
        else: conflict(rel,"untracked_local_difference")
    _progress.update("full","remaining_changes")
    # A cloud-side delete or move is reconciled conservatively, without erasing local files.
    # Keep missing entries in the baseline until they have been observed on 2 full scans
    # and a 24-hour delay has elapsed. Quarantine is on the same encrypted filesystem.
    remote_pending_path=STATE/"remote_missing_candidates.json"
    old_pending=json.loads(remote_pending_path.read_text()) if remote_pending_path.exists() else {}
    new_pending={}
    cloud_missing=[rel for rel in old if rel not in manifest]
    if len(cloud_missing)>max(3,int(len(old)*0.001)):
        log("remote_bulk_missing_blocked",missing=len(cloud_missing))
        results["conflicts"]+=1
    else:
        for rel in cloud_missing:
            local=ROOT/rel
            ancestor=old[rel]
            rec=old_pending.get(rel,{})
            if rec.get("sha1")!=ancestor.get("sha1"):
                rec={"sha1":ancestor.get("sha1"),"first_seen":time.time(),"observations":0}
            rec["observations"]+=1
            new_pending[rel]=rec
            if rec["observations"]<2 or time.time()-rec["first_seen"]<86400:
                log("cloud_missing_pending",path=rel,observations=rec["observations"])
                continue
            if local.is_symlink() or not local.is_file() or local_digest(local)!=ancestor.get("sha1"):
                conflict(rel,"cloud_missing_local_modified")
                continue
            try:
                quarantine=QUARANTINE_ROOT/rel
                quarantine.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                if quarantine.exists():raise RuntimeError("quarantine_target_already_exists")
                os.replace(local,quarantine)
                baseline.pop(rel,None)
                new_pending.pop(rel,None)
                log("cloud_removed_local_quarantined",path=rel,location=str(quarantine))
            except Exception as ex:
                results["errors"]+=1
                log("cloud_quarantine_error",path=rel,detail=str(ex)[:220])
    pending_tmp=remote_pending_path.with_suffix(".tmp")
    pending_tmp.write_text(json.dumps(new_pending,ensure_ascii=False))
    os.replace(pending_tmp,remote_pending_path)
    # Create locally added folders on Proton, but do not recreate folders that
    # held previously tracked cloud files (possible remote deletion/move).
    for d in sorted(ROOT.rglob("*"), key=lambda p:(len(p.parts),str(p))):
        if not d.is_dir() or d.is_symlink(): continue
        rel=d.relative_to(ROOT).as_posix()
        if exc.excluded(rel,directory=True): continue
        if rel.split("/")[0] not in v.FOLDERS: continue
        if rel in folders: continue
        parent=d.parent.relative_to(ROOT).as_posix()
        if parent == ".": parent=""
        if parent not in folders: conflict(rel,"parent_folder_not_available");continue
        if any(k.startswith(rel+"/") for k in old):
            conflict(rel,"previous_remote_folder_missing")
            continue
        try:
            result=v.cli("filesystem","create-folder",v.remote_path(parent.split("/")) if parent else "/my-files",d.name,timeout=180)
            if result.returncode: raise RuntimeError((result.stderr or result.stdout)[-220:])
            info=v.cli("filesystem","info",v.remote_path(rel.split("/")),"-j",timeout=180)
            if info.returncode or json.loads(info.stdout).get("type")!="folder":
                raise RuntimeError("create_folder_readback_failed")
            folders.add(rel)
            log("folder_uploaded",path=rel)
        except Exception as ex:
            results["errors"]+=1;log("folder_upload_error",path=rel,error=str(ex)[:220])
    # Upload new local files only in existing remote directories; no automatic deletion.
    # Preserve potential local rename/move instead of duplicating content in cloud.
    removed_sha={}
    for old_rel, old_item in old.items():
        old_path=ROOT/old_rel
        if old_path.is_symlink() or not old_path.is_file():
            removed_sha.setdefault(old_item.get("sha1"),[]).append(old_rel)
    for folder in sorted(folders):
        d=ROOT/folder
        if not d.is_dir() or d.is_symlink():continue
        for p in d.iterdir():
            if not p.is_file() or p.is_symlink():continue
            rel=p.relative_to(ROOT).as_posix()
            if rel in manifest or rel in old:continue
            if exc.excluded(rel):continue
            if not v.safe_name(p.name): conflict(rel,"unsupported_name");continue
            try:
                before=local_digest(p)
                if before in removed_sha:
                    log("local_rename_pending",path=rel,sources=removed_sha[before][:3])
                    continue
                res=v.cli("filesystem","upload","-f","skip",str(p),v.remote_path(folder.split("/")) if folder else "/my-files",timeout=1800)
                if res.returncode: raise RuntimeError((res.stderr or res.stdout)[-220:])
                info=v.cli("filesystem","info",v.remote_path(rel.split("/")),"-j",timeout=180)
                if info.returncode: raise RuntimeError("readback_failed")
                new=json.loads(info.stdout)
                if remote_digest(new)!=before or local_digest(p)!=before: raise RuntimeError("hash_mismatch")
                baseline[rel]={"sha1":before,"revision":meta_rev(new)}
                results["uploaded"]+=1;log("new_local_uploaded",path=rel)
            except Exception as ex: results["errors"]+=1;log("upload_error",path=rel,error=str(ex)[:220])
    write_baseline(baseline)
    log("run_end",**results,tracked=len(baseline))
    success=not (results["conflicts"] or results["errors"])
    _progress.update("full","finished",status="complete" if success else "error")
    return 0 if success else 1
if __name__=="__main__":
    sys.exit(main())
