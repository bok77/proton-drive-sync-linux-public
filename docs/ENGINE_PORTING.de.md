# Portierung der Sync-Engine – Freigabestand

**Status: IN ARBEIT – NICHT INSTALLIERBAR – NICHT FÜR DEN RELEASE FREIGEGEBEN.**

Die produktiv eingesetzten Skripte wurden am 20. Oktober 2026 als nicht ausführbare Referenzquellen nach `src/proton_sync_engine/reference/` und `packaging/reference/` übernommen. Dadurch liegt der Quellcode der existierenden Zwei-Wege-Engine erstmals zusammen mit der GNOME-Anwendung im Projekt. **Die aktive Fedora-Installation wurde nicht umgestellt.**

Die neue Konfigurationsschicht `src/proton_sync_engine/config.py` verlangt explizite Pfade für lokales Verzeichnis, Mount-Grenze, privaten State und Proton-CLI. Sie blockiert fehlende Mounts, Symlinks, Pfade außerhalb der Mount-Grenze, unerlaubte State-Verzeichnisse und nicht ausführbare CLI-Dateien. Die Portierung ist noch nicht mit der produktiven Engine verdrahtet.

## Verbindliche nächste Schritte

1. **Pfadunabhängigkeit:** Feste Fedora-Pfade, Imports aus `~/.local/bin` und fest hinterlegte Ordnerlisten beseitigen. Installation ohne Datenmigration oder Löschrisiko nachweisen.
2. **Einheitliches Paket:** Zwei-Wege-Engine, lokaler Dateiwächter, SQLite-Warteschlange, Cloud-Polling und verifizierte Downloads zu einer installierbaren Paketstruktur zusammenführen. Keine Zugangsdaten oder Hersteller-Binaries einchecken.
3. **Explizite Erstaktivierung:** Ordner, Prüfintervalle und Grenzen anzeigen; keine stillschweigende Baseline erzeugen oder akzeptieren.
4. **Sicherheitsmatrix:** Gleichzeitige Änderungen, Offline/Neustart, Mountverlust, Symlinks, Pfad-Traversal, fehlende Berechtigung, beschädigte Downloads, Queue-Überlauf und wiederherstellbare Löschungen mit synthetischen Daten prüfen.
5. **Saubere Fedora-Neuinstallation:** Erstinstallation, Verbindung, Sync, Updates und Deinstallation unabhängig vom Entwicklungsrechner demonstrieren. Andere Distributionen sind weiterhin **nicht getestet** und eine Community-Aufgabe.
6. **GitHub-Reife:** Automatische CI-Tests, Sicherheits- und Lizenzprüfung, nachvollziehbarer Release-Prozess, öffentliche Developer-Preview-Kennzeichnung und ausdrückliche Freigabe.
7. **E-Mail nach Release:** Erst nach öffentlichem GitHub-Release und bestätigten Empfängern den Link versenden; siehe `RELEASE_COMMUNICATION.de.md`.

Die vorhandene `install-preview.sh` installiert bisher **nur die GNOME-Oberfläche**. Die portierte Engine ist aktuell eine Referenzkopie, noch kein nutzbares Installationspaket. Der nächste Meilenstein ist daher die kontrollierte Auflösung der festen Pfade und Laufzeitimporte.

## Schritt 2: Pfadabhängigkeiten der Runtime gelöst – 20. Oktober 2026

Unter `src/proton_sync_engine/runtime/` liegen jetzt **zwölf nicht ausführbare Engine-Kandidaten**, aus den unveränderten Referenzquellen reproduzierbar über `scripts/stage_portable_runtime.py` abgeleitet. Sie laden Module aus dem eigenen Paketverzeichnis statt aus `~/.local/bin`, verwenden validierte `local_root`, `mount_root`, `state_dir` und `cli_executable` anstelle fester Fedora-Pfade und beziehen die zu verwaltenden sowie priorisierten Ordner explizit aus der Konfiguration.

