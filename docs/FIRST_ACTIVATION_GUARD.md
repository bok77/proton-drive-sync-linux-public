# First-start pairing verification gate — 20 October 2026

**Status:** Implemented and synthetic-test proven. **NOT approved for live activation or public release.**

The explicit `installer_pairing.approve_pairing` step now writes a private exclusive `initial_pairing_pending.json` marker linked to the approved SHA-256 review before creating the initial baseline; failed approval removes its own pending marker without leaving an accepted baseline. This does not install or activate any service.

The staged portable full engine now checks for an initial pairing state after mount validation but **before** any state-directory, staging-directory, local-file or cloud-file reconciliation:
- No baseline: exit 42. Baseline without valid pending/verified guard: exit 43, with no cloud request or user-file mutation.
- Pending guard: compare the complete local and remote inventory, SHA-1, file sizes and **cloud revision IDs** with the baseline and explicitly approved snapshot fingerprint. Any change/addition/deletion, malformed guard or scan failure: exit 43 without transfers.
- Matching guard: create a private `initial_pairing_verified.json` file, remove pending guard and **return immediately**. The entire first startup is verification-only: no upload, download, automatic folder creation, quarantine or baseline mutation.
- Later runs require the exact verified marker and no leftover pending marker. Existing standard reconciliation then continues. This is intentionally limited to the first-activation gate, so normal legitimate later edits are not blocked by permanent equality checks.

The runtime staging generator `scripts/stage_portable_runtime.py` regenerates this guard; it is not only a manual patch of a generated artifact. Existing legacy-engine synthetic tests opt out via an injected **test fixture attribute**, not a user-configurable JSON field. The real `RuntimePaths` object cannot set that opt-out.

**Limits:** No atomic snapshot is guaranteed across the real Proton service and Linux. A remote change after the final verification can still happen. There is no proven cross-process locking, immutable baseline provenance or revision-condition API at the synchronization write point. Installation/activation and real destructive tests remain prohibited without a separate approved safety gate. Existing live Fedora user services and personal cloud data were not changed.
