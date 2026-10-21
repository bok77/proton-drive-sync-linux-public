# Fedora-MVP: unabhängige VM-Prüfung (21.10.2026)

Status: PREPARED; Fedora-44-Image-Download und SHA256-Verifikation noch nicht abgeschlossen.

VM-Assets außerhalb des Git-Repositories: ~/Projekte/proton-fedora-mvp-vm.
QEMU mit KVM, 4 GiB RAM, 2 vCPUs, gesondertem qcow2-COW-Laufwerk und SSH-Port 127.0.0.1:22922.
Keine Host-Dateisystemfreigaben, keine Proton-Zugangsdaten in der VM.
Vorbereitet: cloud-init seed.iso, start-verified-vm.sh mit SHA256-Gate, run-guest-acceptance.sh für Paket- und Selbsttests.
Noch offen: vollständiger verifizierter Download, Gast-Boot, unabhängiger Testlauf, echte GNOME-Klick-/Accessibility-Abnahme.
Ein Cloud-Base-Image ersetzt keine GNOME-Workstation-Abnahme; öffentlicher Release bleibt NO-GO.
