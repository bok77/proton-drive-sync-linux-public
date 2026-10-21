# V1 – Zusammenhängender cloudfreier MVP-Nutzerablauf (21.10.2026)

**PASS im isolierten Fedora-44-VM-Scope.** `scripts/probe_v1_mvp_cloudfree_journey_vm.py` wurde unter Xvfb + Openbox mit realen GTK4/libadwaita-Dialogen und **echten systemd-User-Kommandos im Gast** ausgeführt. Der Test setzt den expliziten VM-Testmarker und User `mvptest` voraus.

Ablauf: private Testkonfiguration, lokaler synthetischer `ProtonSync-Test`-Ordner, tatsächliche `setup_wizard.verified_isolated_pairing()` (nicht gemockt), GTK-Dialoge mit Cancel-Nichtmutation und Confirm, systemd-Readback sowie sichtbare GTK-Statuszeile für `install → enable → pause → enable → pause → uninstall`. Nach dem Entfernen blieben der lokale Ordner und die verifizierte Pairing-Konfiguration erhalten. Ausgabe: `V1_MVP_LOCAL_PAIRING_VERIFIED_PASS`, sechs `V1_MVP_GUI_*_STATE_PASS`, `V1_MVP_DATA_AND_PAIRING_PRESERVED_PASS`, `V1_MVP_CLOUDFREE_USER_JOURNEY_PASS`; Exit 0.

Der Lauf verwendet ausschließlich eine temporäre, integritätsgeprüfte Bundle-Version mit cloudfreiem Stub (`exit 0`) statt echter Engine. Die **Bundle-Pfadauflösung** wurde auf dieses Testpaket umgebogen, die Pairing-Prüfung und systemd-Operationen hingegen nicht. GUI-Bestätigungsdialoge wurden über programmgesteuerte GTK-Signale bedient; dies ist keine vollständige manuelle GUI-UX-Abnahme. Es gab keine echte CLI-Cloud-Session und keinen Datei-Upload/-Download. Produktive Sync-Dienste und `/mnt/example-drive` blieben unverändert.

**MVP-Restpunkt:** Ein vollständiger beaufsichtigter Endnutzerlauf einschließlich echter Neu-Dateiübertragung im unabhängigen Proton-Testkonto und verständlicher Statusanzeige. V1 weiterhin NOT ACCEPTED.
