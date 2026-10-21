# M1 – Gleichzeitige echte Proton-CLI-Schreibvorgänge (21.10.2026)

**Ergebnis: begrenzter Live-PASS für drei konkrete parallele Testläufe; kein allgemeiner Atomizitätsbeweis.**

Umgebung: authentifizierte offizielle Proton Drive CLI `cli-drive@0.9.0`, SDK `js@0.22.2`. Alle Testnamen waren eigens angelegt und auf `/my-files/ProtonSync-Test` begrenzt; keine bestehenden Nutzerdaten oder produktiven Sync-Units wurden verändert.

1. **Zwei zeitgleich gestartete `filesystem upload -f skip` gegen eine vorhandene synthetische Datei:** Beide CLI-Prozesse Exit 0 mit `Uploaded: 0 / Skipped: 1`. Cloud-SHA1 nach Ausführung unverändert (`decfc8fe6acae337bb0faf1ab059c3f9a5e4b085`). Exit 0 kann also ein Skip sein.
2. **Zwei zeitgleich gestartete `filesystem upload -f skip` gegen einen zuvor nicht vorhandenen Namen:** Beide CLI-Prozesse Exit 0; einer meldete `Uploaded: 1`, der andere `Uploaded: 0 / Skipped: 1`. Remote-Verzeichnis-Readback: exakt **eine** Datei mit dem Namen.
3. **Zwei zeitgleich gestartete `filesystem create-folder` desselben zuvor nicht vorhandenen Namens:** Exit-Codes 1 und 0; ein Prozess meldete `Datei oder Ordner mit diesem Namen existiert bereits`. Cloud-Readback: exakt **ein** gleichnamiger Ordner.

Die Konkurrenz erfolgte jeweils per zwei Hintergrundprozesse mit anschließendem `wait`; eine interne serverseitige Race-Barriere oder garantierte exakt gleiche Request-Eingangszeit wurde nicht kontrolliert. Aussagen gelten nur für diese beobachteten Läufe, diese CLI-Version und den Testaccount; sie sind keine universelle API-Atomizitätsgarantie. **Die fehlende bedingte Aktualisierung bestehender Revisionen ist dadurch nicht gelöst.** `existing_revision_guard` muss weiterhin fail-closed bleiben, bis eine belegte sichere Update-Schnittstelle oder fachlich freigegebene Konfliktstrategie vorliegt.

Diese Live-Tests ergänzen `M1_REAL_CLI_COLLISION_PROOF_20261021.de.md` und `M1_CLI_RACE_DECISION_20261021.de.md`. Öffentlicher Release: **NO-GO**.
