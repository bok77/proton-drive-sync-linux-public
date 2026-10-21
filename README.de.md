# Proton Drive Sync für Linux

**Deutsch** · [English](README.md)

Eine native GNOME-Oberfläche für eine bidirektionale Proton-Drive-Synchronisierung unter Linux, bei der Datensicherheit und Wiederherstellbarkeit im Mittelpunkt stehen.

**Status: lokale Alpha-Vorschau. Nicht veröffentlicht und nicht für fremde Konten oder ungesicherte Datenbestände freigegeben.**

**Die bisherige Entwickleroberfläche darf nicht als allgemeiner Synchronisationsclient eingesetzt werden.** Für den öffentlichen Betrieb fehlen noch Freigaben.

## Linux-Kompatibilität und Cloud-Überwachung

**Bisher ausschließlich auf Fedora getestet.** Andere Linux-Distributionen wie Ubuntu, Debian, Mint, openSUSE oder Arch wurden **noch nicht getestet**. Distributionstests sind eine ausdrücklich gewünschte [Community-Aufgabe](docs/COMPATIBILITY.de.md) mit einer [GitHub-Meldevorlage](.github/ISSUE_TEMPLATE/distribution-test.md). In der Alpha-Phase nur synthetische Testdaten verwenden.

**Beide Richtungen werden überwacht, jedoch unterschiedlich:** Linux erkennt lokale Änderungen ereignisgesteuert durch inotify. Proton-Drive-Änderungen werden durch regelmäßige Cloud-Prüfungen entdeckt, nicht durch einen Echtzeit-Cloud-Watcher. Ein zuverlässiger offizieller Änderungsfeed ist eine [offene Community-Forschungsaufgabe](.github/ISSUE_TEMPLATE/cloud-change-detection.md).

## Was bereits funktioniert

- Native GTK4-/libadwaita-Oberfläche mit Übersicht, Aktivitätsprotokoll, systemd-Dienststatus und Einstellungen.
- Oberfläche auf Deutsch und Englisch; Auswahl manuell oder anhand der Betriebssystemsprache.
- Konfigurierbare Ausschlüsse für neue, bisher nicht synchronisierte Dateien.
- Manueller Start des bestehenden lokalen Sync-Dienstes; Anzeige der Warteschlange und des Gesundheitszustands.
- Die Anwendung nutzt den vorhandenen Synchronisationsdienst mit der offiziellen Proton-Drive-CLI. Sie verwaltet selbst keine Zugangsdaten.

## Was noch nicht fertig ist

Grafische Oberfläche und Synchronisations-Engine sind noch **kein gemeinsam installierbares Paket**. Die vorhandene Engine läuft derzeit auf dem eingerichteten Fedora-Rechner und verwendet teils rechnergebundene Pfade. Deshalb ist diese Vorschau auf einem neuen Linux-Rechner noch kein eigenständiger Sync-Client.

Cloud-Polling, Löschschutz, Quarantäne, Konflikterkennung und Wiederanlauf wurden gezielt getestet. Vor der Veröffentlichung fehlen jedoch unabhängige, reproduzierbare Negativ- und Belastungstests. Proton Docs und Sheets benötigen gegebenenfalls gesonderte Behandlung. Lokale Ereignisse erkennt inotify; Cloud-Änderungen werden derzeit periodisch geprüft.

## Experimentelle Vorschau auf Fedora sicher anzeigen

Der öffentlich prüfbare Quellcode ist **kein freigegebener Synchronisierungsclient**. Ausschließlich mit einem separaten Testbenutzer und synthetischen Daten testen. Erforderlich sind Python 3, PyGObject, GTK4 und libadwaita. Im geklonten Repository:

```bash
PYTHONPATH=src python3 -m proton_sync_desktop --public-alpha
```

**Die Entwickleroberfläche ohne `--public-alpha` nicht starten.** Dieser Altpfad kann maschinenspezifische Benutzerdienste ansteuern und ist nicht für den allgemeinen Betrieb freigegeben. Die isolierte Vorschau führt keinen echten Cloudtransfer aus.

## Schutzregeln

- Die GUI liest nur Metadaten des Sync-Betriebs und keine Dokumentinhalte.
- Sie kann den bestehenden systemd-Synchronisationsdienst starten.
- Ausschlüsse gelten ausschließlich für neu auftauchende Dateien; bereits synchronisierte Dateien bleiben unverändert.
- Die bestehende private Engine verwendet Revisionsprüfungen, geprüfte Download-Zwischenschritte, Wartefristen und wiederherstellbare Löschvorgänge.
- Keine automatische endgültige Löschung.
- Persönliche Dateien, Sync-Protokolle, Tokens, Dateinamenlisten und Zustandsdateien dürfen nicht in Git gelangen.

