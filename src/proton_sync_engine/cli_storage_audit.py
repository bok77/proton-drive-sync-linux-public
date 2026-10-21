"""Only file metadata for the official CLI's local cache; never open contents."""
from dataclasses import dataclass
from pathlib import Path
import os
import stat

@dataclass(frozen=True)
class CliStorageAudit:
    directory_private: bool
    unsafe_entries: tuple[str,...]
    status: str


def inspect(path: Path) -> CliStorageAudit:
    root=Path(path)
    if root.is_symlink() or not root.is_dir():
        return CliStorageAudit(False,('root_missing_or_symlink',),'BLOCKED')
    meta=root.stat()
    root_private=meta.st_uid==os.getuid() and not(meta.st_mode & 0o077)
    problems=[]
    try:
        for entry in root.iterdir():
            # Never read a directory or file: check only lstat metadata.
            info=entry.lstat()
            if entry.is_symlink() or info.st_uid!=os.getuid() or (info.st_mode & 0o077):
                problems.append('unsafe_entry_permissions')
            if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                problems.append('unexpected_entry_type')
    except OSError:
        problems.append('listing_unavailable')
    # Never expose filenames: even names can contain personal information.
    return CliStorageAudit(root_private,tuple(sorted(problems)),'METADATA_ONLY' if root_private and not problems else 'BLOCKED')
