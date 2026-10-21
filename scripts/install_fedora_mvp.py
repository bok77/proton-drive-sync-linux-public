"""Strict installer for a built Fedora MVP user-space bundle.

Never overwrite, enable services or alter personal data.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,os

def verify(bundle):
    bundle=Path(bundle).expanduser().absolute()
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValueError("Invalid candidate")
    manifest=json.loads((bundle/"MANIFEST.json").read_text())
    if manifest.get("status")!="TEST_CANDIDATE_NOT_ACTIVATED":
        raise ValueError("Bundle not accepted for test installation")
    files=manifest.get("files")
    if not isinstance(files,dict) or not files:
        raise ValueError("Invalid manifest")
    actual={p.relative_to(bundle).as_posix() for p in bundle.rglob("*")
            if p.is_file()}
    if actual!=set(files)|{"MANIFEST.json"}:
        raise ValueError("Unexpected/missing bundle files")
    for name,digest in files.items():
        p=bundle/name
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise ValueError("Candidate integrity mismatch")
    return bundle

def install(bundle,prefix):
    bundle=verify(bundle)
    dest=Path(prefix).expanduser().absolute()
    if dest.is_symlink() or dest.exists():
        raise FileExistsError("Refusing to overwrite existing installation")
    if dest==Path.home() or dest==Path("/") or dest.is_relative_to(Path("/mnt/example-drive")):
        raise ValueError("Unsafe install destination")
    if not dest.parent.is_dir() or dest.parent.is_symlink():
        raise ValueError("Parent must exist")
    shutil.copytree(bundle,dest,symlinks=False)
    try:
        verify(dest)
    except BaseException:
        shutil.rmtree(dest)
        raise
    return {"status":"INSTALLED_NOT_ACTIVATED","path":str(dest),
            "run":str(dest/"bin/proton-drive-sync"),
            "runtime":str(dest/"bin/proton-portable-full")}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--prefix",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(install(args.bundle,args.prefix),indent=2))
