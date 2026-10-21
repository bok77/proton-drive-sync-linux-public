# Zustandsabhängige GNOME-Dienststeuerung (21.10.2026)

MVP-Scope: ausschließlich GNOME-Oberfläche des isolierten ProtonSync-Test-Dienstes, keine neue Synchronisationsfunktion. Die vorhandenen produktiven Proton-Dienste bleiben außerhalb dieses UI-Pfades.

- Der Status wird vom vorhandenen Backend `user_service_lifecycle.status()` gelesen. Unklare/ungültige Zustände blockieren Aktionen.
- Abhängig vom bestätigten systemd-Zustand gibt es eine Hauptaktion und höchstens eine Nebenaktion: nicht installiert → installieren; installiert/inaktiv → aktivieren oder entfernen; aktiv → pausieren oder entfernen.
- Vor **jeder** Aktion erscheint ein eigener deutscher/englischer Bestätigungsdialog, Standardantwort ist Abbrechen. Erst nach expliziter Bestätigung wird der bestehende Backend-Aufruf mit seinem unveränderten exakten Freigabetoken ausgeführt. Keine automatische Installation/Aktivierung.
- Backend-Gates bleiben erhalten: Manifest-Prüfsummen, isolierter Testordner, kein produktives `/mnt/example-drive`, private Konfiguration, Pairing-Baseline und unveränderte systemd-Unit-Prüfungen.
- Nach jeder erfolgreichen Operation wird der wirkliche Zustand erneut gelesen. Fehler werden sichtbar und blockieren weitere Aktionen.

Nachweise: 303/303 unittest PASS; neuer Bundle-Build (51 Dateien), separate Installation, Self-Test L10N_OK 62 / BACKEND_OK 5. Die isolierten MVP-Units sind nicht installiert; es erfolgte keine Dienstaktivierung. Die visuelle Prüfung der neuen Oberfläche und die tatsächliche Klick-Abnahme bleiben offen. Öffentlicher Release: NO-GO.
