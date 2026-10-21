"""Desktop ID must exactly match the canonical GNOME launcher and icon."""
import unittest
from pathlib import Path
from proton_sync_desktop.app import APP_ID

ROOT=Path(__file__).resolve().parents[1]

class DesktopLauncherTests(unittest.TestCase):
    def test_canonical_launcher_filename_and_wm_class(self):
        script=(ROOT/"install-preview.sh").read_text()
        self.assertIn('dest="$apps/'+APP_ID+'.desktop"',script)
        self.assertIn('StartupWMClass='+APP_ID,script)
        self.assertIn('Icon='+APP_ID,script)

    def test_icon_is_actual_svg(self):
        icon=(ROOT/"packaging/proton-drive-sync.svg").read_text()
        self.assertIn("<svg",icon)
        self.assertGreater(len(icon),400)

    def test_old_desktop_shortcut_is_migrated_cautiously(self):
        script=(ROOT/"install-preview.sh").read_text()
        self.assertIn("proton-sync-status.desktop",script)
        self.assertIn("before-appid-migration.bak",script)
        self.assertIn('grep -q',script)

if __name__=="__main__":
    unittest.main()
