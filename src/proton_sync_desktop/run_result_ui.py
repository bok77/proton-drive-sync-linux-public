"""Shared GTK result row for both existing V1 wizard and isolated alpha UI."""
import gi
gi.require_version("Adw", "1")
from gi.repository import Adw


def make_result_row(language):
    """Reuse the original result presentation across safe sync entry points."""
    return Adw.ActionRow(title='Noch kein einzelner Testlauf' if language=='de' else 'No single run yet')


def show_result(row, evidence, language):
    """Display authoritative run_end evidence, never a start acknowledgement."""
    status=evidence['status']
    if status=='PENDING':
        row.set_title('Test läuft · Abschluss wird geprüft' if language=='de' else 'Run pending · checking result')
        return False
    if status=='SUCCESS':
        row.set_title('Test abgeschlossen' if language=='de' else 'Test complete')
    elif status=='ATTENTION':
        row.set_title('Test mit Konflikten/Fehlern' if language=='de' else 'Run with conflicts/errors')
    else:
        row.set_title('Ergebnis unklar' if language=='de' else 'Unverified result')
    if status in ('SUCCESS','ATTENTION'):
        row.set_subtitle(f"Upload: {evidence['uploaded']} · Download: {evidence['remote_downloaded']} · "
                         f"Konflikte: {evidence['conflicts']} · Fehler: {evidence['errors']}")
    return True
