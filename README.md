# Proton Drive Sync for Linux

[Deutsch](README.de.md) · **English**

A native GNOME desktop interface for a safety-first, bidirectional Proton Drive synchronization workflow on Linux.

**Status: public experimental source preview; NOT a supported syncing release.**

**Do not run the legacy developer dashboard against another account or valuable files.** The public-alpha mode is strictly experimental; installation and account independence are not yet accepted for a supported sync release. The one-time supervised GTK-to-Proton test succeeded on Fedora, but existing remote-file updates, unattended operation, and clean installation for third parties remain unsupported.

See [public alpha blockers](docs/PUBLIC_ALPHA_READINESS.md), [security policy](SECURITY.md), and [contribution guidelines](docs/CONTRIBUTING.md). New project documentation and issues are in English; historical German evidence is preserved.

## Compatibility and cloud monitoring

**Validated on Fedora only.** Other Linux distributions (Ubuntu, Debian, Mint, openSUSE, Arch and others) have **not** yet been tested. Cross-distribution compatibility is an explicit [community testing task](docs/COMPATIBILITY.md) with a [GitHub report template](.github/ISSUE_TEMPLATE/distribution-test.md). Never test on your personal files.

**Both directions are monitored, but differently:** local Linux changes trigger inotify; Proton Drive changes are discovered by scheduled priority polling and a recurring full cloud scan. This is **not a real-time cloud push listener**. Investigating a verified, supported cloud change feed is a [community research task](.github/ISSUE_TEMPLATE/cloud-change-detection.md).

## What works

- Native GTK4/libadwaita overview, activity log, systemd service status, and settings.
- German and English interface, manually selectable or based on the operating system language.
- Manage exclusion rules for new, previously unsynchronized files.
- Start an existing local sync service, inspect queued events and current health.
- Uses the existing official Proton Drive CLI through a separate private sync engine; it never handles credentials itself.

## What is not ready

The GUI and the underlying synchronization engine are not yet distributed as a single installable package. The sync engine presently lives in the author's Fedora home directory and contains installation-specific paths. The prototype should not be presented as a general-purpose standalone client.

The underlying engine's cloud polling, deletion, local quarantine, conflict detection and durability have received targeted tests, but not yet the independent reproducible test matrix required for a public release. Proton Docs and Sheets may require separate handling. Local file events use inotify; remote cloud events currently require scheduled polling.

## Safely inspect the experimental source preview on Fedora

This is a **source-only experimental preview**, not a generally usable synchronizing client. Use a separate test user and synthetic data only. You need Python 3, PyGObject, GTK4 and libadwaita. From the cloned repository run:

```bash
PYTHONPATH=src python3 -m proton_sync_desktop --public-alpha
```

Do not run the unflagged developer GUI: that legacy route can target machine-specific user services and was not approved for general distribution. The isolated public-alpha preview cannot perform a real cloud transfer. A separate executable release has not been approved.

### Safe public-alpha preview (not a syncing client)

On a Fedora desktop with the required Python/GTK dependencies, an explicitly requested non-mutating preview can be started with:

```bash
PYTHONPATH=src python3 -m proton_sync_desktop --public-alpha
```

This view deliberately has **no synchronization, credential, timer, or production systemd controls**. It is not a working public sync installer and does not imply cloud connectivity. Do not use a private developer installation as an installer for other people.

The legacy developer GUI remains available without `--public-alpha`; it can control an existing machine-specific production synchronizer and is **not safe for general distribution**. The working synthetic-folder live proof is documented in [the V1 test record](docs/V1_REAL_GUI_CLOUD_E2E_20261021.de.md).

This repository currently provides an experimental desktop prototype and a test-only portable-engine candidate. Do not run this standalone on a new computer expecting your files to synchronize.

## Safety model

