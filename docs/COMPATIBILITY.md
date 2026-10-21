# Linux distribution compatibility / Kompatibilität

**Verified / Getestet:** Fedora (GNOME, GTK4, libadwaita, systemd user services, inotify) on the original development workstation.

**Not yet verified / Noch nicht getestet:** Ubuntu, Debian, Linux Mint, openSUSE, Arch, Manjaro, other distributions and desktop environments. The implementation is Linux-oriented, but cross-distribution compatibility is **not proven**. The current prototype is not yet a portable installer.

## Community testing wanted / Community-Tests gesucht

Please test only on disposable synthetic test data and a separate Proton folder or test account. Do not use personal documents in early alpha testing.

We welcome reproducible reports for distributions and environments not yet validated. Please include:

- Distribution and release; GNOME/other desktop and session (Wayland/X11)
- Python, GTK4, libadwaita, and Proton CLI versions
- Installation approach and service-manager availability
- Local watcher, scheduled cloud checks, offline/reconnect, bilingual UI and conflict scenarios
- Sanitized test logs and exact reproduction steps; no personal paths, filenames, tokens or secrets
- Whether tests were simulated, automated or performed against a dedicated Proton test folder

| Distribution | Installation | GUI | Local events | Cloud polling | Status |
|---|---|---|---|---|---|
| Fedora (development workstation) | Existing custom setup | Smoke tested | Live tested | Live tested | Partial, local alpha |
| Ubuntu | Not tested | Not tested | Not tested | Not tested | Community help wanted |
| Debian | Not tested | Not tested | Not tested | Not tested | Community help wanted |
| Linux Mint | Not tested | Not tested | Not tested | Not tested | Community help wanted |
| openSUSE | Not tested | Not tested | Not tested | Not tested | Community help wanted |
| Arch Linux | Not tested | Not tested | Not tested | Not tested | Community help wanted |

## Critical capability: monitor both local AND cloud changes

Both directions must be observed. The existing implementation currently:

- **Linux → Proton Drive:** kernel inotify watches local folders and triggers uploads, with a timer fallback.
- **Proton Drive → Linux:** polls selected cloud folders at a configurable interval and performs a recurring full-cloud scan. These are real scheduled cloud checks, **not a remote push watcher or real-time cloud event feed**.
- The full scan must remain available to catch changes outside selected cloud folders or missed events.

**Community research task:** Investigate whether the official Proton Drive CLI/SDK exposes a stable, supported cloud changes feed (cursor/change token/subscription) that can safely accelerate remote-change detection. Verify permissions, pagination, retries, reconnect, missed-event recovery, and fail-closed behavior before replacing polling. Do not claim real-time cloud monitoring unless live evidence supports it.

**Safety acceptance:** Never equate a successful timer installation with proof that remote cloud checks completed; separate configured/active monitoring from latest successful cloud reconciliation. No silent data deletion.
