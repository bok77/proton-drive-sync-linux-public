# M1A – SDK-Event-API: Iterator statt veralteter Subscription

**21.10.2026 – statischer Hersteller-API-Nachweis und synthetischer Iterator-Test PASS; echter SDK-Live-Proof BLOCKED.**

Offizielle Quelle: https://github.com/ProtonDriveApps/sdk/blob/main/client/js/src/protonDriveClient.ts und https://github.com/ProtonDriveApps/sdk/blob/main/client/js/src/internal/events/index.ts. `subscribeToTreeEvents` ist im Hersteller-Quellcode ausdrücklich mit `@deprecated Use iterateEvents instead` gekennzeichnet. `iterateEvents(treeEventScopeId,lastEventId,signal)` stellt einen Async-Generator dar; bei fehlender Event-ID kann der Generator mit FastForward beginnen. Deshalb verlangt unser isolierter Adapter einen bereits geprüften Cursor und verwirft `fast_forward`, Refresh und unbekannte Events fail-closed.

Neu: `bridge/sdk_event_iterator.mjs` prüft Scope und Cursor, iteriert über die injizierte SDK-kompatible Funktion, reicht nur allowlistete Node-Eventfelder weiter und stoppt bei ungültigen Ereignissen. `sdk_event_iterator.test.mjs` beweist die Verarbeitung mit einem künstlichen Generator, Redaktion fremder Daten, Abbruch von FastForward und Fehlen eines Cursors. Die Fedora-CI führt den Test ebenfalls aus.

**Nicht als Live-Proof ausgeben:** Der Host hat Node, aber keine Projektinstallation des offiziell versionierten SDK bzw. Bun, und es fand weder Proton-Login noch authentifizierte Provider-Eventzustellung statt. Keine Abfrage des privaten CLI-Keyrings, keine direkte Übernahme des CLI-`events.json`, keine Cloud-Dateiveränderung. Weiterhin fehlen SDK-Import/Authentifizierungsgrenze, lokales IPC zum Python-Spool, getrennte Writer-Locks, Absturz-/Recovery-Beweis, verifizierte Cursor-Acknowledgements und Herstellerkonformität. M1A und öffentlicher Release NO-GO.
