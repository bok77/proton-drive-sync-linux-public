# Fedora MVP – Live systemd User-Service-Abnahme (21.10.2026)

**Ergebnis: PASS für einmaligen Live-Service-Lauf und vollständigen Rückbau. Kein dauerhaftes Timer-Enablement.**

## Scope und Vorbedingungen
- Bestehender Fedora-Benutzer, bereits isoliert getesteter Engine-Launcher: `~/Projekte/proton-sync-mvp-install-test-20261020/bin/proton-portable-full`.
- Separate private Konfiguration: `~/.config/proton-sync-isolated/config.json`, Modus 0600; privater State-Modus 0700; `managed_folders=["ProtonSync-Test"]`; ausschließlich synthetische Dateien.
- Bereits verifizierte Baseline und Erststartmarker. Vor dem Lauf: 4 lokale Dateien und 4 Cloud-Dateien, übereinstimmende SHA-1-Werte und Cloud-Revisionen.
- Die vier schon produktiven Sync-Units waren aktiv. Die MVP-Units existierten vor der Abnahme nicht.

## Live-Abnahme und Rückbau
1. Temporäre Installation von `proton-mvp-isolated-full.service` und `proton-mvp-isolated-full.timer` unter `~/.config/systemd/user`, jeweils exklusiv und ohne automatisches Enablement.
2. `systemd-analyze verify --user`: PASS; `systemctl --user daemon-reload`, Service `loaded`, `static`; Timer `disabled` und `inactive`.
3. **Manueller einmaliger Start**: `systemctl --user start proton-mvp-isolated-full.service`, Exit 0; `ActiveState=inactive` nach erfolgreichem OneShot, `Result=success`, `ExecMainStatus=0`. Journal: `scan_ok` mit 4 Dateien, `run_end` mit `valid=4`, `uploaded=0`, `remote_downloaded=0`, `conflicts=0`, `errors=0`, `tracked=4`.
4. Timer blieb `disabled` und `inactive`. Expliziter Stopp und Deaktivierung, sicherheitsgeprüftes Entfernen der zwei exakt erwarteten Unit-Dateien, `daemon-reload`.
5. **Readback nach Rückbau:** beide MVP-Unit-Dateien fehlen; `systemctl --user list-unit-files 'proton-mvp-isolated-full.*'` zeigt 0 Dateien; alle vier bestehenden produktiven Dienste weiter aktiv; 291/291 automatisierte Tests PASS.

## Grenzen der Freigabe
- Dies war ein **manueller, einmaliger Live-Start** und kein Test einer dauerhaft aktivierten Timer-Synchronisierung. Es wurden keine Dateien übertragen, da der Testbestand unverändert war; echte Upload- und Download-Läufe wurden gesondert unter `docs/REAL_ENGINE_BIDIRECTIONAL_PROOF.de.md` nachgewiesen.
- Die Laufzeit der bereits vorhandenen Testinstallation wurde genutzt, nicht die vollständige Installation einer neuen RPM bzw. einer frischen unabhängigen Fedora-VM.
- Der Paket-Installer selbst installiert nach wie vor keine systemd-Units; die einmalige Live-Installation erfolgte als kontrollierter Abnahme-Harness. Ein für Endnutzer geführter Aktivierungs-/Deaktivierungsprozess, unabhängige Fedora-Abnahme und GNOME-UX-Abnahme bleiben offen.
- **Öffentlicher Release: NO-GO. Produktive Timer-Aktivierung: NOT AUTHORIZED.**
