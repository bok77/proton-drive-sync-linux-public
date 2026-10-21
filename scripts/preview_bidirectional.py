#!/usr/bin/env python3
"""Full read-only Linux/Proton Drive change preview, with fail-closed cloud scan."""
import hashlib,importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
from datetime import datetime
PKG=Path.home()/"Projekte/proton-drive-sync-linux/src"
sys.path.insert(0,str(PKG))
from proton_sync_desktop.analyze import classify,summarize
ROOT=Path("/mnt/example-sync-root")
STATE=Path.home()/".local/state/proton-bisync"
BASE=STATE/"baseline.json"
REPORT=STATE/"bidirectional_preview.json"
TOP=("00_Inbox","10_Private","20_Records",
     "30_Learning","40_Knowledge","50_Projects",
     "60_Media","70_Backups","80_Vault","90_Archive")
def production():
    """Import the production engine solely for inventory and digest readers."""
    spec=importlib.util.spec_from_file_location("private_sync_inventory",
                  Path.home()/".local/bin/proton-bisync.py")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
def digest(p):
    """Hash a regular local file without following symbolic links."""
    if p.is_symlink() or not p.is_file():return None
    h=hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def inventory(root,baseline,exclude):
    """Discover nonexcluded local files under the ten managed roots."""
    paths=set()
    for top in TOP:
        base=root/top
        if not base.is_dir() or base.is_symlink():
            raise RuntimeError("Managed root missing or unsafe: "+top)
        for parent,dirs,files in os.walk(base,followlinks=False):
            d=Path(parent)
            for item in dirs[:]:
                path=d/item;rel=path.relative_to(root).as_posix()
                if path.is_symlink():
                    dirs.remove(item)
                    if any(old.startswith(rel+"/") for old in baseline):
                        raise RuntimeError("Tracked directory is symlink: "+rel)
                elif exclude.excluded(rel,directory=True):
                    dirs.remove(item)
            for item in files:
                p=d/item;rel=p.relative_to(root).as_posix()
                if rel not in baseline and exclude.excluded(rel):continue
                paths.add(rel)
    return paths
def save(data):
    """Atomically update only the private analysis report."""
    fd,path=tempfile.mkstemp(prefix=".preview-",suffix=".json",dir=STATE)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False);f.flush();os.fsync(f.fileno())
        os.chmod(path,0o600);os.replace(path,REPORT)
    finally:
        if os.path.exists(path):os.unlink(path)
def analyze(scan=None,root=ROOT,baseline_file=BASE,write=True):
    """Three-way compare both inventories; abort on incomplete scan/baseline drift."""
    if subprocess.run(["mountpoint","-q","/mnt/example-drive"],capture_output=True).returncode:
        raise RuntimeError("Encrypted /mnt/example-drive missing")
    before=baseline_file.read_bytes()
    old=json.loads(before)
    if not isinstance(old,dict):raise RuntimeError("Invalid baseline")
    b=production()
    manifest,folders,errors=(scan or b.scan)()
    if errors:raise RuntimeError("Incomplete remote inventory: "+str(errors[:2]))
    paths=inventory(root,old,b.exc)
    entries=[]
    for rel in sorted(set(old)|set(paths)|set(manifest)):
        m=manifest.get(rel);p=root/rel
        exists=p.exists() or p.is_symlink()
        regular=(p.is_file() and not p.is_symlink()) if exists else True
        action=classify(rel,old.get(rel),digest(p) if regular and exists else None,
                        b.remote_digest(m) if m else None,
                        b.meta_rev(m) if m else None,
                        local_exists=exists,local_regular=regular,
                        remote_exists=m is not None,
                        remote_valid=b.checked_remote(m) if m else True)
        if action["action"]!="unchanged":entries.append(action)
    if baseline_file.read_bytes()!=before:raise RuntimeError("Baseline drift; retry")
    data={"generated_at":datetime.now().astimezone().isoformat(timespec="seconds"),
          "read_only":True,"complete_inventory":True,"cloud_changes_included":True,
          "not_authorization_to_apply":True,
          "checked_paths":len(set(old)|set(paths)|set(manifest)),
          "counts":summarize(entries),"changes":entries,
          "warning":"Preview snapshot only; revalidate all versions before changing data."}
    if write:save(data)
    return data
if __name__=="__main__":
    try:
        result=analyze()
        print(json.dumps({"checked_paths":result["checked_paths"],
                          "counts":result["counts"],"read_only":True}))
    except Exception as exc:
        print("PREVIEW_BLOCKED: "+str(exc)[:250],file=sys.stderr)
        sys.exit(2)
