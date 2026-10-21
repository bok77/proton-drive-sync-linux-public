# V1 – GTK-Fokus/Abbrechen in unabhängiger Fedora-44-VM

**Teilnachweis PASS, tatsächliche Fokus-Rückkehr bleibt OPEN.**

In der unabhängigen Fedora-44-VM per Xvfb liefen `scripts/probe_gtk_v1_focus_vm.py` und die reale GTK4/libadwaita-Oberfläche. Bestätigt: sichtbare Hauptaktion ist fokussierbar und nimmt initial programmatischen Fokus an; Bestätigungsdialog ist modal und hat `cancel` als Default und Close-Antwort; Cancel verursacht keine Backend-Mutation; anschließend ist die Hauptaktion weiter sichtbar, sensitiv und fokussierbar. Ausgabe: `V1_GTK_FOCUSABLE_ACTION_PASS`, `V1_GTK_MODAL_CANCEL_DEFAULT_PASS`, `V1_GTK_CANCEL_ACTION_STAYS_FOCUSABLE_PASS`.

Der erste Test zeigte, dass tatsächlicher Fokus **nach** Schließen des Dialogs unter Xvfb nicht zuverlässig auf den Button zurückkehrte. Eine gezielte `GLib.idle_add`-Rückfokussierung nach Cancel wurde in `setup_wizard.py` ergänzt. Der anschließende Test konnte dennoch kein tatsächliches `has_focus()` belegen; daher **kein PASS-Claim für Focus-Return**. Eine echte Tastatur-Tab-/Escape-/Fokus-Abnahme auf GNOME-Sitzung ist weiterhin offen. Der Test nutzt ausschließlich simuliertes Service-Backend, keine Cloud-Session, keine Produktivdienste.
