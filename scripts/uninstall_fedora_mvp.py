"""Strict removal of a self-contained candidate installation only.

Never remove unknown files, state, configuration, or user systemd units.
"""
import argparse,json
from pathlib import Path
try:
    from .install_fedora_mvp import verify
except ImportError:
    from install_fedora_mvp import verify

def uninstall(prefix):
    dest=Path(prefix).expanduser().absolute()
    verify(dest)
    manifest=json.loads((dest/"MANIFEST.json").read_text())
    expected=set(manifest["files"])|{"MANIFEST.json"}
    actual={p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    if expected!=actual:
        raise RuntimeError("Unknown files; refusing removal")
    for path in sorted(dest.rglob("*"),key=lambda p:len(p.parts),reverse=True):
        if path.is_symlink():
            raise RuntimeError("Symlink; refusing removal")
    for name in sorted(expected):
        (dest/name).unlink()
    dirs=sorted((p for p in dest.rglob("*") if p.is_dir()),key=lambda p:len(p.parts),reverse=True)
    for d in dirs:
        d.rmdir()
    dest.rmdir()
    return {"status":"REMOVED_CANDIDATE_ONLY","path":str(dest)}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--prefix",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(uninstall(args.prefix)))
