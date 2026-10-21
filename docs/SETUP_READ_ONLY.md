# GNOME setup – authentic read-only inspection (20 October 2026)

The Setup tab now accepts an explicit private test configuration JSON path (0600). It invokes `proton_sync_engine.test_cloud_adapter.inspect`, performing cloud `filesystem list` against the configured external test CLI and reading the chosen local test tree. It shows actual counts of identical files, differences and errors, plus up to 30 per-file findings. No sample counts are shown after pressing the inspection button.

The test adapter blocks the workstation's production `/mnt/example-drive` sync root and the personal `~/.local/bin` Proton CLI. It uses an explicitly configured external test CLI executable; it does not log in, install services, save a baseline, upload, download or enable pairing. A test account is required to see real cloud results, and no actual test account has been connected yet.

The approval button remains disabled. The developer-preview setup must not be used as a live installer. Review of authentication isolation, path scope, account ownership, Cloud API semantics and concurrency still blocks release.

## Existing-account test-folder policy (20 October 2026)

A new Proton account is not mandatory. The read-only Setup inspection permits the existing CLI session, but enforces exactly `/my-files/ProtonSync-Test` and refuses the production local sync root. The test folder must be explicitly created and populated with synthetic files; no automatic cloud mutation is performed. This is an application-level guard, **not an account-level permission sandbox**. The approval button remains disabled and write tests require an independent go/no-go decision.