## Vor einem öffentlichen Alpha-Release

1. Sync-Engine portabel machen, Konfiguration externalisieren und Installation/Update/Deinstallation bereitstellen.
2. Reproduzierbare Positiv- und Negativtests für konkurrierende Änderungen, Offlinebetrieb, Neustarts, Cloud-Löschungen, volle Warteschlangen, Symlinks und Übertragungsabbrüche.
3. Visuelle, barrierefreie und responsive GNOME-Abnahme; Übersetzungen durchsehen.
4. CI, Sicherheitsrichtlinien, Release-Verfahren und Wiederherstellungsanleitung.
5. Veröffentlichung erst nach ausdrücklicher Sicherheitsfreigabe.

## Herkunft und Lizenz

Der Quellcode dieses Repositorys wurde eigenständig für dieses Projekt erstellt. Das Projekt `lafontaj/proton-drive-cli-sync` wurde als Architekturvergleich herangezogen; **kein fremder Quellcode wurde kopiert**. Sollte dies künftig erfolgen, müssen die jeweiligen Lizenzbedingungen berücksichtigt werden.

Unabhängiges Community-Projekt ohne Zugehörigkeit oder Unterstützung durch Proton.

Lizenz: MIT (siehe LICENSE).

## Bedienung: synchronisieren ohne Rätselraten

Die kompakte Startseite erklärt die drei tatsächlich eingerichteten Wege:

| Woher | Wohin | Wann |
|---|---|---|
| `<local-sync-root>` | Proton Drive `/my-files` | Bei lokaler Änderung; 5-Minuten-Rückfallprüfung |
| Proton Drive `<priority-folder-a>` und `<priority-folder-b>` | Fedora `<local-sync-root>` | Alle 10 Minuten für direkte Dateien |
| Proton Drive `/my-files` | Fedora `<local-sync-root>` | Stündlicher vollständiger Abgleich |

Die Schaltflächen **„Fedora → Proton jetzt starten“** und **„Proton ↔ Fedora jetzt prüfen“** stehen ohne Ausklappen direkt unter dem Sync-Plan. Die Bestätigung bedeutet nur, dass der systemd-Dienst angefordert wurde. Das tatsächliche Ergebnis steht im Aktivitätsprotokoll. Diagnosedetails sind optional aufklappbar.

Technischer Fallbericht: [Engineering Case Study – Deutsch](docs/ENGINEERING_CASE_STUDY.de.md). Keine garantierten Jobangebote oder Reichweitenbehauptungen.

## Konfigurierbare Synchronisationswege – neue GNOME-Oberfläche

Die Startseite zeigt bei jedem Weg den Button **Bearbeiten**. In diesem Dialog sind die derzeit unterstützten Einstellungen tatsächlich mit den produktiven Diensten verknüpft:

- **Lokaler Upload:** Intervall der zusätzlichen Prüfung auf 5, 10, 15 oder 30 Minuten stellen. Der Dateiwächter läuft weiterhin ereignisgesteuert.
- **Bevorzugte Cloud-Ordner:** Unterordner in Proton Drive direkt eingeben oder im Cloud-Browser auswählen. Jeder konfigurierte Ordner wird real bei den priorisierten Cloud-Prüfungen berücksichtigt. Intervalle: 5, 10, 15, 30 oder 60 Minuten. Nur direkte Dateien dieser Ordner werden im Kurzintervall geprüft.
- **Vollständiger Cloud-Abgleich:** Zeitplan auf 30, 60, 120 oder 180 Minuten setzen.
- **Lokaler Hauptordner:** Der GNOME-Dateiauswahldialog ist verfügbar; gegenwärtig darf nur die bestehende Basis `<local-sync-root>` bestätigt werden. Ein anderer Ordner erfordert zuerst einen ausdrücklich getesteten Migration-/Rebaseline-Vorgang. Die UI zeigt diese Grenze statt einen inaktiven Pfad zu speichern.
- **Cloud-Hauptordner:** `/my-files` bleibt an die bestehende Baseline gebunden. Andere Cloud-Basen werden nicht stillschweigend freigeschaltet.

Validierte Einstellungen werden unter `~/.config/proton-bisync/routing.json` gespeichert. Die systemd-User-Timer werden tatsächlich aktualisiert und vor einer Erfolgsmeldung zurückgelesen; bei Fehlern wird der bisherige Stand wiederhergestellt.

