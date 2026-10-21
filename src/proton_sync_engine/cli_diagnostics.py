"""Read-only Proton CLI diagnostics, with bounded, non-secret results."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import re
import subprocess

_VERSION = re.compile(r'^Proton Drive CLI cli-drive@([0-9]+\.[0-9]+\.[0-9]+)(?:\+[^\s]+)?$', re.M)
_SDK = re.compile(r'^Proton Drive SDK js@([0-9]+\.[0-9]+\.[0-9]+)(?:\+[^\s]+)?$', re.M)

class CliError(str, Enum):
    AUTH='AUTH'
    RATE_LIMIT='RATE_LIMIT'
    TIMEOUT='TIMEOUT'
    CONFLICT='CONFLICT'
    PROVIDER_ERROR='PROVIDER_ERROR'
    UNKNOWN='UNKNOWN'

@dataclass(frozen=True)
class CliVersion:
    cli: str
    sdk: str


def parse_version(output: str) -> CliVersion:
    cli=_VERSION.search(output)
    sdk=_SDK.search(output)
    if not cli or not sdk:
        raise ValueError('cli_version_unrecognized')
    return CliVersion(cli.group(1),sdk.group(1))


def detect_version(executable: str, timeout: float=8) -> CliVersion:
    """Only --version; never perform login, token access, or cloud mutations."""
    try:
        result=subprocess.run([executable,'--version'],capture_output=True,text=True,timeout=timeout,check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('cli_version_timeout') from exc
    except OSError as exc:
        raise RuntimeError('cli_version_unavailable') from exc
    if result.returncode:
        raise RuntimeError('cli_version_failed')
    return parse_version(result.stdout)


def classify_error(*, returncode: int | None, stderr: str='', timed_out: bool=False) -> CliError | None:
    """Classify without returning, persisting or printing raw provider stderr."""
    if timed_out:
        return CliError.TIMEOUT
    if returncode == 0:
        return None
    s=stderr.lower()[:4096]
    if any(x in s for x in ('429','rate limit','too many requests','retry-after')):
        return CliError.RATE_LIMIT
    if any(x in s for x in ('401','unauthorized','session expired','authentication required','not logged in')):
        return CliError.AUTH
    if any(x in s for x in ('already exists','existiert bereits','409 conflict','revision conflict')):
        return CliError.CONFLICT
    if returncode is None:
        return CliError.UNKNOWN
    return CliError.PROVIDER_ERROR
