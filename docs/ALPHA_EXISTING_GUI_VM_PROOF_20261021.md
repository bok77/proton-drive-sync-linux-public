# Reused Alpha GUI — Disposable Fedora VM Proof (2026-10-21)

**PASS — GTK integration smoke only; no cloud operation.**

## Reused implementation

The alpha UI uses `run_result_ui.make_result_row()` and `show_result()`, the same shared result component used by the existing V1 setup wizard, with the original `v1_run_result` evidence reader. It delegates install/start/remove to the existing `alpha_lifecycle` and systemd controller rather than creating a new sync engine or result processor.

## Defect fixed

The opt-in `--public-alpha` window previously fell through `Window.refresh()` into production `backend.snapshot()` and production-only GTK widgets. A mode guard now returns before accessing those controls. The legacy production mode is unchanged. The guard is covered by `tests/test_public_alpha_preview.py`.

## VM proof

Executed `scripts/probe_alpha_existing_gtk_vm.py` under `xvfb-run` on the marked disposable Fedora VM, as user `mvptest`, using GTK4/libadwaita and the updated application sources. Outputs:

- `ALPHA_REUSED_GTK_WINDOW_PASS` (exactly the isolated overview and settings tabs)
- `ALPHA_REUSED_RESULT_ROW_PASS` (existing result row is present)
- `ALPHA_NO_PRODUCTION_WIDGETS_PASS` (no production watcher control; alpha refresh is safe)

This test did not create a profile, install or activate units, authenticate, transfer files, or access Proton cloud. The separate earlier cloud-free real-systemd lifecycle proof is documented in `ALPHA_ISOLATED_LIFECYCLE_PROOF_20261021.md`.

## Remaining gate

A full interactive GUI action sequence with an independently configured account and an authoritative post-run `run_end` still requires a separate accepted proof. No public release or actual cloud operation is approved by this check.