Das neue skalierbare App-Icon liegt in `packaging/proton-drive-sync.svg`. Der Installationsskript installiert es in die persönliche GNOME-Icon-Bibliothek. Keine Proton-Markenrechte werden beansprucht.

**Nachweis:** Echte Änderung 10 → 15 → 10 Minuten mit Konfigurations-Readback, unverändertem Dateibestand; ergänzende Positiv- und Negativtests für Pfadschutz und Rollback.

## Neue Live-Oberfläche mit drei Synchronisationskarten (20. Oktober 2026)

Die native GTK4-/libadwaita-Startseite orientiert sich am freigegebenen Kartenentwurf: Blau für lokale Uploads, Violett für bevorzugte Cloud-Ordner und Grün für den vollständigen Cloud-Abgleich. Jede Karte zeigt Herkunft, Ziel, echtes Prüfintervall, die vorhandene Aktion **Jetzt hochladen / Jetzt prüfen / Jetzt abgleichen** und die zugehörigen Einstellungen. Statuskennzahlen und technische Details stehen darunter.

**Fortschritt:** Während des tatsächlich aktiven systemd-Dienstes pulsiert in der betroffenen Karte ein Fortschrittsbalken. Mangels belastbarer Phasen- und Dateizähler der aktuellen Scan-Engine wird keine erfundene Prozentangabe angezeigt. Ein Balken bedeutet *läuft*, nicht *x Prozent erledigt*. Erfolgreiche Abschlüsse und Fehler stehen im Aktivitätsprotokoll. Lokale Uploads, Cloud-Prioritätsprüfung und Vollabgleich verwenden weiterhin die bestehenden gesicherten systemd-Dienste.

Neue Tests prüfen alle drei Aktionen, Deutsch/Englisch sowie Fehler- und Timeout-Fälle. Der Sync-Kern wird durch die UI-Änderung nicht ersetzt.

## Messbarer Fortschritt und getrennte Dateiüberwachung (20. Oktober 2026)

Die Oberfläche unterscheidet ausdrücklich zwischen:

- **Dateiüberwachung aktiv:** Der `inotify`-Dienst beobachtet laufend lokale Änderungen. Dies ist eine statische Statusmeldung ohne Fortschrittsbalken.
- **Prüfung bekannter Dateien:** Die Sync-Engine schreibt fortlaufend bereits begonnene Prüfungen und die reale bekannte Gesamtzahl in private, atomar aktualisierte Fortschrittsdateien. Die Oberfläche zeigt einen ruhigen Prozentbalken und z. B. `250 von 1000 Dateien geprüft · 25 %`.
- **Cloud-Bestandsaufnahme, neue Dateien und Folgearbeiten:** Solange keine feste Gesamtzahl bekannt ist, steht lediglich der tatsächliche Arbeitsschritt ohne bewegten Balken da. Prozentangaben beziehen sich **nur auf die angegebene Prüfphase**, nicht auf den vollständigen Datentransfer und sind keine Restzeitprognose.
- **Inaktive Dienste:** Alte Fortschrittsdaten werden niemals als laufender Vorgang ausgegeben.

Fortschrittsdateien liegen unter `~/.local/state/proton-bisync/progress_{local,priority,full}.json`. Die Instrumentierung befindet sich im privaten lokalen Sync-Kern; ein portables Open-Source-Engine-Paket ist noch nicht freigegeben. Positive und negative Tests prüfen frische reale Zähler, unbekannte Gesamtzahlen, veraltete Daten und abgebrochene Dienste.

## Kartenhöhe und Dateiüberwachung – 20. Oktober 2026

Alle drei Synchronisationskarten füllen dieselbe GTK-Grid-Zeile. Die flexible Leerfläche oberhalb der Aktionen richtet die Start- und Einstellungsknöpfe auf gleicher Höhe aus, auch wenn Pfade oder Beschreibungen unterschiedlich lang sind.

Die Betriebsanzeige oben zeigt vorrangig den tatsächlichen Status des permanenten `proton-sync-watcher.service`: **Dateiüberwachung läuft** bzw. **Dateiüberwachung gestoppt**. Ein grünes Statussymbol kennzeichnet den aktiven Wächter. Bei Fehlern wird zusätzlich eine sichtbare Warnung angezeigt. Im lokalen Sync-Kärtchen wird kein separater, redundanter Überwachungsstatus mehr dargestellt. Prozentbalken erscheinen weiterhin ausschließlich bei echten, messbaren Datei-Prüfphasen.

