#!/usr/bin/env python3
"""Conservative local renames and delayed cloud trash with validated provenance."""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
from collections import defaultdict
import importlib.util
spec=importlib.util.spec_from_file_location("bisync",str(Path.home()/".local/bin/proton-bisync.py"))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
ROOT=b.ROOT; STATE=b.STATE; BASE=b.BASE
PENDING=STATE/"reconcile_candidates.json"
CACHE=STATE/"local_stat_cache.json"
WAIT_SECONDS=24*3600
def atomic(path,val):
    p=path.with_suffix(path.suffix+".tmp")
    p.write_text(json.dumps(val,ensure_ascii=False,indent=2))
    os.replace(p,path)
def regular(p):
    return p.is_file() and not p.is_symlink()
def safe_remote(path,entry):
    try:
        result=b.v.cli("filesystem","info",b.v.remote_path(path.split("/")),"-j",timeout=90)
        if result.returncode:return None
        obj=json.loads(result.stdout)
        if obj.get("type")!="file":return None
        if b.meta_rev(obj)!=entry.get("revision") or b.remote_digest(obj)!=entry.get("sha1"):return None
        return obj
    except (ValueError,KeyError,subprocess.TimeoutExpired):return None
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--scope",default="",help="Restrict to a single test file prefix")
    ap.add_argument("--delete-wait-seconds",type=int,default=WAIT_SECONDS)
    args=ap.parse_args()
    if subprocess.run(["mountpoint","-q","/mnt/example-drive"]).returncode:raise RuntimeError("Encrypted /mnt/example-drive not mounted")
    STATE.mkdir(parents=True,exist_ok=True)
    baseline=json.loads(BASE.read_text())
    pending=json.loads(PENDING.read_text()) if PENDING.exists() else {}
    cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
    missing={name:entry for name,entry in baseline.items() if (not args.scope or Path(name).name.startswith(args.scope)) and not regular(ROOT/name)}
    candidates=defaultdict(list)
    for root in b.v.FOLDERS:
        for parent,dirs,files in os.walk(ROOT/root,followlinks=False):
            parent=Path(parent)
            dirs[:]=[n for n in dirs if not (parent/n).is_symlink()]
            for name in files:
                p=parent/name
                if not regular(p):continue
                rel=p.relative_to(ROOT).as_posix()
                if rel in baseline:continue
                # Rename candidate must have same full SHA1 as missing file.
                candidates[p.stat().st_size].append((rel,p))
    # Fail closed if a whole subtree/mount appears missing.
    if len(missing)>max(3,int(len(baseline)*0.001)):
        b.log("reconcile_bulk_missing_blocked",missing=len(missing))
        return 3
    tracked_sha=defaultdict(list)
    for rel,entry in missing.items():tracked_sha[entry["sha1"]].append(rel)
    rename_map=defaultdict(list)
    for rel,p in sum(candidates.values(),[]):
        if args.scope and not Path(rel).name.startswith(args.scope):continue
        digest=b.local_digest(p)
        if digest in tracked_sha:
            for old_rel in tracked_sha[digest]:rename_map[old_rel].append((rel,p))
    now=time.time();next_pending={}
    stats={"renamed":0,"trashed":0,"deferred":0,"conflicts":0,"errors":0}
    for old_rel,entry in missing.items():
        options=rename_map.get(old_rel,[])
        parent=(ROOT/old_rel).parent
        if not parent.is_dir() or parent.is_symlink():
            b.log("reconcile_missing_parent",path=old_rel);stats["conflicts"]+=1;continue
        key=old_rel
        rec=pending.get(key,{})
        if options:
            if len(options)!=1 or len(tracked_sha.get(entry["sha1"],[]))!=1:
                b.log("reconcile_ambiguous_rename",path=old_rel);stats["conflicts"]+=1;continue
            dest,p=options[0]
            if not b.v.safe_name(p.name):stats["conflicts"]+=1;continue
            if rec.get("kind")!="rename" or rec.get("destination")!=dest or rec.get("sha1")!=entry["sha1"]:
                rec={"kind":"rename","destination":dest,"sha1":entry["sha1"],"first_seen":now,"observations":0}
            rec["observations"]+=1;next_pending[key]=rec
            if not args.apply or rec["observations"]<2:
                stats["deferred"]+=1;continue
            if b.local_digest(p)!=entry["sha1"] or regular(ROOT/old_rel):
                stats["conflicts"]+=1;continue
            if dest in baseline:
                stats["conflicts"]+=1;continue
            # Target parent must already exist in the cloud: fail closed otherwise.
            target_parent=b.v.remote_path(dest.split("/")[:-1])
            folder_result=b.v.cli("filesystem","info",target_parent,"-j",timeout=90)
            if folder_result.returncode or json.loads(folder_result.stdout).get("type")!="folder":
                stats["conflicts"]+=1;continue
            if not safe_remote(old_rel,entry):
                stats["conflicts"]+=1;b.log("reconcile_stale_remote",path=old_rel);continue
            try:
                source=b.v.remote_path(old_rel.split("/"))
                if old_rel.rsplit("/",1)[0] != dest.rsplit("/",1)[0]:
                    move=b.v.cli("filesystem","move",source,target_parent,timeout=180)
                    if move.returncode:raise RuntimeError("move failed "+move.stderr[-160:])
                    source=b.v.remote_path(old_rel.split("/")[:-1]+[Path(old_rel).name])
                    # After a cross-folder move, original leaf name exists at destination parent.
                    source=b.v.remote_path(dest.split("/")[:-1]+[Path(old_rel).name])
                if Path(old_rel).name != Path(dest).name:
                    rename=b.v.cli("filesystem","rename",source,Path(dest).name,timeout=180)
                    if rename.returncode:raise RuntimeError("rename failed "+rename.stderr[-160:])
                verify=b.v.cli("filesystem","info",b.v.remote_path(dest.split("/")),"-j",timeout=90)
                if verify.returncode:raise RuntimeError("rename readback absent")
                meta=json.loads(verify.stdout)
                if b.remote_digest(meta)!=entry["sha1"] or b.local_digest(p)!=entry["sha1"]:
                    raise RuntimeError("rename hash mismatch")
                baseline[dest]={"sha1":entry["sha1"],"revision":b.meta_rev(meta)}
                del baseline[old_rel]
                if old_rel in cache:cache[dest]=cache.pop(old_rel)
                next_pending.pop(key,None)
                stats["renamed"]+=1;b.log("reconcile_renamed_verified",source=old_rel,destination=dest)
            except Exception as ex:
                stats["errors"]+=1;b.log("reconcile_error",path=old_rel,reason=str(ex)[:200])
        else:
            if rec.get("kind")!="delete" or rec.get("sha1")!=entry["sha1"]:
                rec={"kind":"delete","sha1":entry["sha1"],"first_seen":now,"observations":0}
            rec["observations"]+=1;next_pending[key]=rec
            if not args.apply or rec["observations"]<3 or now-rec["first_seen"]<args.delete_wait_seconds:
                stats["deferred"]+=1;continue
            if regular(ROOT/old_rel) or not safe_remote(old_rel,entry):
                stats["conflicts"]+=1;continue
            try:
                cloud=b.v.cli("filesystem","trash",b.v.remote_path(old_rel.split("/")),timeout=180)
                if cloud.returncode:raise RuntimeError("trash failed "+cloud.stderr[-160:])
                check=b.v.cli("filesystem","info",b.v.remote_path(old_rel.split("/")),"-j",timeout=90)
                if check.returncode==0:raise RuntimeError("trash readback still present")
                baseline.pop(old_rel,None);cache.pop(old_rel,None)
                next_pending.pop(key,None)
                stats["trashed"]+=1;b.log("reconcile_trashed",path=old_rel)
            except Exception as ex:stats["errors"]+=1;b.log("reconcile_error",path=old_rel,reason=str(ex)[:200])
    if args.apply:
        b.write_baseline(baseline)
        atomic(CACHE,cache)
        atomic(PENDING,next_pending)
    b.log("reconcile_run_end",apply=args.apply,**stats,missing=len(missing))
    return 1 if stats["errors"] or stats["conflicts"] else 0
if __name__=="__main__":sys.exit(main())
