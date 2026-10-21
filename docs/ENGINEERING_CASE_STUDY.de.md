# Engineering Case Study – Deutsch

## Problem und Produktentscheidung

Ein Linux-Nutzer benötigt eine bidirektionale, datenschutzorientierte Synchronisierung mit Proton Drive. Das Referenzprojekt *lafontaj/proton-drive-cli-sync* bietet eine fortgeschrittene, aber ausdrücklich einseitige Synchronisierung. Unsere technische Entscheidung: bestehende sichere Zwei-Wege-Engine behalten und lokale Ereigniserkennung, Ausschlussregeln sowie eine native GNOME-Oberfläche ergänzen.

## Architektur

`inotify → persistente SQLite-Warteschlange → systemd-Dienst → bestehender verifizierender Synchronisationskern → Proton-Drive-CLI`

Ein unabhängiger stündlicher Cloud-Scan und eine priorisierte 10-Minuten-Prüfung erkennen Cloud-seitige Änderungen. Die GNOME-Anwendung stellt nur Status, explizite Synchronisationsrouten und vordefinierte Aktionen dar; kein direkter Zugriff auf Kontodaten oder Dateiinhalte.

## UX-Entscheidungen

1. **Aufgaben zuerst:** Herkunft, Ziel und Intervall auf der ersten Ansicht.
2. **Zwei große Aktionen oberhalb der technischen Details:** lokaler Upload und vollständiger bidirektionaler Scan; keine irreführenden Erfolgsmeldungen.
3. **Diagnostik nachrangig:** technische Services und letzte Läufe sind aufklappbar.
4. **Deutsch und Englisch:** alle Bedien- und Fehlermeldungen übersetzbar.
5. **Sicherheit zuerst:** Bei Fehlern fail-closed, keine automatische endgültige Löschung.

## Nachweise und Grenzen

- Unittests für GUI-Adapter und Bedienlogik: Positivfälle sowie Negativfälle für nicht verfügbare Services, fehlgeschlagene Starts und Zeitüberschreitung.
- Früher nachgewiesene Engine-Live-Fälle: verifizierter Upload/Download, Umbenennen, Verschieben und Cloud-Papierkorb an ausschließlich dafür erstellten Testdateien.
- Keine Behauptung eines unabhängig durchgeführten End-to-End-Audits.
- Die Engine ist noch lokal eingerichtet, nicht portabel als vollständiges Installationspaket.
- Späterer öffentlicher Alpha-Release ist **nicht freigegeben**.

## Für technische Gespräche und Bewerbungen

Das Projekt kann reproduzierbare Engineering-Kompetenzen demonstrieren: State-Management, Nebenläufigkeitskontrolle, Fail-closed-Design, verständliche Produktführung, Linux-Integration, Tests und internationale Bedienbarkeit. Das ist ein realistisches Portfolio-Argument; weder eine bestimmte Reichweite noch Angebote großer KI-Unternehmen lassen sich daraus garantieren.

**Nächster Meilenstein:** isolierte portable Engine, CI, öffentliche Testnachweise, Sicherheitsreview und demonstrierbare GNOME-Vorschau ohne persönliche Nutzerdaten.
