# Source-publication review — 21 October 2026

**Decision: NO-GO pending historical privacy acceptance and explicit owner approval. Automated Git-aware scanning passed.**

## Verified

- The repository remains private and GitHub CI passed before this review.
- The Git author email uses GitHub's noreply address; the commit author name is public Git metadata and must be explicitly accepted by the owner.
- The tracked project has an MIT license; the README disclaims Proton affiliation. This review is not a legal opinion or independent dependency license audit.
- Current top-level English and German READMEs now use generic placeholders instead of examples copied from the workstation's actual directory and cloud routing configuration.
- Prior evidence establishes a supervised synthetic-folder transfer on the existing configured machine and a cloud-free, isolated VM full GUI/systemd/result journey. Neither authorizes a publicly distributed sync binary.

## Unresolved release-blocking privacy checks

- An independent Git-aware secret scanner remains unavailable in the currently authorized environment. The previous `detect-secrets` run and exported-blob pass do **not** establish complete historical clearance.
- Archived Git history and long-form historical engineering reports may contain configuration and account-specific folder names and local deployment topology even when they contain no tokens. README edits cannot erase that history.
- A human must review all historical personal identifiers and configuration examples; any sensitive findings require a deliberate Git-history rewrite/rotation decision before publication, with explicit permission because rewriting history is disruptive.
- Verify attribution and licenses for external dependencies and all bundled runtime components before shipping binaries.

## Remaining work to approve PUBLIC source

1. Complete independent full-history credential and privacy review (#2), classify results privately without echoing values.
2. Confirm repository metadata, documentation, examples, attribution and README safety boundaries (#5).
3. Obtain explicit owner approval to change visibility; only then set the repository to PUBLIC.

Source publication and a working syncing alpha release are distinct gates. Neither unattended syncing nor replacement of existing remote files should be advertised as supported.

## Independent Git-aware scanner update

Gitleaks v8.30.1 scanned all 119 commits and reported zero findings (exit 0). See `GITLEAKS_HISTORY_SCAN_20261021.md`. Historical privacy and author-name acceptance remain independent decisions.

## Manual Git-history privacy checkpoint

Historical configuration examples and commit-name metadata were classified in `HISTORICAL_PRIVACY_REVIEW_20261021.md`. Their public exposure is an owner decision; no Git history rewrite or public visibility change was executed.
