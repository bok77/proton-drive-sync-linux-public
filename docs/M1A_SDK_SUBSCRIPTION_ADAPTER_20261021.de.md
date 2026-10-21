# M1A – SDK-Subscription-Adapter (21.10.2026)

**Synthetischer Test PASS; SDK-Live-Anbindung BLOCKED.**

`src/proton_sync_engine/sdk_event_bridge.py` bildet den kleinstmöglichen injizierten Subscription-Vertrag ab: `subscribe(scope_id, callback)` muss eine Subscription-Handle liefern, andernfalls wird blockiert. Der Callback prüft SDK-kompatible Node-Events über den bestehenden Cursorvertrag und legt sie ausschließlich in die private, atomar persistierte `pending.json` ab. Ein bestätigter `cursor.json` wird **nicht** fortgeschrieben. Weitere Batches werden bei offenem Pending blockiert. Ein zweiter Start derselben Instanz wird abgewiesen.

Die lokale Fake-SDK-Testserie bestätigt Subscription-Registrierung, korrekten Scope, Pending-Anlage, unveränderten bestätigten Cursor, Blockade des nächsten Batches und Fehler bei fehlender Handle. Das ist **kein** Live-SDK-E2E: Der Python-Adapter startet weder Bun/Node noch authentifiziert er sich, liest kein `events.json` und ruft keinen Proton-Endpoint auf.

**Vor Live-Prototyp zwingend:** SDK-Version und Auth-Grenze pinnen; tatsächlich kompatiblen Bun/Node-Bridge-Prozess im unabhängigen Fedora-Gast isoliert implementieren; Subscription-Lifecycle und Exceptions im SDK-Callback sicher abfangen; Replay-/Crash-Lock zwischen Prozessen; nachgewiesene Dateiverarbeitung und durable Ack mit exaktem Scope/Cursor/Evidence; FastForward/TreeRefresh-Rebaseline; Rate-Limit/Backoff und Event-Gap-Semantik. Die bestehende Engine, produktiven Timer und der Revisions-Guard bleiben unberührt. Freigabe NO-GO.
