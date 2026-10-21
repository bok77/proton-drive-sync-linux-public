"""Create only the private portable default exclusion file, never overwrite."""
import json,os
from pathlib import Path
from proton_sync_engine.portable_paths import load_paths

DEFAULT={"exclusions":{"file_patterns":[],"directory_names":[],"custom_relative_prefixes":[]}}

def initialize(config_file):
    conf=load_paths(Path(config_file))
    state=conf.state_dir
    if not state.is_dir() or state.is_symlink() or state.stat().st_mode & 0o077:
        raise PermissionError("Private state directory required")
    path=conf.exclusion_settings
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
            raise PermissionError("Unsafe exclusion settings")
        data=json.loads(path.read_text())
        if data!=DEFAULT:
            raise FileExistsError("Existing custom exclusions cannot be replaced")
        return {"status":"ALREADY_PRESENT","path":str(path)}
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,"w") as out:
            json.dump(DEFAULT,out,sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return {"status":"CREATED_DEFAULTS","path":str(path)}
