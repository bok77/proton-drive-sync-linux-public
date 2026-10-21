#!/usr/bin/env python3
"""Fast targeted cloud pull for high-priority folders; full hourly sweep remains authoritative."""
import importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
_progress_spec=importlib.util.spec_from_file_location("proton_progress",str(Path.home()/".local/bin/proton-sync-progress.py"))
_progress=importlib.util.module_from_spec(_progress_spec);_progress_spec.loader.exec_module(_progress)
spec=importlib.util.spec_from_file_location("pbi",str(Path.home()/".local/bin/proton-bisync.py"))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
# Priority folders are user-editable through the GNOME application.
# Validate first; invalid config aborts instead of silently broadening the scan.
_route_spec=importlib.util.spec_from_file_location(
    "routing",str(Path.home()/"Projekte/proton-drive-sync-linux/src/proton_sync_desktop/routing.py"))
_routing=importlib.util.module_from_spec(_route_spec);sys.modules[_route_spec.name]=_routing;_route_spec.loader.exec_module(_routing)
FOLDERS=[tuple(p.split("/")) for p in _routing.load()["priority_cloud_folders"]]
def main():
    if subprocess.run(["mountpoint","-q","/mnt/example-drive"]).returncode:raise RuntimeError("encrypted mount absent")
    if not b.BASE.exists():raise RuntimeError("baseline missing")
    _progress.update("priority","cloud_inventory")
    manifest={}
    for parts in FOLDERS:
        folder=b.v.remote_path(list(parts))
        response=b.v.cli("filesystem","list",folder,"-j",timeout=300)
        if response.returncode:raise RuntimeError("cloud_listing_failed "+folder)
        entries=json.loads(response.stdout)
        if not isinstance(entries,list):raise RuntimeError("invalid_listing "+folder)
        for m in entries:
            name=m.get("name") or {}
            if not name.get("ok") or not b.v.safe_name(name.get("value")):
                raise RuntimeError("unsupported_cloud_name")
            child=parts+(name["value"],)
            if m.get("type")=="file":
                rel="/".join(child)
                if rel in manifest:raise RuntimeError("duplicate_cloud_name")
                manifest[rel]=m
            elif m.get("type")=="folder":
                # Nested subfolders remain covered by full hourly sweep.
                continue
            else: raise RuntimeError("unsupported_cloud_entry")
    baseline=json.loads(b.BASE.read_text())
    counts={"checked":0,"downloaded":0,"valid":0,"conflicts":0,"errors":0}
    _progress.update("priority","file_comparison",done=0,total=len(manifest))
    for _index,(rel,m) in enumerate(manifest.items(),1):
        counts["checked"]+=1
        if _index%5==0 or _index==len(manifest):
            _progress.update("priority","file_comparison",done=_index-1,total=len(manifest))
        p=b.ROOT/rel
        ancestor=baseline.get(rel)
        if not b.checked_remote(m):
            counts["conflicts"]+=1;b.log("priority_cloud_unverifiable",path=rel);continue
        rev=b.meta_rev(m);digest=b.remote_digest(m)
        local=b.local_digest(p) if p.is_file() and not p.is_symlink() else None
        if local==digest:
            baseline[rel]={"sha1":digest,"revision":rev};counts["valid"]+=1;continue
        if ancestor and local!=ancestor.get("sha1"):
            counts["conflicts"]+=1;b.log("priority_both_changed",path=rel);continue
        if not ancestor and p.exists():
            counts["conflicts"]+=1;b.log("priority_untracked_local_conflict",path=rel);continue
        if p.is_symlink() or (p.exists() and not p.is_file()):
            counts["conflicts"]+=1;b.log("priority_nonregular_file",path=rel);continue
        try:
            if not p.parent.is_dir() or p.parent.is_symlink():raise RuntimeError("invalid_parent")
            with tempfile.TemporaryDirectory(prefix="item-",dir=b.STAGE) as staging:
                response=b.v.cli("filesystem","download","-f","skip",b.v.remote_path(rel.split("/")),staging,timeout=1800)
                candidate=Path(staging)/p.name
                if response.returncode:raise RuntimeError("download_failed")
                valid,why=b.v.digest_ok(candidate,m)
                if not valid:raise RuntimeError("hash_check_failed "+why)
                # Recheck local and remote so concurrent writes are blocked.
                if ancestor:
                    if b.local_digest(p)!=ancestor["sha1"]:raise RuntimeError("local_changed_during_download")
                elif p.exists():raise RuntimeError("local_appeared_during_download")
                newer=b.v.cli("filesystem","info",b.v.remote_path(rel.split("/")),"-j",timeout=120)
                if newer.returncode:raise RuntimeError("cloud_readback_failed")
                latest=json.loads(newer.stdout)
                if b.meta_rev(latest)!=rev or b.remote_digest(latest)!=digest:
                    raise RuntimeError("cloud_changed_during_download")
                os.replace(candidate,p)
            baseline[rel]={"sha1":digest,"revision":rev}
            counts["downloaded"]+=1;b.log("priority_downloaded_verified",path=rel)
        except Exception as ex:
            counts["errors"]+=1;b.log("priority_download_error",path=rel,reason=str(ex)[:240])
    b.write_baseline(baseline)
    b.log("priority_run_end",**counts)
    success=not (counts["errors"] or counts["conflicts"])
    _progress.update("priority","finished",status="complete" if success else "error")
    return 0 if success else 1
if __name__=="__main__":sys.exit(main())
