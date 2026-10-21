# Fedora Proton Drive Sync – unabhängiger VM-Proof, 21. Oktober 2026

**PASS (headless Gast, Installations- und Laufzeitgates); GNOME-Klick-/Accessibility-End-to-End weiterhin OFFEN.**

- Echtes QEMU/KVM-Gastsystem mit Fedora 44, eigenem 18-GiB-COW-Datenträger, 4 GiB RAM, 2 vCPUs und SSH-Port ausschließlich auf `127.0.0.1:22922`. Fedora-44-Image wurde vor dem VM-Start per SHA256 verifiziert. Kein Host-Filesystem oder Proton-Zugangstoken in den Gast gemountet.
- Cloud-init-Gast `mvptest` mit eigens erzeugtem Testschlüssel: SSH-Anmeldung erfolgreich, Fedora-Gastversion bestätigt. Host-Key-Vertrauen in einer separaten VM-Datei, keine Änderung des regulären `~/.ssh/known_hosts` zur Umgehung der Host-Key-Warnung.
- Paketinstallation in der VM zuerst durch Mirror-Netzwerkfehler blockiert; erneuter Download mit festen Fedora-Repositories erfolgreich. Keine Fehlerumgehung bei Tests.
- Der Quellcode wurde ohne `.git` in die VM übertragen. Dort `PYTHONPATH=src python3 -m unittest discover -s tests -q`: **323/323 PASS**, Exit 0. `python3 -m proton_sync_desktop --self-test`: `L10N_OK 62`, `BACKEND_OK 5`, Exit 0.
- Innerhalb der VM wurde der MVP-Kandidat eigenständig gebaut und in ein neues Verzeichnis installiert. Nach positivem Installations-Selbsttest wurde er mit dem Manifest-prüfenden Deinstaller wieder vollständig entfernt: `GUEST_INSTALL_REMOVE_PASS`.
- Isolierter GTK-Selbsttest unter `xvfb-run -a`: `L10N_OK 62`, `BACKEND_OK 5`, `Xvfb_SELF_TEST_PASS`. Software-Renderingwarnung bezüglich DRI3 ist kein Abbruch. Es wurde kein tatsächlicher GNOME-Dialog geklickt und keine Accessibility-/Screenreader-Sitzung geprüft.

**Freigabestatus:** Die unabhängige Fedora-VM-Installation/Deinstallation, Regression und technische GTK-Laufzeitprüfung sind erfüllt. Die interaktive GNOME-Bedienung, Tastaturfokus, Abbrechen-ohne-Mutation und Screenreader-Abnahme sind damit ausdrücklich **nicht** belegt. Öffentlicher Release bleibt NO-GO.
