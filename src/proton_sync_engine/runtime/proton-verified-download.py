#!/usr/bin/env python3
"""Read-only Proton source; verified, atomic local download. No remote mutations."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from proton_sync_engine.portable_paths import paths as _load_runtime_paths
_runtime=_load_runtime_paths()
import subprocess
import sys
import tempfile
import time

ROOT = _runtime.local_root
STATE = _runtime.verify_state
CLI = str(_runtime.cli_executable)
FOLDERS = list(_runtime.managed_folders)

def log(event, **kwargs):
    record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": event, **kwargs}
    line = json.dumps(record, ensure_ascii=False)
    print(line, flush=True)
    with (STATE / "events.jsonl").open("a") as f:
        f.write(line + "\n")

def cli(*args, timeout=300):
    from proton_sync_engine.cli_adapter import execute
    return execute(CLI, *args, timeout=timeout)

def remote_path(parts):
    # A literal slash in a Proton node name is escaped in CLI paths.
    return "/my-files/" + "/".join(p.replace("/", "\\/") for p in parts)

def safe_name(name):
    return bool(name) and name not in (".", "..") and "/" not in name and "\\x00" not in name

def digest_ok(path, meta):
    rev = meta.get("activeRevision") or {}
    expected = rev.get("claimedSize")
    if not isinstance(expected, int) or expected < 0:
        return False, "missing_expected_size"
    if not path.is_file() or path.is_symlink():
        return False, "missing_or_nonregular"
    if path.stat().st_size != expected:
        return False, f"size_mismatch_{path.stat().st_size}_vs_{expected}"
    sha1 = (rev.get("claimedDigests") or {}).get("sha1")
    if sha1 and len(sha1) == 40:
        h = hashlib.sha1()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        if h.hexdigest().lower() != sha1.lower():
            return False, "sha1_mismatch"
        return True, "size_and_sha1"
    return True, "size_only"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--protect-local", action="store_true", help="Do not overwrite local conflicts")
    parser.add_argument("--folder", choices=FOLDERS, help="Process one top-level folder only")
    parser.add_argument("--max-files", type=int, default=0, help="Limit checked files for pilot")
    args = parser.parse_args()
    if not subprocess.run(["mountpoint", "-q", str(_runtime.mount_root)]).returncode == 0:
        raise RuntimeError("Configured mount is not mounted")
    if not ROOT.is_dir():
        raise RuntimeError("destination missing")
    STATE.mkdir(parents=True, exist_ok=True)
    STAGE = ROOT / ".verified-staging"
    STAGE.mkdir(exist_ok=True, mode=0o700)
    counters = dict(checked=0, already_valid=0, downloaded=0, failed=0, folders=0, skipped=0)
    failures = []
    seen = set()
    started = time.monotonic()
    def checkpoint(force=False):
        if not force and counters["checked"] % 100:
            return
        tmp = STATE / "progress.json.tmp"
        tmp.write_text(json.dumps({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                   "elapsed_seconds": round(time.monotonic()-started, 2),
                                   "counters": counters}, ensure_ascii=False))
        os.replace(tmp, STATE / "progress.json")
    def walk(parts):
        rp = remote_path(parts)
        result = cli("filesystem", "list", rp, "-j", timeout=300)
        if result.returncode:
            counters["failed"] += 1
            failures.append({"path": rp, "error": "list_failed", "detail": result.stderr[-300:]})
            log("list_failed", path=rp, message=result.stderr[-300:])
            return
        try:
            entries = json.loads(result.stdout)
            if not isinstance(entries, list):
                raise ValueError("not a list")
        except Exception as e:
            counters["failed"] += 1
            failures.append({"path": rp, "error": "invalid_manifest", "detail": str(e)})
            log("invalid_manifest", path=rp, message=str(e))
            return
        for entry in entries:
            name = (entry.get("name") or {}).get("value") if (entry.get("name") or {}).get("ok") else None
            if not safe_name(name):
                counters["skipped"] += 1
                log("unsupported_name", parent=rp, uid=entry.get("uid"))
                continue
            child = parts + [name]
            local = ROOT.joinpath(*child)
            kind = entry.get("type")
            if kind == "folder":
                counters["folders"] += 1
                if local.is_symlink() or (local.exists() and not local.is_dir()):
                    counters["failed"] += 1
                    log("folder_conflict", path=str(local))
                    continue
                local.mkdir(exist_ok=True)
                yield from walk(child)
            elif kind == "file":
                yield (child, entry)
            else:
                counters["skipped"] += 1
                log("unsupported_type", path=remote_path(child), kind=kind)
    log("run_start", folder=args.folder, max_files=args.max_files)
    for folder in ([args.folder] if args.folder else FOLDERS):
        for parts, entry in walk([folder]):
            if args.max_files and counters["checked"] >= args.max_files:
                break
            rp = remote_path(parts)
            uid = entry.get("uid")
            if rp in seen:
                counters["failed"] += 1
                log("duplicate_remote_name", path=rp, uid=uid)
                continue
            seen.add(rp)
            local = ROOT.joinpath(*parts)
            counters["checked"] += 1
            try:
                valid, reason = digest_ok(local, entry)
                if valid:
                    counters["already_valid"] += 1
                    checkpoint()
                    continue
                # On unattended recurring pulls, NEVER overwrite differing local contents.
                # Local edits or stale partials require explicit conflict resolution.
                if args.protect_local and (local.exists() or local.is_symlink()):
                    counters["failed"] += 1
                    failures.append({"path": rp, "uid": uid, "error": "local_conflict:" + reason})
                    log("local_conflict", path=rp, reason=reason)
                    checkpoint()
                    continue
                # Keep incomplete originals untouched until replacement validates.
                with tempfile.TemporaryDirectory(prefix="item-", dir=STAGE) as staging:
                    result = cli("filesystem", "download", "-f", "skip", rp, staging, timeout=1800)
                    candidate = Path(staging) / parts[-1]
                    if result.returncode:
                        raise RuntimeError("CLI_DOWNLOAD_FAILED " + (result.stderr or result.stdout)[-350:])
                    ok, check = digest_ok(candidate, entry)
                    if not ok:
                        raise RuntimeError("VALIDATION_FAILED " + check)
                    if local.is_symlink() or (local.exists() and not local.is_file()):
                        raise RuntimeError("NON_REGULAR_DESTINATION")
                    local.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(candidate, local)
                    counters["downloaded"] += 1
                    log("verified_download", path=rp, bytes=local.stat().st_size, check=check, previous=reason)
            except Exception as e:
                counters["failed"] += 1
                failures.append({"path": rp, "uid": uid, "error": str(e)[:400]})
                log("file_failed", path=rp, error=str(e)[:400])
            checkpoint()
        if args.max_files and counters["checked"] >= args.max_files:
            break
    checkpoint(force=True)
    (STATE / "last_run.json").write_text(json.dumps({"counters": counters, "failures": failures}, ensure_ascii=False, indent=2))
    log("run_end", **counters)
    return 1 if counters["failed"] or counters["skipped"] else 0

if __name__ == "__main__":
    sys.exit(main())
