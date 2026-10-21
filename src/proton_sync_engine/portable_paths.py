"""Explicit, fail-closed runtime paths for a future installable sync engine.

The new runtime is not wired to systemd; importing configuration only
validates paths. No cloud writes, baseline initialization or service start.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass
from pathlib import Path

from .config import EngineConfig,validated_config

@dataclass(frozen=True)
class RuntimePaths:
    """Validated locations and selected managed paths, with no user secrets."""
    base: EngineConfig
    managed_folders: tuple[str,...]
    priority_folders: tuple[str,...]
    @property
    def local_root(self):return self.base.local_root
    @property
    def mount_root(self):return self.base.mount_root
    @property
    def state_dir(self):return self.base.state_dir
    @property
    def cli_executable(self):return self.base.cli_executable
    @property
    def verify_state(self):return self.state_dir/"verified-download"
    @property
    def exclusion_settings(self):return self.state_dir/"settings.json"

def _folder(value:str)->str:
    """Ensure an explicit cloud-relative folder cannot escape its root."""
    if not isinstance(value,str) or not value or len(value)>160:
        raise ValueError("Invalid managed folder")
    if value.startswith("/") or "\\" in value or "\x00" in value:
        raise ValueError("Invalid relative folder")
    parts=value.split("/")
    if any(part in ("",".","..") or len(part)>100 for part in parts):
        raise ValueError("Unsafe folder segment")
    return value

def load_paths(config_file:Path)->RuntimePaths:
    """Load only explicit user-chosen paths from a private JSON configuration."""
    config_file=Path(config_file).expanduser()
    if not config_file.is_absolute() or config_file.is_symlink():
        raise ValueError("Configuration path must be absolute and non-symlink")
    if not config_file.is_file() or config_file.stat().st_mode & 0o077:
        raise ValueError("Configuration must exist and be private (0600)")
    settings=json.loads(config_file.read_text(encoding="utf-8"))
    if not isinstance(settings,dict):
        raise ValueError("Invalid runtime config object")
    config=validated_config(settings)
    folder_list=settings.get("managed_folders")
    priorities=settings.get("priority_cloud_folders")
    if not isinstance(folder_list,list) or not folder_list or len(folder_list)>50:
        raise ValueError("Explicit managed folders required")
    if not isinstance(priorities,list) or len(priorities)>12:
        raise ValueError("Explicit priority folders required")
    folders=tuple(_folder(p) for p in folder_list)
    priority=tuple(_folder(p) for p in priorities)
    if len(set(folders))!=len(folders) or len(set(priority))!=len(priority):
        raise ValueError("Duplicate cloud folder")
    if any("/" in top for top in folders):
        raise ValueError("Managed roots must be direct children")
    if any(p.split("/")[0] not in folders for p in priority):
        raise ValueError("Priority folder outside managed roots")
    if any(not (config.local_root/folder).is_dir() for folder in folders):
        raise ValueError("Managed local folder missing")
    return RuntimePaths(config,folders,priority)

def paths()->RuntimePaths:
    """Only an explicitly supplied configuration path can enable path loading."""
    setting=os.environ.get("PROTON_SYNC_CONFIG","")
    if not setting:
        raise RuntimeError("PROTON_SYNC_CONFIG is required; portable runtime is not installed")
    return load_paths(Path(setting))

def priority_folders(config:RuntimePaths):
    """Supply selected cloud folders without importing a developer GUI path."""
    return [tuple(name.split("/")) for name in config.priority_folders]
