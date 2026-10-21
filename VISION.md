# VISION – proton-drive-sync-linux

**Stand: 21. Oktober 2026 · Produktvision, nicht Release-Freigabe**

## Zielbild

Ein verlässlicher, verständlicher, unabhängig installierbarer und langfristig quelloffener Linux-Client für Proton Drive. Nutzende können ihre eigenen Dateien bidirektional zwischen Linux und Proton Drive synchronisieren, den tatsächlichen Zustand nachvollziehen und im Konfliktfall Daten wiederherstellen. Fedora mit nativer GNOME-/GTK4-/libadwaita-Oberfläche ist die erste Referenzplattform. Die Abkehr von Google-Diensten und die selbstbestimmte Kontrolle über Daten, lokale Ablage und Betrieb sind leitende Motive, ohne proprietäre Cloud-Abhängigkeiten durch unkontrollierte Eigenimplementierungen zu ersetzen.

## Produktversprechen

- **Sicher vor schnell:** Explizites Erst-Pairing, Bestandsvergleich, Revisions- und Prüfsummenkontrollen; im Zweifelsfall blockieren statt stillschweigend überschreiben oder löschen. Konflikte sind sichtbar und wiederherstellbar.
- **Tatsächlicher statt behaupteter Status:** Getrennte Anzeige für Dateiwächter, lokale Uploads, Cloud-Polling, Vollabgleich, Warteschlange, letzte erfolgreiche Ausführung und Fehler; keine erfundenen Fortschrittswerte.
- **Einfacher GNOME-Alltag:** Geführte Einrichtung, eine passende primäre Aktion je Zustand, verständliche deutsche und englische Dialoge, tastatur- und screenreaderfreundlich, kontrollierte Aktivierung und Entfernung.
- **Eigenständig, nachvollziehbar, Linux-zentriert:** Portierbare Engine, explizite Konfiguration, systemd-User-Dienste und CLI-Adapter. Keine Pflicht zu Google-Diensten, Telegram oder einem laufenden Entwicklungswerkzeug. Keine geheimen Produktivpfade im Paket.
- **Reuse before Build:** Vorhandene authentifizierte Proton-CLI und bewährte Linux-Komponenten wiederverwenden. Eigene Anmeldung, Proton-Protokoll-Reimplementierung oder Cloud-Änderungsfeed nur bei belegtem Bedarf und gesonderter Architekturentscheidung.

## Architekturprinzipien

GNOME-UI → kontrollierter Lifecycle-/Statusadapter → portable Sync-Engine → vorhandene authentifizierte Proton-CLI. Lokales inotify erfasst lokale Änderungen; Cloud-Änderungen werden mangels garantierten Live-Feeds in festgelegten Intervallen geprüft. Private Pairing-Baseline, Exclusive Lock und Recovery-Nachweise gehören zur Sicherheitsgrenze. GUI-Freigaben dürfen keine Backend-Gates umgehen. Benutzerdateien, Tokens und Sync-State bleiben aus Repository, Build und Telemetrie heraus.

## Langfristige Abhängigkeitsstrategie

Die **offizielle**, von Proton herausgegebene Proton Drive CLI ist die größte Integrationsabhängigkeit. Der Client hält sie deshalb hinter einem **dünnen, versionierten Adaptervertrag** (List/Info/Download/Upload, Rückgabecodes, Revisionen, Prüfsummen und Fehlerklassen), ohne für das MVP eine zweite Engine oder eine eigene Authentifizierung zu bauen. Unterstützte CLI-Versionen und tatsächlich nachgewiesene Fähigkeiten werden in einer Kompatibilitätsmatrix gepflegt. Bricht eine kritische Fähigkeit, gilt **fail-closed** statt ungeprüftem Weiterbetrieb. Adaptertausch bleibt eine langfristige Option, keine Freigabe zu einer eigenen Protokollimplementierung.

Lokale Authentifizierungsdaten bleiben unter Kontrolle der vorhandenen CLI: die Anwendung referenziert nur ihren autorisierten Zugriff und kopiert weder Tokens noch Session-Dateien in eigenes State, Pakete, Logs oder Telemetrie. Vor öffentlicher Alpha sind die tatsächlich verwendeten Speicherorte, Dateirechte, Fehlerwege und die Nutzungsbedingungen/Lizenzen der Abhängigkeiten zu verifizieren. Rechtliche Unklarheiten werden als Release-Risiko markiert, nicht als stillschweigend geklärt.

## Zielgruppe und Plattformen

Erste Zielgruppe: technisch versierte Fedora- und GNOME-Nutzerinnen und -Nutzer, die Proton Drive unter Linux verlässlich einsetzen möchten. Später weitere Linux-Distributionen nach eigenständigen Plattformtests und Mitwirkung der Community. Kein Anspruch auf offizielle Proton-Unterstützung.

## Reihenfolge

1. **MVP:** Ein unabhängig installierbarer und sicher bedienbarer Fedora-Client für ein bewusst isoliertes synthetisches Testprofil, vollständige technische und menschliche Abnahme vor öffentlichem Alpha.
2. **Öffentliche Alpha:** Dokumentierte Installation, Betrieb, Troubleshooting, Restore und Rollback; kontrolliert erweiterte Testbasis ohne voreilige Freigabe persönlicher Daten.
3. **Stabilisierung und Linux-Erweiterung:** Distributionsunterstützung, Pakete und Usability auf Grundlage realer Nutzer-Evidence.
4. **Langfristig:** Bessere Cloud-Änderungserkennung, Konfliktwerkzeuge, Status-Transparenz und optionale Integrationen, sofern technische Schnittstellen und Sicherheitsargumente tragen.

## Nicht-Ziele des MVP

Keine eigene Proton-Authentifizierung, kein ungesichertes automatisches Löschen, kein universeller Cloud-Sync, keine neuen Plattformen, keine unbewiesenen Atomizitätsgarantien, keine neuen Komfort-Features während der Abnahme. Der vorhandene produktive Fedora-Sync darf durch Tests niemals stillschweigend migriert oder deaktiviert werden.

## Erfolg und Release-Entscheidung

Erfolg bedeutet nachgewiesene bidirektionale Funktion, konservativen Umgang mit Offline-/Race-/Lösch-/Umbenennungsfällen, ein verständliches und barrierearmes GNOME-Erlebnis sowie überprüfte Installation, Aktivierung, Deinstallation und Rollback auf einer unabhängigen Fedora-Umgebung. CI-Grün allein ist kein Release-Gate. Release nur nach dokumentierter Evidenz, Prüfung offener Risiken und expliziter Freigabe; bis dahin **NO-GO**. Details: [MVP.md](MVP.md).