## Nutzerführung: automatische Synchronisierung und regelmäßiger Vollabgleich

Die Oberfläche zeigt nun **zwei Synchronisationsrichtungen** in einem gemeinsamen Bereich:

1. **Linux → Proton Drive:** Lokale Dateien werden mit inotify erkannt und hochgeladen; ein konfigurierbarer Timer prüft als Rückfallebene auf übersehene Änderungen.
2. **Proton Drive → Linux:** Bevorzugte Cloud-Ordner werden in einem konfigurierbaren Intervall auf neue oder veränderte direkte Dateien geprüft.

Darunter steht separat der kompakte **vollständige Sicherheitsabgleich**. Dieser ist **nicht nur initial**, sondern weiterhin wiederkehrend erforderlich, weil der lokale Dateiwächter keine Änderungen erkennt, die in Proton Drive oder an anderen Geräten entstehen und außerhalb der priorisierten Cloud-Ordner liegen.

Oben ist **Automatische Erkennung lokaler Änderungen** über einen gut sichtbaren Schalter **Ein/Aus** steuerbar. Ein/Aus wirkt nur auf `proton-sync-watcher.service`, nicht auf die Zeitpläne für lokale Rückfallprüfung und Cloud-Abgleich. Der Status wird aus der echten systemd-Konfiguration zurückgelesen. Ist die Überwachung absichtlich deaktiviert, wird das nicht als technischer Dienstfehler bewertet.

Die Bezeichnung Linux ist bewusst distributionsneutral. Der zugrundeliegende Stand ist allerdings bislang nur auf dem aktuellen Fedora-System getestet; eine portable distributionsübergreifende Installationsabnahme steht noch aus.

## Überarbeitete Statushierarchie – 20. Oktober 2026

Die Startseite priorisiert den **regelmäßigen vollständigen Abgleich** als Sicherheits- und Konsistenznachweis. Ein erfolgreich abgeschlossener und ausreichend aktueller Lauf wird mit Uhrzeit und tatsächlichem Prüfintervall dargestellt. Warnungen erscheinen nur bei fehlendem, zu altem oder fehlerhaftem Nachweis. Ein aktivierter Timer allein beweist keinen erfolgreichen Lauf.

Linux-Ereigniserkennung und Proton-Cloud-Polling werden untereinander im Überwachungsbereich ausgewiesen. Der missverständliche blaue Schalter wurde aus der Statusanzeige entfernt. Unter **Details** befindet sich stattdessen die eindeutig beschriftete Aktion „Lokale Überwachung ein-/ausschalten“. Die Änderung wirkt nur auf inotify, nicht auf die übrigen Prüfungen. Der bisherige große Sicherheitsabgleich-Kasten wurde entfernt, weil er die obere Statusmeldung duplizierte. Der manuelle Vollabgleich und seine Einstellungen bleiben unter **Details** verfügbar.

## Benutzeroberfläche: zentrale Synchronisierung (20. Oktober 2026)

Die Übersicht zeigt **eine zentrale Aktion „Jetzt synchronisieren“**. Darunter stehen die getrennten Zustände der lokalen Linux-Erkennung und der zeitgesteuerten Cloud-Prüfung; die lokale Erkennung ist direkt schaltbar. Fachliche Einzelprüfungen (lokaler Upload, priorisierte Cloud-Prüfung, vollständiger Abgleich) sowie separate Intervalle befinden sich unter „Erweiterte Einstellungen und Einzelprüfungen“. Der periodische vollständige Abgleich bleibt zwingend, weil Ereignisse außerhalb der priorisierten Cloud-Ordner sonst unentdeckt bleiben könnten.

UX-Vergleich: GoodSync (Analyse vor Sync, automatischer Betrieb), FreeFileSync (bidirektionale Änderungen und Vorschau), Syncthing (klar verständliche Laufzustände). Nächste Produkt-Gates sind portable Installation, reproduzierbare Tests, Fehlerszenarien, belastbare Vorschau von Löschungen und Reifeabnahme. Ein für andere Anwender sicher nutzbarer Client ist noch nicht erreicht.

**Nach dem öffentlichen Release:** E-Mail mit dem verifizierten GitHub-Link versenden. Dieser Schritt ist in [RELEASE_COMMUNICATION.de.md](docs/RELEASE_COMMUNICATION.de.md) verbindlich dokumentiert; bisher wurde keine E-Mail gesendet.

