#!/usr/bin/env python3
"""Explicit exclusion rules. Never retroactively hide tracked files."""
import fnmatch,json
from pathlib import Path
from proton_sync_engine.portable_paths import paths as _load_runtime_paths
_runtime=_load_runtime_paths()
CONFIG=_runtime.exclusion_settings
ROOT=_runtime.local_root
DEFAULT={"exclusions":{"file_patterns":[],"directory_names":[],"custom_relative_prefixes":[]}}
def settings():
    try:
        d=json.loads(CONFIG.read_text())
        e=d["exclusions"]
        if not all(isinstance(e.get(key),list) for key in ("file_patterns","directory_names","custom_relative_prefixes")):
            raise ValueError("invalid exclusions")
        return d
    except FileNotFoundError:
        raise RuntimeError("Proton sync exclusion settings missing; fail closed")
def excluded(rel, directory=False, tracked=False):
    if tracked:return False
    e=settings()["exclusions"]
    parts=Path(rel).parts
    if not parts:return False
    if any(segment in e["directory_names"] for segment in parts):return True
    if any(rel==prefix or rel.startswith(prefix.rstrip("/")+"/") for prefix in e["custom_relative_prefixes"]):return True
    if not directory and any(fnmatch.fnmatchcase(parts[-1],pattern) for pattern in e["file_patterns"]):return True
    return False
