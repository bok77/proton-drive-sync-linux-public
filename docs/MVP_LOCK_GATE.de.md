# MVP-Kurs und exklusive Pairing-Sperre – 20. Oktober 2026

## Entscheidung

**MVP bleibt Ziel.** Die Stabilitätsarbeit ist nicht die Definition des Produkts: Ein nutzbares MVP ist ein unter Fedora eigenständig installierbarer GNOME-Client, der über die vorhandene authentifizierte Proton-CLI Dateien bidirektional und nach explizitem, nachprüfbarem Erst-Pairing synchronisiert, Konflikte nicht stillschweigend überschreibt, den Status anzeigt und sicher wieder deinstallierbar ist. Ein separater Proton-Testaccount ist für die lesende Prüfung nicht zwingend; Cloud-Schreibtests sind auf bewusst freigegebene synthetische Testordner zu begrenzen.

## Jetzt nachgewiesen

- Exklusive, nicht blockierend erzwungene Prozesssperre `pairing_runtime.lock` in privatem State (0600). Lock-Inode wird auf Typ, Besitzerzugriff und Symlink geprüft; Sperrdatei wird nicht gelöscht.
- Installer-Pairing-Vorschau, explizite Pairing-Freigabe, Recovery-Vorschau, Recovery-Freigabe und **gesamte portable Full-Engine-Ausführung** nutzen denselben `fcntl.flock`-Vertrag. Gleichzeitige Zugriffe scheitern ohne Datenübertragung; Engine-Exit 44 kennzeichnet die Konfliktsperre.
- Synthetische Tests für gleichzeitigen Zugriff, verweigerte Verschachtelung, Symlink, unsichere Rechte, Kernel-Lock-Freigabe nach Prozessabsturz, gesperrten Erststart, erneuten freien Start, Pairing- und Recovery-Kollision.
- Die bestehenden positiven und negativen Sync- und Pairing-Tests bleiben grün.

## MVP-Prioritäten ab jetzt (kein weiteres Ausbauprogramm)

1. **Installierbarer Fedora-MVP-Kandidat:** ein Paket mit GNOME-App, CLI-Adapter, Runtime, explizitem Setup/Pairing, Status und Dienststeuerung; vollständige Abnahme auf einem unabhängigen Fedora-Profil.
2. **Echter isolierter End-to-End-Proof:** ausschließlich im bewussten `ProtonSync-Test`-Testordner, unter geprüfter Backup-/Rollback-Vorbedingung. Kein Zugriff auf persönliche Daten.
3. **Nötige Sicherheits-Gates:** Restart, Offline/Online, Dateiumbenennen/Löschen, Mount-/Symlink-Schutz und ein konservativer Abbruch bei Unsicherheit. Es wird keine atomare Cloud-Transaktion behauptet.
4. **Abnahme für erste Veröffentlichung:** GNOME-UX, Accessibility, CI, Paket-Up-/Downgrade und Deinstallation; anschließend ausdrückliches Release-Gate.

**Nicht MVP:** weitere Sync-Optimierungen, zusätzliche Cloud-Change-Feeds, weitere Plattformen, Autorepair bei unklarer Evidence, eigene Cloud-/Login-Implementierung und Komfortfunktionen. Diese folgen erst nach einem installierbaren Fedora-Proof.

**Offener technischer Blocker:** `flock` verhindert parallele Zugriffe zwischen *unseren* kooperierenden Prozessen, aber keine Änderungen über fremde Proton-Clients. Ein Remote-Revisionswechsel zwischen letztem Lesen und Upload kann weiterhin auftreten; Schreiboperationen müssen deshalb konservative Revisionskontrollen mit fail-closed Verhalten behalten. Kein Release ohne dokumentierten Gegencheck.
