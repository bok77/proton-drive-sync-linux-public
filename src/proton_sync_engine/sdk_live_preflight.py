"""Read-only live-proof readiness: never inspect session values or invoke CLI."""
from dataclasses import dataclass
from pathlib import Path
import shutil

@dataclass(frozen=True)
class LiveReadiness:
    status: str
    blockers: tuple[str,...]

def check(*, sdk_manifest: Path, isolated_config: Path, test_scope: str | None,
          explicit_test_session_proof: bool=False, bun_executable: str='bun') -> LiveReadiness:
    problems=[]
    if shutil.which(bun_executable) is None:
        problems.append('BUN_RUNTIME_MISSING')
    # A manifest with verified pinned dependency must be reviewed separately.
    if not sdk_manifest.is_file() or sdk_manifest.is_symlink():
        problems.append('PINNED_SDK_MANIFEST_MISSING')
    if not isolated_config.is_file() or isolated_config.is_symlink():
        problems.append('ISOLATED_CONFIG_MISSING')
    if not test_scope or test_scope != 'ProtonSync-Test':
        problems.append('TEST_SCOPE_NOT_APPROVED')
    if not explicit_test_session_proof:
        problems.append('ISOLATED_AUTH_NOT_VERIFIED')
    # Even perfect inputs only permit manual review, not automatic activation.
    if not problems:
        problems.append('HUMAN_LIVE_PROOF_GATE_REQUIRED')
    return LiveReadiness('BLOCKED',tuple(sorted(problems)))