- The GUI only reads sync metadata. It does not open or read the contents of personal files.
- It can request the existing synchronization systemd service.
- Exclusions apply to **new** files only; already tracked files are unaffected.
- The current private engine uses revision checks, staged downloads, safety delays and recoverable deletion handling.
- No automatic permanent file deletion.
- Do not commit logs, account data, state baselines, credentials, or real file listings to source control.

## Roadmap before public alpha

1. Separate portable sync engine from machine-specific settings and supply an install/upgrade/uninstall process.
2. Add reproducible edge/failure tests: concurrent writes, reconnect, offline mode, remote deletion, full-queue recovery, large directories, symlinks and interrupted transfers.
3. Complete visual and accessibility review on GNOME, including translations and responsive window sizing.
4. Add CI, security policy, releases, and a documented backup/restore procedure.
5. Publish only after an explicit go/no-go security review.

## Code ownership and attribution

The code in this repository is newly authored for this implementation. The project `lafontaj/proton-drive-cli-sync` was consulted for architecture ideas; **no source files have been copied**. Review upstream licenses if copying code in the future.

Proton Drive is a third-party service. This community project is not affiliated with, endorsed by, or maintained by Proton.

## License

MIT (see LICENSE).

## Task-first synchronization view

The compact overview explicitly shows the real operational routes:

| Source | Destination | Schedule |
|---|---|---|
| `<local-sync-root>` | Proton Drive `/my-files` | On local change; five-minute fallback scan |
| Proton Drive `<priority-folder-a>` and `<priority-folder-b>` | Fedora `<local-sync-root>` | Every ten minutes for direct files |
| Proton Drive `/my-files` | Fedora `<local-sync-root>` | Hourly full scan |

**Run Fedora → Proton now** and **Check Proton ↔ Fedora now** are visible directly below the routes. The acknowledgement only confirms that the systemd job was requested, **not** that the sync has completed. Inspect Activity for confirmed outcomes. Diagnostic details are collapsed by default.

Engineering story: [Engineering Case Study](docs/ENGINEERING_CASE_STUDY.md). The repository makes no recruitment or adoption guarantees.

## Editable sync routes – GNOME interface

Each route on the overview offers **Edit**. Settings are backed by the actual user-level sync services:

- **Local uploads:** change the five-minute fallback to 5, 10, 15 or 30 minutes. The file watcher remains event-driven.
- **Priority cloud folders:** type cloud subfolder paths or navigate Proton cloud folders directly; selected paths really drive the priority scanner. Intervals: 5, 10, 15, 30 or 60 minutes. Only direct files in these folders use this faster polling path.
- **Full cloud scan:** select 30, 60, 120 or 180 minutes.
- **Local root:** the native GNOME directory picker is provided, but changing the baseline-bound root `<local-sync-root>` requires a verified data migration; unsupported root changes are blocked explicitly.
- **Cloud root:** `/my-files` remains bound to the current verified baseline. Arbitrary cloud-root remapping is not advertised as ready.

Validated settings reside in `~/.config/proton-bisync/routing.json` and are applied to real systemd user timers. Failures restore the previous units. The new scalable application icon is `packaging/proton-drive-sync.svg`.

The real timer configuration was changed from 10 to 15 minutes and restored to 10 with successful readback. Automated positive and negative tests cover configuration validation, traversal protection, and rollback. Public release remains **not approved**.

## Live three-card GNOME overview (20 October 2026)

The GTK4/libadwaita overview now uses three visually distinct route cards: blue for local uploads, violet for priority cloud folders and green for the full cloud scan. Each card shows actual source, destination and scan interval, with its own explicit **Upload / Check / Sync now** action and settings. Technical diagnostics remain lower on the page.

**Progress indicator:** Each card pulses a GTK progress bar only while its actual systemd service is active. The current sync engine does not yet expose reliable per-file progress, so the app deliberately does not manufacture a percentage. Real completion and errors are recorded by the existing activity log. The native UI remains separate from the guarded sync engine.

Regression tests cover all three service actions, both languages, failures and timeouts.

## Measured progress vs. continuous file monitoring (20 October 2026)

