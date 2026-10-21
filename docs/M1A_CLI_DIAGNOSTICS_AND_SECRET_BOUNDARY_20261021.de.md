# M1A – CLI-Version, Fehlerklassifikation und Secret-Store-Grenze

**21.10.2026 · Teilabnahme PASS (lesender Diagnoseumfang); M1A insgesamt OPEN, Release NO-GO.**

## Anlass: Fehlerbanner vom 21.10.2026

Das Dashboard zeigte `Cloud-Vollabgleich: 1 Fehler`. Die produktiven, ausschließlich **lesend** geprüften Dienstlogs zeigten am 21.10. um 08:11:10 für `40_Knowledge/example-workflow/Current/eu_state.txt` einen abgelehnten Download `size_mismatch_23901_vs_23900`. Der vollständige Lauf endete um 08:11:26 mit einem Fehler. Danach endete der Vollabgleich um 09:08:52 **erfolgreich**, mit 10.974 validen Dateien, 0 Fehlern und 0 Konflikten; Prozess-Exit 0. Die später eingelesene `health.json` zeigte um 09:15:21 `healthy=true`, `issues=[]` sowie diesen erfolgreichen Vollabgleich. Die Warnung auf dem Screenshot war also ein älterer Stand; die Dateigrößenprüfung funktionierte wie vorgesehen. Keine Datei oder Produktiveinstellung wurde repariert oder überschrieben. Die Aktualisierungsfrequenz der Oberfläche und des Health-Checks bleibt ein möglicher UX-Nacharbeitsbereich; kein Live-GUI-Fix ist hiermit behauptet.

## CLI-Versionserkennung und typisierte Fehler

`src/proton_sync_engine/cli_diagnostics.py` ergänzt eine **lesende** `detect_version(executable)`-Prüfung mit Timeout sowie eine Parser-Funktion für CLI- und SDK-Semver. Lokal nachgewiesen: `cli-drive@0.9.0+75612299`, `js@0.22.2+75612299`. Nicht interpretierbare Ausgabe, fehlende CLI und Timeout führen zu expliziten Diagnosefehlern, niemals zu angenommener Kompatibilität.

`classify_error` liefert nur typisierte Kategorien: `AUTH`, `RATE_LIMIT`, `TIMEOUT`, `CONFLICT`, `PROVIDER_ERROR`, `UNKNOWN` oder `None` bei Exit 0. Rohfehlertexte, die Tokens enthalten könnten, werden **nicht** zurückgegeben. Test- und Integrationshinweis: Die bisherige Sync-Engine nutzt diese Funktion noch **nicht flächendeckend** in allen Operationen; ein zentraler CLI-Adapter mit konsistentem Retry-/Backoff-/Rate-Limit-Verhalten ist ein separates M1A-Gate. Exit 0 bei `-f skip` benötigt wie zuvor Readback.

## Secret-Store: lesende Metadatenprüfung

In der Fedora-Host-Benutzersitzung sind die D-Bus-Dienste `org.freedesktop.secrets` und `org.gnome.keyring` vorhanden. `~/.local/share/keyrings` hat Modus `0700`, die isolierte Konfiguration `~/.config/proton-sync-isolated/config.json` `0600`, deren Verzeichnis `0700`. Das ist ein Nachweis für **vorhandenen Secret Service und restriktive Rechte der geprüften Pfade**, nicht für die genaue Ablage von Proton-CLI-Tokens, ihre Verschlüsselungs-/Unlock-Garantie oder vollständigen Geheimnisschutz. Es wurden keine Schlüssel, Tokeninhalte, Sessionwerte oder Datei-Inhalte ausgelesen. Die tatsächliche Schlüsselreferenzierung und andere Speicherorte bleiben zu prüfen; keine Secret-Store-Abnahme ohne providerseitigen Pfadnachweis.

## Grenzen

Kein Produktivdeployment, keine neue Synchronisierung und keine systemd-Mutation; die produktiven Dienste blieben unverändert. M1-Atomizität für bestehende Cloud-Revisionen bleibt durch den fail-closed Guard gesperrt. Rechtliche/SDK-Nutzungsfreigabe weiter separat offen.
