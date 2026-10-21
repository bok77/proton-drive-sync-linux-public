# V1 – Fokusdiagnose mit und ohne Fenstermanager, Fedora-44-VM

**Ergebnis: Fokus-Rückkehr mit Openbox-Fenstermanager PASS; GNOME-Shell-Abnahme weiter offen.**

In derselben isolierten Fedora-44-VM wird `scripts/probe_gtk_v1_focus_diagnostic_vm.py` mit realen X11-Tastaturereignissen via `xdotool` ausgeführt. GTK4/libadwaita-Backend ist gemockt, es findet weder Proton-CLI-/Cloud-Nutzung noch ein systemd-Write statt.

- **Xvfb ohne WM:** Return öffnet Dialog, Escape schließt ihn. `Gtk.Window.get_focus()` referenziert nach Escape weiterhin den Button, aber `Gtk.Button.has_focus()` bleibt selbst nach 0,7 Sekunden und erneutem `grab_focus()` falsch.
- **Xvfb mit Openbox:** Direkt nach Escape referenziert die GTK-Window-Fokusposition den Button und `has_focus()` ist **true**, auch nach 0,7 Sekunden sowie erneutem `grab_focus()`. Echte X11-Eingaben `Tab` und `Shift+Tab` bewegen den Fokus zu einer fokussierbaren `Adw.ActionRow` und zurück zum Ausgangsbutton. Ausgabe `V1_REAL_WM_ESCAPE_FOCUS_TAB_SHIFT_TAB_PASS`.

Ausführung: `PYTHONPATH=src:. xvfb-run -a sh -c 'openbox & sleep 1; V1_REQUIRE_WM=1 python3 scripts/probe_gtk_v1_focus_diagnostic_vm.py'`. Das Testskript prüft bei `V1_REQUIRE_WM=1` die Fokus-Rückkehr mit Assertions.

**Einordnung:** Starke Evidenz, dass der früher beobachtete Fokusverlust durch fehlenden Fenstermanager unter Xvfb entsteht. Kein Beweis für das Verhalten unter GNOME Shell/Wayland, keine Screenreader-Abnahme. Eine vollständige GNOME-Shell-Desktopumgebung ist in der bisherigen schlanken VM nicht installiert. V1 weiterhin NOT ACCEPTED.
