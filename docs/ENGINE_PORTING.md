# Engine porting / Developer Preview gate

**Status: PORTING IN PROGRESS — NOT INSTALLABLE — NOT RELEASE APPROVED.**

This directory now contains non-executable, source-only snapshots of the custom synchronization scripts running on the Fedora development workstation, captured on 2026-10-20. They are reference implementation material, not a second operational engine. The live user's installation under `~/.local/bin` and its systemd units were not replaced.

## Reference inventory

- Full common-ancestor reconciliation: `proton-bisync.py`
- Local incremental check: `proton-bisync-quick.py`
- Selected remote-folder polling: `proton-cloud-priority.py`
- Verified and atomic downloads: `proton-verified-download.py`
- Conservative rename / delayed trash logic: `proton-sync-reconcile.py`
- Linux inotify watcher and persistent SQLite queue: `proton-sync-watcher.py`, `proton-sync-queue.py`
- Exclusions, progress, health, local preview and status: related `proton-*.py` files
- Staged run wrappers: `packaging/reference/*.sh`

No Proton credentials, CLI executable, personal documents, sync baseline, device state or local event log is included.

## Blocking work — order matters

1. **Break dependency on developer filesystem paths.** Replace all `/mnt/example-drive`, `~/.local/bin`, repository-specific paths and assumed top-level folder names with a validated explicit installation configuration. Config must reject absent mounts, symlink escapes, unsafe state locations, and relative paths. A starting `src/proton_sync_engine/config.py` provides a read-only safety gate but is not yet wired into the engine.
2. **Consolidate imports and packaging.** Convert runtime-loaded standalone scripts into a proper installable Python package; remove direct imports from a user's home directory; use an external official Proton Drive CLI supplied by the user. Ship no authentication data or vendor binary.
3. **Make activation an explicit operator action.** A portable installer must first display intended local and cloud roots, exclusions, service schedules, and operation modes, then require explicit approval. Never create a fresh accepted baseline merely because two locations contain files.
4. **Preserve fail-closed behavior.** Test mount loss, path traversal/symlinks, concurrent edits, downloads interrupted mid-write, offline/retry, journal replay, stale baseline, credentials failure, folder deletion/move and trash recovery, against disposable synthetic data.
5. **Independent host proof.** Clean install, initial pairing, GUI startup, sync, restart, disable/uninstall and preservation of unrelated data on a fresh Fedora installation. Subsequent Ubuntu/Debian/openSUSE community validation is explicitly unproven.
6. **Release mechanics.** CI runner with headless core tests, Linux GTK integration tests, reproducible versioned installer, security scan, upstream license/trademark check, CHANGELOG, release notes, and explicit release gate.
7. **Public Developer Preview and communication.** Keep experimental / synthetic test data warnings; after verifying a public GitHub URL, obtain recipients and email approval and send the link as documented in `docs/RELEASE_COMMUNICATION.md`.

## Boundaries

The current `install-preview.sh` is **GUI-only** and must not be described as a complete installer. The reference scripts are kept at mode 0644 and are not wired into any systemd service. The existing Fedora installation remains the production baseline and must not be silently replaced.

**Go/no-go:** This milestone records source migration inventory and config validation only. It **does not** approve running, installing, or publishing this engine as functional portable software.

## Step 2: staged path-decoupled runtime candidates (20 October 2026)

Twelve **non-executable** runtime candidates now live under `src/proton_sync_engine/runtime/`, reproducibly transformed from frozen reference sources by `scripts/stage_portable_runtime.py`. They load sibling modules instead of `~/.local/bin`, replace fixed Fedora roots with explicit validated `local_root`, `mount_root`, `state_dir`, and `cli_executable`, and read managed / priority cloud folders from an explicitly provided configuration.

`portable_paths.py` requires `PROTON_SYNC_CONFIG` pointing to a private (0600) JSON file and rejects unsupported paths and folders. These are not operationally accepted: **no installer, first pairing, production runtime wiring or independent end-to-end proof exists yet**. All active Fedora systemd units continue using only the original `~/.local/bin` production scripts.

