# V1 – Unabhängiges Cloud-Testprofil und Live-Gate, 21.10.2026

**Status: BLOCKED für echte neue Provider-Operationen.** Im aktuellen Projekt liegt kein hinreichender Nachweis einer unabhängig authentifizierten Test-Session vor. Bisherige echte CLI-Kollisionsnachweise gelten als historische Teilbelege, autorisieren aber weder das Wiederverwenden des vorhandenen CLI-Keyrings noch das Lesen von Credentials/Caches oder erneute Cloud-Mutationen.

## Freigabevoraussetzungen

1. Eigenständiges Proton-Testkonto bzw. technisch klar isolierte Testidentität **unabhängig von der vorhandenen produktiven CLI-Session**; Herkunft, Trennung und Testzweck ohne Veröffentlichung von Secrets dokumentieren.
2. Ausschließlich `/my-files/ProtonSync-Test` und frischer eigener lokaler Root, als Verzeichnis Eigentum des Testnutzers mit privaten Rechten; keine Pfade unter `/mnt/example-drive`.
3. Konkrete manuelle Freigabe für neue reale Rename-/Delete-/Offline-Proben **erst nach** Testsession-Nachweis. Kein automatischer Live-Start aus einem Preflight.
4. Vorher: Prüfplan mit eigenen neu erstellten Testdateien, SHA1-/Revision-Readback, Offline-Unterbrechung, Restart und dokumentiertem Rückbau. Nachher: unveränderte Originaldaten, keine unkontrollierte Cloud-Überschreibung, verbleibende Baseline und exakte Resultate kontrollieren.

`src/proton_sync_engine/v1_live_test_gate.py` ist **nur** eine lesende Policy-Entscheidung. `BLOCKED` enthält konkrete Gründe; selbst `READY_FOR_SEPARATE_MANUAL_REVIEW` startet weder eine CLI noch einen Netzwerkaufruf. Tests `tests/test_v1_live_test_gate.py` prüfen fehlende Testsession, Produktionssession-Sperre, falschen Scope und private Dateirechte.

## Nächster sicherer Schritt

Unabhängige Test-Session ausdrücklich bereitstellen und ihre Isolation nachweisen. Erst danach einen genehmigten Live-Durchlauf ausschließlich mit neu angelegten Testobjekten durchführen. In der Zwischenzeit V1-Tastatur-/Fokusbedienung im isolierten Fedora-Gast weiter prüfen. **V1 NOT ACCEPTED.**
