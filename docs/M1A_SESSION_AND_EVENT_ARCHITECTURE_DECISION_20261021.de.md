# M1A – Entscheidung: Session-Grenze und eventbasierte Synchronisierung (21.10.2026)

**Ergebnis: Sicherheits-/Provider-Gate weiterhin BLOCKED; Teilnachweis aus offizieller Quelle erbracht. Keine produktiven Sync-Änderungen.**

## 1. Offizielle Session-Architektur

Primärquellen: https://github.com/ProtonDriveApps/sdk/blob/main/cli/README.md und `cli/src/config.ts`, `cli/src/credentials/index.ts`, `cli/src/credentials/secretCredentialsStore.ts`, `cli/src/credentials/passCredentialsStore.ts`, `cli/src/credentials/fileCredentialsStore.ts` (21.10.2026).

Die offizielle CLI verwendet standardmäßig `PROTON_DRIVE_CREDENTIALS_STORE=keychain`: Authentifizierungs-Sessions werden über Bun.secrets in den OS-Secret-Store geschrieben (Dienst `ch.proton.drive/drive-sdk-cli`, Name `auth-session`). Alternativ existiert `pass` mit GPG-geschütztem Eintrag. `unsafe_file` speichert Klartext unter `auth-session.json` und ist ausschließlich als unsichere Testoption zu behandeln. Der Quellcode legt bei `unsafe_file` 0600 fest, aber das genügt nicht für Release-Freigabe. Auf dem geprüften Host waren die Umgebungsvariablen `PROTON_DRIVE_CREDENTIALS_STORE` und `PROTON_DRIVE_UNSAFE_CACHE` in der befragten Shell nicht gesetzt. Das belegt die Defaults dieser Shell, nicht die tatsächlichen Umgebungen jedes gestarteten Dienstes.

Die Datenverzeichnisse sind getrennt: `~/.cache/proton-drive-cli` (verschlüsselte SQLite-Caches standardmäßig), `~/.local/share/proton-drive-cli` (Anwendungs-/Event-Daten) und `~/.local/state/proton-drive-cli` (Logs). Die auf dem Host geprüften Cache-/App-Daten haben teilweise Modus 0755 bzw. 0644, Logs 0600. Aus diesen Dateirechten allein folgt **kein** nachgewiesenes Token-Leck, wohl aber ein lokales Datenschutz-/Metadatenrisiko. Die Prüfschritte haben keine dieser Dateien geöffnet und weder Keyring-Abfragen noch Credential-Operationen ausgeführt. Kritische Restprüfung: welche tatsächliche Credential-Store-Konfiguration nutzt die CLI unter verschiedenen Startumgebungen, ist sie gesichert und lassen sich App-/Cache-Rechte ohne Nebenwirkungen im isolierten Paket restriktiv setzen?

## 2. Synchronisierungsarchitektur – Entscheidung für zukünftigen MVP

Die offiziellen SDK-Guidelines (`README.md`, Abschnitt Usage Guidelines for Personal Projects) verlangen ereignisbasierte Cloud-Synchronisation statt häufiger rekursiver Gesamtlisten und begrenzte Parallelität/Backoff. Der bisherige portable Full-Sync führt `filesystem list -j` rekursiv durch; der Prioritätspfad fragt Ordner regelmäßig ab. Dass diese Betriebsart die Guidelines erfüllt, ist **nicht** belegt. Ein erfolgreicher Testlauf oder eine niedrige Dateianzahl ist dafür kein Ersatz.

**Zielarchitektur, noch nicht implementiert:**

1. Ein versionierter, autoritativer Cloud-Event-Cursor je isoliertem Account/Scope als privater State mit überprüfter Provenance. Initiales Snapshot/Pairing nur kontrolliert und selten; kein Dauer-Polling vollständiger Ordnerbäume.
2. Eventfeed über eine **belegte öffentliche CLI-/SDK-Schnittstelle** beziehen; Deduplizierung, Reihenfolge, Cursor-Readback, Gap-Detection, Rate-Limit, Backoff und Idempotenz mit synthetischen Tests. Die offizielle CLI hat zwar persistente Events/SDK-internes Eventhandling, aber ein extern nutzbarer und stabiler Eventfeed ist **noch nicht verifiziert**.
3. Bei verlorenen/ungültigen Cursorn oder undeutlichen Writes strikt `BLOCKED` und manuellen kontrollierten Rescan verlangen; nicht in ungebremste periodische Vollscans zurückfallen.
4. Konflikte und Revisionsupdates weiterhin fail-closed, bis ein nachgewiesener atomarer bedingter Write zur Verfügung steht; Events ersetzen keine Compare-and-Swap-Garantie.
5. Performance-/API-Fairness-Nachweis an synthetischen größeren Scopes, Herstellerkompatibilität, Regressionen, sichere Änderung der Dienste im isolierten VM-Setup und erst dann separate Produktionsfreigabe.

**Reuse before Build:** Erst offizielle SDK-Eventinterfaces und CLI-Events-Befehle prüfen; keinen eigenen Drive-API-Client mit neuer Authentifizierung bauen, solange die sichere Nutzung des SDK ungeklärt ist.

## 3. Implementierter Release-Fence

`provider_release_gate.py` fasst ausschließlich lesende Metadaten zusammen und blockiert `unsafe_file`/unbekannten Credentialmodus, ungeprüfte `pass`-Konfiguration, unangemessene lokale Dateirechte sowie nicht nachgewiesenen Event-Sync und Revision-CAS. **Ein PASS setzt explizit bereitgestellte Nachweis-Flags voraus und ist selbst noch kein externer Provider-Beweis**; keine automatische Freigabe, kein geänderter produktiver Sync-Pfad. Unit-Tests prüfen die Default-Sperre, unsichere Modi und Metadaten. Damit ist M1A weiter OPEN und der öffentliche Release NO-GO.
