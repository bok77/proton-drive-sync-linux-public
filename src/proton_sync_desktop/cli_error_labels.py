"""Safe user-facing labels for classified CLI failures; no raw provider text."""
from proton_sync_engine.cli_diagnostics import CliError

_MESSAGES={
 'de': {
  CliError.AUTH:'Proton-Anmeldung erforderlich. Sitzung in der offiziellen CLI prüfen.',
  CliError.RATE_LIMIT:'Proton begrenzt derzeit Anfragen. Später erneut prüfen.',
  CliError.TIMEOUT:'Proton hat nicht rechtzeitig geantwortet. Kein automatischer Schreib-Retry.',
  CliError.CONFLICT:'Konflikt erkannt. Dateien bleiben bis zur Prüfung unverändert.',
  CliError.PROVIDER_ERROR:'Proton-CLI-Aufruf fehlgeschlagen. Details im sicheren Status prüfen.',
  CliError.UNKNOWN:'CLI-Ergebnis unklar. Keine automatische Freigabe.',
 },
 'en': {
  CliError.AUTH:'Proton sign-in required. Check the official CLI session.',
  CliError.RATE_LIMIT:'Proton is limiting requests. Try again later.',
  CliError.TIMEOUT:'Proton did not respond in time. No automatic write retry.',
  CliError.CONFLICT:'Conflict detected. Files remain unchanged pending review.',
  CliError.PROVIDER_ERROR:'Proton CLI operation failed. Check the safe status.',
  CliError.UNKNOWN:'CLI result is unclear. No automatic approval.',
 },
}

def error_label(category: str | CliError | None, language: str='de') -> str:
    try:
        typed=CliError(category)
    except (ValueError,TypeError):
        typed=CliError.UNKNOWN
    return _MESSAGES['de' if language=='de' else 'en'][typed]


def safe_pairing_error(reason: object, language: str='de') -> str:
    """Map only allowlisted classified codes; never reflect unknown raw text."""
    if isinstance(reason,str) and reason.startswith('CLI_'):
        code=reason[4:]
        if code in CliError._value2member_map_:
            return error_label(code,language)
    return error_label(CliError.UNKNOWN,language)
