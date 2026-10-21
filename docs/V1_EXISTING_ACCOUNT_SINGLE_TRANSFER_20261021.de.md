# V1 – Einmaliger echter Proton-CLI-Dateitransfer, 21.10.2026

**Ergebnis: PASS für den direkten CLI-Upload/Download, kein GUI-End-to-End-Beweis.** Nach ausdrücklicher Nutzerwahl „Variante 1“ wurde das vorhandene Proton-Konto einmalig für einen engen Test auf `/my-files/ProtonSync-Test` verwendet. Das ist eine **bewusste einmalige Ausnahme** zur bisherigen Vorgabe einer unabhängigen Test-Session, keine dauerhafte Änderung der allgemeinen Sicherheitsgrenze.

1. Eigens erzeugte Textdatei mit eindeutigem Namen `mvp-v1-once-200eb25f1e3b469d80d3e4f5b2d0f1ee.txt` und unkritischem Testinhalt. Der CLI-Readback bestätigte zunächst, dass der Name noch nicht existierte.
2. Direkter offizieller CLI-Aufruf `filesystem upload -f skip` mit Bestätigung `Uploaded: 1`; kein `create-new-revision` und kein Überschreiben.
3. `filesystem info -j`: SHA-1-Prüfsumme der aktiven Cloudrevision stimmt mit der lokalen Originaldatei überein.
4. `filesystem download -f skip` in temporären lokalen Testordner: heruntergeladene Bytes stimmen vollständig mit dem Original überein.
5. Ergebnis `ONE_TIME_CLI_TRANSFER_PASS`, Exit 0. Die temporären lokalen Testdateien wurden nach Abschluss entfernt. Die eigens neu hochgeladene Cloud-Testdatei verbleibt für einen später explizit autorisierten Rückbau; **kein Cloud-Delete**.

**Grenzen:** Direkte CLI-Aufrufe, nicht die über die GNOME-Oberfläche gestartete vollständige Engine-Übertragung. Die CLI-Anmeldung war die vorhandene Nutzer-Session, nicht ein getrenntes Testkonto. Keine produktiven systemd-Dienste verändert, kein Zugriff auf `/mnt/example-drive` und keine beabsichtigte Veränderung bestehender Cloud-Dateien. Die erteilte Zustimmung galt nur diesem einmaligen Test und ist keine generelle Autorisierung für zukünftige Transfers.

**V1 bleibt NOT ACCEPTED**, bis der tatsächliche GUI→Engine→Cloud-Nutzerablauf als zusammenhängende Bedienung erfolgt; die bekannte Beschränkung von Updates bestehender Cloud-Dateien bleibt bestehen.
