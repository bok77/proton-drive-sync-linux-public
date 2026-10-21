# Fedora Alpha Desktop Promotion and Rollback — 2026-10-21

**ACCEPTED for isolated desktop launcher switching in the disposable Fedora VM. Public release remains blocked.**

`scripts/promote_fedora_mvp.py` registers only a new, explicitly managed `io.github.protondrivesync.Alpha.desktop` entry. A separate consent-gated switch requires two intact, verified sibling bundles and exact matching contents in the previously managed launcher. It uses atomic replacement, leaves both bundles in place, does not change systemd units, and refuses existing unmanaged desktop entries or takeover of an absent launcher. The existing development workstation launcher is never modified by these tests.

The marked Fedora VM exercised initial alpha registration, version 1 → version 2, version 2 → version 1 rollback, preservation of a separate desktop entry, and removal of temporary test bundles. Outputs: `VM_ALPHA_DESKTOP_PROMOTION_PASS`, `VM_ALPHA_DESKTOP_ROLLBACK_PASS`, `VM_ALPHA_PACKAGES_AND_UNRELATED_FILES_PRESERVED_PASS`.

**Remaining release gates:** this is launcher-file promotion, not an authenticated cloud transfer or active-service runtime migration. Real account isolation, provider usage restrictions, and final security review remain open. Never interpret this as approval to change repository visibility or production desktop launchers.
