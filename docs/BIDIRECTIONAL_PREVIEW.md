# Bidirectional change preview: capabilities and safety

The **Analyze changes on both sides** action reads the complete cloud inventory and local files against the last verified common-ancestor baseline. It proposes uploads, downloads, conflicts, and pending local/cloud deletions. No cloud or local user document is modified. The private report is stored at `~/.local/state/proton-bisync/bidirectional_preview.json` with 0600 permissions.

An incomplete cloud scan or baseline drift blocks the preview. A preview is a time-sensitive snapshot, **not** approval to execute actions: actual transfers must recheck local file hashes and remote revision IDs. Destructive operations still require the existing safety delay and quarantine/trash policy.

Known gaps: empty folder changes, folder moves, and complex cloud move pairing are not a complete plan yet. Reconciliation may change after the snapshot. The full scan of approximately 500+ cloud directories can require 20–25 minutes; the GUI runs it in a background thread, without pretending a numeric percentage exists for the inventory phase.

Automated pure and synthetic end-to-end tests plus a real **00_Inbox-only** cloud readback passed. A complete live full-cloud preview has **not yet been verified**, and public release remains blocked pending full-scale validation.
