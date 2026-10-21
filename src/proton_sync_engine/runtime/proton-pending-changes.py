#!/usr/bin/env python3
"""Read-only report of possible local renames and deletions; never mutates cloud."""
import hashlib,json,os,time,importlib.util
from pathlib import Path
from proton_sync_engine.portable_paths import paths as _load_runtime_paths
_runtime=_load_runtime_paths()
ROOT=_runtime.local_root
STATE=_runtime.state_dir
BASE=STATE/"baseline.json"
REPORT=STATE/"pending_changes.json"
_spec=importlib.util.spec_from_file_location("exclusions",str(Path(__file__).resolve().parent/"proton-sync-exclusions.py"))
exc=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(exc)
FOLDERS=set(_runtime.managed_folders)
def sha(path):
    h=hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def main():
    import subprocess
    if subprocess.run(["mountpoint","-q",str(_runtime.mount_root)]).returncode: raise SystemExit("Configured mount missing")
    baseline=json.loads(BASE.read_text())
    missing={key:val for key,val in baseline.items() if not (ROOT/key).is_file() or (ROOT/key).is_symlink()}
    candidates={}
    new=[]
    for top in FOLDERS:
        root=ROOT/top
        if not root.is_dir() or root.is_symlink():continue
        for parent,dirs,files in os.walk(root,followlinks=False):
            parent=Path(parent)
            dirs[:]=[d for d in dirs if not (parent/d).is_symlink()]
            for name in files:
                p=parent/name
                if not p.is_file() or p.is_symlink():continue
                rel=p.relative_to(ROOT).as_posix()
                if rel not in baseline and not exc.excluded(rel):
                    new.append((rel,p))
    missing_by_size={}
    for rel,entry in missing.items():
        # Baseline has digests but no recorded size: infer from SHA1 only for new files.
        missing_by_size[entry["sha1"]]=missing_by_size.get(entry["sha1"],[])+[rel]
    probable_renames=[]
    for rel,p in new:
        hashed=sha(p)
        old=missing_by_size.get(hashed,[])
        if len(old)==1:probable_renames.append({"from":old[0],"to":rel,"sha1":hashed})
    moved={r["from"] for r in probable_renames}
    data={"checked_at":time.strftime("%Y-%m-%dT%H:%M:%S%z"),
          "tracked_missing":len(missing),"new_local":len(new),
          "probable_renames":probable_renames,
          "possible_deletions":[r for r in missing if r not in moved],
          "unmatched_new":[r for r,p in new if r not in {x["to"] for x in probable_renames}],
          "permanent_deletion_enabled":False,"delayed_cloud_trash_enabled":True}
    tmp=REPORT.with_suffix(".tmp");tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));os.replace(tmp,REPORT)
    print(json.dumps({"tracked_missing":data["tracked_missing"],"new_local":data["new_local"],
       "probable_renames":len(probable_renames),"possible_deletions":len(data["possible_deletions"]),
       "permanent_deletion_enabled":False,"delayed_cloud_trash_enabled":True},ensure_ascii=False))
if __name__=="__main__":main()
