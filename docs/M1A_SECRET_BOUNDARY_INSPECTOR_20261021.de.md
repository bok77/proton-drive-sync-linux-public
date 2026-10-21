# M1A – Secret-Store-Grenzprüfung, 21.10.2026

**Metadata-only PASS bei restriktiven Rechten; tatsächliche Tokenablage NICHT nachgewiesen.**

Der neue rein lesende `secret_boundary.inspect` überprüft, ob die isolierte Konfiguration eine reguläre Datei mit ausschließlich Owner-Rechten ist, ihr Konfigurationsverzeichnis nicht für andere Nutzer offen ist, ob das lokale GNOME-Keyring-Verzeichnis restriktive Rechte besitzt und ob `org.freedesktop.secrets` über den User-Bus sichtbar ist. Symlinks und zu offene Rechte führen zu `BLOCKED`. Bei fehlender Bus-Auskunft wird kein Erfolg vorgetäuscht. Der Code fragt **niemals** Schlüsselbund-Einträge oder Session-Tokens ab, entsperrt keine Schlüsselbunde und liest keine Konfigurationsinhalte.

Ein `METADATA_ONLY` bedeutet ausdrücklich nur, dass die geprüften Metadaten den Anforderungen entsprechen, nicht dass Proton seine Sessions sicher genau dort speichert. Die SDK-/CLI-spezifische Secret-Verankerung, der Unlock-/Recovery-Weg und mögliche andere Cache-/Token-Dateien bleiben M1A-Blocker vor der Alpha. Die Tests decken restriktive und unsichere Dateirechte, Symlinks sowie Nichtpreisgabe von Tokeninhalten ab.

Kein Produktivdeployment, keine Änderung von Konfigurationen oder systemd-Units. Release weiterhin NO-GO.