Separately, the production full-run lock bug was fixed: `flock -E 0 -n` previously skipped a full scan and falsely exited successfully on lock contention. The full run now waits up to 1800 seconds and exits 75 on lock timeout. Regression tests exercise real lock contention. Its next live full `run_end` proof remains pending.

**Next gate:** controlled runtime entry points, full installer/initial-pairing configuration and generated systemd units; isolated synthetic end-to-end tests (install, restart, recovery, uninstall), without replacing the current Fedora deployment.

## Inert installer preview and GNOME launcher (20 October 2026)

`src/proton_sync_engine/install_plan.py` supports a read-only installation plan and staging of three intentionally unstartable systemd templates in a new isolated directory. Every template has both `ExecCondition=/usr/bin/false` and `ExecStart=/usr/bin/false`. Staging can be read back and verified; only unchanged, recognized staging output can be removed. No live systemd units, baseline, credentials or user files are modified. Real installation, pairing, activation and safe real-service uninstall **remain open release blockers**.

The GNOME launcher filename now matches the application's actual ID: `io.github.protondrivesync.Fedora.desktop`, including consistent icon and `StartupWMClass`. An older own launcher is backed up and migrated; unrelated entries are preserved. Desktop-file validation and startup via `gtk-launch` succeeded on Fedora.

## Explicitly approved isolated installer exercise (20 October 2026)

`src/proton_sync_engine/test_install.py` installs **only blocked service templates** into fresh, separate disposable temporary directories after the exact approval phrase `I APPROVE ISOLATED TEST INSTALL` and verified preview evidence. Existing directories are never overwritten; neither live user-systemd nor the sync runtime is touched. `verify_test_install` checks exact file content, expected names and SHA-256 digests. `uninstall_test` removes only unchanged test-owned files, refusing unknown content.

Synthetic tests exercise approval, rejection, tampering, path isolation and safe teardown. **This is an installer artifact proof, NOT a working cloud synchronization install or end-to-end pairing proof.** Runtime entry points, secure account pairing, real controlled systemd activation and independent Fedora integration testing remain release blockers.

## Synthetic real-engine integration proof (20 October 2026)

`tests/test_portable_engine_e2e.py` now exercises the actual staged `proton-bisync.py` full-reconciliation algorithm using disposable local files and a simulated in-memory Proton CLI. Covered: new/local edited file uploads with metadata readback, new/remote edited file downloads with digest verification, idempotent second runs, concurrent edit conflict protection, failed download preservation, and a combined isolated stage-install → sync → restart → uninstall cycle. The Proton API is **mocked** and no live service, cloud account or personal file is involved.

Fixed a blocking portability bug: the download adapter now uses the explicitly configured `cli_executable`. The runtime generator no longer hardcodes the developer repository location. A missing accepted baseline now exits 42 **before** mount access, cloud inventory or local writes. The portable candidate cannot silently pair to an arbitrary cloud tree.

Still unproven: real Proton CLI compatibility, explicit initial pairing, independently installed and activated systemd units, recoverable delete/rename, large-scale and failure-injection scenarios. This is NOT approval to run on real user data.


## Pairing post-write guard and installer entry point – 20 October 2026

Pairing now re-scans both sides after writing a newly created baseline and revokes that baseline if drift is detected. Rollback only removes the inode this invocation created, protecting concurrently replaced files. Regression tests cover a simulated remote revision change after baseline write.

`src/proton_sync_engine/installer_pairing.py` exposes a read-only installer review and a distinct explicitly approved pairing action via an injected remote adapter. Existing baselines and unsafe private-state permissions are refused. No service activation or real cloud writes are performed.

**Limitation:** These pre/post checks are not a transaction across the Linux filesystem and Proton Drive. A change just after final verification cannot be ruled out with currently proven API capabilities. Independent actual Proton CLI tests, true initial-pairing guards, GUI integration and installation remain open.
