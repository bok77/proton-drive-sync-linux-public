# Kompatibilität und Community-Tests

**Auf Fedora getestet:** Die bestehende Entwicklungsinstallation verwendet GNOME, GTK4, libadwaita, systemd-Benutzerdienste und Linux-inotify. Dort sind gezielte GUI-Starttests und echte Synchronisationstests erfolgt.

**Auf anderen Linux-Distributionen noch nicht getestet:** Ubuntu, Debian, Linux Mint, openSUSE, Arch Linux und weitere. Die Linux-Ausrichtung ist ein Entwicklungsziel, keine nachgewiesene Distributionskompatibilität. Ein allgemeiner Installer fehlt noch.

## Community-Aufgabe: Distributionen testen

Wer mitmachen möchte, kann zunächst die portabel zu machende Alpha-Version auf einer weiteren Distribution installieren und ausschließlich **synthetische Testdateien in einem separaten Proton-Testordner** verwenden. Bitte keine produktiven Dokumente einsetzen.

Ein Testbericht soll Distribution und Version, Desktop (Wayland/X11), Python-/GTK4-/libadwaita-/Proton-CLI-Version, Installationsweg, lokale Ereigniserkennung, Cloud-Abgleich, Neustart- und Offline-Fälle sowie reproduzierbare Fehler enthalten. Logs und Screenshots müssen vor der Veröffentlichung von persönlichen Pfaden, Namen und Zugangsdaten bereinigt werden.

Die Tabelle und das zweisprachige Berichtsformat befinden sich auch unter [Compatibility / Kompatibilität](COMPATIBILITY.md).

## Verbindliches Ziel: Beide Richtungen überwachen

Die automatische Überwachung soll **Linux und Proton Drive** berücksichtigen.

- Lokal erkennt Linux-inotify Dateiänderungen ereignisgesteuert. Ein Timer dient als Auffangprüfung.
- Cloud-seitig laufen derzeit echte, zeitgesteuerte Prüfungen: häufig für ausgewählte Ordner und stündlich vollständig. Das ist **kein** Echtzeit-Cloud-Watcher.
- Community-Forschungsaufgabe: prüfen, ob die offizielle Proton-CLI oder ihr SDK einen stabilen, unterstützten Änderungsfeed oder Cursor bereitstellt. Nur ein nachgewiesener, wiederanlauffähiger Ansatz darf das Polling ersetzen oder ergänzen.
- Zugriffsrechte, Wiederholungsversuche, vollständiger Delta-Nachweis, Ausfall während Offline-Betrieb, Idempotenz und Datenintegrität sind vor Aktivierung zu testen.

Der Zustand der aktivierten Cloud-Timer allein ist **kein Nachweis eines erfolgreich abgeschlossenen Abgleichs**. Die Anwendung muss dies getrennt anzeigen.
