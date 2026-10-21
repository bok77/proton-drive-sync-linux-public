# Fedora Alpha: Fresh Installation, Staged Update and Uninstall (2026-10-21)

**Result: PASS for the cloud-free package lifecycle; public release NOT APPROVED.**

## Reused building blocks

The existing `build_fedora_mvp.py`, `install_fedora_mvp.py` and `uninstall_fedora_mvp.py` already implement manifest SHA-256 verification, refusal to overwrite installations, refusal to delete unknown files, and safe removal of unchanged candidate-only files. No duplicate installer or uninstaller was built.

The small `stage_fedora_mvp_update.py` adapter verifies the current installation and stages the next verified package in a distinct sibling directory. It does not modify the existing package, switch desktop launchers, activate or stop systemd services, or delete old versions. Explicit promotion of a staged version remains a separate release decision.

## Disposable Fedora VM evidence

Using the existing disposable Fedora VM (`mvptest`, `VM_TEST_ONLY_NO_CLOUD`) and a fresh temporary home directory, `scripts/probe_fedora_fresh_install_vm.py` verified:

- `FEDORA_FRESH_INSTALL_SELFTEST_PASS`: fresh install, integrity readback, `L10N_OK 62` and `BACKEND_OK 5`.
- `FEDORA_OVERWRITE_DENIED_PASS`: duplicate destination refused.
- `FEDORA_UNKNOWN_FILE_GUARD_PASS`: unrecognized files prevent uninstall and remain intact.
- `FEDORA_FRESH_UNINSTALL_PASS`: clean candidate removal without removing the independent profile directory.
- `FEDORA_PRODUCTION_UNIT_FENCE_PASS`: no changes to pre-existing production unit-file contents.

Separately, the real VM verified side-by-side update and rollback:

- `FEDORA_VM_SIDE_BY_SIDE_UPDATE_PASS`
- `FEDORA_VM_UPDATE_ROLLBACK_PASS`

The existing GTK/systemd/synthetic-result journey was already accepted separately in `ALPHA_GUI_SYNTHETIC_E2E_VM_PROOF_20261021.md`; there is no need to rebuild another GUI or result processor.

## Still open

This is not a live Proton Drive transfer or an unattended-sync test. A generally usable fresh-installation setup flow, authenticated independent account integration, verified package promotion/desktop switch, provider API usage guardrails, and a post-promotion rollback acceptance remain pending. The repository must stay private until the independent security and public release gates are complete.
