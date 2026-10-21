# Final source-release review — 2026-10-22

**Decision: CONDITIONAL GO for a source-only public candidate after explicit owner signoff; NO-GO for a runnable syncing alpha or unreviewed legacy UI use. No publication was performed.**

## Privacy review

The sanitized candidate has one new root commit; none of the original private Git history is reachable. All 277 tracked files were inventoried for former private mounts, real home paths, specific personal cloud folder names, private addresses and home-router domain, hardware-identifying model strings, and owner names in file contents. Results were zero for actual environment indicators. One hardware-keyword match in the sanitization policy merely lists forbidden categories, not the owner's hardware. Author display name is preserved intentionally, with GitHub noreply email. Automated pattern coverage cannot guarantee that all inferable context is absent.

## License and provenance review

`LICENSE` contains the MIT license. `lafontaj/proton-drive-cli-sync` is credited in README as architectural inspiration rather than a copied source. The public upstream repository displays an MIT license. The 16 archived `src/.../reference` and `packaging/reference` files were individually inventoried and show no license/SPDX/copyright headers or source-URL provenance assertions. No vendored library was identified through import and path inspection. Python desktop runtime relies on system-provided PyGObject, GTK4/libadwaita, with systemd/Proton CLI as external dependencies; dependency licenses are not relicensed by the repository's MIT license.

A forensic source-to-source similarity comparison and independent legal clearance of contributor provenance have **not** been performed. Therefore the audit cannot certify that no third-party code was ever copied. If that level of assurance is required, resolve provenance prior to publication. The repository's README statement that no source files were copied reflects project records, not forensic proof.

## Functional and documentation evidence

Existing private Fedora VM smoke and full synthetic GUI journey passed on this sanitized source candidate before the final README-only edit. Unit suite passed 461/461 after those edits. README local link check found zero broken paths. README instructs the isolated `--public-alpha` path only, expressly warning against the unflagged legacy route. Gitleaks v8.30.1 returned zero findings. These checks do not prove a real independent Proton account transfer or unattended safe bidirectional operation.

## Required publication controls

- Publish **only the isolated one-commit sanitized candidate** in a newly created repository, not the existing private repository or its prior history.
- Preserve the original Git bundle privately and do not upload private operational evidence or account data.
- Explicitly describe the output as *experimental source*, not a supported sync application or executable alpha release.
- Obtain explicit owner acceptance of the retained author display name and remaining general technology disclosure before setting any repository PUBLIC.
- Re-run full history-aware secret check and CI if modifying the final candidate; never claim stronger license/provenance verification than completed.
