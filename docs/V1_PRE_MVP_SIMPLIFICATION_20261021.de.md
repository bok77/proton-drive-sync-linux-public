# V1 – Pilot-MVP: Proton Drive Sync für Fedora

**Stand 21.10.2026 · IN ABNAHME · isolierter Testordner, keine Freigabe persönlicher Produktivdaten.**

## Ziel / Funktionsumfang

Eigenständig installierbarer GTK4-/GNOME-Client unter Fedora, der über die vorhandene offizielle, bereits authentifizierte Proton-CLI nach explizitem Pairing den Ordner `/my-files/ProtonSync-Test` mit einem isolierten lokalen Testordner abgleicht. Der Client zeigt Status/Fehler und verwaltet ausschließlich die dazugehörigen isolierten systemd-User-Units (Installieren, Aktivieren, Pausieren, Entfernen). Kein eigener SDK-Login und kein Eventdienst erforderlich.

**Bewusste Begrenzung:** Änderungen an bereits bestehenden Cloud-Dateien sind mangels garantierter atomarer Revisionsoperation fail-closed gesperrt. Die eingeschränkte Schreibsemantik muss in der GUI verständlich sein; V1 darf keine normale universelle bidirektionale Synchronisierung versprechen, solange diese Operation fehlt. Kein automatisches Löschen/Überschreiben, keine Nutzung persönlicher Produktivdateien, kein Umbau der laufenden produktiven Sync-Dienste.

## Vorliegende Teilnachweise

- Isolierter echter CLI-/Engine-Transfer und geprüfte Erstverbindung: `docs/REAL_ENGINE_BIDIRECTIONAL_PROOF.de.md`, `docs/PAIRING_RESTART_E2E_PROOF.de.md`.
- GNOME-Einrichtung und reale GTK-Dialog-Signaltests: `docs/MVP_GTK_DIALOG_PROOF_20261021.de.md`; vollständiger Endnutzer-GUI-Lauf fehlt.
- Backend-Lifecycle der isolierten Dienste und Fedora-44-VM-Build/Install/Remove: `docs/MVP_STATEFUL_LIFECYCLE_LIVE_PROOF_20261021.de.md`, `docs/MVP_FEDORA44_VM_LIVE_PROOF_20261021.de.md`.
- Fedora-CI, synthetische Fehlerfälle und konservative bestehende Cloud-Revision-Guard: GitHub Actions; `docs/M1_FAIL_CLOSED_EXISTING_UPLOAD_20261021.de.md`.

## V1-Entwicklungsregel

V1 bleibt ein begrenzter Machbarkeits-/Bedienpilot über die offizielle CLI. CLI ist ein Befehlstool, kein eigenständiger Hintergrund-Syncdienst; den isolierten Scheduler stellt unser Client. Fair-Use und API-Last des Testumfangs müssen bewertet werden; keine ungeprüfte feste 30-Sekunden-Vorgabe. Die offizielle Linux-Client-Roadmap und die SDK-Kryptographiemigration sind V2-Risiken, keine automatische V1-Feature-Anforderung.

**Neuer Teilnachweis (21.10.):** Vierstufige GTK4-Dialog-/Statusfolge (Installieren, Aktivieren, Pausieren, Entfernen) in unabhängiger Fedora-44-VM unter Xvfb PASS; systemd dabei gemockt. Siehe `docs/V1_GTK_FOUR_STEP_VM_PROOF_20261021.de.md`. GUI→echtes systemd wurde anschließend separat bestanden; Tastatur/Screenreader bleiben offen.

**GUI→systemd in unabhängiger Fedora-44-VM: PASS (isolierter Scope).** Vier echte systemd-Aktionen über GTK-Dialogsignale mit Cancel-Nichtmutation und systemd-Readback; manifestierter cloudfreier Test-Stub. Details: `docs/V1_GTK_REAL_SYSTEMD_VM_PROOF_20261021.de.md`. Tatsächliche Tastatur-/Mausbedienung und Screenreader weiter offen.

**V1 Remote-Missing-Konfliktfix (synthetisch PASS):** Geänderter lokaler Inhalt bei fehlender Cloud-Datei blockiert ab der ersten Beobachtung mit Konfliktstatus statt scheinbar erfolgreichem Aufschub. `docs/V1_REMOTE_MISSING_RECOVERY_20261021.de.md`. Echte Cloud-Negativpfade weiter offen.

**Abnahmematrix:** `docs/V1_PILOT_ACCEPTANCE_MATRIX_20261021.de.md` trennt echte CLI-Läufe, synthetische Regressionen und noch offene Nachweise. V1 weiterhin NOT ACCEPTED.