The GNOME overview distinguishes the static **File monitoring active** state of the inotify watcher from actual sync activity. During a bounded known-file comparison phase, the local engine publishes private atomic progress snapshots and the UI shows an honest determinate progress bar (processed entries / known total for that phase). Cloud inventory discovery, new-file traversal and other unbounded phases show a concise text label **without** an oscillating bar or fabricated percentages. A completed or inactive service never reuses a stale percentage.

Progress files reside under `~/.local/state/proton-bisync/progress_{local,priority,full}.json`. Percentages apply to the named phase only, not total wall-clock work or an estimated completion time. Instrumentation of the locally installed sync engine is not yet part of the portable public-alpha package. Positive and negative tests cover bounded counters, unknown totals, stale readings and inactive services.

## Equal-height cards and watcher visibility – 20 October 2026

All three sync cards share a GTK Grid row. An expanding spacer keeps their action buttons aligned at the bottom even when descriptions or source paths wrap differently.

The main status area prioritizes the actual `proton-sync-watcher.service` state: **File monitoring is running** or **File monitoring stopped**, with a green success symbol or a warning. This is separate from individual sync jobs; the redundant watcher label was removed from the first card. Determinate progress bars remain reserved for genuine measured file-check phases.

## Product model: automatic synchronization and recurring integrity checks

The overview now groups two directional paths into **Automatic synchronization**:

1. **Linux → Proton Drive:** local changes are detected by inotify and uploaded; a configurable fallback timer handles missed events.
2. **Proton Drive → Linux:** selected cloud folders are polled for direct-file changes at the configured interval.

The separate compact **Full integrity scan** remains recurring, not one-off, because local inotify cannot see cloud changes made elsewhere or outside the selected priority folders. The clearly visible **Local change detection On/Off** switch controls only the persistent watcher. The fallback and cloud timers keep running, and the actual systemd status is read back after changes. Intentional OFF is not an infrastructure failure.

Linux is the intended product scope; portable, multi-distribution installation has not yet been validated beyond the current Fedora machine.

## Monitoring and full reconciliation hierarchy – 20 October 2026

The main status prioritizes the recurring full reconciliation as a safety and consistency check. It reports the last verified successful run and the configured interval. A warning appears only when evidence is absent, stale, or failed; enabled timers alone are not proof of a completed scan.

Linux inotify and Proton cloud polling are shown on separate stacked lines. The ambiguous blue switch has been removed from the main status; **Details** contains an explicit local monitoring on/off action. The redundant large full-scan card is removed; manual full reconciliation and its interval settings remain accessible under **Details**.

## One-task sync UI and post-release communication (20 October 2026)

The dashboard now has **one primary “Sync now” action** and separate status rows for Linux local monitoring and scheduled cloud polling. Local detection can be toggled directly. Technical per-direction jobs remain in the advanced disclosure. Full cloud reconciliation remains scheduled to catch missed remote events.

UX references: GoodSync (analyze before sync), FreeFileSync (two-way change preview), Syncthing (clear folder states). Key release blockers are a portable installer, independent failure tests and safe deletion previews.

**After public release:** send an email containing the verified GitHub link, once recipients and contents have been approved. See [RELEASE_COMMUNICATION.md](docs/RELEASE_COMMUNICATION.md). No email has been sent.

## Dashboard: both monitoring switches and a read-only change preview (20 October 2026)

Linux and Proton Drive now each have a clear On/Off switch. The Linux switch controls the persistent inotify watcher. The cloud switch controls both scheduled priority and full-cloud systemd timers together. State is read back; failures attempt to restore the prior schedule. Manual synchronization remains available; already-running scans are not canceled by the timer switch.

**Preview changes** creates a read-only report of newly seen local files, possible local deletions and likely local renames. It does not modify cloud contents or execute deletions. It is **not yet a complete two-way preview**: remote changes, exact transfers and concurrent conflicts are not exhaustively captured. A proper full bidirectional analyze-before-sync preview remains a public-release blocker.

