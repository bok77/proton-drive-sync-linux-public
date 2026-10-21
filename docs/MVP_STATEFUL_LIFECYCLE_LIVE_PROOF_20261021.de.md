# MVP – Live-Lifecycle-Abnahme, 21.10.2026

**Ergebnis: PASS für vier reale systemd-Backend-Aktionen. GUI-Klick-Abnahme noch offen.**

Isolierter Kandidat: `~/Projekte/proton-mvp-gui-stateful-20261021`, private Konfiguration `~/.config/proton-sync-isolated/config.json` und ausschließlich synthetischer Ordner `ProtonSync-Test`.

| Aktion | Reale Rückmeldung | Statusprüfung danach |
|---|---|---|
| Installieren | `INSTALLED_NOT_ENABLED` | INSTALLED, enabled=false, active=false |
| Aktivieren | INSTALLED, enabled=true, active=true | INSTALLED, enabled=true, active=true |
| Pausieren | INSTALLED, enabled=false, active=false | INSTALLED, enabled=false, active=false |
| Entfernen | `UNINSTALLED`, config/state retained | NOT_INSTALLED |

Nach dem Rückbau existieren keine `proton-mvp-isolated-*`-User-Unit-Dateien. Alle vier produktiven Einheiten (`proton-sync-watcher.service`, `proton-bisync-quick.timer`, `proton-cloud-priority.timer`, `proton-bisync.timer`) waren vor und nach dem Lauf jeweils `enabled/active`.

Die Tests rufen die identischen Backend-Funktionen auf, die auch die GNOME-Oberfläche verwendet. Dialoge und Mausklicks wurden nicht automatisiert; daraus wird kein GUI-End-to-End-Test abgeleitet. Kein Produktivordner wurde als MVP-Ziel aktiviert. Öffentlicher Release bleibt bis zum vollständigen Acceptance Gate NO-GO.
