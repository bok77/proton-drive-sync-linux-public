# V1-Pilot – Abnahmematrix, 21.10.2026

**Gesamtentscheidung: NOT ACCEPTED.** Getrennte Quellen und Testarten; grünes CI beweist keine sicheren Provideroperationen.

| V1-Gate | Nachweis / Testart | Status | Offener Rest |
|---|---|---|---|
| CLI-Integration & eingeschränkter bidirektionaler Testtransfer | `REAL_ENGINE_BIDIRECTIONAL_PROOF.de.md` (isolierter Testlauf) | PARTIAL PASS | keine vollwertige Update-Synchronisierung bestehender Cloud-Dateien |
| Initial-Pairing, kontrollierter Neustart | `PAIRING_RESTART_E2E_PROOF.de.md`, `PAIRING_RECOVERY_PROOF.de.md` | PARTIAL PASS | unabhängige Gesamtabnahme |
| Bestehende Remote-Datei mit `upload -f skip` | `M1_REAL_CLI_COLLISION_PROOF_20261021.de.md` (echte CLI 0.9.0) | PASS begrenzt | Exit 0 trotz Skip: stets Readback, kein bedingtes Revision-Update |
| Zwei gleichzeitige Neuanlagen/Skip und Folder-Kollision | `M1_PARALLEL_REAL_CLI_PROOF_20261021.de.md` (echte CLI 0.9.0) | PASS begrenzt | keine serverseitige Atomizitätsgarantie |
| Remote-Löschung/Umbenennung bei lokal verändertem Inhalt | `V1_REMOTE_MISSING_RECOVERY_20261021.de.md`, `test_v1_recovery_additional.py` (Fake-CLI) | SYNTHETIC PASS | **echter CLI-Test offen** |
| Offline-Ausfall, erneuter Lauf und Baseline-Erhalt | `test_mvp_failure_matrix.py`, `test_v1_recovery_additional.py` (Fake-CLI) | SYNTHETIC PASS | **echte Unterbrechung im Testprofil offen** |
| Update bestehender Cloud-Revision | `M1_FAIL_CLOSED_EXISTING_UPLOAD_20261021.de.md`, `test_mvp_post_preflight_race.py` | BLOCKED BY DESIGN | sicherer atomarer Vertrag fehlt; in V1 deaktiviert und in UI klar benannt |
| GNOME Dialog-Lifecycle mit echtem systemd | `V1_GTK_REAL_SYSTEMD_VM_PROOF_20261021.de.md` (Fedora-44-VM; cloudfreier Stub) | PASS im Scope | echte Tastatur/Maus/Screenreader-Führung offen |
| Installations-/Rückbau-Probe | `MVP_FEDORA44_VM_LIVE_PROOF_20261021.de.md` | PASS im Scope | Fehler-/Recovery-Abnahme des Gesamtpilots offen |
| Rate-Limits, fairer Providerzugriff | `V1_API_LOAD_ASSESSMENT_20261021.de.md` (Quellcode-Modell, keine API-Telemetrie) | PARTIAL / UNVERIFIED | rekursive 30-Minuten-Scans; unabhängige Messung und Fair-Use-Bewertung nötig |

## V1-Freigabeschranke

Der Pilot bleibt auf ausdrücklich isolierten Testordner, bewusste eingeschränkte Semantik und fail-closed-Schreiboperationen begrenzt. Für die offenen realen Remote-Rename/Delete- und Offline-Proben muss **zuerst** ein unabhängiges Testkonto bzw. eine eindeutig getrennte Test-Session mit gesondertem Scope nachgewiesen werden. Die bestehende produktive CLI-Session oder Cache-Eventdaten dürfen dafür nicht verwendet werden. Das Vorhandensein eines alten Live-Belegs autorisiert keinen erneuten Live-Zugriff.

Nicht in V1 hineinziehen: SDK-Eventdienst, neue Anmeldung, öffentliche Distribution oder V3-Komfort. Öffentliche Freigabe bleibt V2.

**Update:** `V1_INDEPENDENT_CLOUD_TEST_GATE_20261021.de.md` enthält das verpflichtende getrennte Testsession-/Scopes-Gate; `v1_live_test_gate.py` ist fail-closed, es wurde keine echte Cloud-Testsession aktiviert.

**GTK-Fokus-Teilnachweis:** `V1_GTK_FOCUS_VM_PROOF_20261021.de.md` (fokusfähige Aktion und modaler Cancel-Default PASS, tatsächlicher Focus-Return und Tastaturtest OPEN).

**Echte Tastaturereignisse Xvfb:** `V1_REAL_KEYBOARD_VM_PROOF_20261021.de.md`: Enter/Escape PASS; Fokus-Rückkehr und Tab/Shift+Tab OPEN.

**Fokusdiagnose mit WM:** `V1_FOCUS_WM_DIAGNOSIS_20261021.de.md`: Xvfb/Openbox mit echten Return/Escape/Tab/Shift+Tab-Tasten und erfolgreicher Fokus-Rückkehr PASS. GNOME Shell/Wayland und Screenreader OPEN.
