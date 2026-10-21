# M1 / M1A: CLI-Evidenz und Cloud-Race, 21.10.2026

**Status: P0 BLOCKED / NO-GO.** Unveränderte Produktionsdienste; alle Prüfungen lesen nur CLI-Metadaten bzw. nutzen synthetische FakeCloud.

## Herstellerstatus und Vertrag

Die Proton Drive CLI ist **ein offizielles Proton-Produkt** (Ankündigung https://proton.me/blog/proton-drive-cli, 09.06.2026; SDK/CLI https://github.com/ProtonDriveApps/sdk/blob/main/cli/README.md). Die Annahme, sie sei grundsätzlich inoffiziell, ist falsch. Ein offizielles Produkt bedeutet aber nicht, dass jede für bidirektionalen Fremd-Sync benötigte Atomizitätsgarantie besteht. Lokaler CLI-Readback: `cli-drive@0.9.0+75612299`, SDK `js@0.22.2+75612299`. Die offizielle Downloadseite nennt Release 0.9.0 (05.10.2026): https://proton.me/download/drive/cli/index.html.

Lokaler `filesystem upload --help`: `create-new-revision`, `rename`, `replace`, `skip`; kein dokumentierter Parameter für `if-match`, erwartete Revision oder Compare-and-Swap. **Nichtnachweis** einer Funktion ist nicht Beweis, dass interne SDK-Endpunkte sie niemals bereitstellen; vor Freigabe ist ein expliziter Adapter-/API-Contract-Nachweis nötig.

Minimaler Adapter v0 (geplant, nicht implementiert): `list(path)`, `info(path)`, `download(path)`, `upload_new(path)`, `upload_existing_if_revision(path, expected_revision)`, `version()`, `capabilities()`. Fehlerarten: `AUTH`, `RATE_LIMIT`, `TIMEOUT`, `CONFLICT`, `UNSUPPORTED_CAPABILITY`, `PROVIDER_ERROR`, `INTEGRITY_ERROR`. Wenn bedingtes Update fehlt, darf der sichere Client es **nicht** stillschweigend durch unbedingtes `create-new-revision` ersetzen. Bis zu einer gesicherten Umsetzung bleibt Release gesperrt.

## Synthetischer Race-Reproduktionsnachweis

`tests/test_mvp_post_preflight_race.py`: Remote-Revision wird erst **nach** erfolgreicher Engine-Preflight-Abfrage und unmittelbar **vor** dem Fake-CLI-Upload geändert. In der vorhandenen Algorithmus-/CLI-Simulation schreibt das `create-new-revision` den lokalen Inhalt auf die konkurrierende Cloud-Änderung und liefert Erfolg. Der Test protokolliert bewusst den Fehlpfad als Charakterisierungstest und ist **kein** Sicherheitsnachweis. Keine echte Cloud-Datei verändert. Das kann zu verlorener aktiver Cloud-Revision führen, auch wenn die API möglicherweise frühere Revisionen aufbewahrt. Die Existenz einer früheren Version ist kein hinreichender Ersatz für Konfliktvermeidung.

**Entscheidung:** Blocker M1-001. Vor M1-Freigabe serverseitige bedingte Mutation nachweisen und gezielt testen oder den entsprechenden Uploadpfad fail-closed deaktivieren bzw. in einen sichereren, ausdrücklich gekennzeichneten Workflow umstellen. Keine Freigabe aufgrund Preflight/Postflight-Hashchecks allein.

## Nutzungsbedingungen und Secret-Schutz

Protons Nutzungsbedingungen (Stand 09.10.2026) enthalten konkrete Regeln gegen missbräuchliche, vom Standardverhalten deutlich abweichende automatisierte Zugriffe; automatisierter Zugriff ist unter Bedingungen möglich: https://proton.me/de/legal/terms. Der Proton-Artikel zur CLI nennt Automatisierung und Fair-Use/Rate-Limits ausdrücklich. **Nicht** pauschal untersagt; Grenzen für einen öffentlich verteilten Sync-Client bleiben gesondert zu prüfen. Keine Rechtsberatung oder erteilte Herstellerfreigabe.

Laut offizieller SDK/CLI-Dokumentation wird eine Session nach Browser-Login im Betriebssystem-Secret-Store gespeichert. Lokalen tatsächlichen Secret-Store, Rechte, Logging, Session-Fehler und Versionseignung in isoliertem Profil prüfen, ohne Tokeninhalte auszulesen oder zu kopieren. Kein Login-/Produktivzugang wird für dieses Gate benötigt.
