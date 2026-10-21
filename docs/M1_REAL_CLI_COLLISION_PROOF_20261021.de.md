# M1 – Echte Proton-CLI-Kollisionen im isolierten Testordner, 21.10.2026

**Scope:** `/my-files/ProtonSync-Test` ausschließlich; offizielle CLI `cli-drive@0.9.0`, SDK `js@0.22.2`. Keine produktiven Sync-Units oder Produktivdaten verändert. Zwei selbst erzeugte synthetische Testobjekte.

## Datei `m1_skip_probe_20261021.txt`

1. Erste lokale Version (24 Byte) mittels `filesystem upload -f skip` angelegt: Exit 0; `Uploaded: 1`.
2. Anderen lokalen Inhalt unter identischem Namen mit `filesystem upload -f skip` erneut hochgeladen: **Exit 0**, `Uploaded: 0`, `Skipped: 1`.
3. Cloud-`filesystem info -j` vor/nach der Kollision: gleicher SHA-1 und gleiche `activeRevision.uid`. Die vorhandene Remote-Datei wurde nicht verändert.
4. Wichtig: `skip` ist für eine Kollision **kein Nonzero-Exit**. Readback mit Prüfsumme/Revision ist erforderlich. Die Fake-CLI wurde an die beobachtete Exit-0-Semantik angepasst; Regression bleibt grün.

## Ordner `m1_folder_probe_20261021`

1. `filesystem create-folder /my-files/ProtonSync-Test m1_folder_probe_20261021`: Exit 0.
2. Derselbe Befehl ein zweites Mal: **Exit 1**, `Datei oder Ordner mit diesem Namen existiert bereits.` Der zweite Vorgang wurde nicht als Erfolg gewertet.

## Sicherheitsgrenze

Diese echten CLI-Tests bestätigen normale **sequenzielle** Konflikte; sie beweisen keine atomare Server-Operation bei zwei tatsächlich gleichzeitigen Clients. Auch `create-folder` zeigt keinen dokumentierten `if-none-match`-Vertrag. Für bestehende Dateien bleibt der fail-closed-Update-Guard in der portablen Engine erhalten. Der mögliche Post-Preflight-Race bleibt als M1-Blocker offen. Veröffentlichung weiterhin **NO-GO**.
