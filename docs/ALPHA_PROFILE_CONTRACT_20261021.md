# Independent Alpha Profile Contract — 2026-10-21

This is an incremental, read-only implementation for Issue #4, **not** a public cloud-sync activation.

`proton_sync_engine.alpha_profile` checks an explicitly separate private profile directory (`~/.config/proton-drive-sync-alpha/alpha-profile.json`), rather than adopting the owner's historical `~/.config/proton-sync-isolated` profile or the existing production `proton-bisync` configuration. It reuses `portable_paths.load_paths()` and `config.validated_config()` to reject unmounted paths, symlinks, missing CLI executables and invalid managed folders. It additionally requires local/state paths to remain inside the current user's home directory and accepts only the single synthetic root `ProtonSync-Test`. The state directory must not be contained within the synchronized file tree. Private permissions and current-user ownership are required.

The explicit `--public-alpha` preview now displays only `configured but inactive` or `not configured`, with no sensitive paths, service activation, CLI invocation, credentials, or test data. This status is deliberately **not** a claim that authentication, account separation, cloud support, or run-safety is proven.

Test coverage: valid private profile, missing profile, foreign managed folder, world-readable configuration, symlinked file and state-in-sync-tree rejection. The synthetic unit fixture bypasses the real mountpoint check only for path-validation tests; production code continues to enforce the actual mounted boundary.

**Still OPEN:** independent profile creation/approval UX, runtime installation from a configurable package root, isolate-only systemd lifecycle under a fresh Fedora profile, functional transfer evidence, recovery, and user acceptance. No public release approval.
