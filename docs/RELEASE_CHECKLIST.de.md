# Freigabekriterien für die öffentliche Veröffentlichung

Status: **NICHT FÜR EINEN ÖFFENTLICHEN RELEASE FREIGEGEBEN**.

Das Repository enthält momentan eine GNOME-Alpha-Oberfläche und einen lesenden Adapter zur bestehenden lokalen Fedora-Installation. Die produktive Sync-Engine ist noch getrennt.

## Verbindliche Abnahmekriterien

- [ ] Installation, Konfiguration, Aktualisierung und Deinstallation auf einem frischen Fedora-Rechner ohne feste Benutzernamen, Datenpfade oder Konten.
- [ ] Eigenständiges Paket aus getesteter Zwei-Wege-Engine und offizieller Proton-Drive-CLI-Anbindung.
- [ ] Automatisierte Positiv- und Negativtests: gleichzeitige Änderungen, Umbenennen, Verschieben, lokale/Cloud-Löschung, Offline/Online, Symlinks, Lesefehler, verlorene Mounts, unvollständige Dateien, Queue-Überlauf, Absturz und Neustart.
- [ ] Nachweis für wiederherstellbare Löschungen und Blockade bei fehlendem Mount.
- [ ] Vollständiger Wiederabgleich ohne Datenverlust an repräsentativen synthetischen Dateibäumen.
- [ ] Sicherheitsprüfung für Subprozesse, Pfad-Traversal, Symlinks, fremde Dateinamen und Zugangsdaten.
- [ ] Visuelle und barrierefreie GNOME-Abnahme; Deutsch und Englisch bei schmalen Fenstern prüfen.
- [ ] CI, Dokumentation, Codescans, versionierte Releases und reproduzierbare Installation.
- [ ] Lizenzen fremder Bestandteile und Markennutzung klären.
- [ ] Abschließende ausdrückliche Release-Freigabe.

Keine privaten Nutzerdaten einchecken. Öffentliche GitHub-Sichtbarkeit erst nach Freigabe aktivieren.

## Linux and cloud monitoring release requirements / Freigabeanforderungen
- [ ] Installation und Synchronisierung auf mindestens zwei weiteren Linux-Distributionen testen; bislang wurde nur Fedora geprüft. Community-Berichte über `.github/ISSUE_TEMPLATE/distribution-test.md` erfassen.
- [ ] Cloud-Änderungen auch außerhalb priorisierter Ordner zuverlässig erkennen; entweder überprüftes Polling beibehalten oder einen unterstützten Ereignis-/Änderungsfeed nachweisen, bevor Echtzeitüberwachung behauptet wird.

## Nach der Veröffentlichung – verbindliche Kommunikation
- [ ] Öffentlichen GitHub-Link verifizieren.
- [ ] Empfänger und E-Mail-Text bestätigen lassen.
- [ ] E-Mail mit dem Release-Link versenden und Versandnachweis prüfen.
- [ ] Dokumentation: docs/RELEASE_COMMUNICATION.de.md

## Zwischenstand Engine-Portierung (20. Oktober 2026)
- [x] Produktive Engine-Quellen als nicht ausführbare Referenz im Repository inventarisieren, ohne Zugangsdaten oder Gerätestand.
- [x] Erste fail-closed-Konfigurationsprüfung für explizite Pfade, Mount-Grenzen und synthetische Testdaten.
- [ ] Feste Fedora-Pfade und Home-Imports auflösen und die portable Runtime verdrahten.
- [ ] Runtime auf unabhängiger Testinstallation installieren, betreiben und sicher deinstallieren.

## Lauf- und Portierungsbefund 09:00 Uhr (20. Oktober)
- [x] Falsch erfolgreichen übersprungenen Vollabgleich durch `flock -E 0 -n` erkannt und auf wartende Sperre mit Fehlercode bei Timeout korrigiert.
- [x] Portable Runtime-Kandidaten aus Referenzquellen erzeugt; feste Pfade und direkte Home-Imports ersetzt; private Konfiguration mit Negativtests abgesichert.
- [ ] Neuen vollständigen Live-Run nach der Sperrkorrektur anhand von `run_end` abnehmen.
- [ ] Portable Kandidaten zu einem auf einem neuen Rechner getesteten, installierbaren Paket machen. Noch kein Release.

## Isolierter Installer-Nachweis (20. Oktober 2026)
- [x] Explizite Freigabe für das Installieren ausschließlich nicht aktivierbarer Testdienstdateien.
- [x] Keine Überschreibung vorhandener Verzeichnisse; SHA-256-Readback und strikter Rückbau bei unbekannten Dateien.
- [ ] Echte Runtime mit isolierten synthetischen Cloud-/Dateitests sicher installieren und ausführen.
- [ ] Benutzer-systemd-Aktivierung, Rücknahme und unabhängige Fedora-Neuinstallation abnehmen.

## Synthetische Engine-Integration (20. Oktober 2026)
- [x] Portierte Engine mit simuliertem Proton-CLI, lokalen synthetischen Daten und Prüfsummen-Readback getestet.
- [x] Upload, Download, Neuanlage, Konflikt, Downloadfehler und idempotenter Folgelauf nachgewiesen.
- [x] Testinstallation, Engine-Simulation und geschützter Rückbau in einem Szenario kombiniert.
- [x] Fehlende Erst-Baseline blockiert vor Cloud-Lesen und Dateischreiben.
- [ ] Reales Proton-CLI in isoliertem Testkonto, Erst-Pairing, systemd-Laufzeit und alle Ausfall-/Löschtests nachweisen.


## Erweiterte Pairing-Sicherheitsprüfung – 20. Oktober
- [x] Vor- und Nachprüfung der Baseline-Freigabe mit Rücknahme bei erkannter Drift und eigentumsgebundenem Dateirückbau.
- [x] Pairing-Vorschau und explizite Zustimmung als gesonderte Installer-Funktionen mit synthetischen Negativtests.
- [ ] Transaktionsäquivalente Garantien beziehungsweise konservative Aktivierung bei konkurrierenden Cloud-Änderungen beweisen.
- [ ] Echte CLI-Integration, GNOME-Pairing-Ansicht und unabhängige Installation prüfen.
