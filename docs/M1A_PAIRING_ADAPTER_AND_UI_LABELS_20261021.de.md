# M1A – Pairing-CLI-Adapter und sichere GUI-Fehlertexte (21.10.2026)

**PARTIAL PASS; Release NO-GO.** `test_cloud_adapter.py` verwendet für den read-only Pairing-Inventarscan jetzt denselben `cli_adapter.execute` wie die portable Sync-Runtime. Fehlgeschlagene Provideraufrufe werden anhand typisierter Fehlerklassen als kurze Fehlercodes ohne rohe CLI-Ausgabe weitergegeben. Für den Cloud-Inventarscan bleibt allein `/my-files/ProtonSync-Test` erlaubt; es gibt keine Schreiboperationen und keine produktiven Dateizugriffe.

`proton_sync_desktop/cli_error_labels.py` enthält geprüfte deutsche und englische, von externen Fehlertexten unabhängige Benutzermeldungen für `AUTH`, `RATE_LIMIT`, `TIMEOUT`, `CONFLICT`, `PROVIDER_ERROR` und `UNKNOWN`. Dies ist ein **Darstellungsvertrag**, noch **keine** abgeschlossene Verdrahtung aller Meldungen in die laufende GTK-Oberfläche. Bei unbekannten Werten wird ein generischer Hinweis angezeigt, nicht der ungeprüfte Rohtext.

Lokal 386/386 Tests PASS. Das Paket wurde nicht produktiv installiert. Echte provozierte Providerfehler 401/429 sind **nicht** getestet, um keine Konto- oder Rate-Limit-Risiken zu erzeugen. Weitere CLI-Consumers, sichere GUI-Weitergabe des Status und echte Provider-E2E bleiben offen. Ein fehlgeschlagener Update bestehender Revisionen bleibt im portablen MVP weiterhin blockiert.
