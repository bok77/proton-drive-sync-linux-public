"""Safe initial pairing: exact-state binding, no implicit baseline acceptance.

Only byte-identical files are eligible. All managed local and remote entries
must match, with complete verified listings and no symlinks. Approval re-scans
both sides and atomically writes a brand-new baseline without overwrite.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

APPROVAL="I APPROVE EXACT INITIAL PAIRING"
SCHEMA=1

def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def _sha1(path):
    sha=hashlib.sha1()
    with path.open("rb") as file:
        for block in iter(lambda:file.read(1024*1024),b""):
            sha.update(block)
    return sha.hexdigest()

def _local(root:Path,managed):
    entries={}
    errors=[]
    for top in managed:
        folder=root/top
        if folder.is_symlink() or not folder.is_dir():
            errors.append({"path":top,"reason":"missing_or_unsafe_directory"})
            continue
        for base,folders,files in os.walk(folder,followlinks=False):
            parent=Path(base)
            for name in folders:
                node=parent/name
                if node.is_symlink():
                    errors.append({"path":node.relative_to(root).as_posix(),"reason":"symlink_directory"})
            for name in files:
                path=parent/name
                rel=path.relative_to(root).as_posix()
                if path.is_symlink() or not path.is_file():
                    errors.append({"path":rel,"reason":"nonregular_file"})
                    continue
                try:
                    stat_before=path.stat()
                    digest=_sha1(path)
                    stat_after=path.stat()
                    if (stat_before.st_size,stat_before.st_mtime_ns,stat_before.st_ctime_ns,
                        stat_before.st_ino)!=(stat_after.st_size,stat_after.st_mtime_ns,
                        stat_after.st_ctime_ns,stat_after.st_ino):
                        raise RuntimeError("file_changed_during_hash")
                    entries[rel]={"sha1":digest,"size":stat_after.st_size}
                except (OSError,RuntimeError) as error:
                    errors.append({"path":rel,"reason":str(error)[:100]})
    return entries,errors

def _remote(scan,remote_digest,meta_rev):
    manifest,folders,errors=scan()
    entries={}
    for rel,meta in manifest.items():
        revision=meta.get("activeRevision") or {}
        digest=remote_digest(meta)
        size=revision.get("claimedSize")
        uid=meta_rev(meta)
        if (not isinstance(digest,str) or len(digest)!=40
            or type(size)!=int or size<0 or not isinstance(uid,str) or not uid):
            errors.append({"path":rel,"reason":"unverified_cloud_revision"})
            continue
        entries[rel]={"sha1":digest,"size":size,"revision":uid}
    return entries,errors

def compare(root,managed,scan,remote_digest,meta_rev):
    """Return an in-memory read-only review. The user never approves a guess."""
    root=Path(root)
    local,local_errors=_local(root,managed)
    cloud,remote_errors=_remote(scan,remote_digest,meta_rev)
    differences=[]
    baseline={}
    for rel in sorted(set(local)|set(cloud)):
        a=local.get(rel)
        b=cloud.get(rel)
        if a is None:
            differences.append({"path":rel,"reason":"only_in_cloud"})
        elif b is None:
            differences.append({"path":rel,"reason":"only_on_linux"})
        elif a["sha1"]!=b["sha1"] or a["size"]!=b["size"]:
            differences.append({"path":rel,"reason":"different_content"})
        else:
            baseline[rel]={"sha1":b["sha1"],"revision":b["revision"]}
    errors=local_errors+remote_errors
    if not baseline and not errors and not differences:
        errors.append({"path":"","reason":"empty_pairing_requires_separate_review"})
    binding={"version":SCHEMA,"baseline":baseline,
             "local":local,"remote":cloud,
             "differences":differences,"errors":errors}
    token=hashlib.sha256(_canonical(binding)).hexdigest()
    return {"status":"READY_FOR_EXPLICIT_APPROVAL" if not (errors or differences) else "BLOCKED",
            "sha256":token,"matched":len(baseline),"differences":differences,
            "errors":errors,"baseline":baseline}

def approve(root,managed,scan,remote_digest,meta_rev,baseline_file:Path,review:dict,approval:str):
    """Re-check both sides; create baseline exclusively only on an exact match."""
    if approval!=APPROVAL:
        raise PermissionError("Exact pairing approval required")
    if not isinstance(review,dict) or review.get("status")!="READY_FOR_EXPLICIT_APPROVAL":
        raise ValueError("Pairing review is not accepted")
    expected=review.get("sha256")
    if not isinstance(expected,str) or len(expected)!=64:
        raise ValueError("Invalid pairing proof")
    destination=Path(baseline_file)
    root=Path(root)
    if not destination.is_absolute() or destination.is_symlink():
        raise ValueError("Unsafe baseline location")
    if destination.exists():
        raise FileExistsError("Refusing to overwrite an existing baseline")
    if destination.parent.is_symlink() or not destination.parent.is_dir():
        raise ValueError("Baseline parent must exist and be non-symlink")
    if destination.is_relative_to(root):
        raise ValueError("Baseline cannot live under the synchronized directory")
    # Fresh scan both sides before claiming approval; no implicit trust in a
    # previous listing that may have changed during the human review.
    current=compare(root,managed,scan,remote_digest,meta_rev)
    if current["status"]!="READY_FOR_EXPLICIT_APPROVAL" or current["sha256"]!=expected:
        raise RuntimeError("PAIRING_STALE_OR_CONFLICT: no baseline created")
    baseline=current["baseline"]
    if len(baseline)!=current["matched"]:
        raise RuntimeError("Pairing count changed")
    # O_EXCL prevents another pairing writer from replacing any existing
    # baseline. Do not publish an accepted baseline before final readback.
    descriptor=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    created_identity=os.fstat(descriptor)
    try:
        with os.fdopen(descriptor,"w",encoding="utf-8") as file:
            json.dump(baseline,file,ensure_ascii=False,sort_keys=True)
            file.flush()
            os.fsync(file.fileno())
        if json.loads(destination.read_text(encoding="utf-8"))!=baseline:
            raise RuntimeError("PAIRING_BASELINE_READBACK_MISMATCH")
        # Verify AFTER commit too. On any detected drift, revoke the new
        # baseline and block activation instead of returning false success.
        final=compare(root,managed,scan,remote_digest,meta_rev)
        if final["status"]!="READY_FOR_EXPLICIT_APPROVAL" or final["sha256"]!=expected:
            raise RuntimeError("PAIRING_DRIFT_AFTER_WRITE")
        return {"status":"PAIRED","matched":len(baseline),"sha256":expected}
    except BaseException:
        # Roll back only our own newly created inode, including partial JSON.
        # A concurrently replaced path must never be deleted.
        try:
            current_stat=destination.lstat()
            if (current_stat.st_dev,current_stat.st_ino)==(
                created_identity.st_dev,created_identity.st_ino):
                destination.unlink()
        except FileNotFoundError:
            pass
        raise
