# V1 – Pilot-MVP (proton-drive-sync-linux)

**Pilot-MVP · 21. Oktober 2026 · IN ABNAHME, nicht für produktive persönliche Daten freigegeben**

## Definition des MVP

Ein unter Fedora eigenständig installierbarer GNOME-Client, der über die vorhandene authentifizierte Proton-CLI nach **ausdrücklich geprüfter Erstverbindung** ausschließlich einen freigegebenen Testordner bidirektional abgleichen kann. Er stellt Status und Fehler dar und ermöglicht die sichere Verwaltung der isolierten systemd-User-Units. Keine Nutzung persönlicher Produktivdaten während der Abnahme.

**Scope-Entscheidung 21.10.2026:** Ursprüngliches eng begrenztes Pilot-MVP und nachträgliche SDK-/Event-/öffentliche Release-Forschung sind getrennt. Die dokumentierten M1-/M1A-Sicherheitsblocker bleiben verbindlich, ohne dass ein eigenständiger SDK-Dienst automatisch zum ursprünglichen Pilotumfang zählt. Siehe [`docs/MVP_SCOPE_DECISION_20261021.de.md`](docs/MVP_SCOPE_DECISION_20261021.de.md).

## Fertiggestellt und nachgewiesen

| Gate | Status / Evidence |
|---|---|
| Portierbare Engine, Schutz vor unsicherem Pairing, exklusiver Lock | PASS – `docs/MVP_LOCK_GATE.de.md`, `docs/PAIRING_RESTART_E2E_PROOF.de.md` |
| Echte bidirektionale Übertragungen im isolierten Testordner | PASS begrenzter Scope – `docs/REAL_ENGINE_BIDIRECTIONAL_PROOF.de.md` |
| Statusorientierte GNOME-Einrichtung mit Bestätigungsdialogen | PASS technisch, visueller Screenshot – `docs/MVP_STATEFUL_SETUP_UI_20261021.de.md` |
| Installieren → Aktivieren → Pausieren → Entfernen der isolierten User-Units | PASS Backend-Live-Proof – `docs/MVP_STATEFUL_LIFECYCLE_LIVE_PROOF_20261021.de.md` |
| Unabhängiges Fedora-44-QEMU/KVM-Gastsystem, Build, Installation, Selbsttest, Deinstallation | PASS – `docs/MVP_FEDORA44_VM_LIVE_PROOF_20261021.de.md` |
| Reale GTK-Dialog-Signale Abbrechen/Bestätigen/Zustandswechsel mit Mock-Backend | PASS begrenzt – `docs/MVP_GTK_DIALOG_PROOF_20261021.de.md` |
| Fedora-44-CI in privatem GitHub-Repository | PASS – GitHub Actions; Commit `e24ed67` und Folge-Läufe |
| Synthetische Fehlerfälle zu Offline, Konflikten, Rename/Löschung | PARTIAL PASS – `docs/MVP_FAILURE_PROFILE_PROOF.de.md`, Tests |

## Offene Abnahmeschritte – risikobasierte Reihenfolge

**P0 – zuerst klären, keine Umgehung:** Cloud-Datenintegrität und externe CLI-/Rechtsabhängigkeit. **P1 – früh parallel prototypisieren:** sicherer Versionswechsel sowie echte GNOME-/Accessibility-Abnahme. **P2:** konsolidierte Freigabeentscheidung. Status `OPEN/BLOCKED` gilt bis zu einem konkreten Prüfnachweis; vorhandene PASS-Nachweise bleiben in ihrem belegten Scope gültig.

### M1 – Cloud-Race und Datenerhalt (P0, BLOCKING)

**M1-001 weiterhin BLOCKED; isolierte Code-Maßnahme:** Der portable Voll-/Schnellabgleich blockiert nun Updates bestehender Cloud-Dateien, solange atomare Revisionsschreibfähigkeit fehlt; kein Produktivdeploy. Siehe `docs/M1_FAIL_CLOSED_EXISTING_UPLOAD_20261021.de.md`.

**Historischer Befund:** Synthetischer Post-Preflight-Race reproduziert unbedingte neue Revision nach konkurrierender Cloud-Änderung; `docs/M1_CLI_RACE_DECISION_20261021.de.md`. Kein sicherer Atomizitätsnachweis.

