# Fedora MVP – Restart, Offline, Konflikte und isoliertes Nutzerprofil (20.10.2026)

**Gesamtergebnis: PASS für synthetische Fehler- und Installations-/Deinstallationstests; öffentlicher Release weiterhin NO-GO.**

## Engine-Fehlerpfade
`tests/test_mvp_failure_matrix.py` prüft Offline beim Cloud-Listing, anschließenden Wiederanlauf, konkurrierende lokale/Cloud-Inhaltsänderungen und einen abgebrochenen Download mit erfolgreichem späterem Retry. Negativfälle dürfen weder die Ursprungs-Baseline korrumpieren noch stille Überschreibungen oder Datenverlust erzeugen. Die Cloud in diesen Tests ist **simuliert**. Der echte bidirektionale Übertragungsnachweis in `docs/REAL_ENGINE_BIDIRECTIONAL_PROOF.de.md` ist davon unabhängig.

## Installationspfad
`scripts/build_fedora_mvp.py` erstellt ein dateiintegritätsgeprüftes Bundle mit GNOME-Oberfläche und portablem Engine-Laufzeitcode. Die Launcher verhindern Python-Bytecode-Caches im Installationsverzeichnis, weil sonst eine strenge Deinstallation trotz erfolgreichem Selbsttest scheitern würde. `scripts/install_fedora_mvp.py` installiert ausschließlich in ein **neues** Zielverzeichnis, ohne bestehende Dateien oder systemd-Units zu verändern. `scripts/uninstall_fedora_mvp.py` entfernt nur eine zuvor vollständig anhand des Manifests geprüfte Kandidateninstallation; unbekannte Dateien, Symlinks oder manipulierte Paketdateien blockieren den Rückbau.

`tests/test_mvp_profile_lifecycle.py` und ein echter, temporärer Fedora-Praxistest belegen: neu angelegtes isoliertes `HOME`, Bundle-Build, Installation, `proton-drive-sync --self-test` mit `L10N_OK` und `BACKEND_OK`, danach Kandidat entfernt und Nutzer-Home erhalten. Negativtests schützen unbekannte oder manipulierte Dateien.

**Klarstellung:** Das war ein neues Benutzerprofil auf **demselben Fedora-Rechner**, keine zweite Fedora-VM/Neuinstallation und kein von anderen Installationen unabhängiger Host. Das Paket ist noch keine RPM oder vollständige systemd-Dienstinstallation. Der Deinstaller entfernt keine User-Konfigurationsdateien oder Systemdienste.

**Status:** 274/274 automatisierte Tests bestanden. Die vier produktiven systemd-Dienste blieben unverändert aktiv; auf den persönlichen Sync-Pfaden wurden keine Tests ausgeführt. Offene Release-Gates sind unter anderem echte systemd-Integration und Rollback, unabhängige Fedora-Installation, weitere Rename-/Delete-/Concurrent-Cloud-Negativtests sowie GUI-/Accessibility-Abnahme. Keine automatische Cloud-Transaktionsgarantie behaupten.