Disabling both cloud timers stops the automatic full reconciliation and should be shown as a warning. It is not recommended for normal two-way synchronization.

## Bidirectional preview (20 October 2026)

**Analyze changes on both sides** reads local and Proton inventories against the common baseline to propose uploads, downloads, conflicts and pending deletions, without mutating user content. The GUI displays a scrollable change list and writes a private 0600 JSON report. Full cloud scans can be slow. See [BIDIRECTIONAL_PREVIEW.md](docs/BIDIRECTIONAL_PREVIEW.md) for limitations and release gates.

## Dashboard: last verified success and next scheduled run (20 October 2026)

The home screen displays the **last verified successful full reconciliation** (local date and time) and the **next schedule provided directly by systemd** (local date and time). A scheduled trigger is not proof of completion. When the full scan is active the app says so; when the timer is disabled or unknown it does not invent a next run. Failed and incomplete runs never replace the most recent verified success. Both labels are localized in German and English.

## Clear primary sync action and optional preview (20 October 2026)

The overview uses **Sync now** as its single primary action. It requests the existing guarded full reconciliation and may transfer files. **Preview changes first** is styled as a smaller optional action, explicitly stating that previewing never modifies files. The preview report is not an execution approval; the sync engine continues to recheck relevant state.

## Dashboard timers and preview presentation (20 October 2026)

The dashboard directly exposes all three real systemd timer intervals: local fallback (5/10/15/30 minutes), priority cloud folders (5/10/15/30/60 minutes), and full cloud scan (30/60/120/180 minutes). Changes apply only when selecting **Save intervals**, with systemd readback and error handling. Local inotify event detection continues independently. Saving intervals is blocked if cloud monitoring was deliberately disabled, avoiding silent reactivation.

The optional **Preview changes first** action is now a compact, explanatory row with a right-aligned secondary button. The primary **Sync now** button remains visually prominent. Previewing never modifies files.

## Dashboard layout: aligned interval selectors (20 October 2026)

The automatic-check interval editor now uses a single GTK card with equal-width, aligned grid columns. The explanation and Save intervals action share a separate footer row. The change is presentation-only; systemd schedules, stored intervals and the sync engine remain unchanged.

## Automatic interval saving (20 October 2026)

Changing any of the three schedule dropdowns **applies the selection immediately** without a Save button. The GUI updates the existing systemd user timers in a background worker and verifies the persisted readback. Inline status shows Applying / Saved; errors restore the last verified selection and display the failure. Changes made while an update is running are coalesced, and initial dropdown population does not trigger writes. Deliberately disabled cloud monitoring is never silently reactivated by selecting an interval.

## Engine portability — controlled source migration (20 October 2026)

The original custom engine scripts are now committed as **non-executable reference sources** under `src/proton_sync_engine/reference/`, with orchestration wrappers under `packaging/reference/`. They are **not yet installed, portable or connected** to the published GUI prototype. A new validated `src/proton_sync_engine/config.py` provides a fail-closed, read-only setup contract; do not run the reference scripts as a standalone sync client. The existing Fedora deployment remains unmodified. See [Engine porting plan](docs/ENGINE_PORTING.md).

**Porting checkpoint (20 October 2026):** The staged runtime candidates use explicit validated paths, but are not wired to the live services or released as an installer. The hourly scan lock-contention false-success bug has been fixed in the existing Fedora wrapper; fresh full-run readback still needs verification. See [ENGINE_PORTING.md](docs/ENGINE_PORTING.md).

**GNOME launcher:** Desktop filename, app ID, startup WM class and SVG icon now match. The installer offers a safe, inert staging preview; installing the sync engine for unrelated users remains unsupported.

**Engineering checkpoint (20 October 2026):** The staged portable full-sync algorithm now passes synthetic upload/download/conflict/retry and combined inert installation lifecycle tests with a mocked cloud. It still requires a verified initial pairing, actual Proton CLI and real independent installation proofs before use with personal data.