1. Kritischen TOCTOU-Fall zuerst prüfen: eine Cloud-Revision ändert sich nach dem letzten `filesystem info` und unmittelbar vor dem tatsächlichen Upload. Feststellen, ob die CLI/serverseitige API eine **bedingte Revisionsoperation** ermöglicht. Falls nicht, eine konservative, real belegte Konfliktstrategie entwerfen; ein bloßer erneuter Preflight gilt ausdrücklich **nicht** als atomarer Schutz.
2. Kontrollierte synthetische und reale CLI-Läufe ausschließlich im Testordner für Remote-Rename/Delete, gleichzeitige Änderungen, Teiltransfer, Netzwerkausfall, erneuten Start und Recovery. Erwartung: kein unkontrolliertes Überschreiben, beide Originale erhalten, Baseline nur nach konsistenter Verifikation aktualisiert.
3. Pro Test Fall, CLI-/Engine-Version, Zeitpunkt der konkurrierenden Änderung, originale Daten, Status und Readback dokumentieren. Bei ungeklärter Atomizität `BLOCKED` beibehalten.

**Reale sequenzielle CLI-Kollisionen PASS:** Datei-Upload `-f skip` meldet bei Kollision Exit 0 / `Skipped: 1` und belässt Revision/Hash unverändert; wiederholtes `create-folder` meldet Exit 1. Nachweis `docs/M1_REAL_CLI_COLLISION_PROOF_20261021.de.md`. Echte gleichzeitige Operationen und serverseitige Atomizität bleiben BLOCKED.

**Neuanlage-Race (synthetisch PASS, real BLOCKED):** `filesystem upload -f skip` verhindert im korrigierten FakeCloud-Modell eine konkurrierende Neuerstellung ohne Baseline-Fortschreibung. Serverseitige Atomizität und sichere Folder-Neuanlage sind nicht bestätigt; siehe `docs/M1_CREATE_ONLY_RACE_20261021.de.md`.

**Echte parallele Testläufe dokumentiert:** Vorhandene Datei mit `skip`: 2× Skip, kein Überschreiben. Neuer Dateiname: 1× Upload, 1× Skip; Ordner: 1× Erfolg, 1× Namenskonflikt. Siehe `docs/M1_PARALLEL_REAL_CLI_PROOF_20261021.de.md`. Dies ist **keine** generelle Atomizitätszusage; Revision-Update-Blocker bleibt.

### M1A – CLI-Vertrag, Betriebsrisiko und Recht (P0, BLOCKING)

**Capability Contract v1 implementiert, PARTIAL PASS:** `cli_capabilities.py` modelliert fehlende atomare Garantie, `skip`-Exit-0-Semantik und Readback; vorhandene Revision-Updates bleiben fail-closed. Offizielle SDK-Guidelines für Drittanbieter müssen vor öffentlichem Release gesondert beurteilt werden. Siehe `docs/M1A_CLI_SDK_CONTRACT_20261021.de.md`.

**Herstellerstatus korrigiert:** Proton Drive CLI 0.9.0 ist offiziell von Proton; Adapter-/Race-Grenzen und Nutzungsbedingungen bleiben gesondert zu verifizieren. Siehe `docs/M1_CLI_RACE_DECISION_20261021.de.md`.

1. Bereits vorhandene Adaptergrenze inventarisieren und einen minimalen, explizit **versionierten CLI-Adaptervertrag** festhalten: List/Info/Download/Upload, Auth-Fehler, Timeouts, Rate-Limits, Revision, Hash, Exit-Code und Retry-Verhalten. Keine zweite Engine bauen.
2. Unterstützte CLI-Versionen samt tatsächlich ausgeführtem Kompatibilitätstest dokumentieren; bei Breaking Change, ungültiger Session oder Rate-Limit risikoadaptiv fail-closed. Erkennung und Diagnose dürfen keine Zugangsdaten protokollieren.
3. Proton-CLI-Lizenz und einschlägige Nutzungsbedingungen anhand aktueller Primärquellen prüfen, rechtliche Unsicherheit transparent dokumentieren; falls nötig fachkundige rechtliche Bewertung vor Alpha. **Nicht** ohne Beleg behaupten, die Nutzung sei zulässig oder untersagt.
4. Token-/State-Grenze technisch nachweisen: Wo liegen CLI-Sessions, welche Dateirechte gelten, wird ausschließlich referenziert? Kein Kopieren in App-Konfiguration, Builds, Repo, Logs oder Telemetrie.

**M1A-Diagnose-Teilnachweis (PASS im isolierten Scope):** CLI-/SDK-Versionsparser, typisierte Fehlerkategorien und lesende Secret-Service-/Rechteprüfung; die tatsächliche Tokenablage und Engine-weite Integration sind noch **offen**. Siehe `docs/M1A_CLI_DIAGNOSTICS_AND_SECRET_BOUNDARY_20261021.de.md`.

