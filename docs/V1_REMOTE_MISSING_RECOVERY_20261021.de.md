# V1 – Remote-Missing/Recovery-Konflikt vor der Wartefrist

**Synthetischer Engine-Proof PASS, echter Proton-CLI-Negativtest noch offen.**

Die Regression in `tests/test_v1_recovery_additional.py` deckte auf, dass eine nachweislich lokal geänderte Datei bei Remote-Löschung beziehungsweise Remote-Umbenennung in den ersten beiden Scans zunächst nur als `cloud_missing_pending` gemeldet werden konnte. Ein Lauf mit bestehendem Konflikt lieferte deshalb teils Exit 0. Korrigiert ist die Reihenfolge: wenn die Cloud-Datei im bekannten Baseline-Pfad fehlt **und** der lokale Inhalt nicht mehr mit dem Vorfahren übereinstimmt, entsteht bereits im ersten Scan `cloud_missing_local_modified` mit Konfliktstatus/Exit 1. Es erfolgt keine automatische lokale Löschung.

Synthetische Verifikation: Remote-Löschung nach lokalem Edit, Remote-Umbenennung nach lokalem Edit, Offline-Ausfall mit unveränderter Baseline sowie erneuter Start bei bestehendem Cloud-Update-Guard. Bei einer Umbenennung kann der separate neue Cloudpfad nach erfolgreicher Verifikation hinzukommen, die alte konfliktbehaftete Baseline darf nicht überschrieben werden. Keine produktiven Daten, CLI-Session oder systemd-Dienste verändert.

**Noch offen:** echte cloudseitige Rename-/Delete-/Retry-Probe im ausschließlich freigegebenen Test-Scope, Input-Bedienung und V1-Pilot-Abnahme. Die bestehende 24h-/Zwei-Scans-Quarantäneregel für unveränderte lokale Inhalte bleibt bewusst bestehen.
