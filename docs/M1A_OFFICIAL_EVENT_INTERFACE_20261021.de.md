# M1A – Proton-Eventinterface-Entscheidung (21.10.2026)

**Befund: SDK-Ereignisse als möglicher Reuse-Pfad bestätigt; CLI-Eventfeed als externe Schnittstelle NICHT vorhanden/nicht nachgewiesen. Entwicklungs-/Release-Gate bleibt BLOCKED.**

Primärquellen (offizielles SDK):
- https://github.com/ProtonDriveApps/sdk/blob/main/client/js/src/interface/events.ts
- https://github.com/ProtonDriveApps/sdk/blob/main/cli/src/events/manager.ts
- https://github.com/ProtonDriveApps/sdk/blob/main/cli/src/events/providerPersisted.ts
- https://github.com/ProtonDriveApps/sdk/blob/main/cli/src/events/interface.ts

Die öffentliche SDK-Typdefinition beschreibt `DriveEvent` mit `node_created`, `node_updated`, `node_deleted`, `fast_forward`, `tree_refresh`, `tree_remove` und `shared_with_me_updated`, Event-/Scope-IDs und `LatestEventIdProvider`. Die CLI verwendet intern `subscribeToDriveEvents` und `subscribeToTreeEvents`, verwaltet ein persistiertes `events.json` und schützt den Eventstore mit einem Lock. Die installierte CLI `cli-drive@0.9.0` zeigt in `--help` aber keinen Event-Subscribe-, Pull-, Cursor- oder Watch-Befehl. Das interne `events.json` ist ausdrücklich **kein** autorisierter Datenfeed; es kann ohne Vertrag nicht als unabhängige, atomare Eventwarteschlange gelesen werden.

**Architekturentscheidung:** Nicht gegen das interne CLI-JSON entwickeln oder dessen Lock/Cache unterlaufen. Zuerst eine stabile, verifizierte offizielle SDK-Subscription mit eigenem isoliertem Test-Account/State prototypisieren; vorab Betriebskonzept für dauerhaft laufende SDK-Bridge, Rate-Limits, Lifecycle, Auth und ehrliche Client-Identifikation klären. Kein Produktions-Flip und kein eigener direkter Drive-API-Client. Der SDK-Eventfeed ist nicht automatisch ein vollständiger Änderungsverlauf mit garantiert lückenloser Zustellung; TreeRefresh, FastForward, Cursor- und Scopeverlust sind Fail-closed-Signale, die einen kontrollierten Rebaseline-Prozess erfordern.

Die neue pure Python-Funktion `event_cursor_contract.validate_batch` ist eine **synthetische lokale Vorstufe**: Sie prüft Eventtyp, Scope, Cursor-/Node-Felder und Duplikate; sie lehnt unbekannte Events, Refresh/fast-forward und fehlenden Cursor ab. Sie beweist weder echte SDK-Kompatibilität noch Ereignis-Reihenfolge oder lückenlose Providerzustellung. Keine Cloudzugriffe, Tokenzugriffe oder produktive Dienste betroffen.

**Nächster Gate-Schritt:** Isolierte offizielle SDK-Bridge gegen ausschließlich synthetische Testobjekte, incl. Cursor-Persistenz/Replay-Resistenz/Crash-Recovery und Intervall-/Parallelitätsgrenzen. Vor Freigabe muss die Herstellerkonformität des Gesamtclients bewertet werden. P0/M1A und öffentlicher Release bleiben NO-GO.