**Zentraler portabler CLI-Adapter PARTIAL PASS:** Prozess-Timeouts, Fehlerklassifikation und Redaktion von Providerfehlertexten sind in `runtime/proton-verified-download.py` verdrahtet; die weiteren CLI-Pfade und UI-Evidenz bleiben offen. Siehe `docs/M1A_CENTRAL_CLI_ADAPTER_20261021.de.md`.

**Weitere M1A-Integration (PARTIAL PASS):** Der isolierte Pairing-Inventarscan nutzt jetzt ebenfalls den sicheren CLI-Adapter. Typisierte deutsche/englische Fehlertexte sind implementiert und getestet, aber noch nicht vollständig in alle GTK-Meldungsflächen integriert. Siehe `docs/M1A_PAIRING_ADAPTER_AND_UI_LABELS_20261021.de.md`.

**GTK-Setup-Fehlertexte PARTIAL PASS:** Typisierte CLI-Fehler sind im tatsächlichen Setup-Dialog eingebunden, unkontrollierte Providertexte werden ausgeblendet. Unabhängiger VM-GUI-Proof bleibt nach blockiertem Start offen; siehe `docs/M1A_GTK_ERROR_WIRING_20261021.de.md`.

**Unabhängiger Fedora-44-GTK-Fehlerprobe-PASS:** M1A-Fehleranzeigen in beiden Sprachen mit echten Widgets und synthetischen CLI-Antworten verifiziert; siehe `docs/M1A_GTK_ERROR_VM_PROOF_20261021.de.md`. Tastatur-/Screenreader-Gate unverändert offen.

**M1A Secret-Boundary-Inspector PARTIAL PASS:** Metadatenbasierte Rechte-/Symlink-/Secret-Service-Prüfung hinzugefügt, ohne Tokens zu lesen; tatsächlicher Provider-Tokenpfad und Unlock-Sicherheit weiterhin offen. `docs/M1A_SECRET_BOUNDARY_INSPECTOR_20261021.de.md`.

**M1A neuer P0-Befund:** Offizielle SDK-Guidelines priorisieren ereignisbasierte Synchronisierung statt häufiger vollständiger Traversierung; unser periodischer Full-Scan erfordert eine Konformitätsentscheidung. CLI-Cache-Metadaten `0755`/`0644` verfehlen Owner-only (Inhalte nicht gelesen). Siehe `docs/M1A_PROVIDER_USAGE_AND_CLI_STORAGE_20261021.de.md`. Keine produktiven Berechtigungen verändert.

**M1A Architekturentscheidung / Release-Fence:** Offizielle CLI-Sessions liegen standardmäßig im OS-Keychain (alternativ `pass`; `unsafe_file` ist verboten), App-/Cache-Metadaten verlangen Datenschutzprüfung; eventbasierter Sync mit belegter Anbieter-Schnittstelle statt periodischem rekursivem Vollscan ist als Ziel und offenes Gate festgelegt. `provider_release_gate.py` blockiert Freigabe ohne diese Nachweise. Siehe `docs/M1A_SESSION_AND_EVENT_ARCHITECTURE_DECISION_20261021.de.md`.

**Event-Schnittstellen-Entscheidung:** Der offizielle SDK bietet Subscriptions; die installierte CLI 0.9.0 keinen externen Eventbefehl. Internes CLI-`events.json` wird ausdrücklich nicht als API verwendet. Ein synthetischer fail-closed Event-Cursor-Vertrag ist implementiert; externe SDK-Bridge weiterhin BLOCKED. Siehe `docs/M1A_OFFICIAL_EVENT_INTERFACE_20261021.de.md`.

**Event-Bridge-Spool als synthetischer Teilnachweis:** Private Cursor-/Pending-Dateien, vorläufig keine Cursor-Fortschreibung ohne gesondertes Ack, fail-closed nach Crash. Keine echte SDK-Subscription oder aktivierte Engine. Siehe `docs/M1A_EVENT_BRIDGE_SPOOL_20261021.de.md`.

**SDK-Subscription-Adapter synthetisch PASS:** Injizierter Callback → fail-closed Pending-Spool, Cursor bleibt unverändert; keine echte SDK-Session/Cloudverbindung. `docs/M1A_SDK_SUBSCRIPTION_ADAPTER_20261021.de.md`.

**Node-SDK-Eventrelay synthetisch PASS:** injizierter JavaScript-Subscription-Callback filtert Node-Events, hält unkontrollierte Felder zurück und stoppt bei unerwarteten Events; echter offizieller SDK-/IPC-Live-Proof fehlt. `docs/M1A_NODE_SDK_RELAY_20261021.de.md`.

