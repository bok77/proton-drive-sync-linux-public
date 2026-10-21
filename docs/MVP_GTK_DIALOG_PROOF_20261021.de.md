# Proton Drive Sync – GTK-Dialogprobe im unabhängigen Fedora-Gast (21.10.2026)

**PASS:** Realer Gtk4/libadwaita-Dialog in Fedora-44-KVM-Gast auf Xvfb, mit mockbarem isoliertem Service-Backend.

Ausführung: `PYTHONPATH=src xvfb-run -a python3 scripts/probe_gtk_mvp_dialog.py`. Ergebnis: `GTK_DIALOG_CANCEL_NO_MUTATION_PASS`, `GTK_DIALOG_EXPLICIT_CONFIRM_PASS`, `GTK_STATEFUL_NEXT_ACTION_PASS` (Exit 0). Der Dialog wurde real erzeugt, Default-/Close-Aktion war `cancel`, seine deutsche Beschreibung wurde geprüft. Die simulierte Cancel-Antwort löste keine Backend-Mutation aus; die simulierte Confirm-Antwort löste genau eine Installation aus. Danach zeigte die Oberfläche die nächste passende Hauptaktion `Testdienst aktivieren`.

Einschränkungen: Das Backend war absichtlich gemockt; kein echter systemd-Zugriff und kein Proton-Cloud-Zugriff. Signale wurden programmatisch an den echten GTK-Dialog gesendet, nicht per Tastatur oder Maus. Ein echter GNOME-Desktop-Screenreader, Tastatur-Fokus, Escape-Verhalten und die gesamte vierstufige Live-Klick-Sequenz sind **nicht nachgewiesen**. Es wird keine vollständige Accessibility-Abnahme behauptet. Öffentlicher Release weiterhin NO-GO.
