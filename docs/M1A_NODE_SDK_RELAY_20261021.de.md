# M1A – Node-SDK-Eventrelay, isolierter Probevertrag

**Synthetischer Vertrag PASS; echte Proton-Subscription NO-GO.**

`bridge/sdk_event_bridge.mjs` stellt einen zur offiziellen JavaScript-SDK-Subscription passenden injizierten Callback-Rahmen bereit, mit zwingend bestätigter Subscription-Handle und `dispose()`. Das Relay filtert nur `node_created`/`node_updated`/`node_deleted` samt Scope, Event-ID und Node-ID und gibt unbekannte Felder (z. B. potenziell sensitive Informationen) nicht weiter. Unbekannte Events und Fehler beim Weiterreichen blockieren und lösen `dispose` aus. Der ausführbare Node-Test `bridge/sdk_event_bridge.test.mjs` demonstriert diese Eigenschaften ohne Credentials, Netzwerk oder produktive Daten.

**Wichtig:** Es gibt noch keinen echten SDK-Import, keine Bun- oder Node-SDK-Installation und keine authentifizierte, autorisierte Live-Subscription. Ebenso fehlen Ende-zu-Ende-IPC zum privaten Python-Spool, Interprozess-Fencing, cursorbezogenes ACK nach verifizierter Dateiverarbeitung und Nachweis der Event-Replay-/Lücken-Semantik. Die SDK-Lizenz und Anbieter-Guidelines müssen für diesen konkreten Client weiter geprüft werden. Dieser Code wird nicht durch systemd gestartet und darf nicht als bereits aktivierter Event-Sync ausgegeben werden.

Die nächsten technischen Schritte sind ein isolierter, versionsgepinnter offizieller SDK-Client mit einem freigegebenen Test-Scope, ein lokales IPC-Protokoll ohne rohe Providerdaten, robuste Recovery- und Cursor-Beweisführung und danach eine erneute M1A-Abnahme. Bis dahin bleiben periodische produktive Dienste unangetastet und der öffentliche MVP-Release NO-GO.
