# M1A – Fehlerklassen im GNOME-Einrichtungsdialog, 21.10.2026

**Code/Unit-Tests PASS; Fedora-VM-GUI-Live-Proof BLOCKED.**

Im GTK4/libadwaita-Setup (`setup_wizard.py`) werden CLI-klassifizierte Inventarfehler durch `safe_pairing_error` mit eindeutigen deutschen/englischen Handlungshinweisen angezeigt: AUTH, RATE_LIMIT, TIMEOUT, CONFLICT und PROVIDER_ERROR. Unbekannte Exceptions, fremde Fehlercodes und beliebige Providertexte werden nicht mehr als roher Text im Fehlerdialog gezeigt. Auch die Pairing-Freigabe-Fehlermeldung wird konservativ behandelt. Fehler beim Inventarscan bleiben blockierend; die ausdrückliche Pairing-Freigabe wird dadurch nicht möglich.

Der isolierte `test_cloud_adapter.py` liefert die typisierten `CLI_*`-Gründe und nutzt den zentralen `cli_adapter`. Neue Tests `test_cli_pairing_ui_contract.py` prüfen Textzuordnung, Deutsch/Englisch und das Nichtwiedergeben unkontrollierter Fehlermeldungen. Vollständige lokale Suite: 388/388 PASS.

**Grenzen:** Die reale GTK/Xvfb-Ausführung im eigenständigen Fedora-Gast konnte bei diesem Nachweis nicht gestartet werden (Fernsteuerungs-Sicherheitsblockade des VM-Starts); echte visuelle/Fokus-/Screenreader-Abnahme ist daher weiterhin offen. Es wurden keine echten 401/429-Providerfehler erzwungen. Andere GUI-Seiten und der produktive Client wurden nicht verändert. Der öffentliche Release bleibt NO-GO.
