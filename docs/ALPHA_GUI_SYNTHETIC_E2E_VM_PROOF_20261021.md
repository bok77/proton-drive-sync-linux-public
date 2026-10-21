# Independent Alpha GUI Synthetic End-to-End Proof — 2026-10-21

**ACCEPTED for cloud-free GTK/systemd/evidence integration only. NOT a cloud transfer proof.**

The existing Fedora VM (`mvptest`, `VM_TEST_ONLY_NO_CLOUD`) ran the reused GTK4/libadwaita alpha GUI under Xvfb with an independent private alpha profile, a manifest-checked disposable runtime stub, and real user systemd. The existing `alpha_lifecycle`, `user_service_lifecycle`, `v1_run_result`, and shared result row were reused. The stub wrote a new synthetically generated `run_end` to the independent test event log; it did not contact Proton Drive or transfer any files.

The actual interactive GTK confirmation flow was exercised for each operation. Cancellation was checked before approval. Authoritative outputs:

- `ALPHA_GUI_PROFILE_AND_REUSED_RESULT_PASS`
- `ALPHA_GUI_INSTALL_PASS`
- `ALPHA_GUI_VERIFIED_RUN_END_PASS` — displayed synthetic `uploaded=2`, `remote_downloaded=1`, `conflicts=0`, `errors=0`, using the existing result reader rather than treating a start request as completion
- `ALPHA_GUI_REMOVE_PASS`
- `ALPHA_GUI_VM_JOURNEY_PASS`
- Exit status `0`; isolated test service and timer files removed, test profile removed.

The probe is `scripts/probe_alpha_gui_journey_vm.py` and refuses execution outside the marked VM. Earlier attempts identified a test-harness dialog-selection problem: an informational notice persisted after the install operation, so the test now selects only confirmation dialogs by heading. A failed intermediate attempt left a test unit, and a separate marker-checked VM-only cleanup removed exactly the two isolated units; the final accepted run completed cleanup automatically.

**Remaining release gates:** real independently authenticated alpha profile, genuine file transfer and failure cases, installation/uninstall on a fresh Fedora profile, second independent history-aware secret scan, provider API safety assessment, and explicit public release approval. The existing host production synchronizer and account were never accessed by this proof.
