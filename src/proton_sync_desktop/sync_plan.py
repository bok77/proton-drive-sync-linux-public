"""Human-readable synchronization routes and schedules for the current engine.

Only describes actual systemd units; it never changes the user's folder mapping.
Missing services must be shown as inactive instead of claiming a working sync.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SyncRoute:
    """A directional synchronization route and its verified periodic fallback."""

    source: str
    destination: str
    cadence_key: str
    unit: str
    action: str


ROUTES = (
    SyncRoute("local", "cloud", "event_and_five", "proton-bisync-quick.timer", "local"),
    SyncRoute("cloud_priority", "local_priority", "ten_minutes", "proton-cloud-priority.timer", "priority"),
    SyncRoute("cloud", "local", "hourly", "proton-bisync.timer", "full"),
)


def route_descriptions(language, local_path="/mnt/example-sync-root", cloud_path="Proton Drive /my-files"):
    """Build explicit source→destination labels in the requested UI language.

    Args:
        language: Either ``de`` or ``en`` (others fall back to English).
        local_path: Current Fedora synchronization root; informational only.
        cloud_path: Proton Drive location; informational only.
    Returns:
        Immutable ordered tuples of route, destination, and localized schedule.
    """
    de = language == "de"
    return (
        (local_path, cloud_path, "Bei lokaler Änderung; 5-Minuten-Rückfallprüfung" if de else "On local change; 5-minute fallback scan"),
        ("Proton Drive /my-files/00_Inbox + example-workflow/Current", local_path,
         "Alle 10 Minuten (direkte Dateien)" if de else "Every 10 minutes (direct files)"),
        (cloud_path, local_path, "Stündlicher vollständiger Abgleich" if de else "Hourly complete scan"),
    )


def unavailable_route_indices(services):
    """Report routes whose scheduled services are not active.

    This fails closed for a missing service-state key; unknown does not mean OK.
    """
    return tuple(index for index, route in enumerate(ROUTES)
                 if services.get(("local_timer", "cloud_timer", "full_timer")[index]) is not True)
