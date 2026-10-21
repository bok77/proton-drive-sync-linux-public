"""Read-only V1 live test gate: never opens tokens, keyrings or cloud connections."""
from dataclasses import dataclass
from pathlib import Path
import os, stat

@dataclass(frozen=True)
class Decision:
    status: str
    blockers: tuple[str, ...]


def evaluate(*, root: Path, scope: str, independent_session_verified: bool,
             explicit_live_approval: bool, production_session_reused: bool=False) -> Decision:
    """A READY result is a precondition only, never permission for an automated upload."""
    blockers=[]
    root=Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        blockers.append('PRIVATE_ISOLATED_ROOT_REQUIRED')
    else:
        st=root.stat()
        if (st.st_mode & 0o077) or not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.getuid():
            blockers.append('ISOLATED_ROOT_OWNERSHIP_OR_MODE_UNSAFE')
        if root==Path.home() or root==Path('/mnt/example-drive') or root.is_relative_to(Path('/mnt/example-drive')):
            blockers.append('PRODUCTION_ROOT_FORBIDDEN')
    if scope!='/my-files/ProtonSync-Test':
        blockers.append('TEST_SCOPE_MISMATCH')
    if production_session_reused:
        blockers.append('PRODUCTION_SESSION_FORBIDDEN')
    if not independent_session_verified:
        blockers.append('INDEPENDENT_TEST_SESSION_UNVERIFIED')
    if not explicit_live_approval:
        blockers.append('EXPLICIT_LIVE_APPROVAL_MISSING')
    return Decision('BLOCKED' if blockers else 'READY_FOR_SEPARATE_MANUAL_REVIEW',tuple(sorted(blockers)))
