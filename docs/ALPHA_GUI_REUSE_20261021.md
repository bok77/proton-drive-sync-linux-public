# Alpha GUI Integration: Reuse Existing V1 Evidence and GTK Components

Date: 2026-10-21. Status: **code integrated, no real cloud execution authorized**.

The verified V1 wizard already displayed the outcome of an isolated one-shot via `v1_run_result.baseline_lines` and `result_after`. Instead of creating a second result presentation, `run_result_ui.py` now hosts the same `Adw.ActionRow` renderer shared by the existing wizard and the opt-in public-alpha overview.

The opt-in alpha GUI reuses `alpha_lifecycle.install`, `start_once`, and `remove`, behind explicit confirmation dialogs, using only the independent alpha-profile path and the manifest-checked installation prefix determined from the installed application. Each command keeps the existing lifecycle consent and unit checks. The result displays only a new authoritative `run_end` event; a launch acknowledgement does not mean success. The poll times out as UNKNOWN instead of claiming success. Unsupported or absent profiles leave action buttons disabled. The legacy production dashboard/settings are unchanged.

Safety scope: no automatic timer activation, no background running, no production synchronizer requests, no account modification, and no cloud operation was performed in this development step. A portable package, private independent config, validated initial pairing and installed isolated units are prerequisites to a real one-shot. A graphical end-to-end interaction and cloud-transfer proof on an independent test profile remain open before public release.
