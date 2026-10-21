# proton-drive-sync-linux – verbliebene Freigabeprüfungen, 21.10.2026

**Entscheidung: RELEASE NO-GO.** Ausgeführte Regressionen sind von offenen Systemnachweisen getrennt.

## Neu geprüft

1. `tests/test_mvp_release_residuals.py`: zwei voneinander verschiedene, gültig manifestierte Bundles. Eine Überschreibung der laufenden Installation wird verweigert; die Folge `Install A → Remove A → Install B → Remove B → Install A → Remove A` ist im isolierten temporären Dateisystem erfolgreich. Das ist ein bewusstes **Remove/Install**, kein versionsübergreifendes Update mit laufendem systemd-Dienst, keine Migration von Nutzerzustand und keine automatische Wiederherstellung nach Abbruch.
2. Deterministischer Remote-Race vor dem Upload-Preflight: zwischen anfänglichem Listen und erneutem `filesystem info` ändert die Fake-CLI die Cloud-Revision. Die Engine erkennt `remote_changed_before_upload`, bricht ohne Upload ab und verändert weder lokale Datei noch die Baseline. Der Fall ist synthetisch.
3. Vorbestehend: echte GTK/libadwaita-Dialogsignaltests (Cancel ohne Mutation, Confirm mit genau einer simulierten Aktion, korrekter Folgezustand), unabhängige Fedora-44-VM mit Build/Install/Selftest/Uninstall, echte isolierte systemd-Backend-Abfolge, GitHub-CI.

## Nicht durch Tests vorgetäuschte Evidenz

- **TOCTOU im Cloud-Backend:** Eine fremde Änderung *nach* dem letzten `filesystem info` aber *vor* `create-new-revision` kann ohne serverseitige bedingte Revisionsoperation nicht atomar ausgeschlossen werden. Eine identische Inhaltsprüfung nach dem Upload löst die Race nicht zwingend auf. Explizite Entscheidung und realer sicherer Cloud-Gate-Nachweis notwendig.
- **GNOME-Accessibility:** Kein echter Tastatur-/Screenreader-Run mit AT-SPI, Fokus- und Escape-Verifikation auf einem GNOME-Desktop. Xvfb und programmatische Dialogsignale reichen dafür nicht aus.
- **Produktionsnaher GUI-Systemd-Pfad:** Backend-Live-Proof und GTK-Mock-Proof sind getrennt; es fehlt die vollständige tatsächliche Vier-Aktionen-GUI-Live-E2E-Sequenz im isolierten Testnutzer.
- **Paketmigration:** Kein Wechsel mit echtem aktiven, gestopptem oder fehlgeschlagenem Dienst, keine versionierte Nutzerdatenmigration, keine Crash-Recovery; nur sicheres manuelles Remove/Install geprüft.
- **Zusätzliche reale Cloud-Negativpfade:** Remote-Rename/Delete, Parallelbearbeitung, Upload-Unterbrechung und erneuter Start mit echter authentifizierter CLI weiterhin nur partiell belegt.

**Reihenfolge:** Erst Race-Policy und kontrollierte Cloud-Evidence, dann tatsächlicher isolierter GUI-/A11y-Desktoptest, danach versionierter Install/Upgrade/Restore-Proof und finaler Sicherheitsreview. Ohne diese Nachweise keine öffentliche Freigabe.