## Dashboard: zwei Überwachungsschalter und sichere Änderungsvorschau (20. Oktober 2026)

Linux und Proton Drive haben jeweils einen Ein-/Aus-Schalter im Dashboard. Der Linux-Schalter aktiviert oder deaktiviert den inotify-Watcher. Der Cloud-Schalter steuert **beide** systemd-Timer für priorisierte und vollständige Cloud-Prüfungen gemeinsam. Die Schaltstellungen werden mit systemd zurückgelesen; bei Fehlern werden die vorherigen Einstellungen soweit möglich wiederhergestellt. Manuelle Prüfungen bleiben unabhängig davon möglich; laufende Abgleiche werden durch den Cloud-Schalter nicht abgebrochen.

**Änderungen vorher ansehen:** Ein zusätzlicher Knopf erzeugt einen strikt lesenden Bericht über lokal neue Dateien, mögliche Löschungen und wahrscheinliche Umbenennungen. Die Dateiinhalte der Cloud werden dabei nicht verändert. Dies ist ausdrücklich **noch keine vollständige bidirektionale Vorschau**: Cloud-seitige Änderungen, Transferentscheidungen und gleichzeitige Konflikte können damit nicht vollständig vorhergesagt werden. Deshalb werden aus der Vorschau keine Löschungen oder Synchronisierungen automatisch ausgelöst. Der Ausbau zur vollständigen Vorschau vor kritischen Änderungen ist ein offener Release-Blocker.

Nach dem Abschalten der Cloud-Timer gibt es keinen automatischen vollständigen Cloud-Abgleich mehr; die Oberfläche muss deshalb eine Warnung anzeigen. Dauerhaftes Abschalten wird für den normalen Zwei-Wege-Betrieb nicht empfohlen.

## Neue bidirektionale Vorschau (20. Oktober 2026)

„**Beidseitige Änderungen analysieren**“ liest beide Dateibestände und unterscheidet Upload, Download, Konflikte und Löschkandidaten anhand der gemeinsamen Baseline. Der Vorgang ist ausdrücklich **read-only**; alle Änderungen werden in einer durchscrollbaren Ansicht und einem privaten JSON-Bericht dargestellt. Ein vollständiger Cloud-Scan kann längere Zeit dauern. Die Sicherheitsgrenzen und noch offenen Release-Tests stehen in [BIDIRECTIONAL_PREVIEW.de.md](docs/BIDIRECTIONAL_PREVIEW.de.md).

## Dashboard: letzter Erfolg und nächste Ausführung (20. Oktober 2026)

Die Startseite zeigt den **letzten tatsächlich erfolgreichen vollständigen Abgleich** (Datum und Uhrzeit) und die **nächste von systemd geplante Ausführung** (Datum und Uhrzeit). Eine geplante Ausführung ist kein Erfolgsnachweis. Wenn der vollständige Dienst gerade läuft, wird dies statt einer vermeintlich festen nächsten Ausführungsuhrzeit angezeigt. Bei deaktiviertem Timer erscheint „nicht geplant“; bei fehlender Zeitinformation „Zeitplan nicht verfügbar“. Fehlgeschlagene und unvollständige Läufe überschreiben den letzten nachweisbaren Erfolg nicht. Beide Angaben sind auf Deutsch und Englisch verfügbar.

## Klarere Hauptaktion und optionale Vorschau (20. Oktober 2026)

Die Übersicht zeigt „**Jetzt synchronisieren**“ als einzigen hervorgehobenen Hauptknopf. Er führt den bestehenden, geschützten vollständigen Abgleich aus und kann Dateien übertragen. „**Änderungen vorab prüfen**“ ist darunter als kleinere, optionale Aktion gestaltet. Die Erläuterung stellt ausdrücklich klar, dass die Vorschau keine Dateien verändert. Der reine Analysebericht ist keine Ausführungsfreigabe; beim eigentlichen Sync gelten weiterhin erneute Prüfungen.

## Dashboard-Prüfintervalle und Vorschau (20. Oktober 2026)

Die drei systemd-Prüfintervalle sind unmittelbar auf der Startseite auswählbar: lokale Rückfallprüfung (5/10/15/30 Minuten), bevorzugte Cloud-Ordner (5/10/15/30/60 Minuten) und vollständiger Cloud-Abgleich (30/60/120/180 Minuten). Die Einstellungen werden erst mit **„Intervalle speichern“** an die existierenden Timer übergeben und zurückgelesen; eine fehlgeschlagene Übernahme wird gemeldet. Die lokale inotify-Erkennung bleibt davon unabhängig aktiv. Aus Sicherheitsgründen wird das Speichern blockiert, wenn die Cloud-Überwachung ausdrücklich ausgeschaltet ist, damit das Ändern eines Intervalls sie nicht unbemerkt aktiviert.

