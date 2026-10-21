# Real Proton CLI pairing stale-approval proof – 20 October 2026

**Outcome: PASS for local drift between review and approval; release remains BLOCKED.**

Environment: existing Proton account, actual authenticated CLI, dedicated `/my-files/ProtonSync-Test`, isolated local synthetic file `proton-sync-pairing-check.txt` (104 bytes) and separate private state. No production file tree or unit was modified.

1. Read-only inspection returned `READY_FOR_EXPLICIT_APPROVAL` with one identical file.
2. After review, the existing local synthetic fixture was appended to (temporary local-only content modification).
3. `installer_pairing.approve_pairing` was called with the **previous** review and exact consent phrase.
4. Approval refused with `PAIRING_STALE_OR_CONFLICT`; no baseline was created and no cloud writes occurred.
5. Only the known synthetic fixture was restored to its exact original bytes.
6. A fresh real CLI inspection returned `READY_FOR_EXPLICIT_APPROVAL`, matched=1, differences=0, errors=0, baseline absent.

**Scope:** This proves detection of pre-approval local drift against an actual remote listing. It does **not** prove cross-system atomicity, cloud revision changes exactly during write, or safety of activating synchronization. No baseline was authorized or persisted. Cloud-side concurrency and post-write live fault injection are separate, still-open release gates.
