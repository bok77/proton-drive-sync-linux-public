# Kontrolliertes Recovery beim unterbrochenen Erststart (20. Oktober 2026)

**Status:** Nur als isolierter, synthetisch getesteter Recovery-Kern implementiert. Keine Live-Recovery-Freigabe und keine automatische Aktivierung.

Neue Komponente: `src/proton_sync_engine/pairing_recovery.py`.

- Ein blockierter Erststart mit **gleichzeitigem** `initial_pairing_pending.json` und `initial_pairing_verified.json` wird nicht automatisch aufgelöst. Der Runtime-Start bleibt fail-closed.
- `inspect(config,adapter)` prüft die vorhandene Baseline und den offenen Pairing-Nachweis gegen einen **frischen lokalen Bestand und eine frische Cloud-Inventarisierung einschließlich Revisionskennungen**. Unsichere Symlinks, fehlende oder beschädigte Ausgangsnachweise und abweichende Bestände werden blockiert.
- Die Vorschau ist an SHA-256-Prüfsummen der Baseline, des Pairing-Markers sowie an Inhalt und Inode-Metadaten des Verifikationsmarkers gebunden.
- `recover(config,adapter,review,consent)` verlangt die wörtliche, gesonderte Zustimmung `I APPROVE RECHECK OF INTERRUPTED FIRST START`, wiederholt die Prüfung und erstellt eine neue private, exklusive und fsync-gesicherte `initial_pairing_recovery_evidence.json` mit Zeitstempel und Fingerabdruck.
- Erst danach wird **ausschließlich** der zugehörige widersprüchliche Verifikationsmarker entfernt. Die freigegebene Baseline und der offene Pairing-Marker bleiben unverändert. Ein neuer Engine-Erststart muss den gesamten Vergleich erneut durchführen; Recovery überträgt keine Dateien.
- Eine bereits vorhandene Recovery-Evidence führt fail-closed zum Abbruch. Ein erneut ausgeführtes Recover darf sich nicht selbst bestätigen.

**Tests:** Vollständige 235/235 `unittest`-Tests erfolgreich, einschließlich doppelter und teilweiser Marker, manuell veränderter Cloud- oder lokaler Daten, beschädigter Baseline, Replay, Symlink, fehlender Freigabe und ordnungsgemäßem Wiederanlauf nach kontrolliertem Recovery.

**Grenzen und weiterer Gate:** Die Recovery-Komponente ist noch nicht als Oberfläche/Installer-Aktion verbunden und wurde nicht mit dem realen Proton-Konto ausgeführt. Externe konkurrierende Zugriffe während der letzten Recheck-/Marker-Änderung sind nicht atomar ausgeschlossen; vor einem produktiven Einsatz sind eine exklusive Lauf-/Recovery-Sperre, Snapshot-/Provenienzprüfung, Berechtigungs- und Race-Tests erforderlich. Keine produktiven Dienste oder Daten wurden durch diese Umsetzung verändert. Release bleibt gesperrt.
