"""Disposable Fedora VM: verify the reused GTK alpha view without cloud access."""
from pathlib import Path
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from proton_sync_desktop.app import Application, Window

marker = Path('/etc/proton-mvp-disposable-vm')
if not marker.is_file() or marker.read_text().strip() != 'VM_TEST_ONLY_NO_CLOUD' or Path.home().name != 'mvptest':
    raise SystemExit('BLOCKED: disposable VM required')
if not Gtk.init_check():
    raise SystemExit('BLOCKED: no GTK display')
app = Application(lang_override='en', public_alpha=True)
assert app.register(), 'Application registration failed'
window = Window(app)
try:
    assert list(window.pages) == ['overview', 'settings'], list(window.pages)
    assert window.alpha_result.get_title() == 'No single run yet'
    assert not hasattr(window, 'monitor_switch')
    assert window.refresh() is True
    print('ALPHA_REUSED_GTK_WINDOW_PASS', flush=True)
    print('ALPHA_REUSED_RESULT_ROW_PASS', flush=True)
    print('ALPHA_NO_PRODUCTION_WIDGETS_PASS', flush=True)
finally:
    window.close()
