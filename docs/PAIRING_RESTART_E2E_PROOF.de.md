# Synthetischer Pairing-bis-Wiederanlauf-Integrationstest – 20.10.2026

**Status: PASS (synthetisch), keine Produktivfreigabe.**

Nach Wiederherstellung der Fedora-Fernsteuerung wurde der vollständige Ablauf mit synthetischen Dateien, in-memory FakeCloud und temporären Zustandsverzeichnissen ausgeführt. Das neue Testmodul ist `tests/test_pairing_full_lifecycle.py`.

Nachgewiesene Szenarien:
- Echtes `installer_pairing.review_pairing` → ausdrückliches `approve_pairing` → neue Baseline und offener Pairing-Marker
- Erster Engine-Start ausschließlich mit Cloud-Listenabfrage; korrekter Verifikationsmarker und kein Upload/Download
- Zweiter Engine-Start im Normalbetrieb; danach legitimer lokaler Änderungs-Upload mit FakeCloud
- Unterbrochener Start mit vollständigem und gleichzeitig offenem Marker: BLOCKED vor Cloud-Zugriff
- Unterbrochener Start mit nur teilweise geschriebenem Verifikationsmarker: BLOCKED vor Cloud-Zugriff
- Beschädigter offener Pairing-Marker: BLOCKED ohne Dateiübertragung, Baseline unverändert
- Geänderte Cloud-Revision nach Freigabe: BLOCKED ohne Dateiübertragung
- Lokale Änderung nach Freigabe: BLOCKED ohne Dateiübertragung
- Manipulierte Baseline: BLOCKED ohne Dateiübertragung
- Verifikationsmarker als Symlink: BLOCKED
- Wiederholter regulärer Start nach erfolgreicher Erstprüfung: idempotent

**Gesamtergebnis:** 223/223 `unittest`-Tests erfolgreich. Keine echte Cloud-Mutation, kein systemd-Start, keine Änderung der produktiven Sync-Pfade oder der bestehenden Baseline in diesem Test.

**Wichtige Grenze:** Der Crash-Zustand mit gleichzeitig offenem und verifiziertem Marker sperrt derzeit dauerhaft. Das ist fail-closed, aber ein gesondertes kontrolliertes Recovery-Verfahren mit überprüfbarer Evidenz und ausdrücklicher Freigabe fehlt weiterhin. Eine echte atomare Snapshot-/Revisionsgarantie zwischen dem letzten Cloud-Read und einem späteren Schreibzugriff wurde nicht nachgewiesen. Die portable Runtime bleibt nicht produktiv aktiviert und der öffentliche Release bleibt gesperrt.
