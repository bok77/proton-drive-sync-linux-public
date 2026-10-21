# Public Git History Privacy Sanitization Plan — 2026-10-21

**Decision: mandatory privacy gate, PLAN ONLY. No rewrite, force-push, visibility change, or release is authorized.**

## Objective and disclosure boundary

Keep the author's human-readable name in public commit metadata, while preventing the published repository and its historical commits from needlessly revealing the author's actual private workstation configuration, installed software inventory, hardware, personally named cloud folders, real local sync paths, personal unit schedules, private infrastructure, or deployment topology. Ordinary portable technology requirements (Fedora support, GTK4, Python, Proton Drive integration) can remain. Do not promise complete anonymity: software source necessarily reveals some technology choices.

## Scope of the audit

- Inspect **all refs and reachable historical blobs**, commit messages, author/committer metadata, tags, tracked paths, license/docs, issue/PR attachments and GitHub release assets separately. A source rewrite does not sanitize GitHub issue comments, archives, or existing copies.
- Inventory path and folder strings and classify each occurrence: **generic project contract**, **synthetic test fixture**, **private-machine disclosure**, or **unknown**. Do not publish the raw sensitive inventories in Issues or documentation.
- Inspect relevant scripts and archived reference code for executable host-specific assumptions; preserving public technical functionality is distinct from preserving the original private deployment configuration.
- Extend checks to hardware models, hostnames, usernames, daemon names, local install paths, mount points, service versions, internal addresses, schedules, machine IDs and credentials, even if common token detectors find nothing.
- The previous Gitleaks v8.30.1 pass (119 commits at that time; 0 findings) is evidence against detected secrets, **not** a privacy clearance.

## Safety-first execution plan

1. **Freeze and inventory:** note source commit, branch and refs; capture a verified, private, offline mirror backup outside any public tree. Verify restoration before any rewrite. Do not modify working production code or services.
2. **Create a separate publication candidate:** use an isolated clone / separate new repository, initially PRIVATE. Never rewrite or force-push the existing repository as an implicit step.
3. **Classify and sanitize:** replace real workstation-specific values in source, docs, fixtures, and historical revisions with stable generic examples, preserving functionality where possible. If a path is a runtime dependency, refactor to explicit configuration rather than a superficial text substitution. Retain the author's name but not unnecessary private machine metadata.
4. **Choose a history strategy:** prefer a defensible clean public-history baseline if rewriting every old commit is disproportionately costly or risks incomplete redaction. If meaningful history is retained, use a reviewed history-filtering process in the separate candidate; understand that resulting commit IDs differ. Preserve full original history only in the private repository.
5. **Independent review:** scan the candidate's entire Git history with Gitleaks and a complementary privacy inventory, inspect all public-facing docs and GitHub metadata, verify no sensitive values through manual review, and rerun full unit, packaging, GUI and isolated VM proofs as appropriate.
6. **Release decision gate:** record explicit owner acceptance of any remaining unavoidable technology disclosure and the specific candidate repository/history. Only a separate explicit approval can change visibility or create releases.

## Stop conditions

Stop before publication if private device details remain identifiable, a secret is found, technical behavior is broken by redaction, the backup cannot be restored, candidate refs still reach unreviewed commits, or the owner has not explicitly approved the final disclosure scope.

## Current state

The existing private repository remains authoritative and unchanged. This document does not authorize running any Git history rewrite, force-pushing, replacing repositories, sharing source with third parties, or altering sync services. Next step requires review of the candidate history strategy and privacy classification, not more GUI development.
