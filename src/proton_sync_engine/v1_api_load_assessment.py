"""Read-only, model-level V1 CLI invocation estimate. Not provider API telemetry."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ScanEstimate:
    scheduled_runs_per_day: int
    directory_list_calls_per_run: int
    baseline_list_calls_per_day: int
    provider_request_count_known: bool = False


def estimate(*, interval_minutes: int, cloud_directories: int) -> ScanEstimate:
    """An upper bound on timer *opportunities*, not on actual provider requests.

    List operations count only filesystem/list CLI calls. No hidden CLI HTTP
    traffic, extra file calls, retries, manual starts or caching are included.
    """
    if type(interval_minutes) is not int or interval_minutes < 1 or 1440 % interval_minutes:
        raise ValueError('Positive interval dividing one day required')
    if type(cloud_directories) is not int or cloud_directories < 1:
        raise ValueError('At least one cloud directory required')
    runs = 1440 // interval_minutes
    return ScanEstimate(runs, cloud_directories, runs * cloud_directories)
