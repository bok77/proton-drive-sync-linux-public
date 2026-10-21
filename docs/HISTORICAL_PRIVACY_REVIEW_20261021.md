# Historical Git Privacy Review — 2026-10-21

**Outcome: conditional NO-GO for public visibility, pending the owner's explicit decisions.** This is not a finding of exposed authentication secrets.

## Scope and method

Reviewed the entire reachable Git history (120 commits at the checkpoint) and the currently tracked source/documentation file inventory. Searched historical blobs for machine-specific paths, named cloud directories, email patterns, private-key headers, and IPv4 literals, without extracting any token or account content.

- Commit authors/committers: one author identity with a human-readable full display name and a GitHub `noreply` email. The name would become public with the commit history. Public GitHub visibility must not be enabled without the owner's acceptance of that metadata.
- Historical blobs with local workstation mount/path patterns: **78 matches** (counts are historical object occurrences, not distinct sensitive files).
- Historical blobs with named cloud-folder examples: **60 matches**. These refer to actual configuration examples in code, tests, and engineering notes. Exposing names might reveal the owner's personal workflow or folder organization; they are not proven credentials.
- Historical blobs containing `/home/...` path patterns: **10 matches**, associated with prior release-readiness documentation that quotes an old path as a blocked privacy example.
- IPv4 literal matches: **2 blobs**, classified as loopback-only test endpoints in VM documents; no public endpoint observed in this bounded review.
- Historical file contents: **0 email-pattern matches** in the previous content scan, and **0 private-key-header matches** in this review.
- Independent Gitleaks v8.30.1 full Git scan: **0 secret findings across 119 commits** at the preceding checkpoint, documented separately in `GITLEAKS_HISTORY_SCAN_20261021.md`.

## Decisions still required

1. Confirm whether the real display name in Git commit metadata may be public.
2. Confirm whether archived references to workstation mount points and named cloud subfolders may be public. Removing them only from current HEAD does **not** remove historical revisions. A complete sanitization would require a separately approved rewrite of Git history, which can change commit IDs and require coordinated force-pushes.
3. If that historical exposure is unacceptable, choose a controlled history rewrite with backup and post-rewrite rescans. Never silently rewrite or force-push an active repository.
4. Retain the distinction between publicly viewable experimental source and a runnable supported sync client; the latter requires separate acceptance.

**Current decision: PRIVATE remains enforced.** A zero-finding secret scan is necessary evidence, not blanket approval to publish personal configuration history.

## Subsequent owner decision

The owner wants the real author name retained, but does **not** accept exposure of personally attributable computer/software configuration through public history. A separate private publication candidate and reviewed sanitization are required. This remains PLAN ONLY; see `PUBLIC_HISTORY_PRIVACY_SANITIZATION_PLAN_20261021.md`.
