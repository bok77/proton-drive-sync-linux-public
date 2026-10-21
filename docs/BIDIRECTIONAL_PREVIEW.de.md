# Bidirektionale Änderungsvorschau – Sicherheit und Grenzen

## Funktionsumfang

Der Knopf **„Beidseitige Änderungen analysieren“** liest die vollständige Proton-Cloud-Struktur und die lokalen Dateien und vergleicht beide Zustände mit dem letzten gemeinsamen verifizierten Stand.

Ergebnis je Datei:
- `upload`: lokale Änderung nach Proton hochladen
- `download`: Cloud-Änderung lokal übernehmen
- `conflict`: gleichzeitige Änderung, unzuverlässige Metadaten, Symlink oder nicht zuordenbare neue Datei – keine automatische Überschreibung
- `pending_local_deletion`, `pending_cloud_deletion`, `pending_deletion`: Löschkandidaten, deren Ausführung ausschließlich nach den getrennten Wartefrist-/Wiederherstellungsregeln möglich ist
- `unchanged`: gleicher Inhalt; kein Handlungsbedarf

Nur Änderungen erscheinen in der scrollbaren Liste. Der vollständige Analysebericht wird privat als `~/.local/state/proton-bisync/bidirectional_preview.json` mit Dateirechten 0600 abgelegt.

## Sicherheitsvertrag

Die Analyse führt **keine** Cloud-Uploads, Downloads, Verschiebungen, Papierkorb-Aktionen oder endgültigen Löschungen aus. Bei Fehlern im Cloud-Scan oder Drift der gemeinsamen Baseline gibt sie kein gültiges Ergebnis zurück. Ein vorhandener Bericht ist **niemals** eine Ausführungsfreigabe; die spätere Engine muss vor jeder Operation lokale Prüfsummen und Cloud-Revisionsstände erneut validieren.

Ausblick: Diese Vorschau ist noch **keine vollständige planbasierte Freigabe aller Ordneroperationen**. Leere Verzeichnisse, Ordner-Reparenting und direkte Zuordnung von Cloud-Moves sind ein eigener noch offener Punkt. Konflikt- und Löschentscheidungen bleiben weiterhin bei den bestehenden sicherheitsorientierten Engine-Regeln. Die vorgeschlagenen Aktionen können sich während des Scans oder unmittelbar danach ändern.

## Performance und Nachweis

Bei rund 11.000 Dateien und über 500 Cloud-Ordnern benötigt eine vollständige Cloud-Bestandsaufnahme derzeit erheblich Zeit (historisch ca. 20–25 Minuten). Der Knopf führt die Analyse im Hintergrund aus, ohne die GTK-Oberfläche zu blockieren. Währenddessen wird keine erfundene Prozentzahl angezeigt.

Die Klassifizierung sowie vollständige synthetische Inventare sind automatisiert getestet. Zusätzlich ist eine echte, **auf 00_Inbox begrenzte** Cloud-Leseprüfung erfolgreich abgeschlossen. Der vollständige Live-Scan aller Cloud-Ordner ist **noch nicht abgeschlossen nachgewiesen** und bleibt ein Abnahmepunkt vor einem öffentlichen Release.
