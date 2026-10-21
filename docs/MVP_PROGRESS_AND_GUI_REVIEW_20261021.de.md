# Fedora MVP – Fortschritt, Startverhalten und Dienst-Lifecycle (21.10.2026)

## Tatsächliches produktives Startverhalten
Die vorhandenen produktiven User-Units `proton-sync-watcher.service`, `proton-bisync-quick.timer`, `proton-cloud-priority.timer` und `proton-bisync.timer` waren enabled/active; `loginctl` zeigte Linger=yes. Ein Vollabgleich startete am 21.10.2026 um 06:42 und endete um 06:52 mit `run_end`, `tracked=10974`, `uploaded=2`, `errors=0`, `conflicts=0`. Er wartete zunächst auf die Einhängung von `/mnt/example-drive`. Der Haupttimer ist stündlich mit Persistent=true und wird somit automatisch vom User-systemd betrieben, aber es besteht noch kein Garantieversprechen „sofort bei jedem Login“. **Keine zusätzlichen Boot-Trigger angelegt**, um doppelte Vollabgleiche und ungewollte Änderungen am produktiven System zu vermeiden.

## Fortschrittsanzeige
Die GNOME-Übersicht blendet unter der obersten Statuskarte einen Aktivitätsindikator ein, wenn ein tatsächlicher Full-, Quick- oder Cloud-Priority-Dienst aktiv ist. Nur der vollständige Scan bietet – ausschließlich bei tatsächlichen frischen Zählern – einen exakten Prozentsatz; unbekannte Gesamtmengen werden nie als fiktiver Prozentfortschritt ausgegeben. Bei inaktiven Diensten wird kein angeblich laufender Abgleich angezeigt.

## Dienststeuerung und UI
Die vier Dienstaktionen der GNOME-Einrichtung sind zweispaltig für bessere Lesbarkeit angeordnet. Ein gesondert neu gebautes Manifest-geprüftes Testpaket wurde unter `~/Projekte/proton-mvp-gui-accept-20261021` installiert und der GNOME-Prozess damit neugestartet. Die vier dem GUI entsprechenden Backend-Aktionen wurden im echten User-systemd nacheinander erfolgreich getestet: `NOT_INSTALLED` → `INSTALLED_NOT_ENABLED` → Timer enabled+active → paused disabled+inactive → `UNINSTALLED`. Danach waren beide MVP-Units vollständig entfernt, die vier produktiven Units unverändert aktiv.

**Wichtige Abgrenzung:** Die vier Testschritte wurden über dieselben Backend-Funktionen wie die GUI ausgeführt, nicht durch simulierte Klicks in der GNOME-Oberfläche. Visuelle Benutzerabnahme und tatsächliches Klicken/Bestätigen in der GUI bleiben offen. Keine dauerhafte MVP-Timer-Aktivierung.

**Tests:** 301/301 PASS einschließlich UI-Quellregression und Systemd-Lifecycle. Öffentlicher Release bleibt NO-GO.
