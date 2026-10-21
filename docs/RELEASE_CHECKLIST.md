# Public release gate (English)

Status: **NOT APPROVED FOR PUBLIC RELEASE**. Source visibility and executable alpha release have **separate** gates; the current decision and precedence are in [RELEASE_SCOPE_DECISION_20261021.md](RELEASE_SCOPE_DECISION_20261021.md). Historical checklist items below refer to different release scopes and should not be treated as cumulative blockers to publishing clearly labelled experimental source.

The current repository contains a GNOME UI alpha and a read-only adapter for the existing local Fedora installation. The production synchronization engine is still separate.

## Current evidence snapshot (2026-10-21)

- [x] Isolated Fedora VM candidate bundle install and `--self-test` completed without activating systemd services ([proof](FEDORA_FRESH_PACKAGE_PROOF_20261021.md)).
- [x] Explicit `--public-alpha` informational preview path added without existing production control buttons ([design record](ALPHA_RUNTIME_SEPARATION_20261021.md)).
- [x] Current-worktree secret scan and initial history review performed ([security audit](RELEASE_SECURITY_AUDIT_20261021.md)).
- [x] Independent history-aware secret scan (Gitleaks v8.30.1, 119 commits, zero findings).
- [ ] Manual historical privacy review and public author-name acceptance.
- [ ] Validate full fresh-user onboarding, safe sync runtime, and clean uninstall/rollback.
- [x] Verify the public-alpha GTK view in the isolated Fedora VM; see `ALPHA_EXISTING_GUI_VM_PROOF_20261021.md` and the full synthetic GUI journey `ALPHA_GUI_SYNTHETIC_E2E_VM_PROOF_20261021.md`. The earlier host-only test-harness segfault does not invalidate the VM acceptance.
- [ ] Confirm the public README and license obligations with a second reviewer.
- [ ] Obtain explicit authorization to change the repository visibility to PUBLIC.

## Fresh Fedora package lifecycle (21 October 2026)

- [x] Fresh VM installation and package self-test, without unit activation.
- [x] Refuse installation overwrite and removal of unknown files.
- [x] Stage a new version beside the existing verified package without replacing it.
- [x] Remove the staged version and verify the previous version remains intact.
- [x] Isolated alpha-only desktop launcher promotion and rollback in disposable Fedora VM ([proof](FEDORA_ALPHA_DESKTOP_PROMOTION_20261021.md)).
- [ ] Real interactive desktop acceptance and safe migration/rollback if any activated systemd service is wired to a new package.
- [ ] Independently authenticated real alpha-profile transfer on a fresh Linux user profile.

See [Fedora lifecycle evidence](FEDORA_FRESH_INSTALL_UPDATE_UNINSTALL_20261021.md).

## Mandatory acceptance criteria

- [ ] Install, configure, update and uninstall on a clean Fedora machine, with no hard-coded username, root path or account.
- [ ] Package the independently tested two-way engine and the official Proton Drive CLI integration.
- [ ] Automated positive and negative cases: concurrent edits, rename and move, cloud/local deletion, offline/online, symlinks, unreadable paths, mount loss, partial file, queue overflow, crash and restart.
- [ ] Prove all deletions are recoverable and never triggered by missing mounts.
- [ ] Repeat full reconciliation and verify no data loss on representative synthetic trees.
- [ ] Security review for subprocess calls, path traversal, symlinks, untrusted filenames and credentials.
- [ ] GNOME visual and accessibility approval; test German and English at narrow window sizes.
- [ ] CI, documentation, code scanning, tagged releases and reproducible installation.
- [ ] Confirm upstream licenses and trademark attribution.
- [ ] Final explicit release approval.

No third-party data is committed. Public GitHub visibility must not be enabled before approval.

## Linux and cloud monitoring release requirements / Freigabeanforderungen
- [ ] Validate installation and synchronization on at least two additional Linux distributions; Fedora is currently the only tested distribution. Invite community reports using `.github/ISSUE_TEMPLATE/distribution-test.md`.
- [ ] Validate cloud change monitoring beyond priority folders; either keep documented, verified polling or prove a supported event/change-feed alternative before claiming real-time cloud monitoring.

## Mandatory post-release communication
- [ ] Verify the public GitHub release/repository URL.
- [ ] Confirm recipients and email content with the project owner.
- [ ] Send the link by email, verify the send result.
- [ ] See docs/RELEASE_COMMUNICATION.md.

## Engine import checkpoint (20 October 2026)
- [x] Inventory and preserve the running engine source in non-executable reference files, without transferring credentials or device state.
- [x] Add a first fail-closed validation layer for explicitly configured paths and mount boundaries, with synthetic tests.
- [ ] Replace all fixed Fedora paths and dynamic home-directory imports, then wire the portable runtime.
- [ ] Install, operate and safely remove the runtime on an independent test installation.

## 09:00 lock contention and runtime-path checkpoint (20 October)
- [x] Detect and correct falsely successful full-scan lock skips; wait for the lock and report a nonzero timeout.
- [x] Stage non-executable portable runtime candidates using explicit validated paths instead of fixed developer paths.
- [ ] Verify a new full-cloud `run_end` after the contention fix.
- [ ] Complete an independent installable and tested runtime before public release approval.

## Isolated installer proof (20 October 2026)
- [x] Explicit opt-in and test-only blocked service templates.
- [x] Strict preservation of unrelated directories, hash readback and guarded removal.
- [ ] Operational cloud sync E2E with synthetic inputs, safe pairing and user service activation on a separate machine.

## Synthetic portable-engine integration checkpoint (20 October 2026)
- [x] Mocked-Proton-CLI tests of actual staged full reconciliation, local/cloud changes, new files, digest/readback and idempotency.
- [x] Conflict and network failure are fail-closed; missing baseline blocks before any cloud access.
- [x] Combined isolated installer stage, mocked engine run, repeat run and safe teardown.
- [ ] Independent real Proton CLI and user-systemd proof with synthetic test account/data; no release until validated.


## Pairing post-write guard – 20 October
- [x] Pairing rechecks after the exclusive baseline write and rolls back detected drift without deleting unrelated inodes.
- [x] Installer-facing review/approve methods with explicit consent and state permission tests.
- [ ] Prove cross-system race safety, live CLI integration and UI workflow before activation.
