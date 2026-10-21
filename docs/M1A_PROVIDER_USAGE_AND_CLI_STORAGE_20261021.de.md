# M1A – Offizielle SDK-Nutzungsregeln und CLI-Cache-Metadaten (21.10.2026)

## Relevante Primärquelle

Offizielles SDK: https://github.com/ProtonDriveApps/sdk (README / Usage Guidelines for Personal Projects; geprüft 21.10.2026). Proton nennt ausdrücklich persönliche nichtkommerzielle Projekte unter Bedingungen und bezeichnet das SDK als noch nicht bereit für produktive Drittanbieter-Apps. Besonders relevant: ehrliche Client-Identifikation (`x-pm-appversion`, keine First-Party-Imitation), ereignisbasierte Synchronisierung statt wiederholter vollständiger Scans, schonender Umgang mit Caching, Parallelität und exponentiellem Backoff, Branding/Transparenz. Dies ist eine technische/Richtlinien-Bestandsaufnahme und keine abschließende Rechtsberatung.

**Architektur-Blocker:** Der bestehende Sync-Ablauf führt periodische rekursive Bestandsabgleiche aus. Noch nicht belegt ist, dass das reale CLI-Verhalten und die vorgesehenen Sync-Intervalle Protons Anforderungen an eventbasierte Synchronisation und Schonung der API erfüllen. Vor einer öffentlichen Alpha muss dieser Unterschied gelöst oder ausdrücklich mit Proton geklärt werden. Kein stilles Umschalten produktiver Sync-Dienste.

## CLI-Speicher-Metadaten

Auf dem Fedora-Testhost existiert `~/.local/share/proton-drive-cli` mit Modus `0755`; darin liegen `clientUid.json` und `events.json`, jeweils `0644`. Die neue reine Metadatenprüfung `cli_storage_audit.inspect()` ergibt `BLOCKED` und meldet lediglich unsichere Berechtigungen, nicht Dateinamen/Inhalte. Sie liest **niemals** Inhalte oder Tokens. Aus den Namen folgt keine Aussage über das Vorhandensein von geheimen Zugangsdaten. Ein potenzielles lokales Offenlegungsrisiko ist wegen der Rechte aber zu bewerten und die Speicherung/Sensitivität mit dem CLI-Hersteller abzuklären. Keine automatisch ausgeführte Änderung an fremdverwalteten CLI-Dateien.

**Status:** M1A bleibt OPEN / PARTIAL; P0 der Nutzungskonformität und Secret-Store-Nachweis offen; öffentlicher Release NO-GO.
