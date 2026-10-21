# V1 – Einmaliger GUI-Testlauf für isolierten Dienst, 21.10.2026

**Teststatus: PASS für Anforderung/Start des isolierten Dienstes in der Fedora-44-VM. V1-Endnutzer-Cloudtest: NOCH OFFEN.**

Die bestehende GTK4-Einrichtungsseite besitzt jetzt `Einmaligen Testlauf starten`. Die Aktion erscheint nur, wenn der isolierte Dienst installiert und sein Timer pausiert ist. Sie öffnet einen Sicherheitsdialog mit Standardaktion Abbrechen. Erst nach Bestätigung wird `user_service_lifecycle.run_once()` über die bisherige isolierte Service-Identität ausgeführt. Das Backend prüft die exakten installierten Unittexte, die Manifestintegrität, den privaten Testordner-/Config-Scope, das gültige Erst-Pairing und die pausierte Timerstellung. Ausschließlich `proton-mvp-isolated-full.service` wird mit `systemctl --user start --no-block` angefordert; **keiner der produktiven Proton-Dienste** wird benutzt.

**Realprüfungen im Gast:** GTK→Dialog→Bestätigung→echter systemd-Anforderungsweg war innerhalb des Gesamtablaufs install→enable→pause→run once→enable→pause→run once→uninstall erfolgreich. Der Lauf verwendete ausschließlich einen cloudfreien Test-Stub (`exit 0`), keine echte Proton-CLI. Ausgabe `V1_MVP_GUI_ONE_SHOT_REQUEST_PASS` (2×) und `V1_MVP_ONE_SHOT_CLOUDFREE_VM_PASS`. Dazu lokale 434 Unit-/Regressionsprüfungen.

**Wichtige Grenze:** Die Oberfläche zeigt `Testlauf angefordert · Ergebnis noch nicht bestätigt`. Dieser Zustand behauptet ausdrücklich *nicht*, dass ein Transfer stattgefunden hat. Eine konkrete Anzeige von abgeschlossenen Uploads/Downloads und Fehlern aus dem autoritativen isolierten Engine-Run-Evidence ist noch nicht implementiert. Der vorhandene Button `Jetzt synchronisieren` auf der allgemeinen Dashboard-Seite startet dagegen die produktiven Sync-Dienste und ist **keine** V1-MVP-Testaktion.

**Hoststatus:** Der isolierte `proton-mvp-isolated-full.service` ist auf dem Fedora-Host nicht installiert; auch ein valides installiertes MVP-Bundle wurde nicht festgestellt. Deshalb erfolgte dort kein GUI→Cloud-Liveaufruf. Ein direkter echter CLI-Upload/Download im Testordner ist separat nachgewiesen (`V1_EXISTING_ACCOUNT_SINGLE_TRANSFER_20261021.de.md`). Es gibt keine dauerhafte Cloud-Testfreigabe und keine Änderung an produktiven Diensten.

**V1 bleibt NOT ACCEPTED.** Der nächste echte MVP-Schritt ist die sichtbare, isolierte Ergebnis-/Fehleranzeige und anschließend ein vom Nutzer gestarteter GUI→Engine→Cloud-Test mit neuen Dateien.
