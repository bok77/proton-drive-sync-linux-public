# V1 – Vierstufiger GTK-Lifecycle in unabhängiger Fedora-44-VM

**Teilnachweis PASS; vollständige GUI→echtes systemd-E2E noch OFFEN.**

Ausführung am 21.10.2026 in der ausschließlich über `start-verified-vm.sh` gestarteten Fedora-44-KVM-VM: `PYTHONPATH=src xvfb-run -a python3 scripts/probe_gtk_v1_full_lifecycle.py`; Exit 0, Kennung `GTK_V1_FOUR_ACTIONS_CANCEL_CONFIRM_SYNTHETIC_PASS`.

Für Installieren → Aktivieren → Pausieren → Entfernen werden jeweils echte GTK/libadwaita-Buttons und Bestätigungsdialoge auf Xvfb erzeugt; `cancel` und `approve` werden als echte Dialogsignale ausgelöst. Es wird geprüft, dass Abbrechen nichts mutiert, Bestätigen genau eine Backend-Aktion auslöst, das Mock-Backend nach Readback den erwarteten Zustand meldet und die nächste passende Aktion sichtbar wird. Getrennt bleibt der bereits abgeschlossene **reale** isolierte systemd-Backend-Lifecycle-Nachweis in `MVP_STATEFUL_LIFECYCLE_LIVE_PROOF_20261021.de.md`.

**Noch kein Gesamt-E2E:** Der VM-GUI-Test mockt systemd. Tastatur/Maus/Screenreader wurden nicht tatsächlich bedient; Xvfb erfüllt keine GNOME-Session-Abnahme. Eine isolierte GUI→echtes User-systemd-Lifecycle-Probe samt Zustandseinblick bleibt V1-Gate. Kein Provider-Login oder Zugriff auf persönliche Clouddateien. Produktive systemd-Dienste auf dem Fedora-Host wurden nicht angefasst.

Alter GitHub-CI-Lauf `39569736296` auf Commit `de21f66` scheiterte ausschließlich am Groß-/Kleinschreibungsfehler in `test_version_documents_exist`. Der Test wurde in `0422c16` korrigiert; der Folge-Lauf `39569805504` war SUCCESS. Kein erneuter Retry des historischen Runs nötig.
