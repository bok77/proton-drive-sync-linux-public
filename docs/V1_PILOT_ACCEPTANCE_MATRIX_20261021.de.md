# V1-Pilot – kompakte Abnahmematrix, 21.10.2026

**Gesamt: NOT ACCEPTED.** Diese Matrix bewertet nur den tatsächlichen Nutzerablauf. Detaillierte Einzel-/Sicherheitsnachweise bleiben in `V1_PILOT_ACCEPTANCE_MATRIX_DETAIL_20261021.de.md` erhalten.

| MVP-Schritt | Bisheriger Nachweis | Status / noch nötig |
|---|---|---|
| GNOME-App starten und isolierten Testordner einrichten | `V1_MVP_CLOUDFREE_JOURNEY_20261021.de.md`: verifizierte vorhandene lokale Pairing-Konfiguration und GTK in der VM | TEILWEISE; Cloud-Verbindung über GUI offen |
| Neue Datei hochladen und neue Cloud-Datei herunterladen | `V1_REAL_GUI_CLOUD_E2E_20261021.de.md`: echte GUI→Engine→Cloud, 1 Upload + 1 Download mit Baseline-Readback | TECHNICAL PASS; persönliche Nutzerabnahme offen |
| Status anzeigen, Testdienst starten/pausieren/erneut starten | `V1_GTK_REAL_SYSTEMD_VM_PROOF_20261021.de.md`, `V1_FOCUS_WM_DIAGNOSIS_20261021.de.md` | PASS im cloudfreien VM-Scope, inklusive neuem bestätigtem Einmalstart; Transferergebnis über GUI offen |
| Sicherer Stopp und Rückbau ohne Datenverlust | `MVP_STATEFUL_LIFECYCLE_LIVE_PROOF_20261021.de.md`, `MVP_FEDORA44_VM_LIVE_PROOF_20261021.de.md` | PASS im cloudfreien VM-Scope; Cloud-Endnutzerlauf offen |
| Mindestsicherheit/klare Limitierung | `M1_FAIL_CLOSED_EXISTING_UPLOAD_20261021.de.md`, `V1_REMOTE_MISSING_RECOVERY_20261021.de.md` | Bestehende Cloud-Updates bleiben gesperrt; deutliche Nutzeranzeige erforderlich |
| Getrennte Cloud-Testanmeldung vor neuen Live-Operationen | `V1_INDEPENDENT_CLOUD_TEST_GATE_20261021.de.md` | BLOCKED: unabhängige Test-Session nicht nachgewiesen |

**Freigaberegel:** Nur ein kurzer, beaufsichtigter Testordner-Pilot nach tatsächlichem GUI→Cloud-Endnutzerlauf, unabhängiger Test-Session und erfolgreicher Prüfung der grundlegenden Daten- und Dienstgrenzen. Kein unbeaufsichtigter Dauerbetrieb.

**Nicht eigenständige V1-Pflichtgates:** vollständige SDK-/API-Lastmessung, reale Rename-/Delete-Race-Matrix, zusätzliche Fenster-/Screenreader-Testprogramme oder öffentliche Distribution. Bereits bekannte Risiken bleiben dokumentiert, werden aber nicht als neues Infrastrukturprojekt vor den grundlegenden Nutzertest gestellt. Wenn ein solcher Fall im Piloten zu unsicherem Verhalten führt, wird der Pilot gestoppt.

**Ausnahme zum Testkonto-Gate:** Für genau einen echten CLI-Transfer hat der Nutzer Variante 1 (bestehendes Konto, nur Testordner) ausdrücklich gewählt. Der Nachweis `V1_EXISTING_ACCOUNT_SINGLE_TRANSFER_20261021.de.md` deckt ausschließlich diese einzelne Operation; künftige Live-Aktionen sind dadurch nicht freigegeben.

**GUI-Einmalstart:** `V1_MVP_GUI_ONE_SHOT_20261021.de.md` belegt mit echtem isoliertem systemd im Gast nur die Startanforderung. Resultat und Cloud-Endnutzertransfer weiter offen.

**Isolierte GUI-Ergebnisanzeige:** `V1_MVP_RUN_RESULT_GUI_20261021.de.md` (neue Abschluss-Events statt Startbestätigung, Backend-Tests PASS; echter GUI→Cloud-Abschluss noch nicht nachgewiesen).

**21.10. E2E Live-Pilot:** `V1_REAL_GUI_CLOUD_E2E_20261021.de.md` TECHNICAL PASS; echte GNOME-UI, isolierte systemd-Unit, reales Proton-Konto/Testordner, 1 Upload/1 Download, Ergebnis in GUI, Units zurückgebaut. Nutzerabnahme/Dauerbetriebsfreigabe NICHT ERTEILT.
