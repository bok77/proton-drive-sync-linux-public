# Live-Proof: echter Upload und Download der portablen Engine (20.10.2026)

**Ergebnis: PASS, isolierter Fedora-Testordner. Keine produktive Aktivierung.**

**Scope:** bestehendes Proton-Konto mit authentifizierter CLI; ausschließlich `/my-files/ProtonSync-Test` und `~/Projekte/proton-sync-isolated/Sync/ProtonSync-Test`; separate private Konfiguration und Baseline. Vor Testbeginn: 2 identische Baseline-Dateien, überprüfte Remote-Revisionen, gültiger Erststartmarker. Laufender produktiver Sync nicht umgestellt.

1. **Echter Engine-Upload:** Die nur lokal angelegte synthetische `mvp-engine-upload-proof-20261020.txt` (85 Byte) wurde mit dem installierten portablen Full-Engine-Kandidaten synchronisiert. `new_local_uploaded`, Exit 0; `run_end`: uploaded=1, remote_downloaded=0, valid=2, conflicts=0, errors=0, tracked=3. Eine anschließende Lesekontrolle bestätigte die Übereinstimmung von lokaler SHA-1, Cloud-SHA-1 und Baseline-Revision.
2. **Echter Engine-Download:** Die synthetische `mvp-engine-download-proof-20261020.txt` (49 Byte) wurde ausschließlich zur Anlage der Cloud-Testfixture über die CLI hochgeladen. Die lokale Datei war zuvor nicht vorhanden. Die portable Engine lud die neue Cloud-Datei eigenständig herunter; `downloaded_verified`, Exit 0, `run_end`: remote_downloaded=1, uploaded=0, valid=3, conflicts=0, errors=0, tracked=4. Die zurückgelesenen Bytes stimmten exakt mit der Testfixture überein.
3. **Abschluss-Readback:** Sämtliche vier lokalen Dateien stimmten mit der Baseline (SHA-1) sowie den jeweils aktiven Cloud-Revisionskennungen und -Prüfsummen überein. Der Erststartmarker blieb gültig; alle vier produktiven systemd-Dienste blieben aktiv und wurden nicht verändert.

**Einschränkung:** Zwei synthetische Übertragungen beweisen den grundlegenden realen bidirektionalen Engine-Pfad, aber nicht alle Nebenläufigkeits-, Offline-, Lösch-, Rename-, Update- und Rollback-Fälle oder die Installation und Aktivierung auf einer unabhängig eingerichteten Fedora-Umgebung. Insbesondere ist weiterhin keine atomare Remote-Revisionstransaktion garantiert. **Öffentlicher Release bleibt NO-GO.**
