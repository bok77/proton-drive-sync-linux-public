# Fedora Proton Drive Sync – GUI-/Clean-Host-Abnahme, 21.10.2026

## Belegte Teilnachweise

- GitHub Actions `39551899761` auf Commit `b009811`: SUCCESS. Fedora-44-Container mit vollständiger Suite und Python-Syntaxprüfung.
- `PYTHONPATH=src python3 -m unittest tests.test_mvp_profile_lifecycle -v`: 3/3 PASS am 21.10.2026. Hierbei wurde ein frisches isoliertes HOME angelegt, der Bundle-Kandidat installiert, per `--self-test` gestartet und deinstalliert. Manipulierte/zusätzliche Dateien blockierten die Deinstallation sicher.
- Dieser Test ist **kein eigenständig gebooteter Fedora-Desktop/VM-Host**. Es existiert auf dem aktuell erreichbaren Host kein vorbereitetes Fedora-ISO in ~/Downloads und keine verfügbare automatisierbare Display-Testumgebung (kein Xvfb, Weston oder ydotool). Daher wird eine GUI-Klick-/Screenreader-Abnahme nicht als PASS markiert.

## Verbindliche manuelle GNOME-E2E-Prüfung auf einem separaten Fedora-Desktop

1. In einem frisch eingerichteten Fedora-Desktop-Benutzer mit eigenem **synthetischen** `ProtonSync-Test`-Profil das manifestgeprüfte Paket installieren. Keine produktiven Sync-Verzeichnisse auswählen.
2. Einrichtung öffnen, mit Tab/Shift+Tab die Hauptaktion fokussieren und per Enter/Space den Bestätigungsdialog öffnen. Prüfen: verständlicher deutscher Text, Fokus im Dialog, `Abbrechen` als Standard, Escape ohne Mutation, keine Aktivierung.
3. `Dienst installieren` bestätigen: Status `Installiert · nicht aktiv`; `systemctl --user is-enabled/is-active proton-mvp-isolated-full.timer` muss deaktiviert/inaktiv zeigen.
4. `Testdienst aktivieren` bestätigen und die aktive Timer-Anzeige mit tatsächlichem systemd-Readback vergleichen; anschließend `Pausieren` und `Entfernen`, beide separat bestätigen. Beim Abbrechen jeweils keine Mutation. Kein Schritt darf die bestehenden produktiven Units berühren.
5. Per Tastatur alle Schaltflächen und Dialoge erreichen; Screenreader prüft Beschriftungen, Warntext, Zustandswechsel und Fokus-Rückkehr. Negative Fälle: Status-Fehler und fehlende Konfiguration verhindern Aktion, ohne anderen Sync-Dienst zu beeinflussen.
6. Paket in derselben frischen Umgebung vollständig entfernen; Config/State nur nach ausdrücklicher Nutzereinwilligung löschen. Für Upgrade/Downgrade eine separat definierte Vorgängerversion verwenden; keine erzwungene Überschreibung.

**Freigabeentscheidung: BLOCKED / NO PUBLIC RELEASE**, bis Schritte 1–6 auf einer tatsächlich unabhängig eingerichteten Fedora-Desktopumgebung belegt sind. Dieser Record autorisiert keine produktive Timer-Aktivierung.
