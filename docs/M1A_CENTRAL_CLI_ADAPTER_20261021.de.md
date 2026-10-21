# M1A – Zentraler CLI-Aufrufadapter (21.10.2026)

**PARTIAL PASS – portabler MVP-Code; öffentlicher Release weiterhin NO-GO.**

`src/proton_sync_engine/cli_adapter.py` bündelt die Prozessausführung mit explizitem Timeout und gibt entweder erfolgreiches stdout oder eine standardisierte Fehlerklasse zurück: `AUTH`, `RATE_LIMIT`, `TIMEOUT`, `CONFLICT`, `PROVIDER_ERROR`. Bei Fehlern werden weder rohe stdout/stderr-Nachrichten noch potenziell sensitive Providerdetails an den Engine-Logpfad weitergegeben. `FileNotFoundError`/andere `OSError` schlagen ebenso kontrolliert fehl. Keine automatische Wiederholung von Schreibbefehlen (insbesondere keine unkontrollierte Wiederholung nach unklar abgeschlossenem Upload).

Der portable Sync-Aufruf in `runtime/proton-verified-download.py` nutzt den Adapter. Der volle und der schnelle portable Abgleich leiten darüber bereits ihre CLI-Aufrufe. Bestehende Revisionen bleiben aufgrund der unabhängigen `existing_revision_guard`-Sperre weiterhin fail-closed; der neue Adapter schaltet keine Cloud-Schreibfähigkeit frei.

Die neuen Tests `tests/test_cli_adapter.py` prüfen erfolgreiche JSON-Ausgabe, vier Fehlerklassen, Geheimnis-Redaktion, Timeout, fehlende CLI und **genau einen** Aufruf pro Versuch. Die vollen Regressionstests wurden lokal ausgeführt.

**Nicht erfüllt:** Durchgängige Integration jeder sonstigen CLI-Aufrufstelle (z. B. Setup-/Pairing-/Servicehilfen), echter Provider-Test von 401/429/Timeout, SDK-Kompatibilitäts-Gate, sichere Backoff-Policy für reine Leseaufrufe und vollständige lokale Tokenablageprüfung. Fehlersemantik in der späteren Benutzeroberfläche ist gesondert nachzuweisen. Produktive Installationen und Dienste wurden nicht verändert.
