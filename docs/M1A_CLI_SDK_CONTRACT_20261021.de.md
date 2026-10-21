# M1A – CLI-/SDK-Adaptervertrag und Provider-Grenzen (21.10.2026)

**Status: PARTIAL PASS für den Codevertrag; P0/Release weiterhin BLOCKED.** Keine Änderungen an produktiven systemd-Units oder privaten Dateien.

## Verifizierter Stand

Lokaler CLI-Readback: `cli-drive@0.9.0+75612299`, SDK `js@0.22.2+75612299`. `filesystem upload --help` kennt `create-new-revision`, `rename`, `replace`, `skip`; jedoch keinen dokumentierten Parameter für einen atomaren Vergleich mit einer erwarteten aktiven Revision. Die öffentliche SDK-Schnittstelle bietet `getFileRevisionUploader(nodeUid,metadata,signal)`, was **keinen** nachgewiesenen expected-revision/Compare-and-Swap-Vertrag darstellt. Es ist nicht belegt, dass die SDK-Implementierung grundsätzlich keine solchen Mechanismen intern verwendet; dem Projekt fehlt aber eine dafür belastbare zugesagte Schnittstelle.

Quelle: https://github.com/ProtonDriveApps/sdk und https://github.com/ProtonDriveApps/sdk/blob/main/client/js/src/protonDrivePublicLinkClient.ts . Das offizielle SDK-README beschreibt die primäre Ausrichtung auf Proton-eigene Clients, erlaubt persönliche nichtkommerzielle Projekte innerhalb seiner Guidelines und bezeichnet kommerzielle/produktive Drittanbieter-Anwendungen als noch nicht bereit. Das ist keine pauschale Aussage, dass private CLI-Automatisierung verboten ist. Eine öffentliche Alpha benötigt eine gesonderte Nutzungs-/Lizenzbewertung und bei Unklarheiten Klärung mit Proton.

## Capability Contract v1

`src/proton_sync_engine/cli_capabilities.py` hält die minimalen, unveränderlichen Capability-Aussagen bereit:

- `conditional_existing_revision_write = False`: Updates vorhandener Revisionen bleiben im **portablen** Runtime-Pfad fail-closed.
- `atomic_create_only = False`: Echte Race-Läufe mit `-f skip` waren erfolgreich, bieten aber keinen allgemeinen Provider-Atomizitätsvertrag.
- `verified_folder_create_only = False`: Wiederholte/überlappende `create-folder`-Tests erfolgreich, jedoch keine Schnittstellen-Garantie.
- `skip_exit_zero_on_conflict = True`: Echte CLI meldete `Skipped: 1` bei Exit 0.
- `readback_required = True`: Rückprüfung nach Cloud-Operationen erforderlich.

`existing_revision_guard` verwendet diesen Vertrag; keine Konfiguration oder Umgebungsvariable kann die Sperre eigenständig deaktivieren. Tests prüfen die konservativen Defaults und den unveränderlichen Datenträger. Positive Upload-Regressionen mit hypothetischem Atomic Provider bleiben explizit *nur synthetisch* gemockt.

## Offene M1A-Nachweise

Versionserkennung und typed Fehlerklassifikation (`AUTH`, `RATE_LIMIT`, `TIMEOUT`, `CONFLICT`, `PROVIDER_ERROR`) am tatsächlichen Adapter, sichere Secret-Store-/Dateirechte-Inspektion ohne Auslesen von Tokens, Nutzungsbedingungen/SDK-Guidelines sowie die Entscheidung über technische Unterstützung realer konditionaler Writes. Bis dahin `NO-GO` für öffentliche Alpha und keine automatische Freigabe bestehender Cloud-Revisionen.
