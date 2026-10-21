# Fedora Proton Drive Sync – MVP Acceptance Gate (21.10.2026)

**Entscheidung: MVP RELEASE BLOCKED / NOT ACCEPTED.** Bereits erfolgreiche Teilnachweise werden anerkannt, aber nicht mit einer vollständigen Endnutzer- oder Veröffentlichungsabnahme verwechselt.

| Prüffeld | Stand | Evidenz / fehlender Schritt |
|---|---|---|
| Automatisierte Regression | PASS | 303/303 via `PYTHONPATH=src python3 -m unittest discover -s tests -q` am 21.10. |
| Sicheres isoliertes Pairing und portables Upload/Download | PASS (begrenzter Scope) | Isolierter echter Engine-Proof, `REAL_ENGINE_BIDIRECTIONAL_PROOF.de.md`. Keine Aussage über alle Sonderfälle. |
| GNOME Einrichtungsoberfläche – Darstellung | PASS (Screenshot) | Nutzer-Screenshot: abgeschlossene Erstverbindung, Testhinweis, `Nicht installiert`, eine primäre Aktion. |
| GNOME Bestätigungsdialoge – Klick-End-to-End | **OFFEN** | Dialog öffnen, Abbrechen ohne Mutation, explizite Bestätigung und Zustandswechsel über die GUI noch nicht verifiziert. |
| Isolierter realer systemd-Lifecycle | PASS | Installieren → aktivieren → pausieren → entfernen samt Status-Readback, `MVP_STATEFUL_LIFECYCLE_LIVE_PROOF_20261021.de.md`. Keine Produktiv-Unit verändert. |
| Synthetische Restart-/Offline-/Sicherheitsfälle | PARTIAL PASS | `MVP_FAILURE_PROFILE_PROOF.de.md`; weitere Lösch-, Rename- und konkurrierende Remote-Änderungsfälle sowie Recovery-Auswirkungen bleiben Release-Gates. |
| Installation/Deinstallation in unabhängig eingerichtetem Fedora | **OFFEN** | Bisher nur weiterer Benutzer auf demselben Rechner, keine unabhängige VM/Host-Abnahme. |
| Accessibility | **OFFEN** | Tastaturbedienbarkeit, Dialogfokus und Screenreader der finalen GNOME-Seite prüfen. |
| CI | **OFFEN** | Keine `.github/workflows` in diesem Repository gefunden, lokaler Test ist keine CI-Abnahme. |
| Paket-Upgrade/-Downgrade und Rollback | **OFFEN** | Installierbarer isolierter Kandidat vorhanden, aber kein belastbarer Upgrade-/Downgrade-Nachweis. |
| Öffentlicher Release | **NO-GO** | Keine Freigabe ohne belastbare Closure der offenen Gates. |

Die installierte lokale Vorschau lief beim Test; sie wurde nicht per Remote-GUI-Klick gesteuert. Ein Remote-Terminal ohne DISPLAY/WAYLAND_DISPLAY und ohne GUI-Automation darf nicht als GUI-E2E-Nachweis ausgegeben werden.

**Nächste priorisierte Schritte ohne Scope-Ausweitung:** (1) GNOME-Dialog und Accessibility manuell oder instrumentiert abnehmen, (2) echte unabhängige Fedora-Neuinstallation mit Deinstallation und Rollback, (3) risikobasierte fehlende Engine-/Cloud-Fehlerfälle und automatisierten CI-Testlauf prüfen. Danach erneut entscheiden; keine zusätzlichen Komfortfunktionen.

## Zusatzprüfung 21.10.2026 (nachgelagert)

- **CI-Konfiguration hinzugefügt, Cloud-CI noch NICHT verifiziert:** `.github/workflows/fedora-mvp-tests.yml` nutzt einen Fedora-42-Container, installiert die GTK/libadwaita-Abhängigkeiten und führt `unittest` + Syntaxcheck aus. Lokal 305/305 PASS, Syntaxcheck PASS. Ein GitHub-Actions-Lauf fehlt; CI-Gate bleibt daher offen.
- **Dialog-Sicherheitsvertrag lokal geprüft:** zwei zusätzliche statische Prüfungen für Default-Abbrechen, explizite Freigabeantwort, Fensterzuordnung und getrennte Backend-Tokens. Keine tatsächlichen UI-Klicks oder Screenreader-Prüfung; GUI-E2E bleibt offen.
- **Paket-Rückbau lokal testbar:** isolierter Build/Install/Verify/Uninstall für zwei Kandidaten im temporären Verzeichnis. Kein echtes versionsübergreifendes Upgrade/Downgrade und kein externer Fedora-Host; Release-Gate bleibt offen.

## Folgeprüfung 21.10.2026 – CI und unabhängiges Fedora