**Live-Proton-Negativtests:** Vorprüfung `docs/V1_INDEPENDENT_CLOUD_TEST_GATE_20261021.de.md` dokumentiert die fehlende unabhängige Test-Session und sperrt neue Cloudoperationen ausdrücklich. Die lokale Policy-Prüfung ist implementiert, kein authentifizierter Provider-Lauf behauptet.

**GTK-Fokus-Vorprüfung (VM/Xvfb):** Aktionsbutton fokussierbar, Dialog modal mit sicherem Cancel-Default, Cancel ohne Mutation PASS. Tatsächliche Fokus-Rückkehr nach Dialogschluss und physische Tab-/Escape-Bedienung offen. `docs/V1_GTK_FOCUS_VM_PROOF_20261021.de.md`.

**Reale Tastaturereignisse (Xvfb):** Enter öffnet den GTK-Bestätigungsdialog, Escape schließt ihn ohne Mutation: PASS. Fokus-Rückkehr und Tab/Shift+Tab bleiben offen; siehe `docs/V1_REAL_KEYBOARD_VM_PROOF_20261021.de.md`.

**Fokusdiagnose mit Fenstermanager PASS:** In isolierter Fedora-44-VM unter Xvfb + Openbox funktionieren Escape, Fokus-Rückkehr und echte Tab-/Shift+Tab-Navigation. Das Xvfb-ohne-WM-Problem bleibt als Testumgebungseffekt erkennbar; GNOME Shell/Wayland und Screenreader noch offen. `docs/V1_FOCUS_WM_DIAGNOSIS_20261021.de.md`.

**API-Lastprüfung (Codebewertung):** `docs/V1_API_LOAD_ASSESSMENT_20261021.de.md`: nominell 48 geplante Läufe pro Tag mit mindestens einem CLI-List-Aufruf pro besuchtem Cloudverzeichnis und Lauf; tatsächliche HTTP-/Rate-Limit-Last unbekannt. Unbeaufsichtigter Dauerbetrieb NOT ACCEPTED.

## Offene V1-Gates in Reihenfolge

1. **Benutzbare V1-Semantik:** Reale kontrollierte CLI-Negativfälle und Wiederanlauf prüfen, inklusive Remote-Rename/Delete und konkurrierender Änderungen. Für nicht unterstützte Revision-Updates eine klare, getestete Anzeige und blockierte Aktion nachweisen.
2. **GNOME-Bedienung:** Einrichtung, Abbrechen/Bestätigen, Installieren, Aktivieren, Pausieren und Entfernen als zusammenhängenden isolierten GUI-Live-Prozess auf Fedora prüfen; Tastatur-/Fokusgrundfunktionen prüfen. Screenreader-Spezialprüfung kann risikoadaptiert im öffentlichen V2-Release vertieft werden, sofern V1 zugänglich und sicher bedienbar bleibt.
3. **Installation und Recovery:** Isolierten Neustart, Offline-/Fehler-Wiederaufnahme, kontrollierten Rückbau und unveränderte Testdateien beweisen. Kein umfassender versionsübergreifender produktiver Upgrade/Auto-Rollback-Mechanismus als V1-Pflicht.
4. **Pilot-Abnahme:** Kompakte Testmatrix, ehrliche Einschränkungen, bestätigter Test-Scope und explizite Freigabe für den isolierten Pilotbetrieb. Keine automatische öffentliche Veröffentlichung.

Die offiziellen Proton-SDK-Guidelines dürfen auch im Pilot nicht ignoriert werden: API-Last/Scanintervalle im begrenzten Scope bewerten. Wenn der Pilot nachweislich nicht zulässig oder technisch unsicher wäre, bleibt er blockiert; dies erzwingt aber nicht automatisch eine eigene Event-Bridge in V1.

## Ausdrücklich nicht V1

Getrennte SDK-Authentifizierung, Event-Subscriptions, Node→Python-IPC, umfassende Produktisierung, breite Distribution und zusätzliche Komfortfunktionen gehören zur Bewertung in `V2.md` beziehungsweise `V3.md`. Die gesamte bisherige Detail- und Forschungshistorie bleibt unter `docs/MVP_PRE_VERSION_SPLIT_20261021.de.md` sowie den Einzel-Proofs erhalten.

**Entscheidung:** V1 noch NOT ACCEPTED; persönlicher Produktivbetrieb und öffentlicher Release weiterhin NO-GO.
