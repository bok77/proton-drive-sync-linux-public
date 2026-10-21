"""Validated configuration for a future portable Linux Proton Drive sync engine.

No defaults point at the developer's Fedora filesystem. The adapter is inert
until a user has explicitly supplied and confirmed the local sync root,
mounted filesystem boundary and Proton CLI executable.
"""
from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess

@dataclass(frozen=True)
class EngineConfig:
    """Immutable, explicitly confirmed paths for a single sync installation."""
    local_root: Path
    mount_root: Path
    state_dir: Path
    cli_executable: Path
    cloud_root: str = "/my-files"

def validated_config(values:dict[str,str],*,require_mount:bool=True,runner=subprocess.run)->EngineConfig:
    """Fail closed on missing paths, root escapes, symlinks, or absent mounts.

    Directory existence is required; this function performs no writes.
    The caller must separately obtain affirmative permission before installing
    or starting any service and before creating an initial baseline.
    """
    required=("local_root","mount_root","state_dir","cli_executable")
    if any(not isinstance(values.get(key),str) or not values[key].strip() for key in required):
        raise ValueError("Every path must be configured explicitly")
    if values.get("cloud_root","/my-files")!="/my-files":
        raise ValueError("Unsupported cloud root")
    paths={key:Path(values[key]).expanduser() for key in required}
    if any(not p.is_absolute() for p in paths.values()):
        raise ValueError("Paths must be absolute")
    if any(p.is_symlink() for p in paths.values()):
        raise ValueError("Symbolic-link config paths are not supported")
    local=paths["local_root"].resolve(strict=True)
    mount=paths["mount_root"].resolve(strict=True)
    cli=paths["cli_executable"].resolve(strict=True)
    state=paths["state_dir"].resolve(strict=False)
    if local==Path("/") or mount==Path("/") or local==mount:
        raise ValueError("Dangerous root or mount")
    if not local.is_dir() or not mount.is_dir():
        raise ValueError("Local and mount roots must be directories")
    if not local.is_relative_to(mount):
        raise ValueError("Local root is outside the configured mount")
    if state==Path("/") or state==local or state.is_relative_to(local):
        raise ValueError("State directory cannot be under synchronized files")
    if not cli.is_file() or not os.access(cli,os.X_OK):
        raise ValueError("Proton CLI must exist and be executable")
    if require_mount:
        result=runner(["mountpoint","-q",str(mount)],capture_output=True,timeout=5)
        if result.returncode!=0:
            raise ValueError("Configured filesystem is not mounted")
    return EngineConfig(local,mount,state,cli)

def installation_ready(config:EngineConfig)->bool:
    """Explicitly false until portable package and safety proofs are accepted."""
    return False
