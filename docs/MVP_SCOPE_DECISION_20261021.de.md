# MVP-Scope-Korrektur – 21. Oktober 2026

## Entscheidung

Die ursprüngliche MVP-Definition in `MVP.md` verlangt einen installierbaren Fedora-GNOME-Client mit ausdrücklich geprüfter Erstverbindung über **die bereits vorhandene authentifizierte offizielle Proton-CLI**, bidirektionalem Abgleich im isolierten freigegebenen Testordner, Status/Fehlern und sicherer Bedienung isolierter User-Units.

**Nicht Bestandteil der ursprünglichen MVP-Definition** sind: separate SDK-Authentifizierung, eigener Node-SDK-Eventdienst, langlebige Event-Subscription, Cursor-Protokoll, Node→Python-IPC. Diese nachträglich entstandenen M1A-Forschungspfade bleiben separat dokumentiert und werden nicht mehr als Bedingung für das *ursprüngliche eingeschränkte Pilot-MVP* ausgegeben. Sie können für öffentliche Produktisierung und Guideline-Konformität später erforderlich werden.

## Unverzichtbare Pilot-Gates

1. Kein bekannt unsicheres Überschreiben von bestehenden Cloud-Dateien; bedingte Revisionsupdates mangels Garantien weiterhin deaktiviert. Eingeschränkte Semantik in Oberfläche klar kenntlich machen.
2. Echte bidirektionale isolierte Übertragungen, Offline-, Konflikt-, Neustart- und Recovery-Fälle, keine stillen Datenverluste.
3. Installieren/Starten/Pausieren/Entfernen, minimale GNOME-Bedienbarkeit, unabhängiger Fedora-Test und CI.
4. Technische und rechtliche Nutzung des offiziellen CLI **für den gewählten, eng begrenzten Pilotbetrieb** prüfen; insbesondere Herstelleranforderung zur Schonung der API und eventbasierter Verarbeitung. Ein `Pilot-MVP` ist damit nicht automatisch zur breiten Nutzung freigegeben.

## Separates Nach-MVP-/Release-Programm

- Offizielle SDK-Eventintegration (abhängig vom bestätigten verfügbaren Auth-/Event-Vertrag), Cursor-Recovery, IPC und operative Hardening-Gates.
- Verlässlicher produktiver Versionswechsel inklusive belastbarem Rollback und umfassende Accessibility-Abnahme.
- Breiter Sync-Scope, öffentliche Distribution, kommerzielle Produktisierung und alle Änderungen an bestehenden Cloud-Revisionen erst nach gesonderter Entscheidung.

**Keine rückwirkende Akzeptanz:** M1/M1A bleiben mit ihren P0-Risiken offen. `NO-GO` für öffentlichen Release unverändert. Der bisherige Fortschrittswert 70–75 % ist eine grobe, nicht evidenzbasierte Aufwandsschätzung und sollte nicht als Abnahmequote verwendet werden.
