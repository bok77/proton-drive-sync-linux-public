# Isolierter realer Zweitstart – 20. Oktober 2026

**Ergebnis: erfolgreich, jedoch nur unveränderter Zwei-Dateien-Bestand.**

- Der Nutzer bestätigte ausdrücklich das Erst-Pairing in der GNOME-Oberfläche. Die Baseline wurde mit zwei rein synthetischen Dateien in dem separaten privaten Test-State angelegt. Der erste Runtime-Start war ausschließlich verifizierend und erreichte Exit 0.
- Vor dem zweiten Start: genau zwei lokale Testdateien mit gleicher SHA-1-Prüfsumme und Cloud-Revisionskennung wie in der Baseline; keine Datei oder Konfiguration unter `/mnt/example-sync-root` berührt.
- **Erster Zweitstart:** nach erfolgreicher Cloud-Erfassung mit Exit 1 abgebrochen; die portable Runtime verlangte `settings.json` mit Ausschlussregeln, die der Paket-/Einrichtungsweg noch nicht erzeugte. Der Abbruch blieb fail-closed; keine Testdateien oder Baseline wurden verändert.
- **Korrektur:** `prepare_exclusions.initialize` erstellt die private leere Standardkonfiguration `settings.json` mit Modus 0600 exklusiv und fsync, ohne vorhandene benutzerdefinierte Einstellungen zu überschreiben. Vier synthetische Regressionstests decken Erstanlage, wiederholte Ausführung, Symlink und unsichere Verzeichnisrechte ab.
- **Wiederholung:** Echter Proton-CLI-gestützter Full-Engine-Lauf beendet mit Exit 0; `scan_ok` 2 Cloud-Dateien, `run_end` valid=2, uploaded=0, remote_downloaded=0, conflicts=0, errors=0, tracked=2.
- **Readback:** lokaler Bestand, Cloud-SHA-1, Revisionskennungen, Baseline und First-Start-Marker erneut erfolgreich geprüft. Vier bereits produktive systemd-Dienste bleiben aktiv und unverändert.

**Noch nicht bewiesen:** Echte Upload-/Download-Übertragungen **durch die portable Engine** nach dem Pairing, Recovery unter realen Cloud-Änderungen sowie Fedora-Neuinstallation mit eigenem Dienst-Lifecycle. Das separat erfolgreich getestete Hoch- und Herunterladen über die echte CLI ersetzt diese Tests nicht. Kein öffentlicher Release ohne verbleibende Gates.
