"""Single safe subprocess boundary for the portable Proton CLI.

No automatic retries of writes. Provider output is suppressed on failure so
it cannot leak sessions or personal paths to the engine event journal.
"""
from __future__ import annotations
from dataclasses import dataclass
import subprocess
from .cli_diagnostics import classify_error, CliError

@dataclass(frozen=True)
class CliResult:
    returncode: int
    stdout: str = ''
    stderr: str = ''
    error_class: CliError | None = None


def execute(executable: str, *args: str, timeout: int = 300) -> CliResult:
    try:
        result=subprocess.run([executable,*args],capture_output=True,text=True,timeout=timeout,check=False)
    except subprocess.TimeoutExpired:
        return CliResult(124,stderr='CLI_TIMEOUT',error_class=CliError.TIMEOUT)
    except OSError:
        return CliResult(127,stderr='CLI_UNAVAILABLE',error_class=CliError.PROVIDER_ERROR)
    category=classify_error(returncode=result.returncode,stderr=result.stderr or result.stdout)
    if category is not None:
        return CliResult(result.returncode or 1,stderr='CLI_'+category.value,error_class=category)
    return CliResult(0,stdout=result.stdout)