`portable_paths.py` fordert `PROTON_SYNC_CONFIG` mit privater JSON-Datei (0600), validiert die Pfad- und Mount-Grenzen und verweigert die Nutzung bei fehlenden oder ungültigen Ordnern. Es gibt **noch keinen Installer, keine Erstinitialisierung und keine produktiv verdrahtete Runtime**. Die generierten Kandidaten dürfen vor einer vollständigen Paket-, Betriebs- und Sicherheitsabnahme nicht ausgeführt oder mit systemd aktiviert werden. Die Fedora-Dienste verwenden weiterhin ausschließlich die alten produktiven Pfade.

Ein Bug der laufenden Umgebung wurde separat behoben: Der volle stündliche Scan nutzt nicht mehr `flock -E 0 -n`, das bei einer belegten Sperre ohne Durchführung erfolgreich zurückkehrte. Er wartet jetzt bis zu 1800 Sekunden auf die Sperre und liefert bei Timeout Exit 75. Gezielte Lock-Tests prüfen den Wartemechanismus und die Fehlerkennung. Ein erfolgreicher stündlicher Live-Lauf **nach** diesem Fix muss noch über ein neues `run_end` verifiziert werden.

**Als Nächstes:** Runtime-Entry-Points und systemd-Units aus einer vollständigen Installationskonfiguration erzeugen, mit ausdrücklicher Erstaktivierung und ohne die bestehende Fedora-Installation zu überschreiben. Danach synthetische End-to-End- und Uninstall-Tests auf isolierter Installation. Erst danach Releaseentscheidung.

## Installationsvorschau und GNOME-Starter – 20. Oktober 2026

Der vorbereitete Installer unter `src/proton_sync_engine/install_plan.py` bietet eine ausschließlich lesende Installationsplanung und die Erzeugung von drei **nicht aktivierbaren** systemd-Servicevorlagen in einem neuen isolierten Testverzeichnis. Jede Einheit enthält sowohl `ExecCondition=/usr/bin/false` als auch `ExecStart=/usr/bin/false`. `verify_stage` kontrolliert die Vorlage nach dem Schreiben; `unstage` entfernt nur ein unverändertes, eindeutig identifizierbares Preview-Verzeichnis. Es werden weder systemd-Benutzerverzeichnisse verändert noch Daten übertragen oder Baselines angelegt. Ein vollständiger Installer sowie Erst-Pairing, Aktivierung und Rückbau realer Dienste bleiben offen.

Der bestehende GNOME-GUI-Starter wurde separat repariert: Die Desktop-Datei heißt jetzt entsprechend der tatsächlichen App-ID `io.github.protondrivesync.Fedora.desktop`, das Icon und `StartupWMClass` verwenden dieselbe ID. Der alte eigene Starter wurde mit Sicherung entfernt, ohne fremde Starter zu löschen. Ein Start über `gtk-launch io.github.protondrivesync.Fedora` wurde nachgewiesen.

## Testinstallation mit ausdrücklicher Freigabe – 20. Oktober 2026

Ein zusätzlicher isolierter Installationspfad liegt unter `src/proton_sync_engine/test_install.py`. `install_test` erfordert die exakte Freigabe `I APPROVE ISOLATED TEST INSTALL`, einen zuvor verifizierten Preview-Stand und zwei neue, voneinander getrennte Verzeichnisse ausschließlich unter einem temporären Testbereich. Bestehende Verzeichnisse werden niemals überschrieben. Installiert werden nur drei **nicht startfähige** Servicevorlagen mit `ExecCondition=/usr/bin/false` und `ExecStart=/usr/bin/false`. Es gibt weder eine Verbindung zum echten Benutzer-systemd noch den Aufruf der Sync-Runtime.

`verify_test_install` prüft Dateinamen, den signifikanten Inhalt und SHA-256-Nachweise. `uninstall_test` löscht ausschließlich diese unveränderten Testartefakte und scheitert bei fremden oder manipulierten Dateien, ohne Benutzerdaten zu entfernen. Automatisierte synthetische Tests decken Zustimmung, Verweigerung, Datenpfade, Manipulation und Rückbau ab.