- Lokales Repository hat **keinen Git-Remote** (`git remote -v` leer). Die GitHub-Anmeldung des Hosts ersetzt keine Repository-Zuordnung. Ein echter GitHub-Actions-Run ist deshalb ohne eine explizite Remote-Zuordnung nicht möglich; kein Remote wurde geraten oder neu angelegt.
- CI-Container-Basis von Fedora 42 auf Fedora 44 aktualisiert. Isolierter Podman-Fedora-Test ist eine zusätzliche Linux-Umgebungsprüfung, **keine** unabhängige Desktop-/VM-Installation und **kein** GitHub-Actions-Run.
- Der Remote-Terminalkontext verfügt nicht über GUI-Automation (kein `DISPLAY`, `WAYLAND_DISPLAY`, `xdotool` oder `ydotool`); bestehende GNOME-Dialoge sind dadurch nicht zuverlässig klickprüfbar. Dialog-/Accessibility-Gate bleibt OFFEN.

## Fedora-44-Container-Abnahme – abgeschlossen (21.10.2026)

- Ausgeführt via rootless Podman im vorhandenen offiziellen Image `registry.fedoraproject.org/fedora:latest`; Paketmanager bestätigte Fedora-44-Pakete. GTK4, libadwaita, PyGObject und Python3 wurden innerhalb des temporären Containers installiert. Das Projekt wurde **read-only** ins Container-Dateisystem eingehängt.
- Tatsächlicher Befehl: `PYTHONPATH=src python3 -m unittest discover -s tests -q` im Container. **305 Tests PASS, Exit 0.** Container lief anschließend mit `--rm` aus.
- Dies bestätigt, dass die Tests in einer isolierten Fedora-44-Laufzeit laufen. Es ersetzt weder das Desktop-GUI-E2E-Gate noch eine unabhängige Fedora-Desktop-/VM-Installation oder einen GitHub-Actions-Workflow-Run.

## Zusätzliche synthetische Datenerhaltungsprüfungen

Zwei zusätzliche E2E-Regressionsfälle für Cloud-Löschung nach Pairing und lokale Umbenennung wurden mit der isolierten Fake-CLI eingeführt. Beide bestätigen, dass die jeweils andere Originaldatei nicht stillschweigend entfernt wird. Dies ist **keine** reale Nebenläufigkeits- oder Proton-Cloud-Transaktionsgarantie. CI und unabhängiger Desktop-Host bleiben offen.

## GUI-/Clean-Host-Gate, ergänzende Prüfung 21.10.2026

Siehe `MVP_GUI_INDEPENDENT_FEDORA_ACCEPTANCE_20261021.de.md`. Echter GitHub-CI-Lauf `39551899761`: SUCCESS. Isolierter Clean-HOME-Installations-/Deinstallationstest erneut 3/3 PASS. Eine unabhängig gebootete Fedora-Desktopumgebung und GNOME-Klick-/Screenreader-Prüfungen sind noch nicht nachgewiesen; diese Gates bleiben BLOCKED, nicht PASS.

## Unabhängige Fedora-VM – abgeschlossener technischer Proof (21.10.2026)

Siehe `MVP_FEDORA44_VM_LIVE_PROOF_20261021.de.md`: Fedora-44-KVM-Gast, 323/323 Tests PASS, frischer Build/Install/Selbsttest/Uninstall PASS und Xvfb-GTK-Selbsttest PASS. Der zuvor offene unabhängige **headless** Fedora-Installationsnachweis ist nun erbracht. GNOME-Dialogbedienung, Accessibility sowie versionsübergreifendes Upgrade/Downgrade und realistische Remote-Cloud-Race-Tests bleiben offen; Release weiterhin NO-GO.

## GTK-Dialogprüfung im unabhängigen Fedora-44-Gast (21.10.2026)

Drei echte GTK/libadwaita-Dialog-Signaltests unter Xvfb erfolgreich; siehe `MVP_GTK_DIALOG_PROOF_20261021.de.md` und `scripts/probe_gtk_mvp_dialog.py`. Bestätigung und Abbruch mit Mock-Backend nachgewiesen. Manuelle Tastatur-/Screenreaderprüfung und echtes GNOME-E2E-Gate bleiben offen.

## Konsolidierter Prüfstand und verbleibende Blocker (21.10.2026)

Aktuelle Produktplanung: `VISION.md` und `MVP.md`; aktualisierte Evidence und offene Sicherheitsgrenzen: `docs/MVP_REMAINING_GATES_20261021.de.md`. Preflight-Revisionsdrift und manifestierte A→B→A-Remove/Install-Folge wurden synthetisch geprüft. Kein atomarer Cloud-Race-Schutz oder aktiv betriebener Upgrade-/Rollback daraus abgeleitet; GNOME-Screenreader- und GUI-Live-Lifecycle bleiben offen. Release weiterhin **NO-GO**.
