# Release scope and remaining gates — 2026-10-21

Decision: **Do not change repository visibility or publish binaries yet.** The scope must distinguish source visibility from software safety.

## Gate A — Public SOURCE repository (no usable sync release)

**Mandatory before making GitHub PUBLIC:**
1. **#2:** Independently scan full Git history with a Git-aware secret scanner; review repository metadata, commit identities, docs and artifacts for personal information. Resolve findings privately. The earlier `detect-secrets` blob export does not fully establish history coverage.
2. **#5:** Remove or clearly mark machine-specific examples and all operational instructions that could accidentally operate an existing production synchronizer. Confirm third-party attribution and MIT license scope; clearly label the repository **experimental source only / no supported package**.
3. Explicit owner approval to change visibility. Do not infer approval from requests to prepare the release.

**Not a prerequisite for publishing explicitly non-operational source:** real cloud transfer, automatic cloud polling, full GTK accessibility signoff, cross-distribution support, active service migration, photo synchronization, or completing every edge-case sync test. These remain important for a usable binary release, not publication of clearly labelled source.

## Gate B — Public experimental Fedora ALPHA binary / working sync

In addition to Gate A:
1. **#3/#4:** Prove a fresh Fedora user's full isolated profile onboarding, genuine independently authenticated synthetic-folder transfer, and recoverable uninstall. The cloud-free GUI-to-systemd-to-`run_end` proof is accepted but cannot substitute for a real transfer.
2. Confirm restricted folder scope, reliable results, no unauthorized overwrites/deletions, and explicit consent before any service start; document safe failure/rollback and provider CLI constraints.
3. Test a usable packaged alpha on the target Fedora version with reproducible installation, no inherited developer-machine state, accurate documentation, and a tagged release candidate.
4. Explicit separate approval to publish executable artifacts.

**Deferred beyond a narrowly scoped, supervised Fedora alpha:** full unattended bidirectional sync, safe replacement of existing remote revisions, full multi-distribution coverage, real-time cloud push monitoring, and Proton Photos (V2 #1). Never advertise unsupported features.

## Existing evidence — avoid duplicate work

- Shared GTK result presentation, isolated lifecycle, and synthetic VM GUI journey: `ALPHA_GUI_SYNTHETIC_E2E_VM_PROOF_20261021.md`.
- Fresh install, intact-package uninstall, side-by-side staging: `FEDORA_FRESH_INSTALL_UPDATE_UNINSTALL_20261021.md`.
- Isolated desktop launcher promotion/rollback: `FEDORA_ALPHA_DESKTOP_PROMOTION_20261021.md`.
- Existing supervised, machine-specific single real file transfer: `V1_REAL_GUI_CLOUD_E2E_20261021.de.md`; this does **not** independently validate a new user/account.
- Partial scanner report: `RELEASE_SECURITY_AUDIT_20261021.md`.

## Execution order and stop conditions

**Next:** finish #2 history privacy review → finish the source-publication documentation portion of #5 → owner Gate A decision. Then, only if a usable binary release is desired, complete the actual missing integration in #3/#4 and owner Gate B decision. Do not build a new GUI, result parser, or installer. Do not activate services or touch a real Proton account without explicit per-run authorization.

## Owner privacy decision (21 October 2026)

**Mandatory:** preserve the author name while removing unnecessary evidence of the owner's real private software, computer, installed service setup and cloud-folder organization from any public history. Preparation must use an isolated PRIVATE candidate with backup/restore checks; no rewrite or visibility change is authorized. See `PUBLIC_HISTORY_PRIVACY_SANITIZATION_PLAN_20261021.md`.
