# Geführte Fedora-MVP-Dienststeuerung – 21.10.2026

**Status: Implementiert und synthetisch getestet; neue Timer-Aktivierung NICHT durchgeführt.**

Die GNOME-Einrichtung hat einen fünften Schritt „Synchronisierung steuern“. Das Eingabefeld für die Testkonfiguration wird wiederverwendet; die vier Aktionen *Installieren*, *Aktivieren*, *Pausieren* und *Entfernen* erfordern jeweils eine andere, exakt eingegebene Freigabe. Die GUI führt die Aktionen in einem Worker-Thread aus und zeigt Fehler an; bloßes Öffnen der Anwendung löst keine systemd-Änderung aus.

Autoritatives Backend: `src/proton_sync_engine/user_service_lifecycle.py`, im Installationspaket enthalten. Das Backend kontrolliert unveränderte Bundle-Prüfsummen, eine private 0600-Konfiguration und die Beschränkung auf den isolierten Ordner `ProtonSync-Test`. Es akzeptiert keine anderen managed_folders und keinen lokalen Pfad unter `/mnt/example-drive`. Alle Operationen arbeiten mit den eindeutig benannten `proton-mvp-isolated-full.service` und `proton-mvp-isolated-full.timer`, nie mit den vorhandenen produktiven Sync-Units.

- **Installieren** legt Service und Timer mit exklusiver Neuanlage in `~/.config/systemd/user` ab und führt `daemon-reload` aus, ohne den Timer zu aktivieren.
- **Aktivieren** verlangt eine neue Bestätigung sowie `INITIAL_PAIRING_VERIFIED_V1` ohne Pending-Marker. Erst danach wird `systemctl --user enable --now` für den MVP-Timer ausgeführt.
- **Pausieren** deaktiviert und stoppt den MVP-Timer und stoppt den MVP-Service.
- **Entfernen** prüft beide Unit-Dateien vor jeder Änderung bytegenau, deaktiviert/stoppt beide Einheiten und entfernt anschließend ausschließlich diese beiden Dateien. Testkonfiguration und Baseline bleiben erhalten. Unbekannte oder modifizierte Einheiten werden nicht überschrieben oder gelöscht.

**Belege:** 299/299 Regressionstests grün, darunter sieben spezifische Lifecycle-Tests mit mockbarem systemctl; frischer isolierter Paket-Build und Installation mit `--self-test` (L10N_OK 62, BACKEND_OK 5), erneuter Manifest-Integritätstest und Vorhandensein aller vier GUI-Aktionen: PASS. Keine Änderungen an den bestehenden produktiven systemd-Diensten. Die vorherige einmalige echte systemd-Start-/Stopp-/Rückbauabnahme ist separat dokumentiert in `docs/MVP_SYSTEMD_LIVE_PROOF.de.md`.

**Offen:** tatsächlicher visueller GNOME-Bedientest mit dieser Version (der Remote-Terminalprozess hat keine `DISPLAY`/`WAYLAND_DISPLAY`-Variable), Live-Bedienung aller vier neuen GUI-Aktionen, unabhängige Fedora-VM und Release-Härtung. Insbesondere wurde `enable --now` hier bewusst nicht produktiv ausgeführt. Öffentlicher Release bleibt NO-GO.
