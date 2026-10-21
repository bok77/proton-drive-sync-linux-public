# Independent Alpha Lifecycle — Fedora VM Proof (2026-10-21)

**Scope: isolated control flow PASS; portable cloud transfer still OPEN.**

`src/proton_sync_engine/alpha_lifecycle.py` delegates `status`, `install`, `start_once`, and `remove` to the existing `user_service_lifecycle` implementation. Before forwarding any operation, it reloads the independent alpha profile, verifies the package integrity and exact isolated unit identities, and rejects packages placed inside synchronized files or state. All mutations require the already existing exact consent strings. It cannot select the historic production sync service or timer names. The existing owner's desktop behavior remains unchanged.

The disposable Fedora 44 VM probe `scripts/probe_alpha_lifecycle_vm.py` uses the exact marker `VM_TEST_ONLY_NO_CLOUD` and user `mvptest`, synthesizes only a private test profile and a manifest-checked cloud-free runtime stub, then drives **real user-systemd**: `install → start_once → remove`. The recorded outputs were `ALPHA_REAL_SYSTEMD_INSTALL_PASS`, `ALPHA_REAL_SYSTEMD_START_REQUEST_PASS`, `ALPHA_REAL_SYSTEMD_REMOVE_PASS`, `ALPHA_VM_CLOUDFREE_LIFECYCLE_PASS`. Cleanup checked that neither isolated service nor timer was left installed. No CLI credentials, provider access, personal sync content, or production unit writes occurred.

The VM profile reader was replaced by a controlled synthetic fixture solely for this proof; the underlying existing lifecycle still performed its own config, manifest, pairing and systemd checks. The production alpha profile validator was tested separately and continues to enforce real mounted filesystems.

**Release restrictions:** The alpha user interface does not yet expose these mutating operations. A start request is not proof of completion. This does not authorize ongoing cloud sync or unattended timers. A fresh-profile GUI integration, result evidence, auth isolation, provider usage review, rollback, and explicit publication approval remain mandatory. Issue #4 remains OPEN.