**Hersteller-API-Korrektur:** `subscribeToTreeEvents` ist als deprecated markiert; künftige SDK-Anbindung soll `iterateEvents` verwenden. Rein synthetischer Iterator-Adapter mit Fail-closed-Ereignistypen integriert, noch keine echte Providerverbindung. `docs/M1A_SDK_ITERATOR_DECISION_20261021.de.md`.

**Node→Python-Prozessgrenze PASS im synthetischen Scope:** JSON-Line-Validierung mit Längen-/Schema-Guards und private Pending-Persistenz; bestätigter Cursor bleibt unverändert. Kein authentifizierter Provider-SDK-Eventfeed. `docs/M1A_NODE_PYTHON_IPC_PROOF_20261021.de.md`.

**SDK-Live-Preflight BLOCKED:** Bun und fest installierte SDK-Version sowie unabhängig belegte Testauthentifizierung fehlen. Read-only Fail-closed-Preflight ergänzt; keine produktive Session berührt. Siehe `docs/M1A_SDK_LIVE_PREFLIGHT_20261021.de.md`.

### M3 – Paket, Upgrade und Rollback (P1, früh parallel; BLOCKING)

1. **Vorziehen:** Ein sicheres Pilotverfahren mit zwei wirklich unterschiedlichen, manifestierten Builds und getrennter Testkonfiguration entwerfen. Dienst explizit stoppen, Zustand sichern, Zielversion installieren, Manifest und Funktion prüfen, erst nach Readback wieder freigeben. Bei Fehler den ursprünglichen Stand mit intaktem Nutzer-State wiederherstellen.
2. Vollständiger Test unter unabhängiger Fedora-VM einschließlich aktiver/pausierter Units, fehlgeschlagener Installation, unerwarteter Fremddateien, Crash/Unterbrechung und Downgrade. Die existierende A→B→A-Remove/Install-Prüfung belegt **keine** sichere Live-Migration.
3. Isolierte Erstverbindung, realer synthetischer Transfer, Neustart und vollständiger Rückbau; niemals gegen produktive Pfade oder Kontodaten. Nur explizit autorisierte Dienstaktivierung.

### M2 – GNOME-End-to-End und Accessibility (P1, BLOCKING)

1. In einer echten isolierten GNOME-Sitzung Sprachtexte, Tab/Shift+Tab, Enter/Leertaste, Escape, Fokus-Rückkehr und Screenreader prüfen; Xvfb-Signaltests sind kein Ersatz. Nach Möglichkeit unabhängige Accessibility-Expertise zur kritischen Bediensequenz einbinden.
2. Installieren, Aktivieren, Pausieren und Entfernen **durch die GUI**: jeweils Abbrechen ohne Mutation sowie Bestätigen mit tatsächlichem systemd-Readback; bei fehlender Testkonfiguration fail-closed.
3. Barrieren konkret dokumentieren, beheben und anschließend erneut testen; keine formale PASS-Kennzeichnung ohne tatsächliche Bedien-Evidence.

### M4 – Abschluss und Release (P2, BLOCKING)

1. Alle P0/P1-Nachweise in einer Evidence-Matrix mit PASS/FAIL/BLOCKED, Commits, CI, Host-Protokollen und Residualrisiken sammeln.
2. Sicherheits-, Datenschutz- und Lizenz-/ToS-Review einschließlich CLI-Session-Dateirechten, Secret-Schutz und Wiederherstellung abschließen.
3. Öffentliche Alpha ausschließlich nach expliziter Freigabe; bis dahin privates Repo und **NO-GO**.

## Aufwand und Steuerung

Orientierung: **mehrere Wochen bis wenige Monate**, abhängig von tatsächlichen CLI-Fähigkeiten, externen Schnittstellen, verfügbarer Accessibility-Kompetenz und Testkapazität; **keine Termin- oder Ressourcen-Zusage**. Früh die P0-Machbarkeit evaluieren, um bei fundamentalen Schnittstellenblockern keine unnötige GUI-/Paketarbeit zu investieren. Fortschritt anhand geschlossener Gates und Belegen statt Prozentzahlen berichten.

## Regeln für die Umsetzung

Kein Feature-Aufbau während dieser Gates. Jede Änderung mit passendem Test, reproduzierbarem Lauf, Commit und CI-Readback. Kein Claim „PASS“ bei fehlender Evidence. Produktive Sync-Dienste, Ordner und Accounts dürfen nicht verändert werden. Fehler führen zu einem klaren Blocker statt zu einer künstlichen Erfolgsmeldung.

Aktueller, fortgeschriebener Nachweis: [`docs/MVP_ACCEPTANCE_GATE_20261021.de.md`](docs/MVP_ACCEPTANCE_GATE_20261021.de.md). Vision: [`VISION.md`](VISION.md).
