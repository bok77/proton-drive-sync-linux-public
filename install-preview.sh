#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
apps="$HOME/.local/share/applications"
icons="$HOME/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$icons"
install -m 644 "$root/packaging/proton-drive-sync.svg" "$icons/io.github.protondrivesync.Fedora.svg"
mkdir -p "$apps"
dest="$apps/io.github.protondrivesync.Fedora.desktop"
if [[ -f "$dest" ]]; then
  cp -p "$dest" "$dest.before-gtk4-alpha.bak"
fi
cat > "$dest" <<EOF
[Desktop Entry]
Name=Proton Drive Sync
Name[de]=Proton Drive Sync
Name[en]=Proton Drive Sync
Comment=Bidirektionale Synchronisierung: Status und Einstellungen
Comment[en]=Bidirectional synchronization: status and settings
Icon=io.github.protondrivesync.Fedora
StartupWMClass=io.github.protondrivesync.Fedora
Exec=/usr/bin/env PYTHONPATH=$root/src /usr/bin/python3 -m proton_sync_desktop
Type=Application
Terminal=false
Categories=Utility;
StartupNotify=true
Keywords=Proton;Sync;Cloud;Fedora;
EOF
if command -v desktop-file-validate >/dev/null; then
  desktop-file-validate "$dest"
fi
# Remove the older differently named launcher only when it is ours.
# An unmatched / user-customized desktop file is never deleted.
legacy="$apps/proton-sync-status.desktop"
if [[ -f "$legacy" ]] && grep -q '^Icon=io.github.protondrivesync.Fedora$' "$legacy" &&
    grep -q 'proton_sync_desktop' "$legacy"; then
  cp -p "$legacy" "$legacy.before-appid-migration.bak"
  rm -- "$legacy"
fi
if command -v update-desktop-database >/dev/null; then
  update-desktop-database "$apps" || true
fi
echo "Installed GNOME application launcher: $dest"
