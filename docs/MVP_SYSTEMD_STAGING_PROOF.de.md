# Fedora MVP: isolierte systemd-Dienstvorlagen – 20.10.2026

**Status: STAGED / NOT ACTIVATED. Keine Produktivinstallation.**

- Service `proton-mvp-isolated-full.service`: `Type=oneshot`, explizite private `PROTON_SYNC_CONFIG`, keine eigene `[Install]`-Autostartbindung.
- Timer `proton-mvp-isolated-full.timer`: `OnCalendar=*-*-* *:00,30:00`, `Persistent=false`, `WantedBy=timers.target`; nicht installiert, nicht aktiviert. Der 30-Minuten-Takt ist nur ein technischer Platzhalter.
- `service_integration.stage_pair()` legt beide Units ausschließlich in einem explizit vorgegebenen privaten, **nicht produktiven** Verzeichnis mit exklusiver Neuanlage ab. `remove_pair()` vergleicht vor der Entfernung den vollständigen Inhalt beider Dateien. Keine systemctl-Befehle in diesem Pfad.
- Korrektur des Timer-Generierungsfehlers: echte Zeilenumbrüche anstelle literaler `\\n`. `systemd-analyze verify --user` mit echten isolierten Konfigurations- und Runtime-Pfaden: EXIT 0.
- Automatisierte Gesamttests: 291/291 PASS, insbesondere ergänzende Unit-/Timer-Tests.
- Frischer Fedora-Praxislauf: Bundle bauen, in neues temporäres Installationsverzeichnis kopieren, Service/Timer in temporärem privaten Verzeichnis erzeugen und nach Inhaltsvergleich vollständig entfernen: PASS.
- Frühere Testinstallation mit zusätzlichen Cachedateien wurde durch die strenge Paketprüfung abgelehnt und bewusst nicht verändert.
- Alle vier bestehenden produktiven Proton-Sync-Service/Timer-Einheiten blieben aktiv und unverändert.

**Offen für Endabnahme:** Live-`systemctl --user`-Installations-, Start-, Stopp- und Deinstallationspfad, unabhängiges Fedora-System, Produkt-UX/GUI. Explizite Aktivierung ist ein gesondertes Gate. Keine Behauptung, dass der neue Dienst bereits automatisch läuft.