Die optionale Aktion **„Änderungen vorab prüfen“** ist als gemeinsame Zeile mit erklärendem Text und rechts ausgerichteter Schaltfläche dargestellt. Der hervorgehobene Hauptknopf bleibt **„Jetzt synchronisieren“**. Die Analyse ist weiterhin rein lesend und löst keine Dateiänderung aus.

## Dashboard-Layout: aufeinander ausgerichtete Prüfintervalle (20. Oktober 2026)

Der Bereich „Automatische Prüfintervalle“ ist nun eine einheitliche GTK-Karte. Alle drei Auswahlfelder verwenden eine gemeinsame Grid-Zeile mit bündigen Beschriftungen und gleichen Spaltenbreiten. Erklärungstext und „Intervalle speichern“ liegen darunter in einer gemeinsamen Footer-Zeile. Nur die grafische Anordnung wurde geändert: Die bestehenden systemd-Intervalle und Dateisynchronisationsregeln bleiben unverändert.

## Intervalle ohne Speichern-Knopf (20. Oktober 2026)

Eine Änderung in einem der drei Auswahlfelder für Linux-Prüfung, bevorzugte Cloud-Ordner und Gesamtabgleich wird jetzt **direkt übernommen**. Die Anwendung aktualisiert im Hintergrund die bestehenden systemd-Benutzertimer, liest die Einstellungen zurück und meldet dezent „Wird übernommen …“ beziehungsweise „Gespeichert“. Ein expliziter Speichern-Knopf ist nicht mehr erforderlich. Bei einem Fehler wird auf den zuletzt gespeicherten Wert zurückgestellt und eine Fehlermeldung angezeigt. Weitere Auswahlen während der Bearbeitung werden zusammengefasst; beim Öffnen des Fensters werden keine Schreibvorgänge ausgelöst. Wenn die Cloud-Überwachung bewusst deaktiviert wurde, bleibt die bestehende Schutzsperre bestehen – Intervalländerungen aktivieren sie nicht stillschweigend.

## Portierung der Engine – erster gesicherter Quellstand (20. Oktober 2026)

Die bestehende Zwei-Wege-Engine ist jetzt als **nicht ausführbare Referenzkopie** unter `src/proton_sync_engine/reference/` im Repository erfasst; die Start-Wrapper liegen in `packaging/reference/`. Die Skripte sind **noch nicht portabel, installiert oder mit einer neuen Installation verdrahtet**. Eine separate, prüfende Konfigurationsschicht unter `src/proton_sync_engine/config.py` blockiert gefährliche Pfade und fehlende Mounts. Die produktive Fedora-Synchronisierung wurde nicht verändert. Siehe [Portierungsplan](docs/ENGINE_PORTING.de.md).

**Portierungsfortschritt (20. Oktober 2026):** Die Engine-Kandidaten unter `src/proton_sync_engine/runtime/` verwenden explizite Konfigurationspfade und sind nicht mit den produktiven Diensten verdrahtet. Die stündliche Sperrkonkurrenz wurde im bestehenden Fedora-Startskript behoben; ein neuer vollständiger Live-Lauf ist als Nachweis noch offen. Details: [ENGINE_PORTING.de.md](docs/ENGINE_PORTING.de.md).

**GNOME-Taskleiste:** Der Starter ist jetzt mit der GNOME-Anwendungs-ID und dem Projektsymbol verknüpft. Er wird unter `io.github.protondrivesync.Fedora.desktop` installiert. Der Installer hat eine isolierte, ausdrücklich nicht aktivierbare Test-Vorschau; eine Installation der Sync-Engine auf fremden Rechnern ist noch nicht freigegeben.

**Entwicklungsstand (20. Oktober 2026):** Die portable Vollabgleich-Engine wurde mit einer simulierten Proton-Cloud erfolgreich auf Uploads, Downloads, Konflikte, Fehler und Wiederholung getestet. Ein fehlender Erstabgleich wird weiterhin strikt blockiert. Dies ist noch **kein Test mit dem echten Proton-Konto** und keine Freigabe für persönliche Daten. Einzelheiten unter [Engine-Portierung](docs/ENGINE_PORTING.de.md).
