# Korrektur des Sync-Status und abgeschlossener Pairing-Einrichtung – 21.10.2026

**Problem:** GNOME zeigte gleichzeitig den grünen Erfolgstitel „Meine Dateien sind synchronisiert“ und die Meldung „Vollständiger Abgleich läuft gerade …“. Das war semantisch falsch: Der grüne Titel bezog sich auf einen früheren erfolgreichen Lauf, während aktuell ein neuer Vollabgleich aktiv war.

**Korrektur:** Die aktive Vollsynchronisierung hat nun Vorrang in der Überschrift und zeigt „Synchronisierung läuft“ beziehungsweise „Synchronization in progress“. Der letzte erfolgreiche Abschluss wird als separate Historienangabe beibehalten. Das Statussymbol wechselt während der laufenden Synchronisierung auf „Aktualisieren“. Bei einem abgeschlossenen und gesunden Zustand bleibt die Erfolgsmeldung, bei einem defekten Zustand die Warnmeldung. Keine fiktiven Fortschrittsprozente.

**Einrichtung:** Der frühere Schritt zum erstmaligen Vergleich und expliziten Pairing bleibt für noch nicht eingerichtete Testkonfigurationen verfügbar, wird jedoch auf diesem Fedora-Host nach sicher nachgewiesenem `INITIAL_PAIRING_VERIFIED_V1` (private Konfiguration; `managed_folders=["ProtonSync-Test"]`; kein Pending-Marker) ausgeblendet. Die anschließende Dienststeuerung mit vier Aktionen bleibt sichtbar; der bereits geprüfte Pfad wird automatisch intern gesetzt und ist nicht erneut freizugeben.

**Nachweise:** Testfunktion gegen den vorhandenen isolierten State meldet `True`; frisches gebautes Installationspaket mit gültigem Manifest und `--self-test` (L10N_OK 62, BACKEND_OK 5); 303/303 automatisierte Tests bestanden. Neue GNOME-Testinstanz auf Fedora gestartet. Alte Vorschauinstanz gezielt beendet. Die bestehenden vier produktiven systemd-Units laufen weiter, die MVP-Unit-Dateien sind nicht installiert.

**Offen:** Die zwei aktuellen Screenshots stammen von vor dieser Korrektur. Die tatsächliche visuelle Abnahme der neuen Oberfläche muss separat erfolgen; aus laufendem GUI-Prozess allein wird kein Screenshot-Ergebnis abgeleitet. Öffentlicher Release weiterhin NO-GO.
