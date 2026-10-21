# Fedora MVP-Kandidat: Installation, Einrichtung und realer Test (20.10.2026)

**Status: isolierter Testkandidat, keine öffentliche Freigabe.**

1. Build: `python3 scripts/build_fedora_mvp.py --output /PFAD/ZUM/NEUEN-BUNDLE`. Inhalt: GTK4-App, portierte Python-Engine, lokaler Startbefehl, prüfbares SHA-256-Dateimanifest. Keine Dienstaktivierung.
2. Sichere Probeinstallation in ein **noch nicht vorhandenes** Verzeichnis: `python3 scripts/install_fedora_mvp.py --bundle /PFAD/ZUM/BUNDLE --prefix /PFAD/ZUM/INSTALL`. Es werden nur Bundle-Dateien angelegt; keine systemd-Units installiert oder gestartet. Existierende Ziele werden nicht überschrieben.
3. GUI: `/PFAD/ZUM/INSTALL/bin/proton-drive-sync`; im Bereich Einrichtung die private Konfiguration `~/.config/proton-sync-isolated/config.json` auswählen, echte Bestände prüfen und nur für `READY_FOR_EXPLICIT_APPROVAL` den exakten Satz `I APPROVE EXACT INITIAL PAIRING` eingeben. Dadurch wird nur die Erst-Baseline plus offener Erststartmarker erzeugt. Kein Sync-Dienststart.
4. Die portable Runtime ist separat über `bin/proton-portable-full` verfügbar; sie benötigt explizit `PROTON_SYNC_CONFIG` und bleibt ohne Baseline/Erststartprüfung gesperrt. **Nicht gegen persönliche Daten starten.**

**Durchgeführter Realtest:** Im vorhandenen, eigens isolierten `/my-files/ProtonSync-Test` wurde `mvp-roundtrip-20261020.txt` (79 Byte) hochgeladen und in ein temporäres Linux-Verzeichnis zurückgeladen; SHA-1-Readback war identisch. Erneute echte Cloud-Pairing-Vorschau: 2 identische Dateien, 0 Differenzen, 0 Fehler. Keine Baseline erstellt; kein portable Engine-Dienst aktiviert. Bestehende produktive systemd-Dienste und `/mnt/example-sync-root` unverändert.

**Offener Abnahmeblocker:** End-to-End vom explizit bestätigten Pairing über den ersten, rein lesenden Runtime-Start bis zum regulären schreibenden Engine-Betrieb ist mit der echten Proton-CLI **noch nicht nachgewiesen**. Das erfordert die tatsächliche bewusste Zustimmung zur Test-Pairing-Baseline, abgesicherte Prozess-/Pfadgrenzen, anschließende Revisionsprüfung und den Test auf einem unabhängig eingerichteten Fedora-Profil. GNOME-Anzeige/Bedienbarkeit des Freigabedialogs benötigt zusätzlich eine visuelle Abnahme. Eine persistente eigene systemd-Integration/Installer-Upgrade-Routine fehlt noch. Öffentlicher Release: NO-GO.
