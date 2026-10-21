# Public Alpha Readiness Review

Date: 2026-10-21
Decision: **NO-GO pending separate source-publication and executable-release gates**. See [the consolidated scope decision](RELEASE_SCOPE_DECISION_20261021.md) for the current prioritized requirements.

## Evidence reviewed

- Repository remains private; there is no public release authorization.
- MIT license and GitHub CI are present. A real, supervised Fedora GTK-to-isolated-systemd-to-Proton CLI transfer uploaded one synthetic file and downloaded one synthetic file; see `V1_REAL_GUI_CLOUD_E2E_20261021.de.md` (historical German evidence).
- A read-only history audit inspected 474 text blobs across Git history. There were no matches for common private-key headers or token-shaped patterns, no hard-coded `/home/example-user/` strings, and no email-address matches in that scan. A single credential-assignment heuristic matched a source-code blob in `provider_release_gate.py`: **needs human classification**; a regex match is not proof of a leaked secret.
- The tracked filenames/history showed no obvious `.env`, `.pem`, `.key`, or credential-store artifact; this is **not** a substitute for a specialist secret scanner or manual review.

## Blocking decisions

1. Run an independent secret scanner (including Git history) and manually assess all findings before changing repository visibility.
2. Remove machine-specific installation assumptions and ensure the documented package is reproducible for a fresh Fedora installation; do not imply the host's existing production synchronizer is part of a portable install.
3. Audit GUI routes that can control the author's existing production system, and provide a fail-closed, account-agnostic public alpha mode.
4. Document the absence of safe conditional remote updates, unattended-service readiness, and proven provider API fairness. Restrict any eventual public alpha to clearly described test-data scenarios.
5. Complete a Fedora fresh-profile installation/uninstallation exercise, independently review licensing/attribution, and obtain explicit publication approval.

Historical evidence files are retained verbatim. New documentation, docstrings, release decisions, and issues use English; UI translations may remain German/English.

## 2026-10-21 security and runtime update

Read `RELEASE_SECURITY_AUDIT_20261021.md` and `ALPHA_RUNTIME_SEPARATION_20261021.md`. Current-checkout `detect-secrets` findings are synthetic test data; the Git-history scan has coverage limitations and is not a complete clearance. The `--public-alpha` preview has no sync controls. **Decision stays NO-GO; do not change visibility.**

## Fresh Fedora package smoke test

The built portable package installed to a new temporary VM prefix and passed the localization/backend self-test without creating any user-systemd units. See `FEDORA_FRESH_PACKAGE_PROOF_20261021.md`. This does **not** close the fresh-user sync onboarding gate or grant public release approval.

## Independent alpha profile guard

A read-only independent-profile validator is now available; see `ALPHA_PROFILE_CONTRACT_20261021.md`. No service, account or cloud activation has been enabled. Issue #4 remains OPEN.

## Isolated lifecycle VM proof

The reused alpha service lifecycle completed install → one-shot start request → remove in a disposable Fedora VM with a cloud-free stub. See `ALPHA_ISOLATED_LIFECYCLE_PROOF_20261021.md`. Real alpha GUI-to-cloud and production release are **not** approved.

## Alpha GUI VM smoke proof

The shared GTK result widget and isolated two-tab alpha startup were exercised in the disposable Fedora VM with Xvfb, and a production-dashboard refresh escape was fixed. See `ALPHA_EXISTING_GUI_VM_PROOF_20261021.md`. No cloud authorization or release approval follows.

## Fresh-install, side-by-side update and uninstall VM proof

Manifest-checked installation, duplicate-target rejection, unknown-file deletion protection, side-by-side update and rollback passed in the disposable Fedora VM; see `FEDORA_FRESH_INSTALL_UPDATE_UNINSTALL_20261021.md`. Promotion and a real independently authenticated sync remain blocked.

## Alpha desktop launcher rollback

A separate managed alpha launcher was switched between two verified packages and back on the disposable Fedora VM. See `FEDORA_ALPHA_DESKTOP_PROMOTION_20261021.md`. No production launcher, account, or service was modified; release stays NO-GO.

## Final gate consolidation (21 October 2026)

`RELEASE_SCOPE_DECISION_20261021.md` distinguishes the blockers for making source public from the stricter requirements for distributing a working syncing alpha. Older sections above are a historical trail, not additional independent mandatory gates. The cloud-free GTK GUI/systemd/result proof and Fedora package/launcher rollback proofs are accepted; do not recreate them.

## Source-publication audit checkpoint

See `SOURCE_PUBLICATION_REVIEW_20261021.md`. Current README routes are generalized but historical Git privacy clearance is still pending. Repository visibility remains PRIVATE.

## Completed independent secret scan

Gitleaks v8.30.1 passed a 119-commit Git history scan, no findings; see `GITLEAKS_HISTORY_SCAN_20261021.md`. Manual history privacy review and explicit public-visibility approval are still required.

## Historical metadata decision pending

The bounded human-readable historical privacy review found workstation paths and named cloud-folder examples in old Git blobs. See `HISTORICAL_PRIVACY_REVIEW_20261021.md`. Publication remains blocked until the owner decides whether to accept this exposure or authorize a history rewrite.
