# V1 – API-Last-/Fair-Use-Bewertung (21.10.2026)

**Befund: NOT ACCEPTED / UNVERIFIED gegenüber Provider-Richtlinien.** Es wurden keine neuen Provideranfragen ausgelöst und keine produktiven Sessiondaten oder CLI-Caches ausgelesen. Die Bewertung basiert auf Quellcode, nicht auf HTTP-/Rate-Limit-Messdaten.

## Beobachtbare Mechanik

- `service_integration.timer_text()` plant mit `OnCalendar=*-*-* *:00,30:00` nominell **48 mögliche Startzeitpunkte pro Tag**; tatsächliche Starts sind abhängig von Aktivierung, Systemlaufzeit und systemd. `Persistent=false` holt verpasste Zeitpunkte nicht automatisch nach. Manuelle Starts können hinzukommen.
- `runtime/proton-bisync.py` führt bei jedem vollständigen Scan ein rekursives `filesystem list -j` je besuchtem Cloudordner aus. Bei **N Ordnern im gemanagten Cloudbaum** entsprechen das bei 48 Ausführungen rechnerisch **48 × N CLI-List-Aufrufe pro Tag**, solange die Verzeichnisstruktur unverändert ist. Bei N=1 sind es 48, bei N=12 sind es 576. Die Zahlen sind illustrative Szenarien, keine gemessenen Tageswerte.
- Bei Änderungen können zusätzliche `filesystem info`, `upload`, `download` oder `create-folder` folgen. Initial-Pairing, Fehlerfälle, Retries und manuelle Starts sind nicht in der Grundrechnung enthalten.
- **Ein CLI-Aufruf ist keine garantierte einzelne Proton-API-/HTTP-Anfrage.** Die interne CLI-Aufrufzahl, Retry-Verhalten, serverseitige Rate-Limits und Event-Nutzung werden mit diesem Modell nicht ermittelt. Ein Vorzeichen für Rate-Limit-Konformität kann daraus nicht abgeleitet werden.
- Ein kontinuierliches vollständiges Polling steht in potenzieller Spannung zu den offiziellen SDK-Nutzungshinweisen zu eventbasierten Verfahren und rücksichtsvollem API-Zugriff (siehe `M1A_PROVIDER_USAGE_AND_CLI_STORAGE_20261021.de.md`). Eine normative 30-Sekunden-Vorgabe wurde nicht bestätigt. Das 30-Minuten-Timerintervall ist kein Hersteller-Endorsement.

## Entscheidung für V1

**Keine Freigabe für unbeaufsichtigten Dauerbetrieb.** Vorher sind in einem strikt unabhängigen Testprofil reale Laufzeiten, Anzahl der CLI-Aufrufe pro Lauf, innere Requestlast soweit vom Provider offengelegt, Rate-Limit-/Retry-Antworten sowie Schonung der API zu dokumentieren. Für einen klar zeitlich begrenzten, manuell gesteuerten Pilot ist ein eigener risikoadaptiver Freigabeentscheid nötig; ein erfolgreiches E2E allein reicht nicht. Keine SDK-Event-Bridge als V1-Fix beauftragt.

Das Modell `v1_api_load_assessment.py` ist lesend/rechnerisch und enthält keinerlei Provider-Zugriff. **Nicht** als tatsächliche API-Lasttelemetrie ausgeben.