**Grenze:** Dies ist ein auf den Dateisystem- und Unit-Vertrag beschränkter Installer-Integrationsnachweis, **kein vollständiger Cloud-Sync-End-to-End-Beweis**. Für den produktiven Installer fehlen weiterhin ein eigenständiger ausführbarer Runtime-Einstieg, eine sichere Erstverknüpfung mit Proton, überprüfbare Systemd-Aktivierung und Neustarttests auf einer separaten Fedora-Installation. Öffentliche Freigabe bleibt gesperrt.

## Portierte Engine: synthetischer End-to-End-Nachweis (20. Oktober 2026)

Die echte portierte `proton-bisync.py`-Ablauflogik wird in `tests/test_portable_engine_e2e.py` mit einer vollständig synthetischen Cloud und temporären lokalen Dateien geprüft. Das getestete Protokoll umfasst lokale Änderungen und neue Dateien mit Upload-Readback, Cloud-Änderungen und neue Dateien mit verifiziertem Download, einen zweiten idempotenten Lauf, konkurrierende Änderungen ohne Überschreibung sowie fehlgeschlagene Downloads ohne lokale Datenverluste. Ein kombinierter Test führt vorbereitete isolierte Dienstdateien durch Installation, Readback, Engine-Simulation und verifizierten Rückbau. **Alle Cloud-Operationen werden simuliert; es wird kein echter Proton-Zugriff ausgelöst und kein systemd-Dienst aktiviert.**

Ein Portierungsdefekt wurde korrigiert: `proton-verified-download.py` verwendet jetzt `_runtime.cli_executable` aus der expliziten Konfiguration statt fälschlich ein CLI im Paketordner vorauszusetzen. Der Generator ist vom Rechnerpfad unabhängig. Die portable Vollabgleich-Engine verweigert ohne bestehende geprüfte Baseline bereits vor Mount-, Cloud- und Dateischreibzugriffen mit Exit 42 den Start; sie darf **keine automatische Erst-Pairing-Baseline erzeugen**. Referenzquellen und produktive Fedora-Dienste wurden dadurch nicht verändert.

Noch nicht abgenommen: explizite und verifizierte Erst-Pairing-Prozedur, echte Cloud-CLI-Kompatibilität, kontrollierte systemd-Aktivierung, unabhängige Fedora-Installation, Symlink-/Rename-/Delete-/Offline-/Crash- und Multi-Datei-Tests sowie Backup/Rollback. Release-Gate bleibt gesperrt.


## Pairing-Härtung und Installer-Anbindung – 20. Oktober 2026

Der Pairing-Freigabepfad kontrolliert nun die geprüfte lokale und entfernte Bestandsaufnahme **vor und nach** dem erstmaligen Schreiben der Baseline. Bei nachweisbarer Drift wird die neu erzeugte Baseline zurückgenommen und die Freigabe verweigert. Der Rückbau ist an die Inode-Identität der selbst erzeugten Datei gebunden und darf keine später ersetzte fremde Datei löschen. Die Prüfschritte sind durch Negativtests für konkurrierende Cloud-Änderungen nach dem Schreiben abgedeckt.

Über `src/proton_sync_engine/installer_pairing.py` können Installationskomponenten eine lesende Vorschau und eine gesonderte Freigabe mittels explizitem Adapter aufrufen. Existierende Baselines und unsichere State-Verzeichnisberechtigungen werden abgewiesen. Die Anbindung startet weder systemd-Dienste noch führt sie produktive Cloud-Synchronisierung aus.

**Grenze:** Ein echter atomarer Cross-System-Snapshot ist mit den bislang geprüften Proton-CLI-Primitiven nicht nachgewiesen. Änderungen direkt nach der abschließenden Nachprüfung können nicht ausgeschlossen werden. Darum bleiben Runtime-Aktivierung, echter Proton-Login und öffentlicher Release gesperrt. Der Adapter ist in Tests simuliert, noch keine vollständige GUI-Seite.
