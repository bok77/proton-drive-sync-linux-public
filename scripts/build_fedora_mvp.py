"""Build a self-contained Fedora user-space candidate without enabling services."""
from pathlib import Path
import argparse,json,shutil,hashlib,os
ROOT=Path(__file__).resolve().parents[1]
def build(dest):
    dest=Path(dest).expanduser().absolute()
    if dest.exists() or dest.is_symlink() or dest==Path.home() or dest==Path("/"):
        raise FileExistsError("Refuse to overwrite existing candidate")
    if not dest.parent.is_dir() or dest.parent.is_symlink():
        raise ValueError("Destination parent must be a real directory")
    if dest.is_relative_to(Path("/mnt/example-drive")):
        raise ValueError("Production volume excluded")
    dest.mkdir(mode=0o700)
    try:
        shutil.copytree(ROOT/"src"/"proton_sync_desktop",dest/"src"/"proton_sync_desktop",
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        shutil.copytree(ROOT/"src"/"proton_sync_engine",dest/"src"/"proton_sync_engine",
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
        shutil.copy2(ROOT/"packaging"/"proton-drive-sync.svg",dest/"proton-drive-sync.svg")
        bin_dir=dest/"bin";bin_dir.mkdir()
        entry=bin_dir/"proton-drive-sync"
        entry.write_text('#!/usr/bin/env bash\nset -euo pipefail\nroot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\nexport PYTHONPATH="$root/src"\nexport PYTHONDONTWRITEBYTECODE=1\nexec /usr/bin/python3 -m proton_sync_desktop "$@"\n')
        entry.chmod(0o700)
        runtime=bin_dir/"proton-portable-full"
        runtime.write_text('#!/usr/bin/env bash\nset -euo pipefail\nroot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\nexport PYTHONPATH="$root/src"\n: "${PROTON_SYNC_CONFIG:?Private explicit config required}"\nexec /usr/bin/python3 "$root/src/proton_sync_engine/runtime/proton-bisync.py" "$@"\n')
        runtime.chmod(0o700)
        manifest={}
        for item in sorted(dest.rglob("*")):
            if item.is_file() and not item.is_symlink():
                manifest[item.relative_to(dest).as_posix()]=hashlib.sha256(item.read_bytes()).hexdigest()
        (dest/"MANIFEST.json").write_text(json.dumps({"status":"TEST_CANDIDATE_NOT_ACTIVATED","files":manifest},indent=2))
        return {"status":"TEST_CANDIDATE_NOT_ACTIVATED","destination":str(dest),"files":len(manifest)}
    except BaseException:
        shutil.rmtree(dest)
        raise
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.output),indent=2))
